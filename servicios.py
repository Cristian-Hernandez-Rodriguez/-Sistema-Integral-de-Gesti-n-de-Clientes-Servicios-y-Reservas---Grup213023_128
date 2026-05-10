"""
servicios.py — Clase abstracta Servicio y tres servicios especializados.
              Implementa polimorfismo, métodos sobrescritos y sobrecargados.
"""
from abc import abstractmethod
from entidades import EntidadBase
from excepciones import (
    ServicioNoDisponibleError,
    ParametroFaltanteError,
    CalculoInconsistenteError,
)
import logger


# ─────────────────────────────────────────────
# Clase abstracta Servicio
# ─────────────────────────────────────────────
class Servicio(EntidadBase):
    """Clase abstracta que representa un servicio de Software FJ."""

    IVA_DEFAULT = 0.19   # 19 %

    def __init__(self, nombre: str, precio_base: float, disponible: bool = True):
        super().__init__(nombre)
        if precio_base is None:
            raise ParametroFaltanteError("precio_base")
        if not isinstance(precio_base, (int, float)) or precio_base < 0:
            raise CalculoInconsistenteError(
                f"precio_base debe ser un número positivo, se recibió {precio_base!r}"
            )
        self._precio_base = float(precio_base)
        self._disponible  = disponible

    # ── Propiedades ────────────────────────────
    @property
    def precio_base(self) -> float:
        return self._precio_base

    @property
    def disponible(self) -> bool:
        return self._disponible

    @disponible.setter
    def disponible(self, valor: bool) -> None:
        self._disponible = bool(valor)

    # ── Métodos abstractos (polimorfismo) ──────
    @abstractmethod
    def calcular_costo(self, duracion_horas: float, **kwargs) -> float:
        """Calcula el costo total del servicio."""
        ...

    @abstractmethod
    def validar_parametros(self, duracion_horas: float, **kwargs) -> None:
        """Valida los parámetros antes de crear una reserva."""
        ...

    # ── Método sobrecargado: calcular_costo_con ─
    def calcular_costo_con(
        self,
        duracion_horas: float,
        descuento: float = 0.0,
        con_iva: bool = True,
        iva: float = None,
    ) -> float:
        """
        Versión enriquecida del cálculo de costo.
        Soporta descuento porcentual, IVA configurable.
        """
        if iva is None:
            iva = self.IVA_DEFAULT
        if not (0 <= descuento < 1):
            raise CalculoInconsistenteError(
                f"Descuento debe estar entre 0 y 1, se recibió {descuento}"
            )
        if not (0 <= iva <= 1):
            raise CalculoInconsistenteError(
                f"IVA debe estar entre 0 y 1, se recibió {iva}"
            )
        base = self.calcular_costo(duracion_horas)
        subtotal = base * (1 - descuento)
        total = subtotal * (1 + iva) if con_iva else subtotal
        return round(total, 2)

    # ── Verificar disponibilidad ───────────────
    def verificar_disponibilidad(self) -> None:
        if not self._disponible:
            raise ServicioNoDisponibleError(self._nombre, "marcado como no disponible")

    # ── EntidadBase ────────────────────────────
    def validar(self) -> bool:
        return self._disponible and self._precio_base >= 0

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "tipo": type(self).__name__,
            "nombre": self._nombre,
            "precio_base": self._precio_base,
            "disponible": self._disponible,
        }


# ─────────────────────────────────────────────
# 1. Reserva de Sala
# ─────────────────────────────────────────────
class ReservaSala(Servicio):
    """Servicio de reserva de salas de reuniones o conferencias."""

    CAPACIDADES_VALIDAS = [5, 10, 20, 50]

    def __init__(self, nombre: str, precio_hora: float, capacidad: int = 10):
        super().__init__(nombre, precio_hora)
        if capacidad not in self.CAPACIDADES_VALIDAS:
            raise CalculoInconsistenteError(
                f"Capacidad {capacidad} no válida. Opciones: {self.CAPACIDADES_VALIDAS}"
            )
        self._capacidad = capacidad
        logger.info(f"Servicio ReservaSala creado: {nombre}, cap={capacidad}")

    @property
    def capacidad(self) -> int:
        return self._capacidad

    def calcular_costo(self, duracion_horas: float, **kwargs) -> float:
        """Costo = precio_hora × horas. Horas extra (>4) tienen recargo del 20 %."""
        self.validar_parametros(duracion_horas)
        if duracion_horas <= 4:
            return round(self._precio_base * duracion_horas, 2)
        base = self._precio_base * 4
        extra = self._precio_base * (duracion_horas - 4) * 1.20
        return round(base + extra, 2)

    def validar_parametros(self, duracion_horas: float, **kwargs) -> None:
        self.verificar_disponibilidad()
        if not isinstance(duracion_horas, (int, float)) or duracion_horas <= 0:
            raise CalculoInconsistenteError("Duración debe ser > 0 horas")
        if duracion_horas > 12:
            raise CalculoInconsistenteError("No se puede reservar sala por más de 12 horas")

    def describir(self) -> str:
        return (
            f"[Sala] {self._nombre} (id={self._id})\n"
            f"  Precio/hora : ${self._precio_base:,.0f}\n"
            f"  Capacidad   : {self._capacidad} personas\n"
            f"  Disponible  : {'Sí' if self._disponible else 'No'}"
        )


# ─────────────────────────────────────────────
# 2. Alquiler de Equipos
# ─────────────────────────────────────────────
class AlquilerEquipo(Servicio):
    """Servicio de alquiler de equipos tecnológicos."""

    def __init__(self, nombre: str, precio_dia: float, cantidad_disponible: int = 1):
        super().__init__(nombre, precio_dia)
        if not isinstance(cantidad_disponible, int) or cantidad_disponible < 0:
            raise CalculoInconsistenteError("cantidad_disponible debe ser entero ≥ 0")
        self._stock = cantidad_disponible
        logger.info(f"Servicio AlquilerEquipo creado: {nombre}, stock={cantidad_disponible}")

    @property
    def stock(self) -> int:
        return self._stock

    def reducir_stock(self, cantidad: int = 1) -> None:
        if cantidad > self._stock:
            raise ServicioNoDisponibleError(
                self._nombre, f"stock insuficiente ({self._stock} disponibles)"
            )
        self._stock -= cantidad

    def calcular_costo(self, duracion_horas: float, **kwargs) -> float:
        """Costo por días completos (fracción se redondea al alza). Mín. 1 día."""
        self.validar_parametros(duracion_horas)
        import math
        dias = max(1, math.ceil(duracion_horas / 8))
        return round(self._precio_base * dias, 2)

    def validar_parametros(self, duracion_horas: float, **kwargs) -> None:
        self.verificar_disponibilidad()
        if self._stock <= 0:
            raise ServicioNoDisponibleError(self._nombre, "sin stock disponible")
        if not isinstance(duracion_horas, (int, float)) or duracion_horas <= 0:
            raise CalculoInconsistenteError("Duración debe ser > 0 horas")

    def describir(self) -> str:
        return (
            f"[Equipo] {self._nombre} (id={self._id})\n"
            f"  Precio/día  : ${self._precio_base:,.0f}\n"
            f"  Stock       : {self._stock} unidades\n"
            f"  Disponible  : {'Sí' if self._disponible else 'No'}"
        )


# ─────────────────────────────────────────────
# 3. Asesoría Especializada
# ─────────────────────────────────────────────
ESPECIALIDADES = ["Tecnología", "Jurídica", "Financiera", "Estratégica", "RRHH"]


class AsesoriaEspecializada(Servicio):
    """Servicio de asesoría con expertos de Software FJ."""

    def __init__(self, nombre: str, precio_hora: float, especialidad: str, nivel_experto: int = 1):
        super().__init__(nombre, precio_hora)
        if especialidad not in ESPECIALIDADES:
            raise CalculoInconsistenteError(
                f"Especialidad '{especialidad}' no reconocida. Válidas: {ESPECIALIDADES}"
            )
        if nivel_experto not in (1, 2, 3):
            raise CalculoInconsistenteError("nivel_experto debe ser 1, 2 o 3")
        self._especialidad  = especialidad
        self._nivel_experto = nivel_experto
        logger.info(f"Servicio Asesoría creado: {nombre}, esp={especialidad}, nivel={nivel_experto}")

    # Factor de precio según nivel (1=Junior, 2=Senior, 3=Principal)
    _FACTOR_NIVEL = {1: 1.0, 2: 1.5, 3: 2.2}

    @property
    def especialidad(self) -> str:
        return self._especialidad

    @property
    def nivel_experto(self) -> int:
        return self._nivel_experto

    def calcular_costo(self, duracion_horas: float, **kwargs) -> float:
        """Costo = precio_base × horas × factor_nivel. Mínimo 1 hora."""
        self.validar_parametros(duracion_horas)
        horas = max(1, duracion_horas)
        factor = self._FACTOR_NIVEL[self._nivel_experto]
        return round(self._precio_base * horas * factor, 2)

    def validar_parametros(self, duracion_horas: float, **kwargs) -> None:
        self.verificar_disponibilidad()
        if not isinstance(duracion_horas, (int, float)) or duracion_horas <= 0:
            raise CalculoInconsistenteError("Duración de asesoría debe ser > 0 horas")
        if duracion_horas > 8:
            raise CalculoInconsistenteError("Asesoría no puede exceder 8 horas por sesión")

    def describir(self) -> str:
        niveles = {1: "Junior", 2: "Senior", 3: "Principal"}
        return (
            f"[Asesoría] {self._nombre} (id={self._id})\n"
            f"  Especialidad : {self._especialidad}\n"
            f"  Nivel        : {niveles[self._nivel_experto]}\n"
            f"  Precio/hora  : ${self._precio_base:,.0f}\n"
            f"  Disponible   : {'Sí' if self._disponible else 'No'}"
        )
