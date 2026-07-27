import { useState } from "react";
import { BsArrowRight } from "react-icons/bs";

import MessageList from "./MessageList";
import { askQuestion as askQuestionAPI } from "../../api/api";

import "./Chat.css";

/**
 * Componente Chat — Interfaz principal de consultas al sistema RAG.
 * Gestiona el envío de preguntas mediante la API centralizada, el control de estados de carga
 * y la actualización dinámica del historial de mensajes de la conversación.
 */
function Chat() {
    // Estado local para almacenar el texto que introduce el usuario en el área de entrada
    const [question, setQuestion] = useState("");

    // Estado local para almacenar el historial completo de mensajes (preguntas del usuario y respuestas del asistente)
    const [messages, setMessages] = useState([]);

    // Estado local para bloquear la interfaz, cambiar el texto del botón y prevenir peticiones simultáneas
    const [loading, setLoading] = useState(false);

    /**
     * Envía la pregunta actual al backend mediante el servicio centralizado de la API,
     * actualiza de forma optimista el historial con la consulta del usuario y añade la respuesta obtenida.
     */
    const askQuestion = async () => {
        // Validar que el texto no esté vacío y que no haya otra petición en curso
        if (!question.trim() || loading) return;

        const currentQuestion = question;

        // Añadir inmediatamente la pregunta del usuario al historial visual de la interfaz
        setMessages(prev => [
            ...prev,
            {
                role: "user",
                content: currentQuestion
            }
        ]);

        // Limpiar el campo de entrada de texto y activar el indicador de carga
        setQuestion("");
        setLoading(true);

        try {
            // Realizar la consulta al backend utilizando la función centralizada de la capa API
            const data = await askQuestionAPI(currentQuestion);

            // Añadir la respuesta estructurada del asistente al historial de mensajes
            setMessages(prev => [
                ...prev,
                {
                    role: "assistant",
                    content: data.answer,
                    elapsed: data.elapsed_ms
                }
            ]);

        } catch (error) {
            // Registrar el error en consola y añadir un mensaje de fallo genérico en el chat
            console.error(error);

            setMessages(prev => [
                ...prev,
                {
                    role: "assistant",
                    content: "Error conectando con el servidor."
                }
            ]);

        } finally {
            // Desactivar el estado de carga independientemente del éxito o fallo de la petición
            setLoading(false);
        }
    };

    /**
     * Intercepta las pulsaciones de teclado en el área de texto para permitir
     * el envío rápido de la consulta mediante la tecla Enter (sin combinar con Shift).
     */
    const handleKeyDown = (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            askQuestion();
        }
    };

    return (
        <div className="chat-wrapper">
            {/* Cabecera descriptiva superior con el título y subtítulo de la sección de chat */}
            <div className="chat-header">
                <h2>
                    ¿Qué quieres consultar?
                </h2>
                <p>
                    Pregunta cualquier información contenida
                    en los manuales indexados.
                </p>
            </div>

            {/* Componente contenedor del listado dinámico de mensajes de la conversación */}
            <MessageList messages={messages} />

            {/* Contenedor inferior que agrupa el área de texto (textarea) y el botón de envío */}
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