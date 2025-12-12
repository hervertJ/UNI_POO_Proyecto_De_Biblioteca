from abc import ABC, abstractmethod
from datetime import date, timedelta
from typing import List, Union
import random

# === CLASES ABSTRACTAS PARA POLIMORFISMO ===


class Persona(ABC):
    def __init__(self, id: int, nombre: str, correo: str):
        self._id = id
        self._nombre = nombre
        self._correo = correo

    @abstractmethod
    def validar_datos(self) -> bool:
        pass

    @property
    def id(self):
        return self._id

    @property
    def nombre(self):
        return self._nombre


# --- NUEVA CLASE: RESEÑA ---
class Resena:
    def __init__(
        self, usuario: "Usuario", calificacion: int, comentario: str, fecha: date
    ):
        self._usuario = usuario
        self._calificacion = max(0, min(5, int(calificacion)))  # Asegurar rango 0-5
        self._comentario = comentario
        self._fecha = fecha

    @property
    def usuario(self):
        return self._usuario

    @property
    def calificacion(self):
        return self._calificacion

    @property
    def comentario(self):
        return self._comentario

    @property
    def fecha(self):
        return self._fecha


class MaterialBibliografico(ABC):
    def __init__(
        self,
        id: int,
        titulo: str,
        autor: str,
        año_publicacion: int,
        descripcion: str,
        portada_url: str,
        materia: str,
        total_unidades: int = 1,
    ):
        self._id = id
        self._titulo = titulo
        self._autor = autor
        self._año_publicacion = año_publicacion
        self._descripcion = descripcion
        self._portada_url = portada_url
        self._materia = materia

        self._total_unidades = max(1, total_unidades)
        self._unidades_prestadas = 0

        self._lista_reservas: List[Usuario] = []
        self._resenas: List[Resena] = []  # NUEVO: Lista de reseñas

    @abstractmethod
    def calcular_dias_prestamo(self, usuario: "Usuario") -> int:
        pass

    @abstractmethod
    def es_renovable(self) -> bool:
        pass

    # --- Métodos de Reserva ---
    def agregar_reserva(self, usuario: "Usuario"):
        if usuario not in self._lista_reservas:
            self._lista_reservas.append(usuario)

    def obtener_siguiente_reserva(self) -> Union["Usuario", None]:
        if self._lista_reservas:
            return self._lista_reservas.pop(0)
        return None

    def tiene_reservas(self) -> bool:
        return len(self._lista_reservas) > 0

    def esta_reservado_por(self, usuario: "Usuario") -> bool:
        return usuario in self._lista_reservas

    def obtener_posicion_reserva(self, usuario: "Usuario") -> int:
        try:
            return self._lista_reservas.index(usuario) + 1
        except ValueError:
            return 0

    # --- NUEVOS MÉTODOS: RESEÑAS ---
    def agregar_resena(self, resena: Resena):
        self._resenas.append(resena)

    @property
    def resenas(self) -> List[Resena]:
        return self._resenas

    @property
    def promedio_calificacion(self) -> float:
        if not self._resenas:
            return 0.0
        total = sum(r.calificacion for r in self._resenas)
        return round(total / len(self._resenas), 1)

    # --- Propiedades ---
    @property
    def id(self):
        return self._id

    @property
    def titulo(self):
        return self._titulo

    @property
    def autor(self):
        return self._autor

    @property
    def año_publicacion(self):
        return self._año_publicacion

    @property
    def descripcion(self):
        return self._descripcion

    @property
    def portada_url(self):
        return self._portada_url

    @property
    def materia(self):
        return self._materia

    @property
    def lista_reservas(self):
        return self._lista_reservas

    # --- Propiedades de Stock ---
    @property
    def total_unidades(self) -> int:
        return self._total_unidades

    @property
    def unidades_disponibles(self) -> int:
        return self._total_unidades - self._unidades_prestadas

    @property
    def esta_disponible(self) -> bool:
        return self.unidades_disponibles > 0

    @property
    def esta_prestado(self) -> bool:
        return not self.esta_disponible


class EstadoPrestamo(ABC):
    def __init__(self, prestamo: "Prestamo"):
        self._prestamo = prestamo
        self._notificacion: str | None = None

    @abstractmethod
    def procesar_prestamo(self):
        pass

    @abstractmethod
    def calcular_multa(self, fecha_actual: date) -> float:
        pass

    @property
    def notificacion(self) -> str | None:
        return self._notificacion


# === JERARQUÍA DE USUARIOS ===
class Usuario(Persona):
    def __init__(self, id: int, nombre: str, correo: str, rol: str):
        super().__init__(id, nombre, correo)
        self._rol = rol
        self._prestamos: List[Prestamo] = []
        self._limite_prestamos: int = 5

    def validar_datos(self) -> bool:
        return (
            self._id > 0
            and len(self._nombre) > 0
            and "@" in self._correo
            and len(self._rol) > 0
        )

    def registrar(self):
        if self.validar_datos():
            return True
        return False

    def agregar_prestamo(self, prestamo: "Prestamo"):
        self._prestamos.append(prestamo)

    def tiene_multas(self, fecha_actual: date) -> bool:
        for p in self._prestamos:
            if p.calcular_multa(fecha_actual) > 0:
                return True
        return False

    @property
    def limite_prestamos(self) -> int:
        return self._limite_prestamos

    @property
    def prestamos(self) -> List["Prestamo"]:
        return self._prestamos

    @property
    def rol(self) -> str:
        return self._rol

    @property
    def correo(self) -> str:
        return self._correo


class Estudiante(Usuario):
    def __init__(self, id: int, nombre: str, correo: str, carrera: str, semestre: int):
        super().__init__(id, nombre, correo, "Estudiante")
        self._carrera = carrera
        self._semestre = semestre
        self._limite_prestamos = 5

    @property
    def carrera(self):
        return self._carrera

    @property
    def semestre(self):
        return self._semestre


class Profesor(Usuario):
    def __init__(
        self, id: int, nombre: str, correo: str, departamento: str, tipo_contrato: str
    ):
        super().__init__(id, nombre, correo, "Profesor")
        self._departamento = departamento
        self._tipo_contrato = tipo_contrato
        self._limite_prestamos = 20

    @property
    def departamento(self):
        return self._departamento

    @property
    def tipo_contrato(self):
        return self._tipo_contrato


class Administrativo(Usuario):
    def __init__(self, id: int, nombre: str, correo: str, area_trabajo: str):
        super().__init__(id, nombre, correo, "Administrativo")
        self._area_trabajo = area_trabajo
        self._limite_prestamos = 999

    @property
    def area_trabajo(self):
        return self._area_trabajo


# === JERARQUÍA DE MATERIALES BIBLIOGRÁFICOS ===


class Libro(MaterialBibliografico):
    def __init__(
        self,
        id: int,
        titulo: str,
        autor: str,
        año_publicacion: int,
        descripcion: str,
        portada_url: str,
        editorial: str,
        materia: str,
        total_unidades: int = 1,
        isbn: str = "",
    ):
        super().__init__(
            id,
            titulo,
            autor,
            año_publicacion,
            descripcion,
            portada_url,
            materia,
            total_unidades,
        )
        self._editorial = editorial
        self._isbn = isbn

    @property
    def isbn(self):
        return self._isbn

    @property
    def editorial(self):
        return self._editorial

    def calcular_dias_prestamo(self, usuario: Usuario) -> int:
        if isinstance(usuario, Profesor):
            return 90
        else:
            return 15

    def es_renovable(self) -> bool:
        return True


class Revista(MaterialBibliografico):
    def __init__(
        self,
        id: int,
        titulo: str,
        autor: str,
        año_publicacion: int,
        descripcion: str,
        portada_url: str,
        numero_edicion: int,
        materia: str,
        total_unidades: int = 1,
        issn: str = "",
    ):
        super().__init__(
            id,
            titulo,
            autor,
            año_publicacion,
            descripcion,
            portada_url,
            materia,
            total_unidades,
        )
        self._numero_edicion = numero_edicion
        self._issn = issn

    @property
    def issn(self):
        return self._issn

    @property
    def numero_edicion(self):
        return self._numero_edicion

    def calcular_dias_prestamo(self, usuario: Usuario) -> int:
        return 7

    def es_renovable(self) -> bool:
        return False


class Tesis(MaterialBibliografico):
    def __init__(
        self,
        id: int,
        titulo: str,
        autor: str,
        año_defensa: int,
        descripcion: str,
        portada_url: str,
        universidad: str,
        materia: str,
        total_unidades: int = 1,
    ):
        super().__init__(
            id,
            titulo,
            autor,
            año_defensa,
            descripcion,
            portada_url,
            materia,
            total_unidades,
        )
        self._universidad = universidad

    @property
    def universidad(self):
        return self._universidad

    def calcular_dias_prestamo(self, usuario: Usuario) -> int:
        if isinstance(usuario, Profesor):
            return 30
        else:
            return 10

    def es_renovable(self) -> bool:
        return True


class MaterialDigital(MaterialBibliografico):
    def __init__(
        self,
        id: int,
        titulo: str,
        autor: str,
        año_publicacion: int,
        descripcion: str,
        portada_url: str,
        formato: str,
        materia: str,
    ):
        super().__init__(
            id,
            titulo,
            autor,
            año_publicacion,
            descripcion,
            portada_url,
            materia,
            total_unidades=1,
        )
        self._formato = formato

    @property
    def formato(self):
        return self._formato

    def calcular_dias_prestamo(self, usuario: Usuario) -> int:
        return 3

    def es_renovable(self) -> bool:
        return False

    @property
    def total_unidades(self) -> int:
        return 1

    @property
    def unidades_disponibles(self) -> int:
        return 1

    @property
    def esta_disponible(self) -> bool:
        return True

    @property
    def esta_prestado(self):
        return False

    def agregar_reserva(self, usuario: "Usuario"):
        pass

    def tiene_reservas(self) -> bool:
        return False


# === ESTADOS DE PRÉSTAMO ===
class Prestamo:
    def __init__(
        self, usuario: Usuario, material: MaterialBibliografico, fecha_inicio: date
    ):
        self._id = random.randint(10000, 99999)
        self._usuario = usuario
        self._material = material
        self._fecha_prestamo = fecha_inicio
        dias_limite = material.calcular_dias_prestamo(usuario)
        self._fecha_vencimiento = self._fecha_prestamo + timedelta(days=dias_limite)
        self._estado: EstadoPrestamo = PrestamoActivo(self)
        self._veces_renovado = 0
        self._limite_renovaciones = 1 if material.es_renovable() else 0
        if not isinstance(material, MaterialDigital):
            self._material._unidades_prestadas += 1

    def cambiar_estado(self, nuevo_estado: EstadoPrestamo):
        self._estado = nuevo_estado

    def procesar_prestamo(self):
        self._estado.procesar_prestamo()

    def calcular_multa(self, fecha_actual: date) -> float:
        return self._estado.calcular_multa(fecha_actual)

    def realizar_renovacion(self) -> (bool, str):
        if not isinstance(self._estado, PrestamoActivo):
            return (False, "No se puede renovar un préstamo vencido o devuelto.")
        if self._material.tiene_reservas():
            return (
                False,
                "No se puede renovar; hay otros usuarios esperando en reserva.",
            )
        if self._veces_renovado >= self._limite_renovaciones:
            return (
                False,
                f"Has alcanzado el límite de {self._limite_renovaciones} renovaciones.",
            )
        dias_extra = self._material.calcular_dias_prestamo(self._usuario)
        self._fecha_vencimiento += timedelta(days=dias_extra)
        self._veces_renovado += 1
        return (
            True,
            f"Renovación exitosa. Vence: {self._fecha_vencimiento.strftime('%d-%m-%Y')}.",
        )

    @property
    def id(self):
        return self._id

    @property
    def estado(self):
        return self._estado

    @property
    def usuario(self):
        return self._usuario

    @property
    def material(self):
        return self._material

    @property
    def fecha_prestamo(self):
        return self._fecha_prestamo

    @property
    def fecha_vencimiento(self):
        return self._fecha_vencimiento


class PrestamoActivo(EstadoPrestamo):
    def procesar_prestamo(self):
        pass

    def calcular_multa(self, fecha_actual: date) -> float:
        if fecha_actual > self._prestamo.fecha_vencimiento:
            dias_retraso = (fecha_actual - self._prestamo.fecha_vencimiento).days
            return dias_retraso * 5.0
        return 0.0


class PrestamoVencido(EstadoPrestamo):
    def __init__(self, prestamo: Prestamo, dias_retraso: int):
        super().__init__(prestamo)
        self._dias_retraso = dias_retraso

    @property
    def dias_retraso(self):
        return self._dias_retraso

    def procesar_prestamo(self):
        pass

    def calcular_multa(self, fecha_actual: date) -> float:
        return self._dias_retraso * 5.0


class PrestamoDevuelto(EstadoPrestamo):
    def __init__(self, prestamo: Prestamo):
        super().__init__(prestamo)
        material = self._prestamo.material
        if isinstance(material, MaterialDigital):
            return
        if material.tiene_reservas():
            siguiente_usuario = material.obtener_siguiente_reserva()
            self._notificacion = f"ATENCIÓN: '{material.titulo}' devuelto. Ha sido asignado a {siguiente_usuario.nombre} (siguiente en cola)."
        else:
            material._unidades_prestadas = max(0, material._unidades_prestadas - 1)

    def procesar_prestamo(self):
        pass

    def calcular_multa(self, fecha_actual: date) -> float:
        return 0.0


# === CLASES NO IMPLEMENTADAS EN LA WEB AÚN ===
# ... (Multa, Deudor) ...
class Multa:
    def __init__(self, dias_retraso: int):
        self._dias_retraso = dias_retraso
        self._monto = self._calcular_monto()

    def _calcular_monto(self) -> float:
        return self._dias_retraso * 5.0

    def generar_multa(self):
        # CAMBIO DE MONEDA AQUÍ
        print(
            f"Multa generada: S/.{self._monto} por {self._dias_retraso} días de retraso"
        )

    @property
    def monto(self):
        return self._monto


class Deudor(Usuario):
    def __init__(self, usuario: Usuario):
        super().__init__(usuario.id, usuario.nombre, "", usuario._rol)
        self._usuario_base = usuario

    def consultar_historial(self):
        print("Consultando historial de deudas...")

    def generar_alerta(self):
        print("ALERTA: Usuario con deudas pendientes")


# === SISTEMA CENTRAL (RESTAURADO) ===


class Catalogo:
    def __init__(self):
        self._materiales: List[MaterialBibliografico] = []

    def agregar_material(self, material: MaterialBibliografico):
        self._materiales.append(material)

    def retirar_material(self, material_id: int) -> bool:
        material = self.buscar_por_id(material_id)
        if material:
            self._materiales.remove(material)
            return True
        return False

    def buscar(
        self,
        titulo: str = "",
        autor: str = "",
        materia: str = "",
        tipo_material: str = "",
    ) -> List[MaterialBibliografico]:
        resultados = self._materiales
        if titulo:
            resultados = [m for m in resultados if titulo.lower() in m.titulo.lower()]
        if autor:
            resultados = [m for m in resultados if autor.lower() in m.autor.lower()]
        if materia and materia != "Todas":
            resultados = [m for m in resultados if materia.lower() == m.materia.lower()]
        if tipo_material and tipo_material != "Todos":
            resultados = [
                m for m in resultados if m.__class__.__name__ == tipo_material
            ]
        return resultados

    def buscar_por_id(self, material_id: int) -> MaterialBibliografico | None:
        for m in self._materiales:
            if m.id == material_id:
                return m
        return None

    def obtener_materias_unicas(self) -> List[str]:
        materias = set(m.materia for m in self._materiales)
        return sorted(list(materias))


class Biblioteca:
    def __init__(self):
        self._usuarios: List[Usuario] = []
        self._materiales: List[MaterialBibliografico] = []
        self._catalogo = Catalogo()

    def agregar_usuario(self, usuario: Usuario):
        if usuario.registrar():
            self._usuarios.append(usuario)

    def agregar_material(self, material: MaterialBibliografico):
        self._materiales.append(material)
        self._catalogo.agregar_material(material)

    def retirar_material(self, material_id: int) -> (bool, str):
        material = self._catalogo.buscar_por_id(material_id)
        if not material:
            return (False, "El material no existe.")

        if material._unidades_prestadas > 0:
            return (
                False,
                "Hay unidades de este material prestadas. No se puede retirar.",
            )

        self._materiales.remove(material)
        self._catalogo.retirar_material(material.id)
        return (True, "Material retirado exitosamente.")

    def buscar_usuario_por_id(self, usuario_id: int) -> Usuario | None:
        for u in self._usuarios:
            if u.id == usuario_id:
                return u
        return None

    def buscar_material_por_id(self, material_id: int) -> MaterialBibliografico | None:
        return self._catalogo.buscar_por_id(material_id)

    @property
    def catalogo(self) -> Catalogo:
        return self._catalogo

    @property
    def usuarios(self) -> List[Usuario]:
        return self._usuarios

    def verificar_aptitud_prestamo(
        self, usuario: Usuario, material: MaterialBibliografico
    ) -> (bool, str):
        if isinstance(material, MaterialDigital):
            return (True, "")

        for p in usuario.prestamos:
            if p.material.id == material.id and isinstance(p.estado, PrestamoActivo):
                return (
                    False,
                    "Ya tienes una unidad de este material en tu lista de préstamos.",
                )

        if not material.esta_disponible:
            return (False, "No hay unidades disponibles de este material.")

        prestamos_activos = [
            p for p in usuario.prestamos if isinstance(p.estado, PrestamoActivo)
        ]
        if len(prestamos_activos) >= usuario.limite_prestamos:
            return (
                False,
                f"Alcanzaste tu límite de {usuario.limite_prestamos} préstamos.",
            )

        return (True, "")

    def realizar_prestamo(
        self, usuario: Usuario, material: MaterialBibliografico, fecha_inicio: date
    ) -> (bool, str):
        (apto, razon) = self.verificar_aptitud_prestamo(usuario, material)

        if isinstance(material, MaterialDigital):
            nuevo_prestamo = Prestamo(usuario, material, fecha_inicio)
            usuario.agregar_prestamo(nuevo_prestamo)
            msg = f"Acceso a '{material.titulo}' concedido. Vence el {nuevo_prestamo.fecha_vencimiento.strftime('%d-%m-%Y')}."
            return (True, msg)

        if not apto:
            return (False, razon)

        nuevo_prestamo = Prestamo(usuario, material, fecha_inicio)
        usuario.agregar_prestamo(nuevo_prestamo)

        msg = f"¡Préstamo exitoso! Debes devolver '{material.titulo}' antes del {nuevo_prestamo.fecha_vencimiento.strftime('%d-%m-%Y')}."
        return (True, msg)

    def realizar_reserva(
        self, usuario: Usuario, material: MaterialBibliografico
    ) -> (bool, str):
        if isinstance(material, MaterialDigital):
            return (False, "El material digital no se puede reservar.")

        if material.esta_disponible:
            return (
                False,
                "Este material tiene unidades disponibles. No necesitas reservarlo, puedes pedirlo.",
            )

        for p in usuario.prestamos:
            if p.material.id == material.id and isinstance(p.estado, PrestamoActivo):
                return (False, "No puedes reservar un material que ya tienes prestado.")

        if material.esta_reservado_por(usuario):
            return (False, "Ya has reservado este material.")

        material.agregar_reserva(usuario)
        return (
            True,
            f"¡Reserva exitosa! Se te notificará cuando '{material.titulo}' esté disponible.",
        )
