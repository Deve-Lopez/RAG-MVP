import { useState } from "react";
function Chat() {
    const [question, setQuestion] = useState("");
    const [answer, setAnswer] = useState("");
    const [elapsed, setElapsed] = useState(null);
    const [loading, setLoading] = useState(false);
    const askQuestion = async () => {
        if (!question.trim()) return;
        setLoading(true);
        setAnswer("");
        setElapsed(null);
        try {
            const response = await fetch("http://localhost:8000/query", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    question: question
                })
            });
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.detail || "Error en la consulta");
            }
            setAnswer(data.answer);
            setElapsed(data.elapsed_ms);
        } catch (error) {
            console.error(error);
            setAnswer("❌ Error conectando con el RAG");
        } finally {
            setLoading(false);
        }
    };
    return (
        <div>
            <textarea
                className="form-control mb-3"
                placeholder="Escribe una pregunta..."
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
            />
            <button
                className="btn btn-success"
                onClick={askQuestion}
                disabled={loading}
            >
                {loading ? "Consultando..." : "Preguntar"}
            </button>
            {
                answer && (
                    <div className="alert alert-secondary mt-3">
                        <strong>Respuesta:</strong>
                        <p className="mb-0 mt-2">
                            {answer}
                        </p>
                        {
                            elapsed &&
                            <small>
                                Tiempo: {elapsed} ms
                            </small>
                        }
                    </div>
                )
            }
        </div>
    );
}
export default Chat;