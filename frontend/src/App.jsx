import { useState } from "react";
import { BsRobot } from "react-icons/bs";

import Status from "./components/Status/Status";
import UploadManual from "./components/UploadManual/UploadManual";
import ManualList from "./components/ManualList/ManualList";
import Chat from "./components/Chat/Chat";

import "./styles/App.css";

/**
 * Componente App — Componente raíz de la aplicación RAG Manual Assistant.
 * Gestiona la estructura principal de la interfaz, incluyendo la cabecera, la barra lateral 
 * (estado del sistema, subida de archivos y listado de manuales) y el área de contenido (chat inteligente).
 * Controla también los disparadores de actualización global mediante estados de incremento.
 */
function App() {
    // Estado contador para disparar la recarga del listado de manuales indexados
    const [refreshManuals, setRefreshManuals] = useState(0);
    
    // Estado contador para disparar la actualización de la salud del sistema y modelos de IA
    const [refreshStatus, setRefreshStatus] = useState(0);

    return (
        <div className="app">
            {/* ================= HEADER ================= */}
            <header className="app-header">
                <div className="logo">
                    <div className="logo-icon">
                        <BsRobot />
                    </div>
                    <div>
                        <h1>
                            RAG Manual Assistant
                        </h1>
                        <p>
                            Consulta inteligente sobre documentación técnica
                        </p>
                    </div>
                </div>

                {/* Indicador visual de conexión general con el backend */}
                <div className="status-pill">
                    <div className="status-dot online"></div>
                    <span>
                        Backend conectado
                    </span>
                </div>
            </header>

            {/* ================= CONTENIDO ================= */}
            <div className="grid">
                {/* ========= SIDEBAR ========= */}
                <aside className="sidebar">
                    {/* Tarjeta de estado de salud del backend y modelos de IA */}
                    <div className="card-modern">
                        <h3 className="section-title">
                            Estado
                        </h3>
                        <Status refresh={refreshStatus} />
                    </div>

                    {/* Tarjeta de subida de manuales en formato PDF */}
                    <div className="card-modern">
                        <h3 className="section-title">
                            Subir manual
                        </h3>
                        <UploadManual
                            onUploadComplete={() => {
                                // Incrementar contadores para actualizar componentes dependientes tras una subida exitosa
                                setRefreshManuals(r => r + 1);
                                setRefreshStatus(r => r + 1);
                            }}
                        />
                    </div>

                    {/* Tarjeta con el listado de manuales disponibles en el sistema */}
                    <div className="card-modern">
                        <h3 className="section-title">
                            Manuales
                        </h3>
                        <ManualList
                            refresh={refreshManuals}
                        />
                    </div>
                </aside>

                {/* ========= CONTENIDO PRINCIPAL ========= */}
                <main className="content">
                    {/* Tarjeta contenedora del componente de chat conversacional */}
                    <div className="card-modern">
                        <Chat />
                    </div>
                </main>
            </div>
        </div>
    );
}

export default App;