# RAG Híbrido Universal (FAISS + BM25, CPU) + Qwen2.5 (GPU)

Sistema multi-manual para el CRM de oficios: indexación 100% en CPU (Ryzen),
generación de respuestas 100% en GPU (RX 580 vía Ollama).

## Instalación

```bash
pip install -r requirements.txt
```

Además necesitas Ollama corriendo con el modelo:

```bash
ollama pull qwen2.5:7b-instruct-q4_K_M
```

Y, si tu RX 580 no es detectada, exporta antes de lanzar Ollama:

```bash
export HSA_OVERRIDE_GFX_VERSION=8.0.3
```

## Estructura de carpetas

```
manuals/
  fontaneria/manual1.pdf
  electricidad/manual2.pdf
  maquinaria-industrial/manual3.pdf
cache/            <- se genera solo, no lo toques a mano
  manuales.index   (FAISS)
  metadata.pkl     (texto de cada fragmento + manual + página + oficio)
  bm25.pkl         (índice léxico)
  manifest.pkl     (hash de cada PDF ya indexado, para no reprocesar)
```

El nombre de la subcarpeta dentro de `manuals/` se usa como "oficio" de cada
manual (no hay ningún oficio asumido por defecto).

## Uso

1. Coloca tus PDFs en `manuals/<oficio>/`.
2. Indexa (o reindexa) todo lo nuevo/modificado:
   ```bash
   python ingest.py
   ```
3. Pregunta:
   ```bash
   python query.py "¿qué hago si salta el DTC P0126?"
   ```
4. (Opcional) Deja el watcher corriendo en segundo plano para indexar PDFs
   nuevos automáticamente en caliente, sin reiniciar nada:
   ```bash
   python watcher.py
   ```

## Notas de diseño

- **Chunking por bloques con PyMuPDF**: igual que ya validaste contra las
  alucinaciones del manual Mazda de 7452 páginas, se respeta la estructura
  del PDF en vez de trocear por página completa.
- **Fusión híbrida (RRF)**: combina el ranking léxico (BM25, bueno para
  códigos exactos tipo "P0126" o "QK") con el ranking semántico (FAISS,
  bueno para "el aparato que corta la luz" → disyuntor).
- **Reranker + umbral**: el cross-encoder descarta fragmentos irrelevantes
  antes de que lleguen al LLM. `RERANKER_MIN_SCORE` en `config.py` está en
  0.0 de partida — ajústalo con tus propias pruebas, como hiciste antes.
- **Incremental**: `manifest.pkl` guarda el hash de cada PDF, así que
  reindexar solo procesa los manuales nuevos o modificados; los demás no
  se retocan y la carga sigue siendo casi instantánea con 50 manuales.

## Cómo probar el MVP en tu máquina

1. Mete un PDF cualquiera en `manuals/<oficio>/` (p. ej. `manuals/electricidad/prueba.pdf`).
2. `python ingest.py` — deberías ver el fragmento contado en el log.
3. `python query.py "una pregunta sobre ese manual"` — comprueba que:
   - Recupera el fragmento correcto (revisa el log de fusión si algo falla).
   - Qwen responde solo con lo que hay en el fragmento, sin inventar.
4. Repite con una pregunta que NO tenga respuesta en el manual: el sistema
   debe decir explícitamente que no encuentra la respuesta, no inventarla.

Este MVP es intencionalmente simple (sin agente clarificador ni marcador de
decisión) para primero validar que la recuperación híbrida funciona bien.
Cuando esté verificado, añadimos encima cualquier capa extra que necesites.
