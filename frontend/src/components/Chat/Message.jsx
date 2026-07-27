import {
    BsPerson,
    BsRobot,
    BsClock
} from "react-icons/bs";

import "./Message.css";

/**
 * Componente Message — Renderiza un mensaje individual en la interfaz del chat.
 * Muestra el avatar correspondiente (usuario o asistente), el contenido de texto
 * y el tiempo de respuesta si está disponible.
 */
function Message({ message }) {
    return (
        <div className={`message ${message.role}`}>
            {/* Contenedor del avatar con variante visual según el rol del emisor */}
            <div className={`avatar ${message.role === "assistant" ? "ai" : ""}`}>
                {
                    message.role === "assistant"
                        ? <BsRobot />
                        : <BsPerson />
                }
            </div>
            {/* Burbuja que contiene el texto del mensaje y métricas adicionales */}
            <div className="bubble">
                {message.content}
                {
                    message.elapsed &&
                    <div className="elapsed">
                        <BsClock />
                        {message.elapsed} ms
                    </div>
                }
            </div>
        </div>
    );
}

export default Message;