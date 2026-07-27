import { BsArrowRight } from "react-icons/bs";

import "./ChatInput.css";

/**
 * Componente ChatInput — Barra de entrada de texto para las consultas del usuario.
 * Gestiona la escritura de la pregunta, los atajos de teclado (Enter para enviar)
 * y el estado visual del botón según la carga.
 */
function ChatInput({
    question,
    setQuestion,
    loading,
    askQuestion
}) {
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
        <div className="chat-input-box">
            {/* Área de texto donde el usuario introduce su pregunta técnica */}
            <textarea
                rows={4}
                value={question}
                placeholder="Ej.: ¿Cuál es el par de apriete del diferencial?"
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={handleKeyDown}
            />
            {/* Botón de envío que cambia su contenido y se deshabilita si hay una consulta en curso */}
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
    );
}

export default ChatInput;