const API_URL = "http://localhost:8000";


export async function getHealth() {
    const response = await fetch(`${API_URL}/health`);
    return await response.json();
}


export async function uploadManual(file) {

    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_URL}/upload`, {
        method: "POST",
        body: formData,
    });

    return await response.json();
}


export async function getManuals() {

    const response = await fetch(`${API_URL}/manuals`);

    return await response.json();
}


export async function deleteManual(filename) {

    const response = await fetch(
        `${API_URL}/manuals/${filename}`,
        {
            method: "DELETE",
        }
    );

    return await response.json();
}


export async function askQuestion(question) {

    const response = await fetch(`${API_URL}/query`, {

        method: "POST",

        headers: {
            "Content-Type": "application/json",
        },

        body: JSON.stringify({
            question
        }),

    });

    return await response.json();
}