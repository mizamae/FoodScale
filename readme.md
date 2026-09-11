# FoodScale 🍎📊

FoodScale es una plataforma web orientada a la salud y el bienestar que funciona como una **calculadora nutricional avanzada y un gestor de evolución física**. Permite a los usuarios registrar de forma detallada sus ingestas diarias de alimentos, desglosar automáticamente el consumo preciso de macro y micronutrientes, definir metas dietéticas personalizadas y realizar un seguimiento histórico de su peso corporal.

---

## 🛠️ Especificaciones Técnicas y Arquitectura

La aplicación está desarrollada sobre el framework **Django 5.2**, utilizando un enfoque moderno, interactivo y asíncrono para el frontend mediante **HTMX** y **Bootstrap 5**, evitando recargas innecesarias de página.

### Componentes de la Arquitectura (Apps de Django)
*   **`main` (Módulo Core):** Se encarga de la configuración global, la seguridad de las sesiones (`SessionTimeoutMiddleware`), los términos legales y el formulario público de contacto protegido con **Google ReCaptcha v2 Invisible**.
*   **`FoodAPP` (Módulo Nutricional):** Contiene la lógica de alimentos, ingestas y procesamiento bioquímico. Transforma la información base del alimento (por cada 100g) de forma exacta según los gramos ingeridos reales. Genera analíticas visuales mediante **Plotly**.
*   **`UsersAPP` (Módulo de Usuarios):** Gestiona el ciclo de vida de las cuentas utilizando el **Email como identificador único** (en lugar de username). Centraliza el almacenamiento cronológico de datos biométricos (peso) en formato JSON.

### Procesos Asíncronos y Automatizaciones (`Celery Tasks`)
*   **Recordatorios Web Push:** Envía de forma automática notificaciones push (utilizando claves VAPID) a los usuarios suscritos en tres momentos clave del día: **08:00 AM** (Desayuno), **01:00 PM** (Comida) y **08:00 PM** (Cena).
*   **Poblamiento de Datos:** Tarea dedicada a parsear e importar de forma masiva los ingredientes base a partir de un archivo estructurado (`DB.json`), limpiando trazas y rangos complejos.
*   **Mantenimiento Automatizado:** Automatización anual para la renovación y despliegue de certificados SSL de Nginx mediante OpenSSL.

---

## 📦 Requisitos e Instalación

### Requisitos Previos
*   Python 3.10+
*   PostgreSQL
*   Redis (requerido para Celery y sistema de Cache)

### Instalación del Entorno de Desarrollo

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com
    cd FoodScale
    ```

2.  **Crear y activar el entorno virtual:**
    ```bash
    # En Linux/macOS:
    python3 -m venv env
    source env/bin/activate

    # En Windows:
    python -m venv .venv
    .venv\Scripts\activate
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurar variables de entorno:**
    Crea un archivo llamado `local.env` dentro del directorio `main/` basándote en los parámetros requeridos en `settings.py` (Claves secretas, credenciales de BD, Gmail/Office365, ReCaptcha y VAPID).

5.  **Ejecutar migraciones y arrancar el servidor:**
    ```bash
    python manage.py migrate
    python manage.py runserver
    ```

6.  **Iniciar los Workers de Celery (en terminales independientes):**
    ```bash
    # Worker principal
    celery -A main worker --loglevel=info
    # Schedulers (Beat) para tareas programadas
    celery -A main beat --loglevel=info
    ```

---

## 📖 MANUAL DE USUARIO

### 🔐 1. Gestión de Cuenta y Acceso
*   **Registro:** Haz clic en **Regístrate** en el menú superior. Completa tu Nombre, Apellido, Email y Contraseña. Tras guardar, recibirás un correo electrónico automático con un enlace único cifrado con UUID. Haz clic en él para activar tu cuenta.
*   **Inicio de Sesión y Bloqueo:** Inicia sesión con tu correo electrónico. Por seguridad de tus datos médicos, si la aplicación detecta inactividad durante **15 minutos**, cerrará tu sesión automáticamente.
*   **Cambiar Contraseña:** Desde el menú desplegable de tu perfil (esquina superior derecha), selecciona *Cambiar contraseña* para actualizar tus credenciales en cualquier momento.

### 📊 2. Mi Sitio (Configuración y Notificaciones)
Accede haciendo clic en tu nombre en la esquina superior derecha y seleccionando **Mi sitio**:
*   **Configuración Local:** Actualiza tus datos personales y define tu **Franja Horaria** para que los registros de comidas se sincronicen perfectamente con tu hora local.
*   **Alertas Diarias:** En el menú desplegable del perfil verás la opción para gestionar las notificaciones. Haz clic en **Habilitar notificaciones** y otorga permisos en tu navegador para empezar a recibir los recordatorios de comidas diarios.

### 🍎 3. La Calculadora Nutricional (Panel Principal)
*   **Navegación Temporal:** Usa las flechas **⬅️ Izquierda** o **➡️ Derecha** en la parte superior para moverte entre días pasados (para auditar tu historial) o días futuros (para planificar tu menú).
*   **Registrar un Alimento 🍴:** Haz clic en el botón azul con el icono de *Tenedor y Cuchillo*. Selecciona el tipo de comida (Desayuno, Almuerzo, Comida, etc.), escribe las primeras letras del alimento en el buscador interactivo para que el autocompletado te sugiera el correcto, introduce la cantidad exacta en gramos [g] y haz clic en *Guardar*.
*   **Modificar registros:** En la tabla de *Ingesta total* del día podrás corregir las cantidades haciendo clic en **Editar** o eliminar por completo un alimento pulsando **Borrar** de forma instantánea.

### 🥗 4. Metas Nutricionales (Diseñador de Dieta)
*   Haz clic en **Metas nutricionales** en la barra de navegación o página de inicio.
*   Establece los topes y límites diarios de Calorías, Macronutrientes (Proteínas, Carbohidratos), Grasas (Colesterol, Saturadas), Vitaminas y Minerales de acuerdo a tus objetivos de salud o prescripción médica.
*   Haz clic en **Save (Guardar)**. Los objetivos se contrastarán automáticamente con lo que consumas en tu día a día.

### 🧪 5. Lectura de Gráficas y Nutrientes
En la mitad inferior de la calculadora tendrás acceso a la analítica en tiempo real de tu jornada:
*   **Tabla de Desglose:** Mide los miligramos o gramos ingeridos de cada nutriente junto a tu meta diaria para ver tu porcentaje de cumplimiento.
*   **Pestaña Macronutrientes:** Renderiza un gráfico interactivo de barras de Plotly que distribuye visualmente el impacto de las proteínas, grasas y carbohidratos en tu ingesta actual.
*   **Pestañas de Grasas, Vitaminas y Minerales:** Desglosa de manera minuciosa todos los micronutrientes ingeridos para monitorizar e impedir deficiencias alimentarias.

### ⚖️ 6. Control y Registro de Peso
*   En la esquina superior de la calculadora, haz clic en el botón azul con el icono de la **Báscula**.
*   Ingresa los kilogramos actuales (ej: `78.2`) en el campo *Medida*.
*   Verifica la fecha y hora de la medición y haz clic en *Guardar*. El sistema registrará la métrica cronológicamente en tu historial personal.

---
*Desarrollado por Mikel Zabaleta — Última actualización de políticas de datos: 2026.*
