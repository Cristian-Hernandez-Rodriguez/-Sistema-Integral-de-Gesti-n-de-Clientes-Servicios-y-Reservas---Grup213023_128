"""
logger.py — Registro de eventos y errores en archivo de logs
"""
import os
import datetime

LOG_PATH = os.path.join(os.path.dirname(__file__), "sistema_fj.log")


def _timestamp() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def registrar(nivel: str, mensaje: str, exc: Exception = None) -> None:
    """Registra un evento en el archivo de logs y lo retorna como cadena."""
    linea = f"[{_timestamp()}] [{nivel}] {mensaje}"
    if exc is not None:
        tipo = type(exc).__name__
        linea += f" | Excepción: {tipo}: {exc}"
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(linea + "\n")
    except OSError:
        pass  # No bloquear si el log falla
    return linea


def info(mensaje: str) -> str:
    return registrar("INFO ", mensaje)


def advertencia(mensaje: str, exc: Exception = None) -> str:
    return registrar("WARN ", mensaje, exc)


def error(mensaje: str, exc: Exception = None) -> str:
    return registrar("ERROR", mensaje, exc)


def leer_logs() -> list[str]:
    """Devuelve las líneas del archivo de logs."""
    try:
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            return f.readlines()
    except FileNotFoundError:
        return []
