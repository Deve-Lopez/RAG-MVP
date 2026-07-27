"""
watcher.py — Detector automático de PDFs nuevos.

Vigila MANUALS_DIR (y sus subcarpetas de oficio) y, en cuanto aparece o se
modifica un .pdf, llama a ingest.index_pdfs([ruta]) para indexarlo solo,
sin tocar los manuales que ya estaban procesados.

Uso:
    python watcher.py
"""
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import config
import ingest


class PDFHandler(FileSystemEventHandler):
    """
    Gestor de eventos del sistema de archivos para la librería watchdog.
    Filtra las acciones y procesa únicamente los archivos con extensión PDF.
    """
    def _maybe_index(self, path):
        """
        Comprueba si la ruta corresponde a un PDF, espera a que termine de escribirse
        y dispara la indexación individual del archivo.
        """
        if path.lower().endswith(".pdf"):
            print(f"\nCambio detectado: {path}")
            # Pequeña espera para asegurarnos de que el archivo terminó de copiarse
            time.sleep(1)
            try:
                ingest.index_pdfs([path])
            except Exception as e:
                print(f"Error indexando {path}: {e}")

    def on_created(self, event):
        """Se activa al detectarse la creación de un nuevo archivo en el directorio."""
        if not event.is_directory:
            self._maybe_index(event.src_path)

    def on_modified(self, event):
        """Se activa cuando un archivo existente sufre modificaciones."""
        if not event.is_directory:
            self._maybe_index(event.src_path)


if __name__ == "__main__":
    print(f"Vigilando {config.MANUALS_DIR} para nuevos manuales...")
    handler = PDFHandler()
    observer = Observer()
    observer.schedule(handler, config.MANUALS_DIR, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()