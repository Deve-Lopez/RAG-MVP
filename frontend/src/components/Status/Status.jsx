import { useEffect, useState } from "react";
import {
    BsCheckCircleFill,
    BsXCircleFill,
    BsCpu,
    BsDatabase
} from "react-icons/bs";

import { getHealth } from "../../api/api";

import "./Status.css";

/**
 * Componente Status — Verifica y muestra el estado de salud del backend FastAPI
 * y el estado de carga de los modelos de inteligencia artificial.
 */
function Status({ refresh }) {
    // Estado local para almacenar la respuesta de salud del servidor
    const [status, setStatus] = useState(null);
    
    // Estado local para controlar si ha ocurrido un error de conexión con la API
    const [error, setError] = useState(false);

    // Efecto para consultar el estado de salud al montar el componente o al actualizar la prop 'refresh'
    useEffect(() => {
        // Función asíncrona interna para realizar la petición al módulo de la API
        async function checkHealth() {
            try {
                const data = await getHealth();
                setStatus(data);
                setError(false);
            } catch (err) {
                console.error(err);
                setError(true);
            }
        }

        checkHealth();
    }, [refresh]);

    // Renderizado condicional si no se puede establecer comunicación con el servidor
    if (error) {
        return (
            <div className="status-error">
                <BsXCircleFill />
                <span>
                    No se puede conectar con FastAPI
                </span>
            </div>
        );
    }

    // Renderizado condicional mientras se espera la respuesta del servidor
    if (!status) {
        return (
            <div className="status-loading">
                Comprobando sistema...
            </div>
        );
    }

    return (
        <div className="status-container">
            {/* Elemento de estado general del sistema RAG */}
            <div className="status-item">
                <div className="status-icon success">
                    <BsDatabase />
                </div>
                <div>
                    <span className="status-label">
                        Estado
                    </span>
                    <strong>
                        {
                            status.status === "ready"
                                ? "Sistema listo"
                                : "Esperando manual"
                        }
                    </strong>
                </div>
            </div>
            {/* Elemento de estado de carga de los modelos de IA con estilo dinámico */}
            <div className="status-item">
                <div
                    className={
                        status.models_loaded
                            ? "status-icon success"
                            : "status-icon warning"
                    }
                >
                    {
                        status.models_loaded
                            ? <BsCheckCircleFill />
                            : <BsCpu />
                    }
                </div>
                <div>
                    <span className="status-label">
                        Modelos
                    </span>
                    <strong>
                        {
                            status.models_loaded
                                ? "Cargados"
                                : "No cargados"
                        }
                    </strong>
                </div>
            </div>
        </div>
    );
}

export default Status;