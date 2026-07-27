import { useEffect, useState } from "react";
import { getHealth } from "../api/api";


function Status() {

    const [status, setStatus] = useState(null);
    const [error, setError] = useState(false);

    useEffect(() => {
        async function checkHealth() {
            try {
                const data = await getHealth();
                setStatus(data);
            } catch (err) {
                console.error(err);
                setError(true);
            }
        }
        checkHealth();
    }, []);

    if (error) {
        return (
            <div className="alert alert-danger">
                ❌ No se puede conectar con FastAPI
            </div>
        );
    }

    if (!status) {
        return (
            <div className="alert alert-info">
                Comprobando estado del sistema...
            </div>
        );
    }

    return (
        <div
            className={
                status.status === "ready"
                    ? "alert alert-success"
                    : "alert alert-warning"
            }
        >
            <h5>
                {status.status === "ready"
                    ? "🟢 Sistema listo"
                    : "🟡 Esperando manual"
                }
            </h5>
            <p className="mb-0">
                Modelos cargados:
                {" "}
                {status.models_loaded ? "Sí" : "No"}
            </p>
        </div>
    );
}
export default Status;