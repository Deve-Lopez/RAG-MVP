import { useState } from "react";
import { BsArrowRight } from "react-icons/bs";

import MessageList from "./MessageList";

import "./Chat.css";

/**
 * Componente Chat — Interfaz principal de consultas al sistema RAG.
 * Gestiona el envío de preguntas, el estado de carga y el historial de mensajes de la conversación.
 */
function Chat() {
    // Estado para almacenar el texto que escribe el usuario en el textarea
    const [question, setQuestion] = useState("");
    
    // Estado para almacenar el historial de mensajes (preguntas del usuario y respuestas del asistente)
    const [messages, setMessages] = useState([]);
    
    // Estado para controlar si hay una petición en curso (deshabilita el botón y cambia el texto)
    const [loading, setLoading] = useState(false);

    /**
     * Envía la pregunta actual al backend, actualiza el historial con la respuesta
     * y gestiona los estados de carga y error.
     */
    const askQuestion = async () => {
        // Validar que la pregunta no esté vacía y que no haya otra petición en curso
        if (!question.trim() || loading) return;

        const currentQuestion = question;

        // Añadir inmediatamente la pregunta del usuario al historial visual
        setMessages(prev => [
            ...prev,
            {
                role: "user",
                content: currentQuestion
            }
        ]);

        // Limpiar el campo de entrada y activar el estado de carga
        setQuestion("");
        setLoading(true);

        try {
            // Realizar la petición HTTP POST al endpoint de consultas del servidor FastAPI
            const response = await fetch(
                "http://localhost:8000/query",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        question: currentQuestion
                    })
                }
            );

            const data = await response.json();

            // Comprobar si la respuesta del servidor indica un error HTTP
            if (!response.ok) {
                throw new Error(data.detail || "Error");
            }

            // Añadir la respuesta generada por el asistente al historial de mensajes
            setMessages(prev => [
                ...prev,
                {
                    role: "assistant",
                    content: data.answer,
                    elapsed: data.elapsed_ms
                }
            ]);
        } catch {
            // Manejar errores de red o excepciones capturadas durante la petición
            setMessages(prev => [
                ...prev,
                {
                    role: "assistant",
                    content: "Error conectando con el servidor."
                }
            ]);
        } finally {
            // Desactivar el estado de carga independientemente del resultado
            setLoading(false);
        }
    };

    /**
     * Intercepta las pulsaciones de teclas en el área de texto para permitir
     * el envío rápido de la consulta mediante la tecla Enter (sin Shift).
     */
    const handleKeyDown = (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            askQuestion();
        }
    };

    return (
        <div className="chat-wrapper">
            {/* Cabecera descriptiva de la sección de chat */}
            <div className="chat-header">
                <h2>
                    ¿Qué quieres consultar?
                </h2>
                <p>
                    Pregunta cualquier información contenida
                    en los manuales indexados.
                </p>
            </div>

            {/* Componente que renderiza el listado acumulado de mensajes */}
            <MessageList messages={messages} />

            {/* Contenedor del área de entrada de texto y el botón de envío */}
            <div className="chat-input-box">
                <textarea
                    rows={4}
                    placeholder="Ej.: ¿Cuál es el par de apriete del diferencial?"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyDown={handleKeyDown}
                />
                <button
                    className="btn-modern"
                    disabled={loading}
                    onClick={askQuestion}
                >
                    {
                        loading
                            ? "Consultando..."
                            : (
                                <>
                                    Consultar
                                    <BsArrowRight />
                                </>
                            )
                    }
                </button>
            </div>
        </div>
    );
}

export default Chat;