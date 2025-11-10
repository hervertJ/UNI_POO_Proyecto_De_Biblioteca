from abc import ABC, abstractmethod
from datetime import date, timedelta
from typing import List


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


class MaterialBibliografico(ABC):
    def __init__(self, id: int, titulo: str, autor: str):
        self._id = id
        self._titulo = titulo
        self._autor = autor

    @abstractmethod
    def calcular_dias_prestamo(self) -> int:
        pass

    @abstractmethod
    def es_renovable(self) -> bool:
        pass

    @property
    def id(self):
        return self._id

    @property
    def titulo(self):
        return self._titulo


class EstadoPrestamo(ABC):
    def __init__(self, prestamo: "Prestamo"):
        self._prestamo = prestamo

    @abstractmethod
    def procesar_prestamo(self):
        pass

    @abstractmethod
    def calcular_multa(self) -> float:
        pass


# === JERARQUÍA DE USUARIOS ===
class Usuario(Persona):
    def __init__(self, id: int, nombre: str, correo: str, rol: str):
        super().__init__(id, nombre, correo)
        self._rol = rol
        self._prestamos: List[Prestamo] = []

    def validar_datos(self) -> bool:
        return (
            self._id > 0
            and len(self._nombre) > 0
            and "@" in self._correo
            and len(self._rol) > 0
        )

    def registrar(self):
        if self.validar_datos():
            print(f"Usuario {self._nombre} registrado exitosamente")
            return True
        return False

    def agregar_prestamo(self, prestamo: "Prestamo"):
        self._prestamos.append(prestamo)


class Estudiante(Usuario):
    def __init__(self, id: int, nombre: str, correo: str, carrera: str, semestre: int):
        super().__init__(id, nombre, correo, "Estudiante")
        self._carrera = carrera
        self._semestre = semestre

    def validar_datos(self) -> bool:
        return (
            super().validar_datos()
            and len(self._carrera) > 0
            and 1 <= self._semestre <= 12
        )

    def consultar_prestamos_activos(self):
        return [p for p in self._prestamos if isinstance(p.estado, PrestamoActivo)]


class Profesor(Usuario):
    def __init__(
        self, id: int, nombre: str, correo: str, departamento: str, tipo_contrato: str
    ):
        super().__init__(id, nombre, correo, "Profesor")
        self._departamento = departamento
        self._tipo_contrato = tipo_contrato

    def validar_datos(self) -> bool:
        return (
            super().validar_datos()
            and len(self._departamento) > 0
            and len(self._tipo_contrato) > 0
        )

    def solicitar_material_especial(self, material: str):
        print(f"Profesor {self._nombre} solicita material especial: {material}")


class Administrativo(Usuario):
    def __init__(self, id: int, nombre: str, correo: str, area_trabajo: str):
        super().__init__(id, nombre, correo, "Administrativo")
        self._area_trabajo = area_trabajo

    def validar_datos(self) -> bool:
        return super().validar_datos() and len(self._area_trabajo) > 0

    def generar_reportes(self):
        print(f"Reporte generado por administrativo {self._nombre}")


# === JERARQUÍA DE MATERIALES BIBLIOGRÁFICOS ===
class Libro(MaterialBibliografico):
    def __init__(
        self, id: int, titulo: str, autor: str, editorial: str, categoria: str
    ):
        super().__init__(id, titulo, autor)
        self._editorial = editorial
        self._categoria = categoria

    def calcular_dias_prestamo(self) -> int:
        return 15  # Libros: 15 días

    def es_renovable(self) -> bool:
        return True  # Los libros son renovables


class Revista(MaterialBibliografico):
    def __init__(
        self,
        id: int,
        titulo: str,
        autor: str,
        numero_edicion: int,
        fecha_publicacion: date,
    ):
        super().__init__(id, titulo, autor)
        self._numero_edicion = numero_edicion
        self._fecha_publicacion = fecha_publicacion

    def calcular_dias_prestamo(self) -> int:
        return 7  # Revistas: 7 días

    def es_renovable(self) -> bool:
        return False  # Las revistas no son renovables


class Tesis(MaterialBibliografico):
    def __init__(
        self, id: int, titulo: str, autor: str, universidad: str, año_defensa: int
    ):
        super().__init__(id, titulo, autor)
        self._universidad = universidad
        self._año_defensa = año_defensa

    def calcular_dias_prestamo(self) -> int:
        return 10  # Tesis: 10 días

    def es_renovable(self) -> bool:
        return True  # Las tesis son renovables


# === ESTADOS DE PRÉSTAMO ===
class Prestamo:
    def __init__(self, usuario: Usuario, material: MaterialBibliografico):
        self._usuario = usuario
        self._material = material
        self._fecha_prestamo = date.today()
        self._estado: EstadoPrestamo = PrestamoActivo(self)
        self._multa: Multa = None

    def cambiar_estado(self, nuevo_estado: EstadoPrestamo):
        self._estado = nuevo_estado

    def procesar_prestamo(self):
        self._estado.procesar_prestamo()

    def calcular_multa(self) -> float:
        return self._estado.calcular_multa()

    @property
    def estado(self):
        return self._estado

    @property
    def usuario(self):
        return self._usuario

    @property
    def material(self):
        return self._material


class PrestamoActivo(EstadoPrestamo):
    def procesar_prestamo(self):
        print("Préstamo activo - En curso")

    def calcular_multa(self) -> float:
        return 0.0  # No hay multa si está activo

    def renovar(self):
        print("Préstamo renovado")


class PrestamoVencido(EstadoPrestamo):
    def __init__(self, prestamo: Prestamo, dias_retraso: int):
        super().__init__(prestamo)
        self._dias_retraso = dias_retraso

    def procesar_prestamo(self):
        print(f"Préstamo vencido - {self._dias_retraso} días de retraso")

    def calcular_multa(self) -> float:
        return self._dias_retraso * 5.0  # $5 por día

    def generar_notificacion(self):
        print(f"Notificación enviada por préstamo vencido")


class PrestamoDevuelto(EstadoPrestamo):
    def procesar_prestamo(self):
        print("Préstamo devuelto - Procesado")

    def calcular_multa(self) -> float:
        return 0.0  # Ya devuelto, no hay multa

    def archivar(self):
        print("Préstamo archivado en historial")


# === CLASES ADICIONALES ===
class Multa:
    def __init__(self, dias_retraso: int):
        self._dias_retraso = dias_retraso
        self._monto = self._calcular_monto()

    def _calcular_monto(self) -> float:
        return self._dias_retraso * 5.0

    def generar_multa(self):
        print(
            f"Multa generada: ${self._monto} por {self._dias_retraso} días de retraso"
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


class Catalogo:
    def __init__(self):
        self._materiales: List[MaterialBibliografico] = []

    def agregar_material(self, material: MaterialBibliografico):
        self._materiales.append(material)

    def buscar_por_palabras_clave(self, palabra_clave: str):
        return [
            m for m in self._materiales if palabra_clave.lower() in m.titulo.lower()
        ]

    def filtrar_por_autor(self, autor: str):
        return [
            m
            for m in self._materiales
            if hasattr(m, "_autor") and autor.lower() in m._autor.lower()
        ]


class Biblioteca:
    def __init__(self):
        self._usuarios: List[Usuario] = []
        self._materiales: List[MaterialBibliografico] = []
        self._prestamos: List[Prestamo] = []
        self._multas: List[Multa] = []
        self._catalogo = Catalogo()

    def gestionar_usuarios(self):
        print("Gestión de usuarios")

    def gestionar_materiales(self):
        print("Gestión de materiales")

    def gestionar_prestamos(self):
        print("Gestión de préstamos")

    def agregar_usuario(self, usuario: Usuario):
        if usuario.registrar():
            self._usuarios.append(usuario)

    def agregar_material(self, material: MaterialBibliografico):
        self._materiales.append(material)
        self._catalogo.agregar_material(material)


# === DEMOSTRACIÓN DEL USO ===
if __name__ == "__main__":
    biblioteca = Biblioteca()

    estudiante = Estudiante(1, "Ana García", "ana@universidad.edu", "Ingeniería", 5)
    profesor = Profesor(
        2, "Dr. Pérez", "perez@universidad.edu", "Matemáticas", "Tiempo Completo"
    )

    libro = Libro(
        101,
        "Python para Principiantes",
        "Autor Python",
        "Editorial Tech",
        "Programación",
    )
    revista = Revista(
        102, "Revista Científica", "Varios Autores", 15, date(2024, 1, 15)
    )

    biblioteca.agregar_usuario(estudiante)
    biblioteca.agregar_usuario(profesor)
    biblioteca.agregar_material(libro)
    biblioteca.agregar_material(revista)

    print("=== POLIMORFISMO EN USUARIOS ===")
    usuarios = [estudiante, profesor]
    for usuario in usuarios:
        print(f"{usuario.nombre}: Validación = {usuario.validar_datos()}")

    print("\n=== POLIMORFISMO EN MATERIALES ===")
    materiales = [libro, revista]
    for material in materiales:
        print(f"{material.titulo}: Días préstamo = {material.calcular_dias_prestamo()}")

    prestamo = Prestamo(estudiante, libro)
    prestamo.procesar_prestamo()

    prestamo_vencido = PrestamoVencido(prestamo, 3)
    prestamo.cambiar_estado(prestamo_vencido)
    prestamo.procesar_prestamo()
    print(f"Multa por retraso: ${prestamo.calcular_multa()}")
