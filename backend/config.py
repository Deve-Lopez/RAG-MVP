"""
Configuración central del RAG Híbrido (FAISS + BM25 en CPU).
Define las rutas del proyecto, los modelos de inteligencia artificial y
los parámetros que controlan la búsqueda y fragmentación de los manuales.
"""
import os

# Directorios base del proyecto calculados de forma dinámica.
# Usamos rutas relativas para evitar que falle al mover o clonar el repositorio.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MANUALS_DIR = os.path.join(BASE_DIR, "manuals")
CACHE_DIR = os.path.join(BASE_DIR, "cache")

# Rutas para almacenar de forma local los índices y metadatos generados.
# Esto evita tener que reprocesar los PDFs desde cero cada vez que iniciamos el sistema.
FAISS_INDEX_PATH = os.path.join(CACHE_DIR, "manuales.index")
METADATA_PATH = os.path.join(CACHE_DIR, "metadata.pkl")
BM25_PATH = os.path.join(CACHE_DIR, "bm25.pkl")
MANIFEST_PATH = os.path.join(CACHE_DIR, "manifest.pkl")

# Modelo de embeddings multilingüe. Es clave para que las preguntas y los manuales
# se entiendan correctamente incluso si están redactados en idiomas diferentes.
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

# Modelo Cross-Encoder para el reranking. Su función es reordenar los resultados
# preliminares analizando directamente la relación de sintonía entre la pregunta y cada fragmento.
RERANKER_MODEL = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"

# Umbral de puntuación mínima para el reranker. Como genera valores numéricos libres,
# se ajusta mediante pruebas para descartar únicamente la morralla o ruido inservible.
RERANKER_MIN_SCORE = -1.2

# Configuración de Ollama y el modelo local de lenguaje (LLM) que redactará la respuesta final
# basándose exclusivamente en los manuales encontrados.
OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "qwen2.5:3b"

# Límites de caracteres para hacer el chunking (fragmentación) de los PDFs.
# Evitamos bloques ridículamente cortos (como títulos sueltos) y cortamos los muy largos
# para que el buscador encuentre con precisión milimétrica la información.
MIN_CHUNK_CHARS = 80
MAX_CHUNK_CHARS = 1200

# Cuotas para equilibrar la búsqueda híbrida, la fusión de ránkings (RRF) y el recorte final.
# Combinamos la precisión exacta de palabras clave (BM25) con la semántica de los vectores.
TOP_K_BM25 = 25
TOP_K_VECTOR = 25
TOP_K_FUSION = 20  # candidatos que pasan de la fusión al reranker
TOP_K_FINAL = 3   # cuántos fragmentos, ya reordenados por el reranker, se envían finalmente al LLM
RRF_K = 60         # constante estándar de Reciprocal Rank Fusion
TOP_K_RERANK = 10   # cuántos pasa el reranker (antes de deduplicar)

# Umbral de similitud para eliminar fragmentos duplicados o casi idénticos antes de pasárselos
# al modelo de lenguaje, ahorrando espacio de contexto y evitando redundancias.
DEDUP_THRESHOLD = 0.75   # 0.0 = nada se descarta, 1.0 = idénticos se descartan