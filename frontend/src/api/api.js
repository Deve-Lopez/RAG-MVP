/**
 * api.js — Módulo de comunicación con la API del backend.
 * Centraliza todas las peticiones HTTP (health check, subida, listado, borrado y consultas).
 */
const API_URL = import.meta.env.VITE_API_URL;

/**
 * Comprueba el estado de salud del servidor y la carga de los modelos.
 */
export async function getHealth() {
    const response = await fetch(`${API_URL}/health`);
    return await response.json();
}

/**
 * Envía un archivo PDF al backend mediante una petición multipart/form-data.
 */
export async function uploadManual(file) {
    const formData = new FormData();
    formData.append("file", file);
    const response = await fetch(`${API_URL}/upload`, {
        method: "POST",
        body: formData,
    });
    return await response.json();
}

/**
 * Obtiene la lista de manuales almacenados junto con sus metadatos y estado.
 */
export async function getManuals() {
    const response = await fetch(`${API_URL}/manuals`);
    return await response.json();
}

/**
 * Solicita al backend la eliminación de un manual específico a través de su nombre.
 */
export async function deleteManual(filename) {
    const response = await fetch(`${API_URL}/manuals/${filename}`, {
        method: "DELETE",
    });
    return await response.json();
}

/**
 * Envía una pregunta en formato JSON al pipeline RAG para obtener una respuesta.
 */
export async function askQuestion(question) {
    const response = await fetch(`${API_URL}/query`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ question }),
    });
    return await response.json();
}