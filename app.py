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
    Resena,
)
import random

# --- IMPORTACIONES PARA RECOMENDACIONES (ML / NLP) ---
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- IMPORTACIONES PARA GRÁFICOS ---
import io
import base64
from collections import Counter
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

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
    offset_dias = session.get("time_offset", 0)
    return date.today() + timedelta(days=offset_dias)


# --- CREACIÓN DE DATOS ---
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
    descripcion="Un libro ideal para comenzar a programar en Python.",
    portada_url="https://placehold.co/300x400/5a0000/ffffff?text=Python",
    editorial="Editorial Tech",
    materia="Programación",
    total_unidades=10,
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
    materia="Matemáticas",
    total_unidades=3,
    isbn="978-1-23-456789-7",
)
# Revista
revista_ciencia = Revista(
    id=102,
    titulo="Revista Científica",
    autor="Varios Autores",
    año_publicacion=2024,
    descripcion="Publicación mensual con los últimos descubrimientos.",
    portada_url="https://placehold.co/300x400/5a0000/ffffff?text=Ciencia",
    numero_edicion=15,
    materia="Ciencias",
    total_unidades=10,
    issn="1234-5678",
)
# Tesis
tesis_ia = Tesis(
    id=104,
    titulo="IA en Medicina",
    autor="Estudiante Investigador",
    año_defensa=2023,
    descripcion="Tesis sobre machine learning en diagnóstico.",
    portada_url="https://placehold.co/300x400/5a0000/ffffff?text=Tesis+IA",
    universidad="Universidad Ficticia",
    materia="Medicina",
    total_unidades=1,
)
# Material Digital
ebook_ia = MaterialDigital(
    id=201,
    titulo="Ebook: Fundamentos de IA",
    autor="Autor Digital",
    año_publicacion=2023,
    descripcion="Un ebook introductorio a la Inteligencia Artificial.",
    portada_url="https://placehold.co/300x400/2d2d2d/ffffff?text=Ebook+IA",
    formato="PDF",
    materia="Programación",
)

# Reseñas Dummy
resena1 = Resena(profesor, 5, "Excelente libro introductorio.", date.today())
libro_python.agregar_resena(resena1)
resena2 = Resena(estudiante, 4, "Muy bueno.", date.today())
libro_python.agregar_resena(resena2)
resena3 = Resena(estudiante, 5, "Imprescindible.", date.today())
revista_ciencia.agregar_resena(resena3)

biblioteca.agregar_usuario(estudiante)
biblioteca.agregar_usuario(profesor)
biblioteca.agregar_usuario(admin)
biblioteca.agregar_material(libro_python)
biblioteca.agregar_material(revista_ciencia)
biblioteca.agregar_material(libro_calculo)
biblioteca.agregar_material(tesis_ia)
biblioteca.agregar_material(ebook_ia)

# Préstamos Dummy para generar popularidad
prestamo_activo = Prestamo(estudiante, libro_python, date.today() - timedelta(days=5))
estudiante.agregar_prestamo(prestamo_activo)
prestamo_vencido = Prestamo(
    estudiante, libro_calculo, date.today() - timedelta(days=20)
)
estudiante.agregar_prestamo(prestamo_vencido)
prestamo_profesor = Prestamo(profesor, tesis_ia, date.today() - timedelta(days=10))
profesor.agregar_prestamo(prestamo_profesor)

# === CORRECCIÓN AQUÍ ===
# Antes añadíamos el ESTADO a la lista de préstamos, lo cual rompía el código.
# Ahora creamos el PRÉSTAMO, cambiamos su estado, y añadimos el PRÉSTAMO.

# Préstamo Histórico 1
p_hist1 = Prestamo(estudiante, libro_python, date.today() - timedelta(days=50))
p_hist1.cambiar_estado(PrestamoDevuelto(p_hist1))  # Cambiamos estado
estudiante.agregar_prestamo(p_hist1)  # Agregamos el OBJETO PRÉSTAMO

# Préstamo Histórico 2
p_hist2 = Prestamo(profesor, libro_python, date.today() - timedelta(days=60))
p_hist2.cambiar_estado(PrestamoDevuelto(p_hist2))  # Cambiamos estado
profesor.agregar_prestamo(p_hist2)  # Agregamos el OBJETO PRÉSTAMO
# =======================

# ML Setup
todos_los_materiales = biblioteca.catalogo.buscar()


def crear_documento_material(m):
    texto = f"{m.titulo} {m.autor} {m.descripcion} {m.materia} "
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
            session["time_offset"] = 0
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
        return [], 0.0, None
    info_prestamos = []
    total_multa = 0.0
    today = get_fecha_actual()
    for p in usuario_actual.prestamos:
        # Ahora 'p' siempre es un objeto Prestamo válido, no un EstadoPrestamo
        if isinstance(p.estado, PrestamoActivo) and today > p.fecha_vencimiento:
            dias_retraso = (today - p.fecha_vencimiento).days
            nuevo_estado = PrestamoVencido(p, dias_retraso)
            p.cambiar_estado(nuevo_estado)
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
    return info_prestamos, total_multa, usuario_actual


def _generar_y_codificar_grafico(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"


# --- RUTA PRINCIPAL UNIFICADA (HOME) ---
@app.route("/")
def home():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    info_prestamos, total_multa, usuario_actual = _obtener_datos_prestamos(
        session["usuario_id"]
    )

    tipo_filtro = request.args.get("tipo", "")
    materia_filtro = request.args.get("materia", "")

    materiales_disponibles = biblioteca.catalogo.buscar(
        tipo_material=tipo_filtro, materia=materia_filtro
    )
    materias_unicas = biblioteca.catalogo.obtener_materias_unicas()

    populares = []
    mejor_valorados = []
    if not tipo_filtro and not materia_filtro:
        conteo_prestamos = Counter()
        for u in biblioteca.usuarios:
            for p in u.prestamos:
                conteo_prestamos[p.material.id] += 1
        ids_populares = [id for id, count in conteo_prestamos.most_common(4)]
        populares = [
            biblioteca.buscar_material_por_id(id)
            for id in ids_populares
            if biblioteca.buscar_material_por_id(id)
        ]
        con_resenas = [m for m in materiales_disponibles if m.resenas]
        mejor_valorados = sorted(
            con_resenas, key=lambda m: m.promedio_calificacion, reverse=True
        )[:4]

    admin_data = {}
    if session.get("rol") == "Administrativo":
        today = get_fecha_actual()
        todos_los_prestamos = []
        for u in biblioteca.usuarios:
            todos_los_prestamos.extend(u.prestamos)

        plot_url_barras = ""
        plot_url_pie = ""
        if todos_los_prestamos:
            conteo_tipos = Counter()
            for p in todos_los_prestamos:
                if isinstance(p.material, MaterialDigital):
                    continue
                conteo_tipos[p.material.__class__.__name__] += 1
            fig_bar, ax_bar = plt.subplots(figsize=(7, 4))
            ax_bar.bar(
                list(conteo_tipos.keys()),
                list(conteo_tipos.values()),
                color=["#8B0000", "#A52A2A", "#5a0000"],
            )
            ax_bar.set_ylabel("Préstamos")
            plt.tight_layout()
            plot_url_barras = _generar_y_codificar_grafico(fig_bar)

            prestamos_actuales_list = [
                p
                for p in todos_los_prestamos
                if not isinstance(p.estado, PrestamoDevuelto)
            ]
            conteo_estados = Counter()
            for p in prestamos_actuales_list:
                if isinstance(p.estado, PrestamoVencido) or (
                    isinstance(p.estado, PrestamoActivo) and today > p.fecha_vencimiento
                ):
                    conteo_estados["Vencidos"] += 1
                else:
                    conteo_estados["Activos"] += 1
            fig_pie, ax_pie = plt.subplots(figsize=(5, 4))
            if sum(conteo_estados.values()) > 0:
                ax_pie.pie(
                    list(conteo_estados.values()),
                    labels=list(conteo_estados.keys()),
                    autopct="%1.1f%%",
                    colors=["#e74c3c", "#27ae60"],
                )
            plt.tight_layout()
            plot_url_pie = _generar_y_codificar_grafico(fig_pie)

        global_prestamos_activos = []
        for u in biblioteca.usuarios:
            for p in u.prestamos:
                if not isinstance(p.estado, PrestamoDevuelto):
                    estado_display = "Activo"
                    dias_retraso_calc = 0
                    if today > p.fecha_vencimiento:
                        estado_display = "Vencido"
                        dias_retraso_calc = (today - p.fecha_vencimiento).days

                    global_prestamos_activos.append(
                        {
                            "usuario": u,
                            "material": p.material,
                            "fecha_vencimiento": p.fecha_vencimiento,
                            "estado_str": estado_display,
                            "dias_retraso": dias_retraso_calc,
                            "multa": p.calcular_multa(today),
                        }
                    )

        materiales_con_cola = [
            m for m in biblioteca.catalogo.buscar() if m.tiene_reservas()
        ]

        admin_data = {
            "plot_barras": plot_url_barras,
            "plot_pie": plot_url_pie,
            "global_prestamos": global_prestamos_activos,
            "materiales_con_cola": materiales_con_cola,
        }

    return render_template(
        "index.html",
        materiales=materiales_disponibles,
        info_prestamos=info_prestamos,
        total_multa=total_multa,
        usuario_actual=usuario_actual,
        rol=session.get("rol"),
        current_year=get_fecha_actual().year,
        palabra="",
        autor="",
        materias_disponibles=materias_unicas,
        filtros_activos={"tipo": tipo_filtro, "materia": materia_filtro},
        offset_dias=session.get("time_offset", 0),
        fecha_actual_str=get_fecha_actual().strftime("%d-%m-%Y"),
        admin_data=admin_data,
        populares=populares,
        mejor_valorados=mejor_valorados,
    )


@app.route("/perfil")
def perfil():
    return redirect(url_for("home", view="perfil"))


@app.route("/admin/dashboard")
def admin_dashboard():
    return redirect(url_for("home", view="admin"))


@app.route("/buscar", methods=["POST"])
def buscar():
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    palabra = request.form.get("palabra", "")
    autor = request.form.get("autor", "")
    materia = request.form.get("materia", "")
    tipo = request.form.get("tipo_material", "")

    resultados = biblioteca.catalogo.buscar(
        titulo=palabra, autor=autor, materia=materia, tipo_material=tipo
    )
    info_prestamos, total_multa, usuario_actual = _obtener_datos_prestamos(
        session["usuario_id"]
    )
    materias_unicas = biblioteca.catalogo.obtener_materias_unicas()

    return render_template(
        "index.html",
        materiales=resultados,
        palabra=palabra,
        autor=autor,
        info_prestamos=info_prestamos,
        total_multa=total_multa,
        usuario_actual=usuario_actual,
        rol=session.get("rol"),
        current_year=get_fecha_actual().year,
        materias_disponibles=materias_unicas,
        filtros_activos={"tipo": tipo, "materia": materia},
        offset_dias=session.get("time_offset", 0),
        fecha_actual_str=get_fecha_actual().strftime("%d-%m-%Y"),
    )


@app.route("/material/<int:material_id>")
def detalle_material(material_id):
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    material = biblioteca.buscar_material_por_id(material_id)
    usuario = biblioteca.buscar_usuario_por_id(session["usuario_id"])
    if not material or not usuario:
        return redirect(url_for("home"))
    (puede_prestar, razon_no_prestamo) = biblioteca.verificar_aptitud_prestamo(
        usuario, material
    )
    mostrar_reserva = (
        not puede_prestar and "no hay unidades disponibles" in razon_no_prestamo.lower()
    )
    posicion_cola = 0
    if material.esta_reservado_por(usuario):
        posicion_cola = material.obtener_posicion_reserva(usuario)

    prestamos_activos_material = []
    if session.get("rol") == "Administrativo":
        today = get_fecha_actual()
        for u in biblioteca.usuarios:
            for p in u.prestamos:
                if p.material.id == material.id and not isinstance(
                    p.estado, PrestamoDevuelto
                ):
                    if (
                        isinstance(p.estado, PrestamoActivo)
                        and today > p.fecha_vencimiento
                    ):
                        p.cambiar_estado(
                            PrestamoVencido(p, (today - p.fecha_vencimiento).days)
                        )
                    prestamos_activos_material.append(
                        {
                            "usuario": u,
                            "prestamo": p,
                            "estado": p.estado.__class__.__name__,
                            "deuda": p.calcular_multa(today),
                        }
                    )

    recomendaciones = []
    if material_id in id_a_indice:
        idx_origen = id_a_indice[material_id]
        sim_scores = list(enumerate(cosine_sim_matrix[idx_origen]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        indices_recomendados = [i[0] for i in sim_scores[1:4]]
        recomendaciones = [todos_los_materiales[i] for i in indices_recomendados]

    return render_template(
        "material_detalle.html",
        material=material,
        puede_prestar=puede_prestar,
        razon=razon_no_prestamo,
        mostrar_reserva=mostrar_reserva,
        posicion_cola=posicion_cola,
        prestamos_activos_material=prestamos_activos_material,
        recomendaciones=recomendaciones,
    )


@app.route("/comentar/<int:material_id>", methods=["POST"])
def comentar_material(material_id):
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    usuario = biblioteca.buscar_usuario_por_id(session["usuario_id"])
    material = biblioteca.buscar_material_por_id(material_id)

    if not usuario or not material:
        return redirect(url_for("home"))

    calificacion = request.form.get("calificacion")
    comentario = request.form.get("comentario")

    if calificacion and comentario:
        nueva_resena = Resena(
            usuario, int(calificacion), comentario, get_fecha_actual()
        )
        material.agregar_resena(nueva_resena)
        flash("¡Gracias por tu opinión! Reseña agregada.", "success")
    else:
        flash("Debes asignar estrellas y un comentario.", "error")

    return redirect(url_for("detalle_material", material_id=material_id))


@app.route("/prestar/<int:material_id>", methods=["POST"])
def prestar_material(material_id):
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    usuario = biblioteca.buscar_usuario_por_id(session["usuario_id"])
    material = biblioteca.buscar_material_por_id(material_id)
    if not usuario or not material:
        return redirect(url_for("home"))
    (exito, mensaje) = biblioteca.realizar_prestamo(
        usuario, material, get_fecha_actual()
    )
    flash(mensaje, "success" if exito else "error")
    return redirect(
        url_for("home")
        if exito
        else url_for("detalle_material", material_id=material_id)
    )


@app.route("/reservar/<int:material_id>", methods=["POST"])
def reservar_material(material_id):
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    usuario = biblioteca.buscar_usuario_por_id(session["usuario_id"])
    material = biblioteca.buscar_material_por_id(material_id)
    (exito, mensaje) = biblioteca.realizar_reserva(usuario, material)
    flash(mensaje, "success" if exito else "error")
    return redirect(url_for("detalle_material", material_id=material_id))


@app.route("/renovar/<int:prestamo_id>", methods=["POST"])
def renovar_prestamo(prestamo_id):
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    usuario = biblioteca.buscar_usuario_por_id(session["usuario_id"])
    prestamo_a_renovar = next(
        (p for p in usuario.prestamos if p.id == prestamo_id), None
    )
    if prestamo_a_renovar:
        (exito, mensaje) = prestamo_a_renovar.realizar_renovacion()
        flash(mensaje, "success" if exito else "error")
    return redirect(url_for("home", view="prestamos"))


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
    return redirect(url_for("home", view="prestamos"))


@app.route("/admin/agregar", methods=["POST"])
def admin_agregar_material():
    if session.get("rol") != "Administrativo":
        return redirect(url_for("home"))
    titulo = request.form.get("titulo")
    autor = request.form.get("autor")
    año = int(request.form.get("año") or get_fecha_actual().year)
    tipo_material = request.form.get("tipo_material")
    total_unidades = int(request.form.get("unidades") or 1)
    descripcion = request.form.get("descripcion") or f"Nuevo material ({tipo_material})"
    materia = request.form.get("materia") or "General"
    portada_input = request.form.get("portada_url")
    portada = (
        portada_input.strip()
        if portada_input and portada_input.strip()
        else f"https://placehold.co/300x400/5a0000/ffffff?text={titulo.replace(' ', '+')}"
    )

    nuevo_id = random.randint(200, 9999)
    nuevo_material = None
    if tipo_material == "libro":
        nuevo_material = Libro(
            id=nuevo_id,
            titulo=titulo,
            autor=autor,
            año_publicacion=año,
            descripcion=descripcion,
            portada_url=portada,
            editorial=request.form.get("editorial", "Genérica"),
            materia=materia,
            total_unidades=total_unidades,
            isbn=request.form.get("isbn", "S/N"),
        )
    elif tipo_material == "revista":
        nuevo_material = Revista(
            id=nuevo_id,
            titulo=titulo,
            autor=autor,
            año_publicacion=año,
            descripcion=descripcion,
            portada_url=portada,
            numero_edicion=int(request.form.get("numero_edicion", 1)),
            materia=materia,
            total_unidades=total_unidades,
            issn=request.form.get("issn", "S/N"),
        )
    elif tipo_material == "tesis":
        nuevo_material = Tesis(
            id=nuevo_id,
            titulo=titulo,
            autor=autor,
            año_defensa=año,
            descripcion=descripcion,
            portada_url=portada,
            universidad=request.form.get("universidad", "Uni"),
            materia=materia,
            total_unidades=total_unidades,
        )
    elif tipo_material == "digital":
        nuevo_material = MaterialDigital(
            id=nuevo_id,
            titulo=titulo,
            autor=autor,
            año_publicacion=año,
            descripcion=descripcion,
            portada_url=portada,
            formato=request.form.get("formato", "PDF"),
            materia=materia,
        )

    if nuevo_material:
        biblioteca.agregar_material(nuevo_material)
        flash(f"'{titulo}' añadido con éxito.", "success")
        global todos_los_materiales, tfidf_matrix, cosine_sim_matrix, id_a_indice
        todos_los_materiales = biblioteca.catalogo.buscar()
        documentos = [crear_documento_material(m) for m in todos_los_materiales]
        if documentos:
            tfidf_matrix = tfidf_vectorizer.fit_transform(documentos)
            cosine_sim_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
            id_a_indice = {m.id: i for i, m in enumerate(todos_los_materiales)}
    return redirect(url_for("home", view="admin"))


@app.route("/admin/retirar/<int:material_id>", methods=["POST"])
def admin_retirar_material(material_id):
    if session.get("rol") != "Administrativo":
        return redirect(url_for("home"))
    (exito, mensaje) = biblioteca.retirar_material(material_id)
    flash(mensaje, "success" if exito else "error")
    if "material" in request.referrer:
        return redirect(url_for("home"))
    return redirect(url_for("home", view="admin"))


@app.route("/debug/avanzar-tiempo", methods=["POST"])
def avanzar_tiempo():
    session["time_offset"] = session.get("time_offset", 0) + int(
        request.form.get("dias", 7)
    )
    return redirect(request.referrer or url_for("home", view="tiempo"))


@app.route("/debug/reset-tiempo", methods=["POST"])
def reset_tiempo():
    session["time_offset"] = 0
    return redirect(request.referrer or url_for("home", view="tiempo"))


if __name__ == "__main__":
    app.run(debug=True)
