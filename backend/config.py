"""
Configuración central del RAG Híbrido Universal (FAISS + BM25, todo en CPU).
Ajusta estas rutas/modelos según tu máquina.
"""
import os

# --- Rutas ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MANUALS_DIR = os.path.join(BASE_DIR, "manuals")   # subcarpetas por oficio: manuals/fontaneria/, manuals/electricidad/, etc.
CACHE_DIR = os.path.join(BASE_DIR, "cache")       # aquí se guardan los .index, .pkl y el manifest

FAISS_INDEX_PATH = os.path.join(CACHE_DIR, "manuales.index")
METADATA_PATH = os.path.join(CACHE_DIR, "metadata.pkl")       # lista de chunks (texto + fuente + página + oficio)
BM25_PATH = os.path.join(CACHE_DIR, "bm25.pkl")               # corpus tokenizado para BM25
MANIFEST_PATH = os.path.join(CACHE_DIR, "manifest.pkl")       # hash de cada PDF ya indexado (para no reprocesar)

# --- Modelos ---
# IMPORTANTE: tus manuales pueden estar en un idioma y tus preguntas en otro
# (ej. manual en inglés, pregunta en español). Un modelo monolingüe en inglés
# NO alinea bien un vector en español con uno en inglés, así que hay que usar
# modelos multilingües (mismo concepto = mismo punto en el espacio vectorial
# sin importar el idioma). Es más lento en CPU que un modelo solo-inglés,
# pero es el que ya validaste que funciona en el prototipo anterior con Chroma.
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

# Cross-encoder multilingüe (mMARCO) para reranking; también soporta consulta
# y fragmento en idiomas distintos, a diferencia de un cross-encoder solo-inglés.
RERANKER_MODEL = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"

# Los cross-encoders devuelven logits sin rango fijo (pueden ser negativos
# incluso para pares relevantes), así que no hay un "0.0 universal" que sirva
# de umbral. Arranca permisivo (no filtra nada) y sube el valor viendo los
# scores reales que imprime query.py, igual que calibraste el umbral con Chroma.
RERANKER_MIN_SCORE = -1.2

# Ollama
OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "qwen2.5:3b"

# --- Chunking ---
# Extracción por bloques con PyMuPDF (respeta la estructura del PDF, igual que solucionaste
# las alucinaciones en el manual de Mazda de 7452 páginas)
MIN_CHUNK_CHARS = 80          # descarta bloques demasiado cortos (títulos sueltos, ruido)
MAX_CHUNK_CHARS = 1200        # bloques muy largos se subdividen

# --- Fusión híbrida ---
TOP_K_BM25 = 25
TOP_K_VECTOR = 25
TOP_K_FUSION = 20  # candidatos que pasan de la fusión al reranker (generoso: aquí prima recall)
TOP_K_FINAL = 3   # cuántos fragmentos, ya reordenados por el reranker, se envían finalmente al LLM
RRF_K = 60         # constante estándar de Reciprocal Rank Fusion
TOP_K_RERANK = 10   # cuántos pasa el reranker (antes de deduplicar)

# --- Deduplicación de chunks ---
DEDUP_THRESHOLD = 0.75   # 0.0 = nada se descarta, 1.0 = idénticos se descartan