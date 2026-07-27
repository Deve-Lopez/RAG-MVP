import { useEffect, useRef } from "react";

import Message from "./Message";

import "./MessageList.css";

/**
 * Componente MessageList — Contenedor del historial de mensajes del chat.
 * Mapea y renderiza cada mensaje y gestiona el desplazamiento automático
 * hacia el final de la lista cada vez que se añade un nuevo mensaje.
 */
function MessageList({ messages }) {
    // Referencia al elemento final para controlar el scroll automático
    const bottomRef = useRef(null);

    // Efecto para desplazar la vista suavemente hacia abajo al actualizarse los mensajes
    useEffect(() => {
        bottomRef.current?.scrollIntoView({
            behavior: "smooth"
        });
    }, [messages]);

    return (
        <div className="messages-container">
            {
                messages.map((message, index) => (
                    <Message
                        key={index}
                        message={message}
                    />
                ))
            }
            {/* Elemento ancla invisible al final de la lista para el scroll */}
            <div ref={bottomRef}></div>
        </div>
    );
}

export default MessageList;