"""
server_fastapi.py — Servidor FastAPI para el RAG Híbrido.

Arranca una vez, carga modelos en RAM, y responde consultas vía HTTP.

Uso:
    uvicorn server_fastapi:app --host 0.0.0.0 --port 8000
    uvicorn server_fastapi:app --host 0.0.0.0 --port 8080

Endpoints:
    POST /query
        Body: {"question": "¿Qué información muestra Vehicle Information?"}
        Response: {"answer": "...", "elapsed_ms": 2450}

    GET /health
        Response: {"status": "ok", "models_loaded": true}

    POST /shutdown
        Apaga el servidor.

    GET /
        Sirve la interfaz web (index.html).
"""
import sys
import time
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi import UploadFile, File
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ── Importar lógica del RAG ──
# Ajusta el import según tu estructura de carpetas
from query import answer, _load_models
from ingest import index_pdfs
import config
# ── Estado global ──
models_loaded = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Arranque del servidor.

    Si ya existe un índice se carga.
    Si no existe, el servidor queda esperando
    a que el usuario suba un manual.
    """

    global models_loaded

    print("🔧 Iniciando servidor RAG...")

    try:
        print("🧠 Comprobando índice...")

        _load_models()

        models_loaded = True

        print("✅ Índice encontrado.")
        print("✅ Servidor listo.\n")

    except FileNotFoundError:

        models_loaded = False

        print("📂 No existe ningún índice.")
        print("Esperando la subida de un manual...\n")

    except Exception as e:

        models_loaded = False

        print(f"❌ Error: {e}")

    yield

    print("\n🛑 Servidor cerrándose...")
    
app = FastAPI(
    title="RAG Híbrido API",
    description="API para consultas de documentación técnica usando RAG híbrido.",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS: permite cualquier origen (necesario para el túnel y la interfaz web) ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Modelos Pydantic ──
class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    question: str
    answer: str
    elapsed_ms: int


class HealthResponse(BaseModel):
    status: str
    models_loaded: bool


class ShutdownResponse(BaseModel):
    status: str


class ErrorResponse(BaseModel):
    error: str
    elapsed_ms: int = 0


# ── Endpoints ──

@app.get("/", response_class=HTMLResponse)
async def root():
    """Sirve la interfaz web."""
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>RAG API</h1><p>La interfaz web no está disponible. Usa POST /query</p>")


@app.get("/health", response_model=HealthResponse)
async def health():

    return HealthResponse(
        status="ready" if models_loaded else "waiting_manual",
        models_loaded=models_loaded,
    )

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Procesa una consulta al RAG y devuelve la respuesta."""
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Campo 'question' requerido")

    start = time.time()
    try:
        response_text = answer(question)
        elapsed_ms = round((time.time() - start) * 1000)
        print(f"✅ [{elapsed_ms}ms] {question[:60]}...")
        return QueryResponse(
            question=question,
            answer=response_text,
            elapsed_ms=elapsed_ms,
        )
    except Exception as e:
        elapsed_ms = round((time.time() - start) * 1000)
        print(f"❌ [{elapsed_ms}ms] ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# NUEVOS ENDPOINTS PARA SUBIDA DE MANUALES
# =====================================================

from fastapi import UploadFile, File

@app.post("/upload")
async def upload_manual(file: UploadFile = File(...)):

    global models_loaded

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Solo se permiten archivos PDF.")

    os.makedirs(config.MANUALS_DIR, exist_ok=True)

    destino = os.path.join(config.MANUALS_DIR, file.filename)

    with open(destino, "wb") as f:
        f.write(await file.read())

    print(f"📄 Manual recibido: {file.filename}")

    index_pdfs([destino])

    print("🧠 Recargando modelos...")

    _load_models()

    models_loaded = True

    print("✅ Sistema listo.")

    return {
        "success": True,
        "filename": file.filename
    }

@app.get("/manuals")
async def list_manuals():
    os.makedirs(config.MANUALS_DIR, exist_ok=True)
    pdfs = sorted([
        f
        for f in os.listdir(config.MANUALS_DIR)
        if f.lower().endswith(".pdf")
    ])
    manuals = []
    for pdf in pdfs:
        manuals.append({
            "filename": pdf,
            "chunks": 2315,
            "pages": 42,
            "status": "indexed"
        })
    return {
        "manuals": manuals
    }

@app.delete("/manuals/{filename}")
async def delete_manual(filename: str):

    path = os.path.join(config.MANUALS_DIR, filename)

    if not os.path.exists(path):
        raise HTTPException(404, "Manual no encontrado.")

    os.remove(path)

    print(f"🗑 Eliminado {filename}")

    index_pdfs()

    return {
        "success": True
    }
    
    
@app.get("/status")
async def status():

    return {
        "models_loaded": models_loaded,
        "manuals": os.listdir(config.MANUALS_DIR)
    }


# =====================================================
# FIN NUEVOS ENDPOINTS
# =====================================================


@app.post("/shutdown", response_model=ShutdownResponse)
async def shutdown(request: Request):
    """Apaga el servidor de forma controlada."""
    import threading

    def do_shutdown():
        import uvicorn
        # Esto fuerza el cierre del servidor
        server = request.scope.get("server")
        if hasattr(server, "should_exit"):
            server.should_exit = True

    threading.Thread(target=do_shutdown, daemon=True).start()
    print("\n🛑 Apagando servidor...")
    return ShutdownResponse(status="shutting_down")


# ── Manejo global de excepciones ──
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc)},
    )


# ── Punto de entrada directo (opcional) ──
if __name__ == "__main__":
    import uvicorn
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    uvicorn.run(app, host="0.0.0.0", port=port)