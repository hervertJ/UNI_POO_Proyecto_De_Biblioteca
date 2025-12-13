# 🏛️ Gestor de Biblioteca Universitario (Intralu Core)

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.x-lightgrey?style=for-the-badge&logo=flask)
![Frontend](https://img.shields.io/badge/Jinja2-HTML5-orange?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Beta-yellow?style=for-the-badge)

> **Una solución integral para la gestión de recursos bibliográficos físicos y digitales, impulsada por algoritmos de recomendación y una arquitectura orientada a objetos.**

Este proyecto simula el ecosistema de una biblioteca universitaria moderna. No solo administra el inventario, sino que automatiza la lógica de negocios compleja: cálculo de multas, gestión de colas de espera, diferenciación de roles académicos y análisis de datos en tiempo real.

---

## 📑 Tabla de Contenidos

1. [Características Principales](#-características-principales)
2. [Arquitectura y Patrones de Diseño](#-arquitectura-y-patrones-de-diseño)
3. [Instalación y Configuración](#-instalación-y-configuración)
4. [Guía de Uso y Credenciales](#-guía-de-uso-y-credenciales)
5. [Estructura del Proyecto](#-estructura-del-proyecto)
6. [Tecnologías](#-tecnologías)

---

## 🚀 Características Principales

### 📦 Gestión Híbrida de Inventario
El sistema maneja dos tipos de recursos con comportamientos distintos:
* **Físicos (Libros, Revistas, Tesis):** Tienen stock limitado. Si se agotan, el sistema activa automáticamente una **Cola de Reserva**.
* **Digitales (Ebooks/PDF):** Stock ilimitado y acceso inmediato sin necesidad de devolución física.

### 👥 Roles y Permisos Granulares
La lógica de negocio se adapta al tipo de usuario:
* **Estudiantes:** Límite de 5 préstamos simultáneos.
* **Profesores:** Límite extendido (20 préstamos) y plazos de devolución más largos (hasta 90 días).
* **Administrativos:** Acceso total al panel de control y gestión de inventario.

### 🤖 Motor de Inteligencia Artificial (NLP)
Implementación de un sistema de recomendación de contenido ("Content-Based Filtering") utilizando **Scikit-Learn**:
* Vectorización TF-IDF de títulos y descripciones.
* Cálculo de Similitud del Coseno para sugerir material relacionado en la vista de detalles.

### 💰 Automatización Financiera & Simulación
* **Cálculo de Multas:** Generación automática de deuda (S/. 5.00/día) tras el vencimiento.
* **Simulador de Tiempo:** Herramienta de depuración que permite "avanzar" días o semanas para probar la caducidad de los préstamos sin esperar tiempo real.
* **Pasarela de Pago Simulada:** Integración visual con métodos locales (Yape/BCP).

---

## 🏗️ Arquitectura y Patrones de Diseño

El núcleo del sistema (`models.py`) está construido sobre una arquitectura robusta de **Programación Orientada a Objetos (POO)**, evitando el "código espagueti" y facilitando la escalabilidad.

### 1. Polimorfismo y Herencia
Se utiliza una jerarquía de clases estricta para manejar la diversidad de objetos:
* **Clase Abstracta `MaterialBibliografico`:** Define el contrato base.
    * `Libro`, `Revista`, `Tesis` implementan sus propias reglas de negocio (ej. `calcular_dias_prestamo()` varía según el tipo).
* **Clase Abstracta `Usuario`:**
    * `Estudiante`, `Profesor`, `Administrativo` heredan atributos base pero modifican propiedades como `limite_prestamos`.

### 2. Patrón State (Estado)
Para manejar el ciclo de vida de un préstamo, se evita el uso excesivo de `if/else` anidados mediante clases de estado:
* `PrestamoActivo`: Permite renovación, no genera multa.
* `PrestamoVencido`: Bloquea renovación, calcula multa diaria.
* `PrestamoDevuelto`: Estado final, libera stock.

### 3. Principios SOLID
* **Responsabilidad Única:** La lógica de visualización (`app.py`) está separada de la lógica de negocio (`models.py`).
* **Abierto/Cerrado:** Se pueden agregar nuevos tipos de materiales (ej. `Audiolibro`) creando una nueva clase sin modificar el código base de préstamos.

---

## 💻 Instalación y Configuración

### Prerrequisitos
* Python 3.8 o superior.
* Git.

### Pasos

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/tu-usuario/sistema-biblioteca-flask.git](https://github.com/tu-usuario/sistema-biblioteca-flask.git)
    cd sistema-biblioteca-flask
    ```

2.  **Crear entorno virtual:**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install flask scikit-learn matplotlib
    ```

4.  **Ejecutar la aplicación:**
    ```bash
    python app.py
    ```

5.  **Abrir en navegador:**
    Visita `http://127.0.0.1:5000`

---

## 🎮 Guía de Uso y Credenciales

El sistema viene con datos precargados ("seed data") para facilitar las pruebas inmediatas.

### 🔐 Credenciales de Acceso (Password: `123`)

| Rol | Usuario (Email) | Características a probar |
| :--- | :--- | :--- |
| **Estudiante** | `ana@uni.edu` | Solicitar libros, ver recomendaciones, pagar multas simuladas. |
| **Profesor** | `perez@uni.edu` | Probar plazos de préstamo extendidos (90 días). |
| **Admin** | `admin@uni.edu` | Acceso al Dashboard de métricas y alta de inventario. |

### ⏱️ Cómo usar el "Simulador de Tiempo"
1. Inicia sesión y realiza un préstamo.
2. Ve al menú lateral -> **Simulación**.
3. Avanza el tiempo `+15 días`.
4. Ve a **Mis Préstamos**: Verás que el estado ha cambiado a "Vencido" y se ha generado una multa.

---

## 📂 Estructura del Proyecto

```text
├── app.py                  # [Controlador] Rutas Flask, Configuración y Lógica ML
├── models.py               # [Modelo] Clases POO, Lógica de Negocio y Datos en Memoria
├── static/
│   └── style.css           # Estilos CSS (Dark Mode, Grid Layout)
├── templates/
│   ├── base.html           # Layout maestro (Sidebar, Headers)
│   ├── index.html          # Vista principal (Catálogo y Préstamos)
│   ├── login.html          # Login Page
│   ├── material_detalle.html # Vista detalle + Sistema de Reseñas
│   ├── admin_dashboard.html  # Panel Admin + Gráficos
│   └── perfil.html         # Perfil de usuario
└── README.md               # Documentación

