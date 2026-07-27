"""
query.py — Motor de búsqueda híbrida.

Uso interactivo:
    python query.py "¿qué hago si salta el DTC P0126?"

Uso como módulo (batch / benchmark):
    from query import answer
    respuesta = answer("¿qué hago si salta el DTC P0126?")
"""
import sys
import os
import pickle
from difflib import SequenceMatcher  # ← AÑADIR ESTA LÍNEA

import faiss
import numpy as np
import httpx
from sentence_transformers import SentenceTransformer, CrossEncoder

import config


# ── Singletons: se cargan una sola vez, la primera vez que se llama answer() ──
_embed_model = None
_reranker_model = None
_metadata = None
_bm25 = None
_index = None


def _load_models():
    """Carga todos los modelos e índices una sola vez (lazy initialization)."""
    global _embed_model, _reranker_model, _metadata, _bm25, _index

    if _metadata is None:

        if (
            not os.path.exists(config.METADATA_PATH)
            or not os.path.exists(config.BM25_PATH)
            or not os.path.exists(config.FAISS_INDEX_PATH)
        ):
            raise FileNotFoundError("No hay ningún índice creado.")

        print("[query] Cargando índice y metadata...")

        with open(config.METADATA_PATH, "rb") as f:
            _metadata = pickle.load(f)

        with open(config.BM25_PATH, "rb") as f:
            _bm25 = pickle.load(f)

        _index = faiss.read_index(config.FAISS_INDEX_PATH)

    if _embed_model is None:
        print(f"[query] Cargando modelo de embeddings ({config.EMBEDDING_MODEL})...")
        _embed_model = SentenceTransformer(config.EMBEDDING_MODEL)

    if _reranker_model is None:
        print(f"[query] Cargando reranker ({config.RERANKER_MODEL})...")
        _reranker_model = CrossEncoder(config.RERANKER_MODEL)

    return _metadata, _bm25, _index, _embed_model, _reranker_model

def hybrid_search(query, embed_model, metadata, bm25, index):
    # --- Léxico ---
    tokenized_query = query.lower().split()
    bm25_scores = bm25.get_scores(tokenized_query) if bm25 else np.zeros(len(metadata))
    bm25_ranked = np.argsort(bm25_scores)[::-1][: config.TOP_K_BM25]

    # --- Vectorial ---
    q_vector = embed_model.encode([query], normalize_embeddings=True).astype("float32")
    _, vec_ranked = index.search(q_vector, config.TOP_K_VECTOR)
    vec_ranked = vec_ranked[0]

    # --- Fusión RRF ---
    scores = {}
    for rank, idx in enumerate(bm25_ranked):
        scores[idx] = scores.get(idx, 0) + 1.0 / (config.RRF_K + rank + 1)

    for rank, idx in enumerate(vec_ranked):
        if idx == -1:
            continue
        scores[idx] = scores.get(idx, 0) + 1.0 / (config.RRF_K + rank + 1)

    fused = sorted(scores.items(), key=lambda x: x[1], reverse=True)[: config.TOP_K_FUSION]

    return [metadata[idx] for idx, _ in fused]


def rerank(query, candidates, reranker_model):
    if not candidates:
        print("[reranker] hybrid_search no devolvió ningún candidato.")
        return []

    pairs = [(query, c["text"]) for c in candidates]
    scores = reranker_model.predict(pairs)

    ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
    print(f"[reranker] {len(ranked)} candidatos (se pasan {config.TOP_K_RERANK} al LLM, sin umbral):")
    for i, (c, s) in enumerate(ranked):
        marca = "-> LLM" if i < config.TOP_K_RERANK else "descartado"
        print(f"  score={s:.3f}  [{marca}]  {c['source']} pág.{c['page']}  -> {c['text'][:80]}...")

    return ranked[: config.TOP_K_RERANK]

def _similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def deduplicate_chunks(chunks_with_scores, threshold=config.DEDUP_THRESHOLD):
    """
    Recibe lista de (chunk, score) ordenada por relevancia.
    Descarta chunks que sean >threshold similares a uno ya aceptado.
    """
    unique = []
    for chunk, score in chunks_with_scores:
        text = chunk["text"]
        if any(_similarity(text, u["text"]) > threshold for u in unique):
            continue
        unique.append(chunk)
    return unique


def expand_neighbors(chunks, metadata):
    """
    Expande vecinos PERO preserva el orden de relevancia del reranker.
    Los chunks originales se presentan primero.
    Los vecinos se añaden al final, ordenados por posición en el documento.
    """
    seen = set()
    primary = []
    neighbors = []

    for chunk in chunks:
        idx = chunk["id"]
        if idx not in seen:
            primary.append(chunk)
            seen.add(idx)

    for chunk in chunks:
        idx = chunk["id"]
        source = chunk["source"]

        for j in (idx - 1, idx + 1):
            if (
                0 <= j < len(metadata)
                and metadata[j]["source"] == source
                and j not in seen
            ):
                neighbor = dict(metadata[j])
                neighbor["_rerank_score"] = None
                neighbors.append(neighbor)
                seen.add(j)

    neighbors.sort(key=lambda x: x["id"])
    return primary + neighbors

def build_prompt(query, chunks, max_chars=15000):
    if not chunks:
        return None

    fragmentos = []
    total_len = 0

    for i, c in enumerate(chunks):
        score_str = ""
        if c.get("_rerank_score") is not None:
            score_str = f" [relevancia: {c['_rerank_score']:.2f}]"

        frag = (
            f"[Fragmento {i+1}{score_str} | manual: {c['source']} | "
            f"pág. {c['page']} | oficio: {c['oficio']}]\n{c['text']}"
        )

        if total_len + len(frag) > max_chars:
            break
        fragmentos.append(frag)
        total_len += len(frag)

    fragmentos_str = "\n\n".join(fragmentos)

    return (
        "Eres un asistente técnico experto. Responde ÚNICAMENTE con información "
        "presente en los fragmentos de abajo. NO inventes causas, valores ni pasos "
        "que no aparezcan en el texto.\n\n"

        "REGLAS OBLIGATORIAS:\n"
        "1. Prioriza los fragmentos por [relevancia: X.XX].\n"
        "2. Los fragmentos sin relevancia son solo contexto adicional.\n"
        "3. Si no hay respuesta explícita, responde exactamente: "
        "'No se encontró información específica sobre esto en los manuales consultados.'\n"
        "4. Cita siempre el manual y la página.\n"
        "5. No repitas información.\n"
        "6. Sé conciso (1-3 párrafos).\n"
        "7. Si hay contradicción, confía en el fragmento de mayor relevancia.\n\n"

        "REGLAS PARA DATOS CRÍTICOS:\n"
        "8. Para tiempos, pares, voltajes, temperaturas, distancias, presiones, cantidades y rutas de menús, copia EXACTAMENTE el valor del fragmento.\n"
        "9. NO combines números o pasos de fragmentos distintos.\n"
        "10. El número, la acción y la condición deben aparecer juntos en el mismo fragmento.\n"
        "11. Si hay varios valores y no puedes determinar cuál corresponde a la pregunta, responde exactamente: "
        "'Los fragmentos contienen varios valores y no es posible determinar con certeza cuál corresponde a esta pregunta.'\n\n"
        "12. La respuesta final debe tener un máximo de 120 palabras, salvo que la pregunta solicite un procedimiento paso a paso claramente presente en los fragmentos."

        "PROCESO INTERNO OBLIGATORIO:\n"
        "A. Identifica el fragmento que responde directamente.\n"
        "B. Extrae literalmente el dato clave.\n"
        "C. Redacta la respuesta usando solo ese dato y su cita.\n"
        "D. Ignora fragmentos que no respondan directamente.\n\n"

        f"FRAGMENTOS RECUPERADOS:\n{fragmentos_str}\n\n"
        f"PREGUNTA: {query}\n\n"
        "Responde en español, de forma clara y concisa, incluyendo la cita correspondiente."
    )
def ask_qwen(prompt):
    payload = {
        "model": config.OLLAMA_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {"temperature": 0,
                    "num_predict": 180,
                    "repeat_penalty": 1.1,
                    "num_ctx": 4096}
    }
    try:
        with httpx.Client(timeout=120) as client:
            r = client.post(config.OLLAMA_URL, json=payload)
            r.raise_for_status()
            return r.json()["message"]["content"]
    except httpx.ConnectError:
        return "Error: No se pudo conectar con Ollama. Verifica que esté corriendo en localhost:11434."
    except httpx.HTTPStatusError as e:
        return f"Error de Ollama ({e.response.status_code}): {e.response.text}"
    except Exception as e:
        return f"Error inesperado: {str(e)}"


def answer(query):
    """
    Función principal. Puede llamarse desde CLI o importarse como módulo.
    Los modelos se cargan lazy (solo la primera vez).
    """
    metadata, bm25, index, embed_model, reranker_model = _load_models()

    candidates = hybrid_search(query, embed_model, metadata, bm25, index)
    ranked_with_scores = rerank(query, candidates, reranker_model)

    deduped_chunks = deduplicate_chunks(
        ranked_with_scores,
        threshold=config.DEDUP_THRESHOLD
    )

    top_chunks = deduped_chunks[:config.TOP_K_FINAL]

    chunks = expand_neighbors(top_chunks, metadata)

    prompt = build_prompt(query, chunks)

    if prompt is None:
        return "No se encontró ningún fragmento relevante en los manuales indexados para esta pregunta."

    return ask_qwen(prompt)

# ── CLI: solo si se ejecuta directamente ──
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python query.py \"tu pregunta\"")
        sys.exit(1)
    pregunta = " ".join(sys.argv[1:])
    print(answer(pregunta))