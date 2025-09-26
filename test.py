from abc import ABC, abstractmethod
from datetime import date


# === CLASES ABSTRACTAS BASE ===
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

    @property
    def correo(self):
        return self._correo


class Usuario(Persona):
    def __init__(self, id: int, nombre: str, correo: str, rol: str):
        super().__init__(id, nombre, correo)
        self._rol = rol

    @abstractmethod
    def validar_datos(self) -> bool:
        pass

    @property
    def rol(self):
        return self._rol

    def registrar(self):
        pass


# === HERENCIA DE USUARIO ===
class Profesor(Usuario):
    def __init__(self, id, nombre, correo, rol, departamento, tipo_contrato):
        super().__init__(id, nombre, correo, rol)
        self.departamento = departamento
        self.tipo_contrato = tipo_contrato

    def validar_datos(self):
        return all(
            [
                self.id,
                self.nombre,
                self.correo,
                self.departamento,
                self.tipo_contrato,
                self.rol,
            ]
        )

    def solicitar_material_especial(self):
        pass


class Administrativo(Usuario):
    def __init__(self, id, nombre, correo, rol, area_trabajo):
        super().__init__(id, nombre, correo, rol)
        self.area_trabajo = area_trabajo

    def validar_datos(self):
        return all([self.id, self.nombre, self.correo, self.area_trabajo, self.rol])

    def generar_reportes(self):
        pass


class Deudor(Usuario):
    def __init__(self, id, nombre, correo, rol):
        super().__init__(id, nombre, correo, rol)

    def validar_datos(self):
        return all([self.id, self.nombre, self.correo, self.rol])

    def consultar_historial(self):
        pass

    def generar_alerta(self):
        pass


class Estudiante(Usuario):
    def __init__(self, id, nombre, correo, rol, carrera, semestre):
        super().__init__(id, nombre, correo, rol)
        self.carrera = carrera
        self.semestre = semestre

    def validar_datos(self):
        return all(
            [self.id, self.nombre, self.correo, self.carrera, self.semestre, self.rol]
        )

    def consultar_prestamos_activos(self):
        pass


# === CLASES DE MULTA Y PRESTAMO ===
class Multa:
    def __init__(self, dias_retraso: int, monto: float):
        self.dias_retraso = dias_retraso
        self.monto = monto

    def calcular_dias_retraso(self):
        pass

    def generar_multa(self):
        pass


class EstadoPrestamo(ABC):
    @abstractmethod
    def procesar_prestamo(self):
        pass

    @abstractmethod
    def calcular_multa(self) -> float:
        pass


class PrestamoActivo(EstadoPrestamo):
    def procesar_prestamo(self):
        pass

    def calcular_multa(self):
        pass

    def renovar(self):
        pass


class PrestamoVencido(EstadoPrestamo):
    def __init__(self, dias_retraso: int):
        self.dias_retraso = dias_retraso

    def procesar_prestamo(self):
        pass

    def calcular_multa(self):
        pass

    def generar_notificacion(self):
        pass


class PrestamoDevuelto(EstadoPrestamo):
    def procesar_prestamo(self):
        pass

    def calcular_multa(self):
        pass

    def archivar(self):
        pass


# === MATERIAL BIBLIOGRÁFICO Y DERIVADOS ===
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

    @property
    def autor(self):
        return self._autor


class Libro(MaterialBibliografico):
    def __init__(self, id, titulo, autor, editorial, categoria):
        super().__init__(id, titulo, autor)
        self.editorial = editorial
        self.categoria = categoria

    def calcular_dias_prestamo(self):
        pass

    def es_renovable(self):
        pass


class Revista(MaterialBibliografico):
    def __init__(self, id, titulo, autor, numero_edicion, fecha_publicacion):
        super().__init__(id, titulo, autor)
        self.numero_edicion = numero_edicion
        self.fecha_publicacion = fecha_publicacion

    def calcular_dias_prestamo(self):
        pass

    def es_renovable(self):
        pass


class Tesis(MaterialBibliografico):
    def __init__(self, id, titulo, autor, universidad, anio_defensa):
        super().__init__(id, titulo, autor)
        self.universidad = universidad
        self.anio_defensa = anio_defensa

    def calcular_dias_prestamo(self):
        pass

    def es_renovable(self):
        pass


# === CATÁLOGO Y BIBLIOTECA ===
class Catalogo:
    def buscar_por_palabras_clave(self):
        pass

    def filtrar_por_categoria(self):
        pass

    def filtrar_por_autor(self):
        pass

    def filtrar_por_anio(self):
        pass


class Biblioteca:
    def gestionar_usuarios(self):
        pass

    def gestionar_materiales(self):
        pass

    def gestionar_prestamos(self):
        pass
