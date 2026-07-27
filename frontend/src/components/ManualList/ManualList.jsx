import { useEffect, useState } from "react";
import {
    BsBook,
    BsCheckCircleFill,
    BsClockFill,
    BsFileEarmarkText,
    BsGrid3X3Gap
} from "react-icons/bs";

import "./ManualList.css";

/**
 * Componente ManualList — Muestra el listado de manuales indexados o pendientes.
 * Carga los datos desde el servidor y permite visualizar métricas como páginas y fragmentos.
 */
function ManualList({ refresh }) {
    // Estado local para almacenar la lista de manuales obtenidos del backend
    const [manuals, setManuals] = useState([]);

    // Efecto para realizar la petición HTTP y cargar los manuales al montar
    // el componente o cuando se actualiza la prop 'refresh'
    useEffect(() => {
        // Función asíncrona interna para gestionar la llamada a la API de manuales
        const loadManuals = async () => {
            try {
                // Petición GET al endpoint del servidor para obtener los manuales
                const response = await fetch(
                    "http://localhost:8000/manuals"
                );
                const data = await response.json();
                
                // Actualizar el estado con los manuales recibidos o un array vacío por defecto
                setManuals(data.manuals || []);
            } catch (error) {
                // Capturar y registrar en consola cualquier error de conexión o procesamiento
                console.error(
                    "Error cargando manuales:",
                    error
                );
            }
        };

        // Ejecución inmediata de la función de carga al cumplirse las dependencias
        loadManuals();
    }, [refresh]);

    // Renderizado condicional anticipado si la lista de manuales está vacía
    if (manuals.length === 0) {
        return (
            <div className="manual-empty">
                {/* Icono representativo de libro vacío para el estado sin elementos */}
                <BsBook />
                <p>
                    Todavía no hay manuales indexados.
                </p>
            </div>
        );
    }

    return (
        <div className="manual-list">
            {/* Mapeo de cada objeto manual para renderizar su respectiva tarjeta informativa */}
            {
                manuals.map((manual) => (
                    <div
                        className="manual-card"
                        key={manual.filename}
                    >
                        {/* Cabecera de la tarjeta: icono, nombre del archivo y etiqueta de estado */}
                        <div className="manual-header">
                            <div className="manual-icon">
                                <BsBook />
                            </div>
                            <div>
                                {/* Título del manual limpiando la extensión .pdf del nombre original */}
                                <h4>
                                    {manual.filename.replace(".pdf", "")}
                                </h4>
                                {/* Insignia o badge que cambia de estilo según el estado de indexación */}
                                <span
                                    className={
                                        manual.status === "indexed"
                                            ? "badge-success"
                                            : "badge-warning"
                                    }
                                >
                                    {
                                        manual.status === "indexed"
                                            ? (
                                                <>
                                                    <BsCheckCircleFill />
                                                    {" "}
                                                    Indexado
                                                </>
                                            )
                                            : (
                                                <>
                                                    <BsClockFill />
                                                    {" "}
                                                    Pendiente
                                                </>
                                            )
                                    }
                                </span>
                            </div>
                        </div>
                        {/* Sección inferior con las estadísticas de páginas y fragmentos del documento */}
                        <div className="manual-info">
                            {/* Bloque estadístico que muestra el número total de páginas */}
                            <div className="manual-stat">
                                <BsFileEarmarkText />
                                <span className="manual-stat-value">
                                    {manual.pages}
                                </span>
                                <span className="manual-stat-label">
                                    Páginas
                                </span>
                            </div>
                            {/* Bloque estadístico que muestra el número total de fragmentos vectorizados */}
                            <div className="manual-stat">
                                <BsGrid3X3Gap />
                                <span className="manual-stat-value">
                                    {manual.chunks}
                                </span>
                                <span className="manual-stat-label">
                                    Fragmentos
                                </span>
                            </div>
                        </div>
                    </div>
                ))
            }
        </div>
    );
}

export default ManualList;