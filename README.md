# 🤖 RAG Manual Assistant

<p align="center">

**Asistente inteligente basado en IA para consultar documentación técnica mediante Retrieval-Augmented Generation (RAG).**

Combina búsqueda híbrida (**FAISS + BM25**), **reranking con Cross-Encoder** y un **LLM local ejecutado con Ollama** para ofrecer respuestas precisas utilizando exclusivamente la información contenida en los manuales.

</p>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.116-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-7-646CFF?logo=vite&logoColor=white)
![FAISS](https://img.shields.io/badge/FAISS-Vector%20Search-blue)
![BM25](https://img.shields.io/badge/BM25-Hybrid%20Retrieval-orange)
![Ollama](https://img.shields.io/badge/Ollama-Qwen2.5-black)
![Licencia](https://img.shields.io/badge/Licencia-MIT-success)

</p>

---

## 📖 Descripción

**RAG Manual Assistant** es una aplicación Full Stack desarrollada para consultar manuales técnicos mediante Inteligencia Artificial.

A diferencia de un chatbot tradicional, el modelo no responde utilizando únicamente su conocimiento previo. Antes de generar una respuesta, recupera la información más relevante desde los manuales PDF cargados por el usuario.

Para ello implementa una arquitectura **Retrieval-Augmented Generation (RAG)** basada en recuperación híbrida, combinando búsqueda semántica, búsqueda léxica y un proceso de reranking para construir el mejor contexto posible antes de consultar al modelo de lenguaje.

Toda la inferencia se realiza **de forma local** mediante **Ollama**, garantizando privacidad, rapidez y control total sobre el modelo utilizado.

---

## 🎯 Objetivos

- Consultar documentación técnica mediante lenguaje natural.
- Reducir las alucinaciones del modelo utilizando únicamente información documentada.
- Obtener respuestas precisas incluso en manuales de cientos de páginas.
- Demostrar una arquitectura RAG moderna utilizando herramientas Open Source.
- Servir como proyecto de portfolio para mostrar conocimientos en IA, Backend y Frontend.

---

## ✨ Características principales

- 📄 Carga de manuales PDF.
- ⚡ Indexación automática.
- 🔍 Recuperación híbrida (FAISS + BM25).
- 🎯 Reordenación mediante Cross-Encoder.
- 🤖 Generación de respuestas con Qwen ejecutándose en Ollama.
- 🌍 Embeddings multilingües.
- 💬 Interfaz desarrollada en React.
- ⚡ API REST con FastAPI.
- 📱 Diseño completamente responsive.
- 🗂 Gestión de manuales desde la interfaz.

---

# 🏗️ Arquitectura

El proyecto está dividido en dos aplicaciones independientes:

```text
                ┌──────────────────────────┐
                │      Frontend React      │
                │      (Vite + Bootstrap)  │
                └─────────────┬────────────┘
                              │
                    Peticiones HTTP
                              │
                              ▼
                ┌──────────────────────────┐
                │     Backend FastAPI      │
                │       API REST           │
                └─────────────┬────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
      FAISS Index         BM25 Index        Manuales PDF
          │                   │
          └───────────┬───────┘
                      ▼
          Reciprocal Rank Fusion
                      ▼
            Cross-Encoder Reranker
                      ▼
             Construcción del contexto
                      ▼
                Ollama (Qwen 2.5)
                      ▼
             Respuesta al usuario
```

La separación entre **Frontend** y **Backend** permite desplegar la interfaz de usuario de forma independiente mientras el motor RAG continúa ejecutándose localmente.

---

# ⚙️ Tecnologías utilizadas

## Frontend

- React 19
- Vite
- Bootstrap 5
- React Icons
- Fetch API

## Backend

- Python 3.11
- FastAPI
- Uvicorn

## Inteligencia Artificial

- Ollama
- Qwen 2.5
- Sentence Transformers
- Cross Encoder

## Recuperación de información

- FAISS
- Rank-BM25
- Reciprocal Rank Fusion (RRF)

---

# 🔍 Funcionamiento del sistema

Cada consulta realizada por el usuario sigue el siguiente flujo:

1. El usuario realiza una pregunta desde la interfaz web.
2. El frontend envía la consulta al backend mediante la API REST.
3. FastAPI busca los fragmentos más relevantes utilizando FAISS y BM25.
4. Ambos resultados se fusionan mediante **Reciprocal Rank Fusion (RRF)**.
5. Un **Cross-Encoder** reordena los fragmentos según su relevancia.
6. Se construye el contexto final con los mejores resultados.
7. El contexto se envía al modelo **Qwen**, ejecutándose localmente mediante Ollama.
8. El modelo genera una respuesta basada únicamente en la información recuperada.
9. La respuesta se devuelve al frontend y se muestra al usuario.

---

# 🧠 Pipeline RAG

```text
               Manual PDF
                    │
                    ▼
          Extracción del texto
                    │
                    ▼
              Fragmentación
               (Chunking)
                    │
                    ▼
         Generación de embeddings
                    │
                    ▼
              Índice FAISS
                    │
      ┌─────────────┴─────────────┐
      ▼                           ▼
 Búsqueda semántica         Búsqueda BM25
      │                           │
      └─────────────┬─────────────┘
                    ▼
       Reciprocal Rank Fusion
                    ▼
      Cross-Encoder Reranker
                    ▼
       Construcción del contexto
                    ▼
          Ollama (Qwen 2.5)
                    ▼
          Respuesta final
```

---

# ✨ Funcionalidades

## 📄 Gestión de manuales

La aplicación permite gestionar manuales técnicos directamente desde la interfaz web.

### Características

- 📥 Subida de manuales en formato PDF.
- ⚡ Indexación automática tras la carga.
- 📋 Listado de manuales disponibles.
- 🗑 Eliminación de manuales.
- 🔄 Actualización automática del estado del sistema.

---

## 💬 Chat inteligente

El usuario puede realizar preguntas en lenguaje natural sobre cualquiera de los manuales cargados.

Ejemplos:

- ¿Cuál es el par de apriete de la culata?
- ¿Qué aceite utiliza la caja de cambios?
- ¿Cómo se desmonta el diferencial?
- ¿Cuál es el juego permitido del eje primario?

Las respuestas se generan únicamente utilizando la información presente en la documentación indexada.

---

## 🔍 Recuperación híbrida

Para localizar la información más relevante se combinan distintos métodos de recuperación.

### FAISS

Realiza una búsqueda semántica mediante embeddings, permitiendo encontrar información relacionada aunque no coincidan exactamente las palabras utilizadas.

### BM25

Realiza una búsqueda léxica tradicional, especialmente útil para localizar:

- referencias
- códigos de error
- pares de apriete
- valores numéricos
- nombres de componentes

### Reciprocal Rank Fusion

Los resultados de ambas búsquedas se combinan utilizando **RRF (Reciprocal Rank Fusion)**, mejorando significativamente la calidad de los documentos recuperados.

---

## 🎯 Reranking

Tras la recuperación inicial, un modelo **Cross-Encoder** vuelve a evaluar cada fragmento para ordenar los resultados según su relevancia real respecto a la pregunta del usuario.

Este proceso permite:

- aumentar la precisión;
- eliminar resultados poco relevantes;
- mejorar el contexto enviado al modelo de lenguaje.

---

## 🤖 Generación de respuestas

El contexto final se envía a un modelo **Qwen** ejecutado localmente mediante **Ollama**.

El modelo recibe instrucciones para responder únicamente utilizando la información recuperada de los manuales, reduciendo las alucinaciones y evitando respuestas inventadas.

---

## 📱 Interfaz moderna

La aplicación dispone de una interfaz desarrollada con **React** y **Bootstrap**, diseñada para ofrecer una experiencia sencilla e intuitiva.

Incluye:

- Estado del sistema.
- Gestión de manuales.
- Chat con IA.
- Diseño responsive.
- Interfaz limpia y moderna.

---

## 🔒 Procesamiento local

Todo el procesamiento se realiza en local.

Los documentos, embeddings y consultas permanecen en el equipo donde se ejecuta el backend, sin necesidad de enviar información a servicios externos.

---

# 🧠 ¿Por qué utilizar una arquitectura RAG?

Los modelos de lenguaje (LLMs) poseen un amplio conocimiento general, pero presentan dos limitaciones importantes cuando se utilizan para consultar documentación técnica:

- No conocen documentos privados o específicos del usuario.
- Pueden generar respuestas incorrectas o inventadas (*hallucinations*).

La arquitectura **Retrieval-Augmented Generation (RAG)** soluciona este problema recuperando primero la información más relevante desde los documentos antes de generar la respuesta.

De esta forma, el modelo responde utilizando el contenido real de los manuales en lugar de confiar únicamente en su conocimiento previo.

---

# ⚙️ Decisiones técnicas

Durante el desarrollo del proyecto se tomaron varias decisiones para mejorar la precisión del sistema.

## 🔎 FAISS para búsqueda semántica

FAISS permite realizar búsquedas mediante similitud vectorial utilizando embeddings.

Su principal ventaja es que puede localizar información relacionada incluso cuando la pregunta del usuario utiliza palabras diferentes a las del documento original.

Por ejemplo:

> Usuario:
>
> *¿Qué aceite utiliza la transmisión?*

Aunque el manual únicamente contenga la frase:

> *Manual transaxle oil*

La búsqueda semántica será capaz de relacionar ambos conceptos.

---

## 📚 BM25 para búsqueda léxica

La búsqueda vectorial no siempre es suficiente.

En documentación técnica existen elementos donde la coincidencia exacta resulta especialmente importante:

- códigos de error;
- referencias de piezas;
- números de serie;
- pares de apriete;
- valores de tensión;
- medidas y tolerancias.

Por ello se incorpora BM25 como segundo método de recuperación.

---

## 🔄 Reciprocal Rank Fusion (RRF)

Cada método de búsqueda tiene fortalezas distintas.

En lugar de elegir únicamente uno de ellos, ambos resultados se combinan mediante **Reciprocal Rank Fusion (RRF)**.

Esta estrategia mejora la calidad de los documentos recuperados sin necesidad de ajustar pesos manualmente.

---

## 🎯 Cross-Encoder

Tras recuperar los documentos candidatos, un modelo Cross-Encoder vuelve a evaluarlos individualmente.

Este paso permite:

- aumentar la precisión;
- eliminar documentos poco relevantes;
- construir un contexto de mayor calidad para el LLM.

Aunque este proceso es más costoso computacionalmente, mejora significativamente la calidad de las respuestas finales.

---

## 🤖 Ollama

El modelo de lenguaje se ejecuta completamente en local mediante **Ollama**.

Esto proporciona varias ventajas:

- privacidad de los datos;
- funcionamiento sin conexión;
- coste cero por consulta;
- control total sobre el modelo utilizado.

---

## 💻 Frontend desacoplado

La interfaz web se encuentra completamente separada del backend.

Esta arquitectura permite:

- desplegar el frontend de forma independiente;
- sustituir el backend sin modificar la interfaz;
- facilitar el mantenimiento del proyecto;
- escalar ambos componentes por separado.

---

# 📈 Flujo de una consulta

```text
Usuario

    │

    ▼

Pregunta

    │

    ▼

FastAPI

    │

    ├──────────────┐

    ▼              ▼

 FAISS          BM25

    │              │

    └──────┬───────┘

           ▼

Reciprocal Rank Fusion

           ▼

 Cross-Encoder

           ▼

 Construcción del contexto

           ▼

 Ollama (Qwen)

           ▼

Respuesta final
```

---

# 📂 Estructura del proyecto

El proyecto está dividido en dos aplicaciones independientes: un **frontend** desarrollado con React y un **backend** desarrollado con FastAPI.

```text
rag-mvp/
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   │   ├── Chat/
│   │   │   ├── ManualList/
│   │   │   ├── Status/
│   │   │   └── UploadManual/
│   │   ├── styles/
│   │   ├── App.jsx
│   │   └── main.jsx
│   │
│   ├── package.json
│   ├── vite.config.js
│   └── .env.example
│
└── backend/
    ├── config.py
    ├── main.py
    ├── query.py
    ├── index_manual.py
    ├── requirements.txt
    ├── manuals/
    ├── indexes/
    └── .env.example
```

---

# 📁 Descripción de los directorios

## Frontend

La carpeta `frontend` contiene toda la interfaz de usuario desarrollada con React.

| Directorio | Descripción |
|------------|-------------|
| `src/api` | Funciones encargadas de comunicarse con la API REST. |
| `src/components` | Componentes reutilizables de la interfaz. |
| `src/styles` | Hojas de estilo CSS. |
| `public` | Recursos estáticos. |

---

## Backend

La carpeta `backend` contiene toda la lógica del sistema RAG.

| Archivo / Carpeta | Descripción |
|-------------------|-------------|
| `main.py` | API REST desarrollada con FastAPI. |
| `config.py` | Configuración general del proyecto. |
| `query.py` | Pipeline RAG encargado de responder las consultas. |
| `index_manual.py` | Procesamiento e indexación de nuevos manuales. |
| `manuals/` | Manuales PDF cargados por el usuario. |
| `indexes/` | Índices vectoriales y estructuras de búsqueda generadas automáticamente. |

---

# ⚙️ Requisitos

Para ejecutar el proyecto es necesario disponer de:

- Python 3.11 o superior.
- Node.js 20 o superior.
- Ollama instalado.
- Git.
- npm.

---

# 📦 Dependencias principales

## Backend

- FastAPI
- Uvicorn
- FAISS
- Sentence Transformers
- Rank-BM25
- NumPy
- PyMuPDF
- Watchdog
- Ollama

## Frontend

- React
- Vite
- Bootstrap
- React Icons

---

# 🚀 Instalación

## 1. Clonar el repositorio

```bash
git clone https://github.com/Deve-Lopez/rag-mvp.git

cd rag-mvp
```

---

## 2. Configurar el backend

```bash
cd backend

python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

Instalar las dependencias:

```bash
pip install -r requirements.txt
```

---

## 3. Configurar el frontend

```bash
cd ../frontend

npm install
```

---

## 4. Variables de entorno

### Frontend

Crear un archivo `.env`:

```env
VITE_API_URL=http://localhost:8000
```

### Backend

Crear un archivo `.env`:

```env
OLLAMA_URL=http://localhost:11434
```

---

## 5. Ejecutar el backend

```bash
uvicorn main:app --reload
```

---

## 6. Ejecutar el frontend

```bash
npm run dev
```

La aplicación estará disponible en:

```
http://localhost:5173
```

---

# 🚀 Primer uso

Una vez iniciado el frontend y el backend, el flujo de utilización de la aplicación es muy sencillo.

## 1️⃣ Iniciar Ollama

Antes de ejecutar el backend, asegúrate de que Ollama está en funcionamiento.

```bash
ollama serve
```

También puedes comprobar que el modelo está disponible ejecutando:

```bash
ollama list
```

---

## 2️⃣ Iniciar el backend

Desde la carpeta **backend**:

```bash
uvicorn main:app --reload
```

La API estará disponible en:

```
http://localhost:8000
```

---

## 3️⃣ Iniciar el frontend

Desde la carpeta **frontend**:

```bash
npm run dev
```

La aplicación estará disponible en:

```
http://localhost:5173
```

---

## 4️⃣ Cargar un manual

Accede a la sección **Subir manual** y selecciona un documento PDF.

El sistema procesará automáticamente el documento:

- Extracción del texto.
- División en fragmentos (chunking).
- Generación de embeddings.
- Creación de los índices de búsqueda.

Una vez finalizado el proceso, el manual aparecerá disponible para realizar consultas.

---

## 5️⃣ Realizar una consulta

Escribe cualquier pregunta relacionada con el contenido de los manuales.

Ejemplos:

```text
¿Cuál es el par de apriete de la culata?
```

```text
¿Qué aceite utiliza la caja de cambios?
```

```text
¿Cómo se desmonta el diferencial?
```

```text
¿Cuál es el máximo alabeo permitido del eje primario?
```

El sistema buscará automáticamente la información más relevante y generará una respuesta basada exclusivamente en la documentación disponible.

---

# 🌐 API REST

El backend expone una API REST desarrollada con FastAPI.

## Obtener el estado del sistema

```http
GET /health
```

Respuesta:

```json
{
  "status": "ready",
  "models_loaded": true
}
```

---

## Obtener los manuales disponibles

```http
GET /manuals
```

---

## Subir un manual

```http
POST /upload
```

Tipo de contenido:

```
multipart/form-data
```

Parámetro:

| Campo | Tipo |
|--------|------|
| file | PDF |

---

## Eliminar un manual

```http
DELETE /manuals/{filename}
```

---

## Realizar una consulta

```http
POST /query
```

Ejemplo:

```json
{
  "question": "¿Qué aceite utiliza esta caja de cambios?"
}
```

---

# 📷 Capturas de pantalla

> **Próximamente**

Aquí se incluirán capturas de:

- Pantalla principal.
- Gestión de manuales.
- Chat con IA.
- Vista responsive.

---

# 🚀 Próximas mejoras

Aunque el proyecto ya es completamente funcional, existen varias líneas de evolución que permitirían ampliar sus capacidades.

## Funcionalidades

- [ ] Soporte para múltiples conversaciones.
- [ ] Historial de consultas.
- [ ] Respuestas en streaming.
- [ ] Selección dinámica del modelo de lenguaje.
- [ ] Carga simultánea de múltiples manuales.
- [ ] Filtrado por manual.
- [ ] Búsqueda por categorías.
- [ ] Exportación de conversaciones.

---

## Inteligencia Artificial

- [ ] Soporte para diferentes modelos de embeddings.
- [ ] Reindexación incremental.
- [ ] Optimización automática del tamaño de los fragmentos.
- [ ] Caché de respuestas frecuentes.
- [ ] Evaluación automática de la calidad de las respuestas.
- [ ] Soporte para múltiples bases vectoriales.

---

## Interfaz

- [ ] Modo oscuro.
- [ ] Indicador de progreso durante la indexación.
- [ ] Visualización de las fuentes utilizadas.
- [ ] Copiar respuestas al portapapeles.
- [ ] Mejoras de accesibilidad.
- [ ] Internacionalización.

---

## Despliegue

- [ ] Contenedorización mediante Docker.
- [ ] Despliegue completo en la nube.
- [ ] Integración continua mediante GitHub Actions.
- [ ] Monitorización del sistema.
- [ ] Gestión de variables de entorno mediante secretos.

---

# 💡 Lo que he aprendido

Durante el desarrollo de este proyecto he podido profundizar en distintos conceptos relacionados con la Inteligencia Artificial aplicada a la recuperación de información.

Entre los principales aprendizajes destacan:

- Diseño de una arquitectura RAG completa.
- Procesamiento e indexación de documentos PDF.
- Generación y utilización de embeddings.
- Búsqueda semántica mediante FAISS.
- Recuperación léxica mediante BM25.
- Fusión de resultados mediante Reciprocal Rank Fusion (RRF).
- Reranking mediante Cross-Encoder.
- Integración de modelos LLM ejecutados localmente con Ollama.
- Desarrollo de APIs REST con FastAPI.
- Desarrollo de interfaces modernas con React.
- Comunicación entre frontend y backend.
- Gestión de variables de entorno para distintos entornos de ejecución.
- Preparación del proyecto para su despliegue.

---

# 📄 Licencia

Este proyecto se distribuye bajo la licencia **MIT**.

Esto significa que puedes utilizar, modificar y distribuir el código libremente, siempre respetando los términos de dicha licencia.

Para más información consulta el archivo [`LICENSE`](LICENSE).

---

# 👨‍💻 Autor

## Daniel López Santajustina

Desarrollador Full Stack especializado en aplicaciones web e Inteligencia Artificial.

Actualmente enfocado en el desarrollo de soluciones basadas en:

- 🤖 Inteligencia Artificial
- 🧠 Retrieval-Augmented Generation (RAG)
- ⚙️ FastAPI
- ⚛️ React
- 🐍 Python
- 🗄️ Bases de datos vectoriales

### Contacto

- GitHub: https://github.com/Deve-Lopez
- LinkedIn: https://www.linkedin.com/in/lopezsantajustinadaniel

---

# 🙏 Agradecimientos

Este proyecto ha sido posible gracias a la comunidad Open Source y a las herramientas utilizadas durante su desarrollo.

En especial, gracias a los equipos detrás de:

- Python
- FastAPI
- React
- Vite
- Ollama
- FAISS
- Sentence Transformers
- Hugging Face

Su trabajo hace posible construir aplicaciones de Inteligencia Artificial cada vez más accesibles.

---

# ⭐ Estado del proyecto

> **Proyecto en desarrollo activo.**

Actualmente el proyecto continúa evolucionando con nuevas funcionalidades y mejoras orientadas a aumentar la precisión del sistema RAG y mejorar la experiencia de usuario.

---

<p align="center">

**Gracias por visitar este repositorio.**

Si el proyecto te ha resultado interesante o te ha servido de ayuda, considera dejar una ⭐ en GitHub.

</p>
