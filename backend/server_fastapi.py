
"""
server_fastapi.py — Servidor FastAPI para el RAG Híbrido.
Este script levanta una API REST que gestiona las consultas de los usuarios,
la subida, listado y borrado dinámico de manuales en PDF, y el ciclo de vida
del sistema cargando los modelos en memoria al arrancar.

Uso:
    uvicorn server_fastapi:app --host 0.0.0.0 --port 8000
    uvicorn server_fastapi:app --host 0.0.0.0 --port 8080
    
Endpoints:
    GET /
        Sirve la interfaz gráfica web (index.html).

    GET /health
        Devuelve el estado de salud del servidor y si los modelos están listos.
        Response: {"status": "ready" | "waiting_manual", "models_loaded": true/false}

    POST /query
        Procesa una pregunta del usuario usando el pipeline RAG.
        Body: {"question": "¿Qué hago si salta el DTC P0126?"}
        Response: {"question": "...", "answer": "...", "elapsed_ms": 2450}

    POST /upload
        Recibe un archivo PDF, lo almacena, dispara la indexación y recarga modelos.
        Body: Multipart/form-data con el archivo PDF.
        Response: {"success": true, "filename": "..."}

    GET /manuals
        Lista todos los manuales disponibles con sus estadísticas (chunks, páginas, estado).
        Response: {"manuals": [...]}

    DELETE /manuals/{filename}
        Elimina un manual del disco, purga sus fragmentos y actualiza los índices.
        Response: {"success": true}

    GET /status
        Devuelve un resumen rápido del estado del servidor y los manuales en disco.
        Response: {"models_loaded": true/false, "manuals": [...]}

    POST /shutdown
        Apaga el servidor FastAPI de forma controlada.
        Response: {"status": "shutting_down"}

"""
import sys
import time
import os
import json
import pickle
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from query import answer, _load_models
from ingest import index_pdfs
import config


# Variable global para controlar si los modelos e índices ya están listos en RAM
models_loaded = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestor del ciclo de vida de la aplicación (Lifespan).
    Al arrancar el servidor, comprueba si ya existen índices vectoriales creados:
    - Si existen, los carga en memoria para que el sistema esté operativo de inmediato.
    - Si no existen, avisa por consola y deja el servidor listo para recibir manuales vía API.
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


# Inicialización de la aplicación FastAPI con metadatos descriptivos
app = FastAPI(
    title="RAG Híbrido API",
    description="API para consultas de documentación técnica usando RAG híbrido.",
    version="1.0.0",
    lifespan=lifespan,
)

# Configuración de CORS para permitir solicitudes desde cualquier origen (necesario para la interfaz web)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Modelos Pydantic para validación de datos ---

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


# --- Endpoints de la API ---

@app.get("/", response_class=HTMLResponse)
async def root():
    """Sirve la interfaz gráfica web (index.html) si se encuentra en el directorio."""
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>RAG API</h1><p>La interfaz web no está disponible. Usa POST /query</p>")


@app.get("/health", response_model=HealthResponse)
async def health():
    """Devuelve el estado de salud del servidor y si los modelos están listos para responder."""
    return HealthResponse(
        status="ready" if models_loaded else "waiting_manual",
        models_loaded=models_loaded,
    )


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Procesa una pregunta del usuario a través del pipeline RAG y devuelve la respuesta generada."""
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


@app.post("/upload")
async def upload_manual(file: UploadFile = File(...)):
    """Recibe un nuevo manual en PDF, lo almacena, dispara la indexación y recarga los modelos."""
    global models_loaded

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Solo se permiten archivos PDF.")

    os.makedirs(config.MANUALS_DIR, exist_ok=True)
    destino = os.path.join(config.MANUALS_DIR, file.filename)

    with open(destino, "wb") as f:
        f.write(await file.read())

    print(f"📄 Manual recibido: {file.filename}")

    # Ejecutar indexación automática del nuevo archivo
    index_pdfs()

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
    """Lista todos los manuales disponibles en disco junto con sus estadísticas de fragmentos y páginas."""
    os.makedirs(config.MANUALS_DIR, exist_ok=True)
    pdfs = sorted([
        f for f in os.listdir(config.MANUALS_DIR)
        if f.lower().endswith(".pdf")
    ])

    metadata = []
    if os.path.exists(config.METADATA_PATH):
        with open(config.METADATA_PATH, "rb") as f:
            metadata = pickle.load(f)

    manuals = []
    for pdf in pdfs:
        chunks = [
            m for m in metadata
            if m.get("source") == pdf
        ]
        pages = 0
        if chunks:
            pages = max(
                c.get("page", 0)
                for c in chunks
            )
        manuals.append({
            "filename": pdf,
            "chunks": len(chunks),
            "pages": pages,
            "status": "indexed" if chunks else "pending"
        })

    return {
        "manuals": manuals
    }


@app.delete("/manuals/{filename}")
async def delete_manual(filename: str):
    """Elimina un manual del disco, actualiza los índices y purga sus fragmentos obsoletos."""
    path = os.path.join(config.MANUALS_DIR, filename)

    if not os.path.exists(path):
        raise HTTPException(404, "Manual no encontrado.")

    os.remove(path)
    print(f"🗑 Eliminado {filename}")

    # Reindexar para reflejar la baja del documento eliminado
    index_pdfs()

    return {
        "success": True
    }


@app.get("/status")
async def status():
    """Devuelve un resumen rápido del estado del servidor y los manuales almacenados."""
    return {
        "models_loaded": models_loaded,
        "manuals": os.listdir(config.MANUALS_DIR) if os.path.exists(config.MANUALS_DIR) else []
    }


@app.post("/shutdown", response_model=ShutdownResponse)
async def shutdown(request: Request):
    """Apaga el servidor FastAPI de forma controlada mediante un hilo secundario."""
    import threading

    def do_shutdown():
        server = request.scope.get("server")
        if hasattr(server, "should_exit"):
            server.should_exit = True

    threading.Thread(target=do_shutdown, daemon=True).start()
    print("\n🛑 Apagando servidor...")
    return ShutdownResponse(status="shutting_down")


# --- Manejador global de excepciones ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Captura cualquier error no controlado y devuelve una respuesta HTTP 500 estructurada."""
    return JSONResponse(
        status_code=500,
        content={"error": str(exc)},
    )


# --- Punto de entrada para ejecución directa ---
if __name__ == "__main__":
    import uvicorn
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    uvicorn.run(app, host="0.0.0.0", port=port)