from flask import Flask, render_template, request, session, redirect, url_for, flash
from datetime import date, timedelta
from models import (
    Biblioteca,
    Estudiante,
    Profesor,
    Administrativo,
    Libro,
    Revista,
    Tesis,
    MaterialDigital,
    Prestamo,
    PrestamoActivo,
    PrestamoVencido,
    PrestamoDevuelto,
)
import random

# --- IMPORTACIONES PARA RECOMENDACIONES (ML / NLP) ---
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- IMPORTACIONES PARA GRÁFICOS ---
import io
import base64
from collections import Counter  # Para contar fácilmente
import matplotlib

matplotlib.use("Agg")  # Modo "Agg" para que Matplotlib funcione en un servidor sin GUI
import matplotlib.pyplot as plt

# --- Configuración global de Matplotlib para el tema oscuro ---
plt.rcParams.update(
    {
        "text.color": "#f0f0f0",
        "axes.labelcolor": "#f0f0f0",
        "xtick.color": "#f0f0f0",
        "ytick.color": "#f0f0f0",
        "axes.edgecolor": "#555",
        "figure.facecolor": "none",
        "axes.facecolor": "none",
        "savefig.facecolor": "none",
        "legend.labelcolor": "#f0f0f0",
    }
)

app = Flask(__name__)
app.secret_key = "mi_llave_secreta_super_dificil_12345"

# --------------------------------------------------------
# --- INICIO: LÓGICA DE SIMULACIÓN DE TIEMPO ---
# --------------------------------------------------------


def get_fecha_actual():
    """
    Obtiene la fecha "actual" de la aplicación.
    Si hay un desfase en la sesión, lo aplica a la fecha real.
    """
    offset_dias = session.get("time_offset", 0)
    return date.today() + timedelta(days=offset_dias)


# --------------------------------------------------------
# --- FIN: LÓGICA DE SIMULACIÓN DE TIEMPO ---
# --------------------------------------------------------


# --- Creación de la biblioteca y datos de ejemplo ---
biblioteca = Biblioteca()
estudiante = Estudiante(1, "Ana García", "ana@uni.edu", "Ingeniería", 5)
profesor = Profesor(2, "Dr. Pérez", "perez@uni.edu", "Matemáticas", "Tiempo Completo")
admin = Administrativo(3, "Admin Root", "admin@uni.edu", "Sistemas")

# Libros
libro_python = Libro(
    id=101,
    titulo="Python para Principiantes",
    autor="Autor Python",
    año_publicacion=2022,
    descripcion="Un libro ideal para comenzar a programar en Python. Cubre variables, bucles y funciones.",
    portada_url="https://placehold.co/300x400/5a0000/ffffff?text=Python",
    editorial="Editorial Tech",
    categoria="Programación",
    total_unidades=5,
    isbn="978-3-16-148410-0",
)
libro_calculo = Libro(
    id=103,
    titulo="Cálculo Avanzado",
    autor="Autor Cálculo",
    año_publicacion=2021,
    descripcion="Cubre temas de cálculo multivariable.",
    portada_url="https://placehold.co/300x400/5a0000/ffffff?text=Calculo",
    editorial="Editorial Math",
    categoria="Ciencia",
    total_unidades=3,
    isbn="978-1-23-456789-7",
)
# Revista
revista_ciencia = Revista(
    id=102,
    titulo="Revista Científica",
    autor="Varios Autores",
    año_publicacion=2024,
    descripcion="Publicación mensual con los últimos descubrimientos en ciencia y tecnología.",
    portada_url="https://placehold.co/300x400/5a0000/ffffff?text=Ciencia",
    numero_edicion=15,
    total_unidades=10,
    issn="1234-5678",
)
# Tesis
tesis_ia = Tesis(
    id=104,
    titulo="IA en Medicina",
    autor="Estudiante Investigador",
    año_defensa=2023,
    descripcion="Tesis sobre machine learning en diagnóstico. Aplicación de IA.",
    portada_url="https://placehold.co/300x400/5a0000/ffffff?text=Tesis+IA",
    universidad="Universidad Ficticia",
    total_unidades=1,
)
# Material Digital
ebook_ia = MaterialDigital(
    id=201,
    titulo="Ebook: Fundamentos de IA",
    autor="Autor Digital",
    año_publicacion=2023,
    descripcion="Un ebook introductorio a la Inteligencia Artificial (IA). Siempre disponible. Python y ML.",
    portada_url="https://placehold.co/300x400/2d2d2d/ffffff?text=Ebook+IA",
    formato="PDF",
)

biblioteca.agregar_usuario(estudiante)
biblioteca.agregar_usuario(profesor)
biblioteca.agregar_usuario(admin)
biblioteca.agregar_material(libro_python)
biblioteca.agregar_material(revista_ciencia)
biblioteca.agregar_material(libro_calculo)
biblioteca.agregar_material(tesis_ia)
biblioteca.agregar_material(ebook_ia)

# --- Préstamos de ejemplo ---
# MODIFICADO: Ahora pasamos la fecha de inicio al crear el préstamo
fecha_base_ejemplos = date.today()  # Usamos la fecha real como base para los ejemplos
prestamo_activo = Prestamo(
    estudiante, libro_python, fecha_base_ejemplos - timedelta(days=5)
)
estudiante.agregar_prestamo(prestamo_activo)

prestamo_vencido = Prestamo(
    estudiante, libro_calculo, fecha_base_ejemplos - timedelta(days=20)
)
estudiante.agregar_prestamo(prestamo_vencido)

prestamo_profesor = Prestamo(
    profesor, tesis_ia, fecha_base_ejemplos - timedelta(days=10)
)
profesor.agregar_prestamo(prestamo_profesor)

# --------------------------------------------------------
# --- INICIO: SISTEMA DE RECOMENDACIÓN (ML / NLP) ---
# --------------------------------------------------------
todos_los_materiales = biblioteca.catalogo.buscar()


def crear_documento_material(m):
    texto = f"{m.titulo} {m.autor} {m.descripcion} "
    if hasattr(m, "categoria"):
        texto += m.categoria
    if hasattr(m, "editorial"):
        texto += m.editorial
    if hasattr(m, "universidad"):
        texto += m.universidad
    return texto.lower()


documentos = [crear_documento_material(m) for m in todos_los_materiales]
tfidf_vectorizer = TfidfVectorizer(stop_words="english", max_features=500)
tfidf_matrix = tfidf_vectorizer.fit_transform(documentos)
cosine_sim_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
id_a_indice = {material.id: i for i, material in enumerate(todos_los_materiales)}
# --------------------------------------------------------
# --- FIN: SISTEMA DE RECOMENDACIÓN ---
# --------------------------------------------------------


@app.route("/login", methods=["GET", "POST"])
def login():
    if "usuario" in session:
        return redirect(url_for("home"))
    if request.method == "POST":
        correo = request.form["correo"]
        password = request.form["password"]

        usuario_valido = next(
            (
                u
                for u in biblioteca.usuarios
                if u.correo == correo and password == "123"
            ),
            None,
        )

        if usuario_valido:
            session["usuario_id"] = usuario_valido.id
            session["nombre"] = usuario_valido.nombre
            session["rol"] = usuario_valido.rol
            session["time_offset"] = 0  # Reiniciar el tiempo en login
            return redirect(url_for("home"))
        else:
            flash("Correo o contraseña incorrectos.")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


def _obtener_datos_prestamos(usuario_id):
    usuario_actual = biblioteca.buscar_usuario_por_id(usuario_id)
    if not usuario_actual:
        return [], 0.0

    info_prestamos = []
    total_multa = 0.0

    # MODIFICADO: Usamos la fecha simulada
    today = get_fecha_actual()

    for p in usuario_actual.prestamos:
        if isinstance(p.estado, PrestamoActivo) and today > p.fecha_vencimiento:
            dias_retraso = (today - p.fecha_vencimiento).days
            nuevo_estado = PrestamoVencido(p, dias_retraso)
            p.cambiar_estado(nuevo_estado)

        # MODIFICADO: Pasamos la fecha simulada al cálculo de multa
        multa_individual = p.calcular_multa(today)
        total_multa += multa_individual

        info = {
            "id": p.id,
            "titulo": p.material.titulo,
            "fecha_prestamo": p.fecha_prestamo,
            "fecha_vencimiento": p.fecha_vencimiento,
            "multa": multa_individual,
            "estado_obj": p.estado,
            "es_activo": isinstance(p.estado, PrestamoActivo),
            "es_renovable": p.material.es_renovable(),
        }
        info_prestamos.append(info)

    return info_prestamos, total_multa


@app.route("/")
def home():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    info_prestamos, total_multa = _obtener_datos_prestamos(session["usuario_id"])
    materiales_disponibles = biblioteca.catalogo.buscar()

    # MODIFICADO: Datos de fecha para la plantilla
    fecha_actual_simulada = get_fecha_actual()
    offset_dias = session.get("time_offset", 0)

    return render_template(
        "index.html",
        materiales=materiales_disponibles,
        info_prestamos=info_prestamos,
        total_multa=total_multa,
        rol=session.get("rol"),
        current_year=fecha_actual_simulada.year,  # Año basado en fecha simulada
        palabra="",
        autor="",
        # Pasamos los datos de simulación de tiempo
        offset_dias=offset_dias,
        fecha_actual_str=fecha_actual_simulada.strftime("%d-%m-%Y"),
    )


@app.route("/buscar", methods=["POST"])
def buscar():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    palabra = request.form.get("palabra", "")
    autor = request.form.get("autor", "")
    resultados = biblioteca.catalogo.buscar(titulo=palabra, autor=autor)

    info_prestamos, total_multa = _obtener_datos_prestamos(session["usuario_id"])

    # MODIFICADO: Datos de fecha para la plantilla
    fecha_actual_simulada = get_fecha_actual()
    offset_dias = session.get("time_offset", 0)

    return render_template(
        "index.html",
        materiales=resultados,
        palabra=palabra,
        autor=autor,
        info_prestamos=info_prestamos,
        total_multa=total_multa,
        rol=session.get("rol"),
        current_year=fecha_actual_simulada.year,
        # Pasamos los datos de simulación de tiempo
        offset_dias=offset_dias,
        fecha_actual_str=fecha_actual_simulada.strftime("%d-%m-%Y"),
    )


@app.route("/perfil")
def perfil():
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    usuario = biblioteca.buscar_usuario_por_id(session["usuario_id"])
    if not usuario:
        flash("Error al cargar el perfil.")
        return redirect(url_for("home"))
    return render_template("perfil.html", usuario=usuario)


@app.route("/material/<int:material_id>")
def detalle_material(material_id):
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    material = biblioteca.buscar_material_por_id(material_id)
    usuario = biblioteca.buscar_usuario_por_id(session["usuario_id"])

    if not material or not usuario:
        flash("El material o usuario no existe.")
        return redirect(url_for("home"))

    (puede_prestar, razon_no_prestamo) = biblioteca.verificar_aptitud_prestamo(
        usuario, material
    )

    mostrar_reserva = False
    if not puede_prestar and "no hay unidades disponibles" in razon_no_prestamo.lower():
        mostrar_reserva = True

    # --- LÓGICA DE RECOMENDACIÓN (ML) ---
    recomendaciones = []
    if material_id in id_a_indice:
        idx_origen = id_a_indice[material_id]
        sim_scores = list(enumerate(cosine_sim_matrix[idx_origen]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        indices_recomendados = [i[0] for i in sim_scores[1:4]]
        recomendaciones = [todos_los_materiales[i] for i in indices_recomendados]
    # --- FIN LÓGICA RECOMENDACIÓN ---

    return render_template(
        "material_detalle.html",
        material=material,
        puede_prestar=puede_prestar,
        razon=razon_no_prestamo,
        mostrar_reserva=mostrar_reserva,
        recomendaciones=recomendaciones,
    )


@app.route("/prestar/<int:material_id>", methods=["POST"])
def prestar_material(material_id):
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    usuario = biblioteca.buscar_usuario_por_id(session["usuario_id"])
    material = biblioteca.buscar_material_por_id(material_id)

    if not usuario or not material:
        flash("Error: Usuario o material no encontrado.")
        return redirect(url_for("home"))

    # MODIFICADO: Pasamos la fecha simulada al realizar el préstamo
    (exito, mensaje) = biblioteca.realizar_prestamo(
        usuario, material, get_fecha_actual()
    )

    if exito:
        flash(mensaje, "success")
        return redirect(url_for("home"))
    else:
        flash(mensaje)
        return redirect(url_for("detalle_material", material_id=material_id))


@app.route("/reservar/<int:material_id>", methods=["POST"])
def reservar_material(material_id):
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    usuario = biblioteca.buscar_usuario_por_id(session["usuario_id"])
    material = biblioteca.buscar_material_por_id(material_id)
    if not usuario or not material:
        flash("Error: Usuario o material no encontrado.")
        return redirect(url_for("home"))
    (exito, mensaje) = biblioteca.realizar_reserva(usuario, material)
    if exito:
        flash(mensaje, "success")
        return redirect(url_for("home"))
    else:
        flash(mensaje)
        return redirect(url_for("detalle_material", material_id=material_id))


@app.route("/renovar/<int:prestamo_id>", methods=["POST"])
def renovar_prestamo(prestamo_id):
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    usuario = biblioteca.buscar_usuario_por_id(session["usuario_id"])
    if not usuario:
        flash("Error: Usuario no encontrado.")
        return redirect(url_for("home"))
    prestamo_a_renovar = next(
        (p for p in usuario.prestamos if p.id == prestamo_id), None
    )
    if not prestamo_a_renovar:
        flash("Error: Préstamo no encontrado.")
        return redirect(url_for("home"))
    (exito, mensaje) = prestamo_a_renovar.realizar_renovacion()
    if exito:
        flash(mensaje, "success")
    else:
        flash(mensaje)
    return redirect(url_for("home"))


@app.route("/pagar-multa", methods=["POST"])
def pagar_multa():
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    usuario = biblioteca.buscar_usuario_por_id(session["usuario_id"])
    metodo_pago = request.form.get("metodo_pago", "BCP")
    notificaciones_reserva = []
    for p in list(usuario.prestamos):
        if isinstance(p.estado, PrestamoVencido):
            nuevo_estado = PrestamoDevuelto(p)
            p.cambiar_estado(nuevo_estado)
            if nuevo_estado.notificacion:
                notificaciones_reserva.append(nuevo_estado.notificacion)
    flash(f"¡Pago simulado con {metodo_pago} exitoso! Multas saldadas.", "success")
    for notif in notificaciones_reserva:
        flash(notif, "info")
    return redirect(url_for("home"))


# --- RUTAS DE ADMINISTRADOR ---


# ... (El código de /admin/dashboard y _generar_y_codificar_grafico sigue igual) ...
def _generar_y_codificar_grafico(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    data = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{data}"


@app.route("/admin/dashboard")
def admin_dashboard():
    if session.get("rol") != "Administrativo":
        flash("Acción no autorizada.")
        return redirect(url_for("home"))
    todos_los_prestamos = []
    for u in biblioteca.usuarios:
        todos_los_prestamos.extend(u.prestamos)
    if not todos_los_prestamos:
        flash("No hay datos de préstamos para generar analíticas.")
        return redirect(url_for("home"))
    conteo_tipos = Counter()
    for p in todos_los_prestamos:
        if isinstance(p.material, MaterialDigital):
            continue
        conteo_tipos[p.material.__class__.__name__] += 1
    labels_bar = list(conteo_tipos.keys())
    values_bar = list(conteo_tipos.values())
    fig_bar, ax_bar = plt.subplots(figsize=(7, 4))
    ax_bar.bar(labels_bar, values_bar, color=["#8B0000", "#A52A2A", "#5a0000"])
    ax_bar.set_ylabel("Cantidad de Préstamos")
    ax_bar.set_title("Popularidad por Tipo de Material")
    plt.tight_layout()
    plot_url_barras = _generar_y_codificar_grafico(fig_bar)
    prestamos_actuales = [
        p for p in todos_los_prestamos if not isinstance(p.estado, PrestamoDevuelto)
    ]
    conteo_estados = Counter()
    for p in prestamos_actuales:
        if isinstance(p.estado, PrestamoVencido):
            conteo_estados["Vencidos"] += 1
        else:
            conteo_estados["Activos"] += 1
    labels_pie = list(conteo_estados.keys())
    values_pie = list(conteo_estados.values())
    fig_pie, ax_pie = plt.subplots(figsize=(5, 4))
    if values_pie:
        ax_pie.pie(
            values_pie,
            labels=labels_pie,
            autopct="%1.1f%%",
            colors=["#27ae60", "#e74c3c"],
            startangle=90,
            wedgeprops={"edgecolor": "#f0f0f0", "linewidth": 1},
        )
    ax_pie.set_title("Estado Actual de Préstamos")
    plt.tight_layout()
    plot_url_pie = _generar_y_codificar_grafico(fig_pie)
    return render_template(
        "admin_dashboard.html",
        plot_url_barras=plot_url_barras,
        plot_url_pie=plot_url_pie,
    )


@app.route("/admin/agregar", methods=["POST"])
def admin_agregar_material():
    if session.get("rol") != "Administrativo":
        flash("Acción no autorizada.")
        return redirect(url_for("home"))

    titulo = request.form.get("titulo")
    autor = request.form.get("autor")
    # MODIFICADO: Usamos el año simulado
    año = int(request.form.get("año") or get_fecha_actual().year)
    tipo_material = request.form.get("tipo_material")
    total_unidades = int(request.form.get("unidades") or 1)

    nuevo_id = random.randint(200, 999)
    desc = f"Nuevo material ({tipo_material}) añadido por el administrador."
    portada = (
        f"https://placehold.co/300x400/5a0000/ffffff?text={titulo.replace(' ', '+')}"
    )

    nuevo_material = None
    if tipo_material == "libro":
        nuevo_material = Libro(
            id=nuevo_id,
            titulo=titulo,
            autor=autor,
            año_publicacion=año,
            descripcion=desc,
            portada_url=portada,
            editorial="Editorial Genérica",
            categoria="General",
            total_unidades=total_unidades,
        )
    elif tipo_material == "revista":
        nuevo_material = Revista(
            id=nuevo_id,
            titulo=titulo,
            autor=autor,
            año_publicacion=año,
            descripcion=desc,
            portada_url=portada,
            numero_edicion=1,
            total_unidades=total_unidades,
        )
    elif tipo_material == "tesis":
        nuevo_material = Tesis(
            id=nuevo_id,
            titulo=titulo,
            autor=autor,
            año_defensa=año,
            descripcion=desc,
            portada_url=portada,
            universidad="Universidad",
            total_unidades=total_unidades,
        )

    if nuevo_material:
        biblioteca.agregar_material(nuevo_material)
        flash(f"'{titulo}' (x{total_unidades}) ha sido añadido al catálogo.", "success")

        # --- IMPORTANTE: Re-entrenar el modelo de recomendación ---
        global todos_los_materiales, tfidf_matrix, cosine_sim_matrix, id_a_indice

        todos_los_materiales = biblioteca.catalogo.buscar()
        documentos = [crear_documento_material(m) for m in todos_los_materiales]
        tfidf_matrix = tfidf_vectorizer.fit_transform(documentos)
        cosine_sim_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
        id_a_indice = {
            material.id: i for i, material in enumerate(todos_los_materiales)
        }
        # --- FIN RE-ENTRENAMIENTO ---

    else:
        flash("Error al crear el material.")

    return redirect(url_for("home"))


@app.route("/admin/retirar/<int:material_id>", methods=["POST"])
def admin_retirar_material(material_id):
    if session.get("rol") != "Administrativo":
        flash("Acción no autorizada.")
        return redirect(url_for("home"))
    (exito, mensaje) = biblioteca.retirar_material(material_id)
    if exito:
        flash(mensaje, "success")
    else:
        flash(mensaje)
    return redirect(url_for("home"))


# --- NUEVAS RUTAS: Control de Simulación de Tiempo ---
@app.route("/debug/avanzar-tiempo", methods=["POST"])
def avanzar_tiempo():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    dias = int(request.form.get("dias", 7))
    offset_actual = session.get("time_offset", 0)
    nuevo_offset = offset_actual + dias
    session["time_offset"] = nuevo_offset

    flash(
        f"Has viajado {dias} días al futuro. Desfase total: {nuevo_offset} días.",
        "info",
    )
    # request.referrer nos devuelve a la página anterior (sea 'home' o 'buscar')
    return redirect(request.referrer or url_for("home"))


@app.route("/debug/reset-tiempo", methods=["POST"])
def reset_tiempo():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    session["time_offset"] = 0
    flash("Has vuelto a la fecha actual del sistema.", "success")
    return redirect(request.referrer or url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
