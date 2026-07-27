"""
ingest.py — Indexador multi-manual (FAISS + BM25, 100% CPU).

Uso:
    python ingest.py            # indexa/actualiza todos los manuales en MANUALS_DIR
    python ingest.py ruta.pdf   # indexa (o reindexa) un único PDF, para uso desde watcher.py

Diseño:
- Cada PDF se trocea en bloques con PyMuPDF (respeta la estructura del documento,
  igual que la solución que ya validaste contra las alucinaciones del manual Mazda).
- Los embeddings se calculan con sentence-transformers en CPU (no toca la RX 580).
- FAISS guarda el índice vectorial; rank_bm25 guarda el índice léxico.
- Un manifest.pkl guarda el hash de cada PDF ya procesado, así que solo se
  reindexan los manuales nuevos o modificados; el resto no se retoca.
- El "oficio" de cada manual es el nombre de su subcarpeta dentro de manuals/
  (manuals/fontaneria/..., manuals/electricidad/...), para que el prompt de
  consultas pueda filtrar o mostrar el oficio de origen sin asumir uno por defecto.
"""
import os
import sys
import pickle
import hashlib
import re  # [CORREGIDO] para tokenización BM25 mejorada

import fitz  # PyMuPDF
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

import config


def _file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_chunks_from_pdf(path, oficio):
    """Extrae texto por bloques (no por página completa) para mantener coherencia semántica."""
    chunks = []
    doc = fitz.open(path)
    fname = os.path.basename(path)

    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("blocks")
        blocks.sort(key=lambda b: (round(b[1], 1), b[0]))

        buffer = ""
        for b in blocks:
            text = b[4].strip().replace("\n", " ")
            if not text:
                continue
            if len(buffer) + len(text) < config.MAX_CHUNK_CHARS:
                buffer = f"{buffer} {text}".strip()
            else:
                if len(buffer) >= config.MIN_CHUNK_CHARS:
                    chunks.append({"text": buffer, "source": fname, "page": page_num, "oficio": oficio})
                buffer = text

        if len(buffer) >= config.MIN_CHUNK_CHARS:
            chunks.append({"text": buffer, "source": fname, "page": page_num, "oficio": oficio})
        elif buffer:
            if chunks and chunks[-1]["page"] == page_num:
                chunks[-1]["text"] = f"{chunks[-1]['text']} {buffer}".strip()
            else:
                chunks.append({"text": buffer, "source": fname, "page": page_num, "oficio": oficio})

    doc.close()
    return chunks


# [CORREGIDO] Nueva función: elimina un PDF modificado del índice antes de reindexarlo
def _remove_pdf_from_state(path, manifest, metadata, index, model):
    """
    Elimina todos los chunks de un PDF específico de metadata y reconstruye
    el índice FAISS desde cero (IndexFlatIP no soporta eliminación incremental).
    """
    fname = os.path.basename(path)
    oficio = os.path.basename(os.path.dirname(path)) or "general"

    # Filtrar: quedarse solo con chunks de OTROS PDFs
    new_metadata = [
        m for m in metadata
        if not (m["source"] == fname and m["oficio"] == oficio)
    ]

    removed_count = len(metadata) - len(new_metadata)
    if removed_count == 0:
        return metadata, index  # No había nada que eliminar

    print(f"    [limpieza] Eliminando {removed_count} chunks obsoletos de '{fname}'")

    if not new_metadata:
        # Quedó vacío todo el índice
        return [], None

    # Reconstruir FAISS desde cero (no hay delete en IndexFlatIP)
    texts = [m["text"] for m in new_metadata]
    vectors = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True
    )
    vectors = np.asarray(vectors, dtype="float32")

    dim = vectors.shape[1]
    new_index = faiss.IndexFlatIP(dim)
    new_index.add(vectors)

    # Reasignar IDs secuenciales
    for i, m in enumerate(new_metadata):
        m["id"] = i

    return new_metadata, new_index


def _load_state():
    os.makedirs(config.CACHE_DIR, exist_ok=True)

    if os.path.exists(config.MANIFEST_PATH):
        with open(config.MANIFEST_PATH, "rb") as f:
            manifest = pickle.load(f)
    else:
        manifest = {}

    if os.path.exists(config.METADATA_PATH):
        with open(config.METADATA_PATH, "rb") as f:
            metadata = pickle.load(f)
    else:
        metadata = []

    index = None
    if os.path.exists(config.FAISS_INDEX_PATH):
        index = faiss.read_index(config.FAISS_INDEX_PATH)

    return manifest, metadata, index


def _save_state(manifest, metadata, index):
    with open(config.MANIFEST_PATH, "wb") as f:
        pickle.dump(manifest, f)
    with open(config.METADATA_PATH, "wb") as f:
        pickle.dump(metadata, f)
    if index is not None:
        faiss.write_index(index, config.FAISS_INDEX_PATH)

    # [CORREGIDO] Tokenización BM25 mejorada para español/técnico
    from rank_bm25 import BM25Okapi
    tokenized = [
        re.findall(r"[a-zA-Z0-9]+(?:[-_/][a-zA-Z0-9]+)*", m["text"].lower())
        for m in metadata
    ]
    bm25 = BM25Okapi(tokenized) if tokenized else None
    with open(config.BM25_PATH, "wb") as f:
        pickle.dump(bm25, f)


def index_pdfs(pdf_paths=None):
    """Indexa una lista concreta de PDFs, o todos los que haya bajo MANUALS_DIR si no se especifica."""
    print(f"Cargando modelo de embeddings ({config.EMBEDDING_MODEL})...")
    model = SentenceTransformer(config.EMBEDDING_MODEL)

    manifest, metadata, index = _load_state()

    if pdf_paths is None:
        pdf_paths = []
        for root, _, files in os.walk(config.MANUALS_DIR):
            for fn in files:
                if fn.lower().endswith(".pdf"):
                    pdf_paths.append(os.path.join(root, fn))

    # [CORREGIDO] Detectar PDFs que ya no existen en disco (eliminados por el usuario)
    current_paths_set = set(pdf_paths)
    deleted_paths = [p for p in manifest if p not in current_paths_set]
    for path in deleted_paths:
        print(f"  [eliminado del disco] {os.path.basename(path)}")
        metadata, index = _remove_pdf_from_state(path, manifest, metadata, index, model)
        del manifest[path]

    new_chunks = []
    for path in pdf_paths:
        h = _file_hash(path)

        if path in manifest and manifest[path] != h:
            # [CORREGIDO] PDF modificado: limpiar chunks viejos antes de reindexar
            print(f"  [modificado] {os.path.basename(path)}")
            metadata, index = _remove_pdf_from_state(path, manifest, metadata, index, model)
            # El hash viejo se borra para forzar reindexación completa
            del manifest[path]

        if manifest.get(path) == h:
            print(f"  [sin cambios] {os.path.basename(path)}")
            continue

        oficio = os.path.basename(os.path.dirname(path)) or "general"
        print(f"  [indexando] {os.path.basename(path)}  (oficio: {oficio})")
        chunks = extract_chunks_from_pdf(path, oficio)
        new_chunks.extend(chunks)
        manifest[path] = h

    if not new_chunks and not deleted_paths:
        print("No hay manuales nuevos, modificados o eliminados. Índice al día.")
        return

    if new_chunks:
        print(f"Generando embeddings para {len(new_chunks)} fragmentos nuevos...")
        texts = [c["text"] for c in new_chunks]
        vectors = model.encode(
            texts,
            batch_size=32,
            show_progress_bar=True,
            normalize_embeddings=True
        )
        vectors = np.asarray(vectors, dtype="float32")

        if index is None:
            dim = vectors.shape[1]
            index = faiss.IndexFlatIP(dim)

        index.add(vectors)

        # Asignar IDs secuenciales continuando desde donde quedó metadata
        start_idx = len(metadata)
        for i, chunk in enumerate(new_chunks):
            chunk["id"] = start_idx + i

        metadata.extend(new_chunks)

    _save_state(manifest, metadata, index)
    print(f"Listo. Índice total: {len(metadata)} fragmentos de {len(manifest)} manuales.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        index_pdfs([sys.argv[1]])
    else:
        index_pdfs()