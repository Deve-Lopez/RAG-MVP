import { useState } from "react";

function UploadManual({ onUploadComplete }) {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const handleUpload = async () => {
    if (!file) {
      setStatus("Selecciona un manual PDF");
      return;
    }
    const formData = new FormData();
    formData.append("file", file);
    try {
      setLoading(true);
      setResult(null);
      setStatus("📤 Subiendo manual...");
      const response = await fetch(
        "http://localhost:8000/upload",
        {
          method: "POST",
          body: formData
        }
      );
      if (!response.ok) {
        throw new Error();
      }
      setStatus("🧠 Generando embeddings e índice RAG...");
      const data = await response.json();

      setResult(data);

      setStatus("✅ Manual preparado para consultas");

      if (onUploadComplete) {
        onUploadComplete();
      }
    } catch (error) {
      console.error(error);
      setStatus("❌ Error procesando manual");
    } finally {
      setLoading(false);
    }
  };
  return (
    <div className="container mt-5">
      <div className="card shadow">
        <div className="card-body">
          <h3 className="mb-4">
            📚 Knowledge Base RAG
          </h3>
          <p className="text-muted">
            Sube un manual técnico para crear una base
            de conocimiento consultable mediante IA.
          </p>
          <input
            type="file"
            accept=".pdf"
            className="form-control"
            onChange={(e) => setFile(e.target.files[0])}
          />
          <button
            className="btn btn-primary mt-3"
            disabled={loading}
            onClick={handleUpload}
          >
            {loading
              ? "Procesando..."
              : "Subir manual"
            }
          </button>
          {
            status &&
            <div className="alert alert-info mt-4">
              {status}
            </div>
          }
          {
            result &&
            <div className="card mt-3 border-success">
              <div className="card-body">
                <h5>
                  ✅ Manual listo
                </h5>
                <p>
                  <strong>Archivo:</strong> {result.filename}
                </p>
                <p>
                  <strong>Estado:</strong> Indexado correctamente
                </p>
                {
                  result.chunks &&
                  <p>
                    <strong>Fragmentos:</strong> {result.chunks}
                  </p>
                }
              </div>
            </div>
          }
        </div>
      </div>
    </div>
  );
}

export default UploadManual;