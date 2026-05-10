"""
entidades.py — Clase abstracta base y clase Cliente
"""
import re
from abc import ABC, abstractmethod
from excepciones import ClienteInvalidoError, ParametroFaltanteError
import logger


# ─────────────────────────────────────────────
# Clase abstracta base
# ─────────────────────────────────────────────
class EntidadBase(ABC):
    """Clase abstracta que representa cualquier entidad del sistema."""

    _contador: int = 0

    def __init__(self, nombre: str):
        if not nombre or not isinstance(nombre, str):
            raise ParametroFaltanteError("nombre")
        EntidadBase._contador += 1
        self._id = EntidadBase._contador
        self._nombre = nombre.strip()

    @property
    def id(self) -> int:
        return self._id

    @property
    def nombre(self) -> str:
        return self._nombre

    @abstractmethod
    def describir(self) -> str:
        """Retorna descripción completa de la entidad."""
        ...

    @abstractmethod
    def validar(self) -> bool:
        """Valida la integridad de la entidad."""
        ...

    def __repr__(self) -> str:
        return f"<{type(self).__name__} id={self._id} nombre={self._nombre!r}>"


# ─────────────────────────────────────────────
# Cliente
# ─────────────────────────────────────────────
class Cliente(EntidadBase):
    """Representa un cliente con encapsulación y validaciones estrictas."""

    _CORREO_REGEX = re.compile(r"^[\w.\-+]+@[\w\-]+\.[a-zA-Z]{2,}$")
    _TEL_REGEX    = re.compile(r"^\+?[\d\s\-]{7,15}$")

    def __init__(self, nombre: str, correo: str, telefono: str, documento: str):
        super().__init__(nombre)
        self._correo    = self._validar_correo(correo)
        self._telefono  = self._validar_telefono(telefono)
        self._documento = self._validar_documento(documento)
        self._activo    = True
        logger.info(f"Cliente registrado: {self._nombre} (doc={self._documento})")

    # ── Validaciones privadas ──────────────────
    def _validar_correo(self, correo: str) -> str:
        if not correo or not isinstance(correo, str):
            raise ClienteInvalidoError("correo", correo)
        correo = correo.strip()
        if not self._CORREO_REGEX.match(correo):
            raise ClienteInvalidoError("correo", correo)
        return correo

    def _validar_telefono(self, tel: str) -> str:
        if not tel or not isinstance(tel, str):
            raise ClienteInvalidoError("telefono", tel)
        tel = tel.strip()
        if not self._TEL_REGEX.match(tel):
            raise ClienteInvalidoError("telefono", tel)
        return tel

    def _validar_documento(self, doc: str) -> str:
        if not doc or not isinstance(doc, str):
            raise ClienteInvalidoError("documento", doc)
        doc = doc.strip()
        if len(doc) < 5:
            raise ClienteInvalidoError("documento", doc)
        return doc

    # ── Propiedades (encapsulación) ────────────
    @property
    def correo(self) -> str:
        return self._correo

    @property
    def telefono(self) -> str:
        return self._telefono

    @property
    def documento(self) -> str:
        return self._documento

    @property
    def activo(self) -> bool:
        return self._activo

    def desactivar(self) -> None:
        self._activo = False
        logger.advertencia(f"Cliente desactivado: {self._nombre}")

    # ── Métodos de EntidadBase ─────────────────
    def describir(self) -> str:
        estado = "Activo" if self._activo else "Inactivo"
        return (
            f"Cliente #{self._id} — {self._nombre}\n"
            f"  Documento : {self._documento}\n"
            f"  Correo    : {self._correo}\n"
            f"  Teléfono  : {self._telefono}\n"
            f"  Estado    : {estado}"
        )

    def validar(self) -> bool:
        return bool(self._nombre and self._correo and self._documento and self._activo)

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "nombre": self._nombre,
            "correo": self._correo,
            "telefono": self._telefono,
            "documento": self._documento,
            "activo": self._activo,
        }
