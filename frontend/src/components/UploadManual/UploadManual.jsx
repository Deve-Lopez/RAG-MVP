import { useRef, useState } from "react";
import { BsCloudArrowUp, BsFileEarmarkPdf } from "react-icons/bs";

import { uploadManual } from "../../api/api";

import "./UploadManual.css";

/**
 * Componente UploadManual — Permite la selección, subida e indexación de manuales en formato PDF.
 * Gestiona el formulario multipart, los estados de carga, los mensajes de progreso y las alertas de éxito/error.
 */
function UploadManual({ onUploadComplete }) {
    // Referencia mutable para acceder directamente al elemento input de tipo archivo oculto
    const inputRef = useRef(null);

    // Estado local para almacenar el archivo PDF seleccionado por el usuario
    const [file, setFile] = useState(null);
    // Estado local para mostrar mensajes informativos o de progreso durante la subida
    const [status, setStatus] = useState("");
    // Estado local para almacenar los datos devueltos por el servidor al completar la indexación
    const [result, setResult] = useState(null);
    // Estado local para bloquear la interfaz e indicar que hay un proceso de subida en curso
    const [loading, setLoading] = useState(false);

    /**
     * Envía el archivo PDF seleccionado al backend mediante la capa de servicios centralizada.
     * Gestiona el flujo completo: subida, generación de embeddings y actualización de estados.
     */
    const handleUpload = async () => {
        // Validar que se haya seleccionado un archivo previamente
        if (!file) {
            setStatus("Selecciona un manual PDF");
            return;
        }

        try {
            setLoading(true);
            setResult(null);
            setStatus("Subiendo manual...");

            // Llamada al backend utilizando la función centralizada de la API
            const data = await uploadManual(file);

            setStatus("Generando embeddings...");

            setResult(data);

            setStatus("Manual preparado para consultas");

            // Invocar la función callback externa si está definida para refrescar otros componentes
            if (onUploadComplete) {
                onUploadComplete();
            }

        } catch (error) {
            console.error(error);
            setStatus("Error procesando manual");
        } finally {
            // Desactivar el estado de carga al finalizar la operación (éxito o error)
            setLoading(false);
        }
    };

    return (
        <>
            {/* Zona interactiva de arrastrar y seleccionar archivo que simula el clic en el input oculto */}
            <div
                className="upload-zone"
                onClick={() => inputRef.current.click()}
            >
                <BsCloudArrowUp className="upload-icon" />
                <h4>
                    Selecciona un manual PDF
                </h4>
                <p>
                    Haz clic para elegir un archivo desde tu equipo.
                </p>

                {/* Input de tipo file oculto controlado mediante la referencia mutable */}
                <input
                    ref={inputRef}
                    type="file"
                    accept=".pdf"
                    onChange={(e) => setFile(e.target.files[0])}
                    hidden
                />
            </div>

            {/* Contenedor visual que muestra el nombre del archivo PDF seleccionado */}
            {
                file &&
                <div className="selected-file">
                    <BsFileEarmarkPdf />
                    <span>
                        {file.name}
                    </span>
                </div>
            }

            {/* Botón principal para disparar el proceso de subida e indexación */}
            <button
                className="btn-modern upload-button"
                disabled={loading}
                onClick={handleUpload}
            >
                {
                    loading
                        ? "Procesando..."
                        : "Subir manual"
                }
            </button>

            {/* Píldora informativa que muestra el estado actual del proceso en tiempo real */}
            {
                status &&
                <div className="upload-status">
                    {status}
                </div>
            }

            {/* Bloque de éxito que se muestra cuando el manual ha sido indexado correctamente */}
            {
                result &&
                <div className="upload-success">
                    <strong>
                        ✔ Manual listo
                    </strong>
                    <br />
                    {result.filename}
                </div>
            }
        </>
    );
}

export default UploadManual;