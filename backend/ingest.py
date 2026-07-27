"""
ingest.py — Indexador multi-manual (FAISS + BM25, 100% CPU).
Este script se encarga de procesar los manuales en formato PDF, extraer su texto por bloques,
generar sus representaciones vectoriales (embeddings) y construir/actualizar los índices de búsqueda.
Incluye control de versiones mediante hash SHA256 para reindexar solo lo que ha cambiado.
"""
import os
import sys
import pickle
import hashlib
import re

import fitz  # PyMuPDF
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

import config


def _file_hash(path):
    """
    Calcula la huella digital (SHA256) del archivo PDF en bloques de lectura.
    Permite detectar al instante si el documento es nuevo, si no ha cambiado o si se ha editado.
    """
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_chunks_from_pdf(path, oficio):
    """
    Extrae el texto de un PDF procesando bloque a bloque en lugar de páginas completas.
    Ordena la lectura de arriba a abajo para no romper oraciones y va agrupando
    el texto en fragmentos (chunks) dentro de los límites definidos en la configuración.
    """
    chunks = []
    doc = fitz.open(path)
    fname = os.path.basename(path)

    for page_num, page in enumerate(doc, start=1):
        # Extraer bloques de texto con PyMuPDF y ordenarlos por posición vertical (y) y luego horizontal (x)
        blocks = page.get_text("blocks")
        blocks.sort(key=lambda b: (round(b[1], 1), b[0]))

        buffer = ""
        for b in blocks:
            text = b[4].strip().replace("\n", " ")
            if not text:
                continue

            # Acumular texto mientras no supere el máximo de caracteres establecido por chunk
            if len(buffer) + len(text) < config.MAX_CHUNK_CHARS:
                buffer = f"{buffer} {text}".strip()
            else:
                if len(buffer) >= config.MIN_CHUNK_CHARS:
                    chunks.append({"text": buffer, "source": fname, "page": page_num, "oficio": oficio})
                buffer = text

        # Guardar el último fragmento sobrante de la página si cumple con el tamaño mínimo
        if len(buffer) >= config.MIN_CHUNK_CHARS:
            chunks.append({"text": buffer, "source": fname, "page": page_num, "oficio": oficio})
        elif buffer:
            # Si es muy pequeño pero hay fragmentos previos en la misma página, lo anexa al último
            if chunks and chunks[-1]["page"] == page_num:
                chunks[-1]["text"] = f"{chunks[-1]['text']} {buffer}".strip()
            else:
                chunks.append({"text": buffer, "source": fname, "page": page_num, "oficio": oficio})

    doc.close()
    return chunks


def _remove_pdf_from_state(path, manifest, metadata, index, model):
    """
    Elimina los fragmentos pertenecientes a un PDF específico de los metadatos.
    Como el índice FAISS FlatIP no admite eliminaciones directas, reconstruye
    el índice vectorial desde cero calculando embeddings solo con el resto de chunks válidos.
    """
    fname = os.path.basename(path)
    oficio = os.path.basename(os.path.dirname(path)) or "general"

    # Filtrar metadatos para conservar únicamente los chunks de los demás documentos
    new_metadata = [
        m for m in metadata
        if not (m["source"] == fname and m["oficio"] == oficio)
    ]

    removed_count = len(metadata) - len(new_metadata)
    if removed_count == 0:
        return metadata, index

    print(f"    [limpieza] Eliminando {removed_count} chunks obsoletos de '{fname}'")

    # Si no quedan manuales en el sistema, devolvemos las listas vacías
    if not new_metadata:
        return [], None

    # Reconstruir el índice vectorial FAISS desde cero con los metadatos restantes
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

    # Reasignar identificadores numéricos correlativos a los metadatos filtrados
    for i, m in enumerate(new_metadata):
        m["id"] = i

    return new_metadata, new_index


def _load_state():
    """
    Carga desde la carpeta de caché el registro de versiones (manifest),
    los metadatos acumulados de los fragmentos y el índice de búsqueda vectorial FAISS.
    """
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
    """
    Guarda en disco el estado actual del manifest, metadatos e índice FAISS.
    Además, tokeniza el texto completo y recompila el índice léxico BM25 para búsquedas por palabras clave.
    """
    with open(config.MANIFEST_PATH, "wb") as f:
        pickle.dump(manifest, f)
    with open(config.METADATA_PATH, "wb") as f:
        pickle.dump(metadata, f)
    if index is not None:
        faiss.write_index(index, config.FAISS_INDEX_PATH)

    # Tokenización optimizada para términos técnicos y palabras compuestas
    from rank_bm25 import BM25Okapi
    tokenized = [
        re.findall(r"[a-zA-Z0-9]+(?:[-_/][a-zA-Z0-9]+)*", m["text"].lower())
        for m in metadata
    ]
    bm25 = BM25Okapi(tokenized) if tokenized else None
    with open(config.BM25_PATH, "wb") as f:
        pickle.dump(bm25, f)


def index_pdfs(pdf_paths=None):
    """
    Función principal de ingestión: explora la carpeta de manuales, detecta altas,
    bajas y modificaciones respecto al estado anterior, genera embeddings y actualiza los índices.
    """
    print(f"Cargando modelo de embeddings ({config.EMBEDDING_MODEL})...")
    model = SentenceTransformer(config.EMBEDDING_MODEL)

    manifest, metadata, index = _load_state()

    # Si no se indica una ruta concreta, se escanean subcarpetas en busca de todos los archivos PDF
    if pdf_paths is None:
        pdf_paths = []
        for root, _, files in os.walk(config.MANUALS_DIR):
            for fn in files:
                if fn.lower().endswith(".pdf"):
                    pdf_paths.append(os.path.join(root, fn))

    # Detectar y purgar manuales que han sido borrados directamente del sistema de archivos
    current_paths_set = set(pdf_paths)
    deleted_paths = [p for p in manifest if p not in current_paths_set]
    for path in deleted_paths:
        print(f"  [eliminado del disco] {os.path.basename(path)}")
        metadata, index = _remove_pdf_from_state(path, manifest, metadata, index, model)
        del manifest[path]

    # Analizar el estado de cada manual en busca de cambios
    new_chunks = []
    for path in pdf_paths:
        h = _file_hash(path)

        # Si el PDF existía pero su hash cambió, se elimina la versión vieja antes de reindexar
        if path in manifest and manifest[path] != h:
            print(f"  [modificado] {os.path.basename(path)}")
            metadata, index = _remove_pdf_from_state(path, manifest, metadata, index, model)
            del manifest[path]

        # Si el hash coincide exacto, el documento se omite para no duplicar ni perder tiempo
        if manifest.get(path) == h:
            print(f"  [sin cambios] {os.path.basename(path)}")
            continue

        # Extraer el oficio a partir de la subcarpeta que contiene el archivo (ej: manuals/fontaneria)
        oficio = os.path.basename(os.path.dirname(path)) or "general"
        print(f"  [indexando] {os.path.basename(path)}  (oficio: {oficio})")
        chunks = extract_chunks_from_pdf(path, oficio)
        new_chunks.extend(chunks)
        manifest[path] = h

    # Si no hubo modificaciones ni archivos nuevos, finalizamos sin reescribir la caché
    if not new_chunks and not deleted_paths:
        print("No hay manuales nuevos, modificados o eliminados. Índice al día.")
        return

    # Procesamiento y cálculo de embeddings para los fragmentos recién extraídos
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

        # Inicializar el índice FAISS con la dimensión del modelo si es la primera vez que se ejecuta
        if index is None:
            dim = vectors.shape[1]
            index = faiss.IndexFlatIP(dim)

        index.add(vectors)

        # Asignar identificadores correlativos a los nuevos fragmentos agregados
        start_idx = len(metadata)
        for i, chunk in enumerate(new_chunks):
            chunk["id"] = start_idx + i

        metadata.extend(new_chunks)

    # Persistir los cambios actualizados en los archivos de caché
    _save_state(manifest, metadata, index)
    print(f"Listo. Índice total: {len(metadata)} fragmentos de {len(manifest)} manuales.")


if __name__ == "__main__":
    # Permite ejecutar el script pasando la ruta de un PDF concreto o ejecutarse globalmente
    if len(sys.argv) > 1:
        index_pdfs([sys.argv[1]])
    else:
        index_pdfs()