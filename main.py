"""
main.py — Demostración del sistema Software FJ.
          Simula 12 operaciones (válidas e inválidas) con manejo de excepciones.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from gestor import GestorSistema
from servicios import ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from excepciones import SistemaFJError
import logger

SEP = "─" * 60


def titulo(n: int, texto: str):
    print(f"\n{SEP}")
    print(f"  Operación {n}: {texto}")
    print(SEP)


def ejecutar_simulacion() -> dict:
    """Ejecuta todas las operaciones y retorna log acumulado + resumen."""
    gestor = GestorSistema()
    log_operaciones = []

    def log(msg: str):
        print(msg)
        log_operaciones.append(msg)

    # ═══════════════════════════════════════════
    # OP 1 — Registrar cliente válido
    # ═══════════════════════════════════════════
    titulo(1, "Registrar cliente válido")
    try:
        c1 = gestor.registrar_cliente(
            nombre="María Rodríguez",
            correo="maria@softwarefj.com",
            telefono="3001234567",
            documento="CC1098765432"
        )
        log(f"✅ Cliente registrado: {c1.nombre} (doc={c1.documento})")
    except SistemaFJError as exc:
        log(f"❌ {exc}")

    # ═══════════════════════════════════════════
    # OP 2 — Registrar cliente con correo inválido
    # ═══════════════════════════════════════════
    titulo(2, "Registrar cliente con correo inválido")
    try:
        c_bad = gestor.registrar_cliente(
            nombre="Juan Pérez",
            correo="correo_sin_arroba",
            telefono="3109876543",
            documento="CC9876543210"
        )
        log(f"Cliente: {c_bad.nombre}")
    except SistemaFJError as exc:
        log(f"❌ Error esperado capturado [{exc.codigo}]: {exc}")
    finally:
        log("   (bloque finally ejecutado — sistema sigue activo)")

    # ═══════════════════════════════════════════
    # OP 3 — Registrar segundo cliente válido
    # ═══════════════════════════════════════════
    titulo(3, "Registrar segundo cliente válido")
    try:
        c2 = gestor.registrar_cliente(
            nombre="Carlos Gómez",
            correo="carlos.gomez@empresa.co",
            telefono="+57 310 555 0001",
            documento="CE98765432"
        )
        log(f"✅ Cliente registrado: {c2.nombre}")
    except SistemaFJError as exc:
        log(f"❌ {exc}")

    # ═══════════════════════════════════════════
    # OP 4 — Crear servicios válidos
    # ═══════════════════════════════════════════
    titulo(4, "Crear servicios válidos")
    try:
        sala_a = ReservaSala("Sala Orión", precio_hora=80_000, capacidad=10)
        equipo = AlquilerEquipo("Laptop Dell XPS", precio_dia=150_000, cantidad_disponible=3)
        asesoria = AsesoriaEspecializada(
            "Consultoría Tech", precio_hora=200_000,
            especialidad="Tecnología", nivel_experto=2
        )
        gestor.agregar_servicio(sala_a)
        gestor.agregar_servicio(equipo)
        gestor.agregar_servicio(asesoria)
        log(f"✅ {sala_a.describir()}")
        log(f"✅ {equipo.describir()}")
        log(f"✅ {asesoria.describir()}")
    except SistemaFJError as exc:
        log(f"❌ {exc}")

    # ═══════════════════════════════════════════
    # OP 5 — Crear servicio con parámetros inválidos
    # ═══════════════════════════════════════════
    titulo(5, "Crear servicio con especialidad inválida")
    try:
        bad_srv = AsesoriaEspecializada(
            "Asesoría Fantasma", precio_hora=100_000,
            especialidad="Magia", nivel_experto=1
        )
        gestor.agregar_servicio(bad_srv)
    except SistemaFJError as exc:
        log(f"❌ Error esperado [{exc.codigo}]: {exc}")

    # ═══════════════════════════════════════════
    # OP 6 — Reserva y procesamiento exitoso
    # ═══════════════════════════════════════════
    titulo(6, "Reserva de sala exitosa con IVA y descuento")
    try:
        r1 = gestor.crear_reserva(c1, sala_a, duracion_horas=3, descuento=0.10, con_iva=True)
        r1.confirmar()
        resultado = r1.procesar()
        log(f"✅ {r1.describir()}")
        log(f"   Costo final: ${resultado['costo_total']:,.2f}")
    except SistemaFJError as exc:
        log(f"❌ {exc}")

    # ═══════════════════════════════════════════
    # OP 7 — Reserva de equipo exitosa
    # ═══════════════════════════════════════════
    titulo(7, "Reserva de equipo (2 días) exitosa")
    try:
        r2 = gestor.crear_reserva(c2, equipo, duracion_horas=16)
        resultado2 = r2.procesar()
        log(f"✅ {r2.describir()}")
        log(f"   Costo final: ${resultado2['costo_total']:,.2f}")
    except SistemaFJError as exc:
        log(f"❌ {exc}")

    # ═══════════════════════════════════════════
    # OP 8 — Reserva de asesoría exitosa (nivel Senior)
    # ═══════════════════════════════════════════
    titulo(8, "Reserva de asesoría tecnológica senior")
    try:
        r3 = gestor.crear_reserva(c1, asesoria, duracion_horas=4)
        r3.confirmar()
        resultado3 = r3.procesar()
        log(f"✅ {r3.describir()}")
        log(f"   Costo final: ${resultado3['costo_total']:,.2f}")
    except SistemaFJError as exc:
        log(f"❌ {exc}")

    # ═══════════════════════════════════════════
    # OP 9 — Reserva inválida: duración negativa
    # ═══════════════════════════════════════════
    titulo(9, "Reserva con duración negativa (debe fallar)")
    try:
        r_bad = gestor.crear_reserva(c1, sala_a, duracion_horas=-2)
        r_bad.procesar()
    except SistemaFJError as exc:
        log(f"❌ Error esperado [{exc.codigo}]: {exc}")

    # ═══════════════════════════════════════════
    # OP 10 — Cancelar reserva ya procesada
    # ═══════════════════════════════════════════
    titulo(10, "Cancelar reserva ya procesada (debe fallar)")
    try:
        r1.cancelar("Solicitud del cliente")
    except SistemaFJError as exc:
        log(f"❌ Error esperado [{exc.codigo}]: {exc}")

    # ═══════════════════════════════════════════
    # OP 11 — Servicio marcado no disponible
    # ═══════════════════════════════════════════
    titulo(11, "Reservar servicio no disponible")
    try:
        sala_a.disponible = False
        r_nd = gestor.crear_reserva(c2, sala_a, duracion_horas=2)
        r_nd.procesar()
    except SistemaFJError as exc:
        log(f"❌ Error esperado [{exc.codigo}]: {exc}")
    finally:
        sala_a.disponible = True  # Restaurar
        log("   Sala restaurada a disponible")

    # ═══════════════════════════════════════════
    # OP 12 — calcular_costo_con (método sobrecargado)
    # ═══════════════════════════════════════════
    titulo(12, "Demostración de método sobrecargado calcular_costo_con")
    try:
        sin_iva  = asesoria.calcular_costo_con(2, descuento=0.0,  con_iva=False)
        con_iva  = asesoria.calcular_costo_con(2, descuento=0.0,  con_iva=True)
        con_desc = asesoria.calcular_costo_con(2, descuento=0.20, con_iva=True)
        log(f"  Asesoría 2h sin IVA:            ${sin_iva:>12,.2f}")
        log(f"  Asesoría 2h con IVA 19%:        ${con_iva:>12,.2f}")
        log(f"  Asesoría 2h con 20% desc + IVA: ${con_desc:>12,.2f}")
    except SistemaFJError as exc:
        log(f"❌ {exc}")

    # ═══════════════════════════════════════════
    # Resumen final
    # ═══════════════════════════════════════════
    resumen = gestor.resumen()
    print(f"\n{'═'*60}")
    print("  RESUMEN DEL SISTEMA")
    print(f"{'═'*60}")
    for k, v in resumen.items():
        print(f"  {k:<25}: {v}")
    print(f"{'═'*60}\n")

    logs = logger.leer_logs()
    print(f"  Eventos en log: {len(logs)} líneas → sistema_fj.log")

    return {
        "operaciones": log_operaciones,
        "resumen": resumen,
        "logs": [l.strip() for l in logs],
        "clientes": gestor.listar_clientes(),
        "servicios": gestor.listar_servicios(),
        "reservas": gestor.listar_reservas(),
    }


if __name__ == "__main__":
    ejecutar_simulacion()
