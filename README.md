<div align="center">

# 📚 RAG Manual Assistant

### Consulta inteligente sobre documentación técnica mediante una arquitectura RAG

Aplicación Full Stack desarrollada para investigar cómo integrar una arquitectura **RAG (Retrieval-Augmented Generation)** dentro de una aplicación web, combinando un motor de procesamiento y recuperación en **Python y FastAPI** con una interfaz moderna en **React**.

# 📸 Vista previa

![RAG Manual Assistant Banner](docs/banner.png)

# 🚀 Probar la aplicación

Puedes clonar el repositorio y levantar el entorno localmente para probar el asistente con tu propia documentación técnica.

> **Nota:** El sistema requiere tener en marcha tanto el servidor backend de FastAPI como el entorno de desarrollo del frontend para gestionar la ingesta de PDFs y las consultas conversacionales.

<br>

![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-7-646CFF?logo=vite&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?logo=bootstrap&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

</div>

---

## 📑 Índice

- [Objetivo del proyecto](#-objetivo-del-proyecto)
- [¿Por qué RAG para manuales?](#-por-qué-rag-para-manuales)
- [Arquitectura](#️-arquitectura)
- [Flujo de funcionamiento](#-flujo-de-funcionamiento)
- [Tecnologías](#-tecnologías)
- [Estructura del proyecto](#-estructura-del-proyecto)
- [Instalación y ejecución](#-instalación-y-ejecución)
- [Decisiones de diseño](#-decisiones-de-diseño)
- [Lo aprendido](#-lo-aprendido)

# 🎯 Objetivo del proyecto

Cuando empecé este proyecto no quería construir otro simple chatbot genérico ni depender de búsquedas tradicionales por palabras clave en manuales técnicos.

Internet está lleno de ejemplos donde una aplicación envía un prompt aislado a un LLM. Sin embargo, en el mundo real, la documentación técnica suele ser extensa, densa y específica de cada dominio o producto.

Mi objetivo era responder a una pregunta diferente:

> **¿Cómo podemos dotar a una aplicación de la capacidad de leer, indexar y responder preguntas basándose estrictamente en manuales técnicos reales sin perder precisión?**

La respuesta fue implementar una arquitectura **RAG (Retrieval-Augmented Generation)**, permitiendo que el sistema recupere fragmentos exactos de los documentos antes de generar la respuesta.

---

# 💡 ¿Por qué RAG para manuales?

Las consultas en documentación técnica tradicional presentan grandes limitaciones:
- Búsquedas por texto exacto que no entienden el contexto ni los sinónimos.
- Manuales en PDF de cientos de páginas imposibles de procesar manualmente de forma rápida.
- Necesidad de respuestas fiables y contrastadas con la documentación original.

Con una arquitectura RAG, el modelo de lenguaje deja de adivinar y pasa a actuar sobre un contexto recuperado de forma semántica. 

Este proyecto demuestra cómo estructurar ese flujo completo de extremo a extremo (desde la subida del PDF hasta la interfaz de chat).

---

# ✨ Características

✔ Carga y procesamiento automático de manuales técnicos en formato PDF.

✔ Generación de embeddings e indexación vectorial para búsqueda semántica.

✔ Interfaz moderna con componentes modulares desarrollada en React y Vite.

✔ Panel lateral con control del estado del backend, subida de ficheros y listado de manuales indexados.

✔ Diseño adaptativo (*responsive*) y limpio optimizado para múltiples dispositivos.

✔ Arquitectura desacoplada entre el cliente y el servidor REST de FastAPI.

---

# 🏗️ Arquitectura

La aplicación sigue una arquitectura desacoplada donde el frontend en React se comunica con un backend robusto en FastAPI encargado del pipeline de IA y la gestión vectorial.

```mermaid
flowchart LR

A["👤 Usuario"] --> B["⚛️ React (Frontend)"]

B --> C["⚡ FastAPI (API REST)"]

C --> D["📄 Procesamiento de PDFs"]

D --> E["🧠 Embeddings & Base Vectorial"]

E --> C

C --> B

B --> A
Esta separación permite aislar la lógica pesada de procesamiento de documentos y consultas vectoriales de la experiencia de usuario en el cliente.📂 Estructura del proyectoPlaintextRAG-MVP/
│
├── backend/
│   ├── server_fastapi.py    # Servidor y endpoints de la API REST
│   ├── ingest.py            # Lógica de procesamiento y vectorización de PDFs
│   ├── query.py             # Motor de recuperación y consultas RAG
│   ├── config.py            # Configuración de rutas y variables
│   └── requirements.txt     # Dependencias de Python
│
├── frontend/
│   ├── src/
│   │   ├── api/             # Conexión centralizada con el backend
│   │   ├── components/      # Componentes modulares (Chat, Status, ManualList, UploadManual)
│   │   ├── styles/          # Hojas de estilos personalizadas (App.css, theme.css)
│   │   ├── App.jsx          # Componente raíz de la aplicación
│   │   └── main.jsx         # Punto de montaje de React
│   ├── package.json
│   └── vite.config.js
│
└── .gitignore
🔄 Flujo de funcionamientoCada vez que se sube un documento o se realiza una consulta, el sistema sigue este recorrido:Plaintext1. El usuario sube un PDF a través de la interfaz.
        │
        ▼
2. FastAPI recibe el fichero y ejecuta el script de ingesta.
        │
        ▼
3. El documento se divide en fragmentos y se vectoriza.
        │
        ▼
4. El usuario realiza una pregunta en el chat.
        │
        ▼
5. El motor RAG busca los fragmentos más relevantes en los manuales.
        │
        ▼
6. Se genera la respuesta basada en el contexto recuperado.
        │
        ▼
7. React muestra la respuesta detallada en pantalla.
⚙️ Instalación y ejecuciónClonar el repositorioBashgit clone [https://github.com/Deve-Lopez/RAG-MVP.git](https://github.com/Deve-Lopez/RAG-MVP.git)
1. Configurar y arrancar el BackendBashcd backend
python -m venv .venv

# Activar el entorno virtual:
# En Windows (PowerShell/CMD):
.venv\Scripts\activate
# En macOS / Linux:
source .venv/bin/activate

# Instalar dependencias y ejecutar el servidor
pip install -r requirements.txt
uvicorn server_fastapi.py --host 0.0.0.0 --port 8000
2. Configurar y arrancar el FrontendAbre una nueva pestaña o ventana en tu terminal, dirígete a la carpeta del frontend y arranca el servidor de desarrollo:Bashcd frontend
npm install
npm run dev
Una vez ejecutado, abre tu navegador e ingresa a la URL proporcionada por Vite (por defecto: http://localhost:5173).🧠 Decisiones de diseñoDecisiónMotivoReact + ViteDesarrollo rápido, modular y con una excelente experiencia de usuario en el cliente.FastAPIPermite construir una API REST rápida, tipada y con soporte asíncrono ideal para pipelines de IA.Arquitectura RAGGarantiza que las respuestas del asistente estén estrictamente contextualizadas en la documentación técnica real aportada.Bootstrap + Custom CSSEstilos modulares combinados con variables globales para un diseño limpio, moderno y adaptativo.📊 Diagrama de secuenciaFragmento de códigosequenceDiagram

participant U as Usuario

participant R as React (Frontend)

participant A as FastAPI (Backend)

participant I as Ingest / Vector Engine

U->>R: Sube manual PDF o realiza pregunta

R->>A: POST /upload o POST /query

A->>I: Procesa documento o busca contexto RAG

I-->>A: Retorna fragmentos o estado indexado

A-->>R: Respuesta JSON

R-->>U: Actualiza interfaz (Chat / Lista de manuales)
💡 Lo aprendidoEste proyecto me permitió comprender a fondo cómo conectar el procesamiento de lenguaje natural con bases de conocimiento reales.A diferencia de un chat simple, una arquitectura RAG introduce el reto de gestionar la recuperación precisa de información, el manejo de ficheros binarios y la sincronización de estados entre una interfaz moderna en React y un motor de procesamiento vectorial en Python.
