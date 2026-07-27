import { useEffect, useState } from "react";
function ManualList({ refresh }) {
    const [manuals, setManuals] = useState([]);
    useEffect(() => {
        const loadManuals = async () => {
            try {
                const response = await fetch(
                    "http://localhost:8000/manuals"
                );
                const data = await response.json();
                setManuals(data.manuals || []);
            } catch (error) {
                console.error(
                    "Error cargando manuales:",
                    error
                );
            }
        };
        loadManuals();
    }, [refresh]);
    return (
        <div>
            {
                manuals.length === 0 ? (
                    <p className="text-muted">
                        No hay manuales cargados todavía.
                    </p>
                ) : (
                    manuals.map((manual) => (
                        <div
                            key={manual.filename}
                            className="card mb-3 border-success"
                        >
                            <div className="card-body">
                                <h6 className="card-title">
                                    📄 {manual.filename}
                                </h6>
                                <p className="mb-1">
                                    ⚙️ Indexación: completada
                                </p>

                                <p className="mb-1">
                                    🟢 Disponible para consultas
                                </p>
                                <p className="mb-1">
                                    🧩 Fragmentos: {manual.chunks}
                                </p>
                                <p className="mb-0">
                                    📄 Páginas: {manual.pages}
                                </p>
                            </div>
                        </div>
                    ))
                )
            }
        </div>
    );
}
export default ManualList;