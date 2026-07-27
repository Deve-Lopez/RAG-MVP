import { useState } from "react";
import Status from "./components/Status";
import UploadManual from "./components/UploadManual";
import ManualList from "./components/ManualList";
import Chat from "./components/Chat";
function App() {
  const [refreshManuals, setRefreshManuals] = useState(0);
  return (
    <div className="container py-4">
      <div className="text-center mb-4">
        <h1 className="fw-bold">
          🤖 RAG Manual Assistant
        </h1>
        <p className="text-muted">
          Sistema de consulta inteligente sobre manuales técnicos
        </p>
      </div>
      <div className="row mb-4">
        <div className="col">
          <Status />
        </div>
      </div>
      <div className="row g-4 mb-4">
        <div className="col-md-6">
          <div className="card shadow-sm">
            <div className="card-body">
              <h5 className="card-title">
                📄 Subir manual
              </h5>
              <UploadManual
                onUploadComplete={() =>
                  setRefreshManuals(r => r + 1)
                }
              />
            </div>
          </div>
        </div>
        <div className="col-md-6">
          <div className="card shadow-sm">
            <div className="card-body">
              <h5 className="card-title">
                📚 Manuales disponibles
              </h5>
              <ManualList refresh={refreshManuals} />
            </div>
          </div>
        </div>
      </div>
      <div className="row">
        <div className="col">
          <div className="card shadow-sm">
            <div className="card-body">
              <h5 className="card-title">
                💬 Consulta al modelo
              </h5>
              <Chat />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
export default App;