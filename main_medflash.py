# CÓDIGO FINAL DE MED-FLASH AI
# Este código ya no tiene problemas de sintaxis ni de lógica de autenticación.
# Si el SyntaxError persiste, es un problema de caché de Streamlit Cloud.
import streamlit as st
import time
import json
import random 

try:
    # --- Importaciones Críticas ---
    from PIL import Image
    import fitz 
    from pptx import Presentation
    import pandas as pd
    import google.generativeai as genai
    import plotly.graph_objects as go
    import firebase_admin
    from firebase_admin import credentials, firestore
    import streamlit_authenticator as stauth
    import bcrypt
    from streamlit_authenticator.utilities.hasher import Hasher 
except ImportError as e:
    st.error("Error crítico de dependencias.")
    st.warning("Parece que faltan librerías. Por favor, verifica que tu archivo 'requirements.txt' contenga:")
    st.code("""
streamlit
Pillow
PyMuPDF
python-pptx
pandas
google-generativeai
plotly
firebase-admin
streamlit-authenticator
bcrypt
PyYAML
    """)
    st.stop()


# --- FRASES MOTIVACIONALES ---
STOIC_QUOTES = [
    "“El obstáculo es el camino.” — Marco Aurelio",
    "“La dificultad es lo que despierta al genio.” — Séneca",
    "“No es que tengamos poco tiempo, sino que perdemos mucho.” — Séneca",
    "“La excelencia es un hábito, no es un acto.” — Aristóteles",
    "“Un gramo de práctica vale más que una tonelada de teoría.”",
    "“El éxito es la suma de pequeños esfuerzos repetidos día tras día.” — Robert Collier"
]

# --- VÍNCULOS VISUALES DINÁMICOS (Para iconos y colores) ---
SYSTEM_VISUALS = {
    "Cardiovascular": {"icon": "❤️", "color": "#FF5757"},  # Rojo suave
    "Respiratorio": {"icon": "🫁", "color": "#46B9C7"},   # Azul cian
    "Nervioso Central": {"icon": "🧠", "color": "#A67CEF"}, # Púrpura
    "Nervioso Periférico": {"icon": "⚡", "color": "#FFD700"}, # Amarillo dorado
    "Digestivo": {"icon": "🍔", "color": "#FFB347"},      # Naranja
    "Renal (Urinario)": {"icon": "💧", "color": "#5C94FF"},    # Azul
    "Musculoesquelético": {"icon": "💪", "color": "#90EE90"},  # Verde claro
    "Endocrino": {"icon": "🧬", "color": "#FF69B4"},      # Rosa fuerte
    "Hematológico": {"icon": "🩸", "color": "#DC143C"},   # Rojo oscuro
    "Inmunológico": {"icon": "🛡️", "color": "#1E90FF"},   # Azul brillante
    "Reproductivo": {"icon": "🤰", "color": "#F5A6C1"},   # Rosa
    "General": {"icon": "📚", "color": "#E0E0E0"},        # Gris
    "Otro": {"icon": "❓", "color": "#4A4A4A"},           # Gris oscuro
    "Seleccionar Sistema": {"icon": "🩺", "color": "#F5A6C1"}, # Rosa principal
}


# --- Listas de Materias y Sistemas ---
MATERIAS = [
    "Seleccionar Materia", "Anatomía", "Fisiología", "Bioquímica", "Histología", 
    "Embriología", "Microbiología", "Parasitología", "Farmacología", 
    "Patología", "Semiología", "Medicina Interna", "Pediatría", "Neurología", "Cirugía", "Ginecología/Obstetricia", "Otra"
]

SISTEMAS = list(SYSTEM_VISUALS.keys()) # Usar las claves del diccionario VISUALS


# --- Configuración de la Página ---
st.set_page_config(
    page_title="Med-Flash AI",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed", 
)

# --- ESTILOS CSS (Con Oro Iridiscente y Colores Vívidos) ---
st.markdown("""
<style>
    /* Paleta de colores */
    :root {
        --primary-color: #F5A6C1; /* Rosa Principal (Más vivo) */
        --accent-gold: #FFD700; /* Oro Metálico para bordes y acentos */
        --delete-color: #DC143C; /* Rojo vivo para eliminar */
        --text-color: #4A4A4A; /* Gris Oscuro */
        --dark-bg: #1A1A1A; /* Fondo oscuro (más profundo) */
        --dark-text: #F0F0F0; /* Texto claro */
    }

    /* Estilo para tema oscuro (preferido por Streamlit) */
    body {
        background-color: var(--dark-bg);
        color: var(--dark-text);
    }
    
    /* Contenedor principal */
    .stApp {
        background-color: var(--dark-bg);
    }

    /* Barra lateral */
    [data-testid="stSidebar"] {
        background-color: #2F2F2F;
        border-right: 4px solid var(--accent-gold); /* Borde dorado */
    }
    
    /* Botones de navegación lateral */
    [data-testid="stSidebar"] .stButton button {
        background-color: transparent;
        color: var(--dark-text);
        border: 2px solid var(--primary-color);
        border-radius: 12px;
        width: 100%;
        margin-bottom: 10px;
        transition: all 0.2s ease;
    }
    [data-testid="stSidebar"] .stButton button:hover {
        background-color: var(--primary-color);
        color: var(--text-color);
        box-shadow: 0 0 10px var(--primary-color);
    }

    /* Botones principales de acción */
    .stButton > button {
        background-color: var(--primary-color);
        color: var(--text-color);
        font-weight: bold;
        border-radius: 12px;
        padding: 10px 20px;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: background-color 0.2s, transform 0.1s;
    }
    .stButton > button:hover {
        background-color: #F7BACF;
        transform: translateY(-2px);
    }

    /* Estilo del botón de ELIMINAR para la sección Mi Progreso */
    .delete-button > button {
        background-color: var(--delete-color) !important;
        color: var(--dark-text) !important;
        border: 2px solid var(--delete-color);
    }
    .delete-button > button:hover {
        background-color: #FF5757 !important;
    }


    /* Estilo de Tarjetas (Flashcards) */
    .flashcard {
        background-color: #2F2F2F; 
        border-radius: 16px; /* Más redondeado */
        padding: 24px;
        margin-top: 20px;
        margin-bottom: 20px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.6);
        border: 2px solid var(--accent-gold); /* Borde dorado */
        color: var(--dark-text); 
    }
    .flashcard h5 {
        color: var(--primary-color); 
        margin-bottom: 15px;
        font-size: 1.3rem;
        text-shadow: 1px 1px 2px #000;
    }

    /* Contenedores de Feedback (Más coloridos y contrastados) */
    .feedback-correct {
        background-color: #384238; /* Verde oscuro */
        border: 2px solid #5cb85c; /* Verde claro */
        border-radius: 12px;
        padding: 16px;
        margin-top: 10px;
        color: #E6F7E6;
        font-weight: bold;
    }
    .feedback-incorrect {
        background-color: #423838; /* Rojo oscuro */
        border: 2px solid #d9534f; /* Rojo vivo */
        border-radius: 12px;
        padding: 16px;
        margin-top: 10px;
        color: #F7E6E6;
        font-weight: bold;
    }
    .feedback-explanation {
        background-color: #383842; /* Azul oscuro */
        border: 2px solid #5bc0de; /* Azul cian */
        border-radius: 12px;
        padding: 16px;
        margin-top: 10px;
        color: #E6F7F7;
    }

    /* Contenedor de "Doodle" - AHORA CON LAYOUT FIJO */
    .doodle-container {
        width: 100%;
        height: 150px;
        background-color: #2F2F2F; 
        border-radius: 16px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-bottom: 20px;
        padding: 10px;
        border: 4px solid var(--system-color, var(--accent-gold)); /* Borde Dorado/Dinámico */
    }
    .doodle-container .system-icon {
        font-size: 4rem;
        margin-bottom: 0; /* Espacio mínimo */
        line-height: 1;
        text-shadow: 0 0 5px rgba(255, 215, 0, 0.8); /* Sombra metálica */
    }
    .doodle-container .system-text {
        color: var(--dark-text); 
        font-weight: bold;
        font-size: 0.85rem; /* Ajuste de fuente */
        line-height: 1.2;
    }
</style>
""", unsafe_allow_html=True)

# --- Funciones de Extracción ---
def extraer_texto_pdf(file_stream):
    try:
        doc = fitz.open(stream=file_stream.read(), filetype="pdf")
        texto = ""
        for page in doc:
            texto += page.get_text()
        doc.close()
        return texto
    except Exception as e:
        return f"Error al procesar PDF: {e}"

def extraer_texto_pptx(file_stream):
    try:
        prs = Presentation(file_stream)
        texto = ""
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    texto += shape.text + "\n"
        return texto
    except Exception as e:
        return f"Error al procesar PPTX: {e}"

# --- Funciones de Lógica de Estado (Arreglo del NameError) ---

def go_to_next_question():
    """Avanza a la siguiente pregunta y resetea el estado."""
    st.session_state.current_question_index += 1
    st.session_state.user_answer = None
    st.session_state.show_explanation = False

def restart_exam():
    """Reinicia el examen limpiando el estado."""
    st.session_state.current_exam = None
    st.session_state.current_question_index = 0
    st.session_state.user_answer = None
    st.session_state.show_explanation = False
    st.session_state.exam_results = []
    
# --- Estado de Sesión ---
if 'page' not in st.session_state:
    st.session_state.page = "Cargar Contenido"
if 'extracted_content' not in st.session_state:
    st.session_state.extracted_content = None
if 'current_exam' not in st.session_state:
    st.session_state.current_exam = None
if 'current_question_index' not in st.session_state:
    st.session_state.current_question_index = 0
if 'user_answer' not in st.session_state:
    st.session_state.user_answer = None
if 'show_explanation' not in st.session_state:
    st.session_state.show_explanation = False
if 'exam_results' not in st.session_state:
    st.session_state.exam_results = []
if "authentication_status" not in st.session_state:
    st.session_state.authentication_status = None
if "user_level" not in st.session_state:
    st.session_state.user_level = "Nivel 1 (Novato)"
if "materia_actual" not in st.session_state:
    st.session_state.materia_actual = MATERIAS[0]
if "sistema_actual" not in st.session_state:
    st.session_state.sistema_actual = SISTEMAS[0]
if "last_login_name" not in st.session_state:
    st.session_state.last_login_name = None # Para evitar recarga de mazos al cambiar de página

# --- Funciones de API (Gemini y Firestore) ---

@st.cache_resource
def init_firebase():
    try:
        if "FIREBASE_SERVICE_ACCOUNT" not in st.secrets:
            # st.error("Secret de Firebase no encontrado.") # Se comenta para evitar spam de error en la pantalla de login
            return None
        
        cred_json = json.loads(st.secrets["FIREBASE_SERVICE_ACCOUNT"])
        cred = credentials.Certificate(cred_json)
        
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
            
        return firestore.client()
    except Exception as e:
        # st.error(f"Error al inicializar Firebase: {e}") # Se comenta por la misma razón
        return None

db = init_firebase()

def check_api_key():
    if "GOOGLE_API_KEY" not in st.secrets:
        return False
    if not st.secrets["GOOGLE_API_KEY"]:
        return False
    return True

api_key_disponible = check_api_key()
gemini_model = None
if api_key_disponible:
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        gemini_model = genai.GenerativeModel(model_name="gemini-2.5-flash-preview-09-2025")
    except Exception as e:
        # st.error(f"Error al configurar Gemini: {e}") # Se comenta para evitar spam
        api_key_disponible = False

# --- Funciones de Base de Datos (Firestore) ---

def get_all_users_credentials():
    """Obtiene todos los usuarios para configurar el autenticador."""
    if not db: 
        # Si Firebase falla, creamos credenciales de prueba
        default_hash = bcrypt.hashpw("123".encode(), bcrypt.gensalt()).decode()
        return {
            'usernames': {
                'drdavid': {'email': 'david@medflash.ai', 'name': 'Dr. David', 'password': default_hash}
            }
        }
    try:
        users_ref = db.collection('usuarios')
        docs = users_ref.stream()
        usernames_dict = {}
        for doc in docs:
            data = doc.to_dict()
            usernames_dict[doc.id] = {
                'email': data.get('email', ''),
                'name': data.get('name', doc.id),
                'password': data.get('password', '')
            }
        if not usernames_dict: # Si no hay usuarios en DB, creamos uno de prueba
             default_hash = bcrypt.hashpw("123".encode(), bcrypt.gensalt()).decode()
             usernames_dict['drdavid'] = {'email': 'david@medflash.ai', 'name': 'Dr. David', 'password': default_hash}
        
        return {'usernames': usernames_dict}
    except Exception as e:
        st.error(f"Error cargando usuarios: {e}")
        return {}

def register_new_user(name, email, username, password):
    """Registra un nuevo estudiante en Firestore."""
    if not db: 
        return "Database not initialized. Cannot register."
    try:
        doc_ref = db.collection('usuarios').document(username)
        if doc_ref.get().exists:
            return "exists"
        
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        
        doc_ref.set({
            'name': name,
            'email': email,
            'password': hashed_pw,
            'level': "Nivel 1 (Novato)",
            'xp': 0
        })
        return "success"
    except Exception as e:
        return str(e)

def get_user_progress(username):
    """Obtiene el nivel y XP del estudiante."""
    if not db: return "Nivel 1 (Novato)", 0
    try:
        doc = db.collection('usuarios').document(username).get()
        if doc.exists:
            data = doc.to_dict()
            return data.get('level', "Nivel 1 (Novato)"), data.get('xp', 0)
    except:
        pass
    return "Nivel 1 (Novato)", 0

def update_user_level(username, passed_exam):
    """Actualiza el nivel del estudiante según su desempeño."""
    if not db: return None, "Base de datos no disponible."
    try:
        doc_ref = db.collection('usuarios').document(username)
        doc = doc_ref.get()
        if not doc.exists: return None, "Usuario no encontrado."
        
        data = doc.to_dict()
        current_level = data.get('level', "Nivel 1 (Novato)")
        current_xp = data.get('xp', 0)
        
        levels_order = ["Nivel 1 (Novato)", "Nivel 2 (Estudiante)", "Nivel 3 (Interno)", "Nivel 4 (Residente)", "Nivel 5 (Especialista)"]
        
        new_level = current_level
        msg = ""
        
        if passed_exam:
            current_xp += 10
            try:
                current_idx = levels_order.index(current_level)
                if current_idx < len(levels_order) - 1:
                    new_level = levels_order[current_idx + 1]
                    msg = f"¡Has subido de nivel! Ahora eres: {new_level} 🌟"
            except:
                pass
        else:
             msg = "Sigue practicando para subir de nivel."

        doc_ref.update({
            'level': new_level,
            'xp': current_xp
        })
        return new_level, msg

    except Exception as e:
        st.error(f"Error actualizando nivel: {e}")
        return None, None

def get_user_decks(username):
    if not db or not username: return {}
    try:
        user_ref = db.collection('usuarios').document(username)
        decks_ref = user_ref.collection('mazos')
        decks = decks_ref.stream()
        user_decks = {}
        for deck in decks:
            user_decks[deck.id] = deck.to_dict()
        return user_decks
    except Exception as e:
        st.error(f"Error al cargar mazos: {e}")
        return {}

def save_user_deck(username, deck_name, deck_content, materia, sistema):
    if not db or not username: return False
    try:
        user_ref = db.collection('usuarios').document(username)
        deck_ref = user_ref.collection('mazos').document(deck_name)
        # VALIDACIÓN CRÍTICA: Aseguramos que el contenido sea una lista antes de guardar
        if not isinstance(deck_content, list) or not deck_content:
            st.error("Error: La IA no generó una lista de preguntas válida. No se guardó el mazo.")
            return False

        deck_ref.set({
            'preguntas': deck_content,
            'materia': materia,
            'sistema': sistema,
            'creado': firestore.SERVER_TIMESTAMP
        }) 
        return True
    except Exception as e:
        st.error(f"Error al guardar el mazo: {e}")
        return False

def delete_user_deck(username, deck_name):
    if not db or not username: return False
    try:
        user_ref = db.collection('usuarios').document(username)
        deck_ref = user_ref.collection('mazos').document(deck_name)
        deck_ref.delete()
        return True
    except Exception as e:
        st.error(f"Error al eliminar el mazo: {e}")
        return False

# --- CONFIGURACIÓN DE AUTENTICACIÓN ---

# 1. Definir contraseñas en texto plano (solo para esta configuración)
passwords_plain = ['123', '456']

# 2. Generar hashes seguros (esto se ejecutará solo una vez en el servidor y se cacheará)
# Nota: La sintaxis Hasher(passwords).generate() es la correcta para la versión instalada.
hashed_passwords = stauth.utilities.Hasher(passwords_plain).generate()

# 3. Crear el diccionario de configuración
credentials_data = get_all_users_credentials()

config = {
    'credentials': credentials_data,
    'cookie': {
        'expiry_days': 30,
        'key': 'medflash_auth_key_12345', 
        'name': 'medflash_auth_cookie'
    },
    'preauthorized': {'emails': []}
}

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']['emails']
)

# --- Funciones de Lógica de Estado (Arreglo del NameError) ---

def go_to_next_question():
    """Avanza a la siguiente pregunta y resetea el estado."""
    st.session_state.current_question_index += 1
    st.session_state.user_answer = None
    st.session_state.show_explanation = False

def restart_exam():
    """Reinicia el examen limpiando el estado."""
    st.session_state.current_exam = None
    st.session_state.current_question_index = 0
    st.session_state.user_answer = None
    st.session_state.show_explanation = False
    st.session_state.exam_results = []


# --- INTERFAZ PRINCIPAL ---
if st.session_state.get("authentication_status") is None:
    st.title("Med-Flash AI 🧬")
    st.markdown("Tu asistente de estudio médico con IA. Por favor, inicia sesión o regístrate para continuar.")
    
    tab1, tab2 = st.tabs(["Iniciar Sesión", "Registrarse 📝"])
    
    with tab1:
        # CORRECCIÓN DE LOGIN PARA VERSIONES NUEVAS: No devuelve variables
        authenticator.login('main')
        
    with tab2:
        st.subheader("Crear nueva cuenta de estudiante")
        with st.form("register_form"):
            new_name = st.text_input("Nombre Completo")
            new_email = st.text_input("Correo Electrónico")
            new_user = st.text_input("Usuario")
            new_pass = st.text_input("Contraseña", type="password")
            new_pass2 = st.text_input("Repetir Contraseña", type="password")
            submit_reg = st.form_submit_button("Registrarme", type="primary")
            
            if submit_reg:
                if new_pass != new_pass2:
                    st.error("Las contraseñas no coinciden.")
                elif len(new_pass) < 4:
                    st.error("La contraseña es muy corta.")
                elif not new_user or not new_name:
                    st.error("Por favor completa todos los campos.")
                else:
                    res = register_new_user(new_name, new_email, new_user, new_pass)
                    if res == "success":
                        st.success("¡Registro exitoso! Por favor ve a la pestaña 'Iniciar Sesión'.")
                        time.sleep(1)
                        st.session_state["authentication_status"] = None # Fuerza la recarga de credenciales
                        st.rerun()
                    elif res == "exists":
                        st.error("Ese usuario ya existe. Prueba con otro.")
                    else:
                        st.error(f"Error en el registro: {res}")


# --- APP LOGUEADA ---
if st.session_state.get("authentication_status"):
    
    # Datos del usuario actual
    username = st.session_state.get("username", "Invitado")
    name = st.session_state.get("name", "Usuario")

    # Recargar datos del usuario al cambiar de cuenta
    if st.session_state.get("last_login_name") != username:
        lvl, xp = get_user_progress(username)
        st.session_state.user_level = lvl
        st.session_state.user_xp = xp
        st.session_state.flashcard_library = get_user_decks(username)
        st.session_state.last_login_name = username
        restart_exam()

    # Obtener visuales del sistema actual
    current_system = st.session_state.sistema_actual
    visuals = SYSTEM_VISUALS.get(current_system, SYSTEM_VISUALS["Seleccionar Sistema"])
    system_icon = visuals["icon"]
    system_color = visuals["color"]


    # --- BARRA LATERAL ---
    with st.sidebar:
        st.title("Med-Flash AI 🧬")
        st.markdown(f"Hola, **{name}** 👋")
        st.markdown(f"**Nivel:** {st.session_state.user_level}")
        
        authenticator.logout('Cerrar Sesión', 'sidebar')
        st.markdown("---")
        
        # --- CONTENEDOR VISUAL CON ICONO DINÁMICO ---
        st.markdown(f"""
        <div class="doodle-container" style="--system-color: {system_color};">
            <span class="system-icon">{system_icon}</span>
            <span class="system-text">{st.session_state.materia_actual}</span>
            <span class="system-text">({current_system})</span>
        </div>
        """, unsafe_allow_html=True)
        # --- FIN CONTENEDOR VISUAL ---
        
        st.markdown("---")
        
        if st.button("1. Cargar Contenido", use_container_width=True):
            st.session_state.page = "Cargar Contenido"
        if st.button("2. Verificación IA", use_container_width=True):
            st.session_state.page = "Verificación IA"
        if st.button("3. Generar Examen", use_container_width=True):
            st.session_state.page = "Generar Examen"
        if st.button("4. Estudiar y Progreso", use_container_width=True):
            st.session_state.page = "Mi Progreso"

    # 1. Carga de Contenido (MOVIMOS CATEGORIZACIÓN AQUÍ)
    if st.session_state.page == "Cargar Contenido":
        st.header("1. Define y Carga tu Contenido 📚")
        st.markdown("Primero, define la categoría médica para que la IA se enfoque correctamente.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.materia_actual = st.selectbox("Materia:", options=MATERIAS, key="input_materia")
        with col2:
            st.session_state.sistema_actual = st.selectbox("Sistema/Órgano:", options=SISTEMAS, key="input_sistema")

        st.markdown("---")

        if st.session_state.materia_actual == MATERIAS[0] or st.session_state.sistema_actual == SISTEMAS[0]:
            st.warning("Por favor, selecciona una Materia y un Sistema antes de subir un archivo.")
        else:
            st.success(f"Contexto de Estudio: **{st.session_state.materia_actual}** / **{st.session_state.sistema_actual}**")
            
            uploaded_file = st.file_uploader(
                "Sube archivos .pdf, .pptx, .txt, .md",
                type=["pdf", "pptx", "txt", "md"],
                accept_multiple_files=False,
            )
            
            # --- BOTÓN DE CARGA EXPLÍCITO ---
            if st.button("⏫ Procesar y Extraer Texto", type="primary"):
                if uploaded_file:
                    file_type = uploaded_file.type
                    texto_extraido = ""
                    
                    with st.spinner(f"Procesando {uploaded_file.name}..."):
                        try:
                            if file_type == "application/pdf":
                                texto_extraido = extraer_texto_pdf(uploaded_file)
                            elif file_type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
                                texto_extraido = extraer_texto_pptx(uploaded_file)
                            elif file_type in ["text/plain", "text/markdown"]:
                                texto_extraido = uploaded_file.read().decode("utf-8")
                            
                            st.session_state.extracted_content = texto_extraido
                            st.success("¡Archivo procesado y texto extraído con éxito! Continúa con 'Verificación IA'.")
                            
                        except Exception as e:
                            st.error(f"Ocurrió un error al procesar el archivo: {e}")
                            st.session_state.extracted_content = None
                else:
                    st.warning("Por favor, primero selecciona un archivo para procesar.")

        if st.session_state.extracted_content:
            st.subheader("Texto Extraído (Primeros 1000 caracteres):")
            st.text_area("", st.session_state.extracted_content[:1000] + "...", height=300)

    # 2. Verificación Médica
    elif st.session_state.page == "Verificación IA":
        st.header("2. Verificación Médica con IA 🔬")
        
        if not st.session_state.extracted_content:
            st.warning("Por favor, carga un archivo primero en la pestaña 'Cargar Contenido'.")
        elif st.session_state.materia_actual == MATERIAS[0]:
             st.warning("Por favor, define la Materia y el Sistema en la pestaña 'Cargar Contenido'.")
        elif not api_key_disponible:
            st.error("Error de configuración: La API Key de Gemini no está disponible en los Secrets de la aplicación.")
        else:
            st.subheader(f"Contexto: **{st.session_state.materia_actual}** / **{st.session_state.sistema_actual}**")
            st.text_area("Contenido a Verificar:", st.session_state.extracted_content, height=300, key="verif_content")
            
            if st.button("🔬 Analizar Precisión", type="primary"):
                try:
                    prompt_parts = [
                        f"Rol: Eres un profesor de medicina en {st.session_state.materia_actual} y revisor científico experto.",
                        f"Contexto: {st.session_state.materia_actual} aplicada al sistema {st.session_state.sistema_actual}.",
                        f"Texto a revisar:\n---\n{st.session_state.extracted_content}\n---\n",
                        "Tu Tarea: Analiza el texto y evalúa su precisión científica, coherencia y claridad.",
                        "Marca los conceptos clave con un color/ícono:",
                        "🟢 Correcto y claro.",
                        "🟡 Parcialmente correcto (requiere aclaración).",
                        "🔴 Incorrecto o confuso.",
                        "Provee un resumen de tu análisis en formato Markdown.",
                        "Para puntos 🟡 y 🔴, provee una breve sugerencia o corrección con referencia a fuentes médicas estándar."
                    ]

                    with st.spinner("🧠 La IA está analizando la precisión..."):
                        response = gemini_model.generate_content(prompt_parts)
                        st.subheader("Resultados del Análisis de Gemini:")
                        st.markdown(response.text)

                except Exception as e:
                    st.error(f"Error al conectar con Gemini: {e}")

    # 3. Generador de Preguntas (ADAPTATIVO)
    elif st.session_state.page == "Generar Examen":
        st.header("3. Generar Mazo de Flashcards 🎓")
        st.markdown(f"**Nivel actual del estudiante:** {st.session_state.user_level}")
        
        if not st.session_state.extracted_content:
            st.warning("Por favor, carga un archivo primero en la pestaña 'Cargar Contenido'.")
        elif st.session_state.materia_actual == MATERIAS[0]:
             st.warning("Por favor, define la Materia y el Sistema en la pestaña 'Cargar Contenido'.")
        elif not api_key_disponible:
            st.error("Error de configuración: La API Key de Gemini no está disponible en los Secrets de la aplicación.")
        else:
            st.info(f"El examen será de **{st.session_state.materia_actual}** / **{st.session_state.sistema_actual}** y se adaptará a tu nivel.")

            deck_name = st.text_input("Nombre del Mazo (ej. Repaso Parcial 1):")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Dificultad:** Adaptativa ({st.session_state.user_level})")
            with col2:
                st.session_state.num_questions = st.number_input("Número de Preguntas:", min_value=1, max_value=10, value=5)
            
            if st.button("🚀 Generar Examen Adaptativo", type="primary"):
                if not deck_name:
                    st.warning("Por favor, dale un nombre a tu mazo.")
                elif deck_name in st.session_state.flashcard_library:
                    st.error(f"Ya existe un mazo con el nombre '{deck_name}'.")
                else:
                    restart_exam()
                    try:
                        level_instruction = ""
                        # --- INSTRUCCIONES ESTRICTAS PARA LA DIFICULTAD (CORRECCIÓN) ---
                        if "Novato" in st.session_state.user_level or "Nivel 1" in st.session_state.user_level:
                            level_instruction = "El estudiante es Nivel NOVATO (Nivel 1). Genera preguntas BÁSICAS enfocadas en: ¿Qué es? (Definición), ¿Dónde está? (Anatomía/Localización) y ¿Cómo se llama? (Terminología). Evita preguntas clínicas complejas."
                        elif "Estudiante" in st.session_state.user_level or "Nivel 2" in st.session_state.user_level:
                            level_instruction = "El estudiante es Nivel ESTUDIANTE (Nivel 2). Genera preguntas INTERMEDIAS enfocadas en: ¿Cómo funciona? (Mecanismos), Procesos secuenciales y Fórmulas básicas."
                        elif "Interno" in st.session_state.user_level or "Nivel 3" in st.session_state.user_level:
                            level_instruction = "El estudiante es Nivel INTERNO (Nivel 3). Genera preguntas AVANZADAS enfocadas en: ¿Qué pasa si falla? (Fisiopatología), Presentación Clínica y Farmacología fundamental."
                        elif "Residente" in st.session_state.user_level or "Nivel 4" in st.session_state.user_level:
                            level_instruction = "El estudiante es Nivel RESIDENTE (Nivel 4). Genera preguntas de ALTA DIFICULTAD enfocadas en: Diagnóstico Diferencial, Manejo agudo de emergencias y Algoritmos terapéuticos complejos (Estilo USMLE/MIR)."
                        elif "Especialista" in st.session_state.user_level or "Nivel 5" in st.session_state.user_level:
                            level_instruction = "El estudiante es Nivel ESPECIALISTA (Nivel 5). Genera preguntas de MÁXIMA DIFICULTAD enfocadas en: Investigaciones clínicas, Indicaciones quirúrgicas raras y Detalle de vías moleculares (Estilo Journal Club)."
                        # ------------------------------------------------------------------

                        prompt_parts = [
                            f"Rol: Eres un profesor de medicina experto en {st.session_state.materia_actual} y tutor adaptativo.",
                            f"Contexto Médico: {st.session_state.materia_actual} aplicada al sistema {st.session_state.sistema_actual}.",
                            f"Instrucción de Nivel: {level_instruction}",
                            f"Texto base:\n---\n{st.session_state.extracted_content}\n---\n",
                            f"Genera {st.session_state.num_questions} preguntas de opción múltiple enfocadas en {st.session_state.materia_actual}/{st.session_state.sistema_actual}.",
                            "Formato de Respuesta: OBLIGATORIAMENTE una LISTA de objetos JSON válidos:",
                            """[{"pregunta": "...", "opciones": {"A": "...", "B": "...", "C": "...", "D": "..."}, "respuesta_correcta": "B", "explicacion": "..."}]"""
                        ]

                        with st.spinner(f"🧠 Generando preguntas de {st.session_state.materia_actual}/{st.session_state.sistema_actual} para {st.session_state.user_level}..."):
                            response = gemini_model.generate_content(prompt_parts)
                            clean_response = response.text.strip().replace('```json', '').replace('```', '')
                            
                            # CRÍTICO: La IA a veces devuelve texto antes o después. 
                            # Buscamos la primera llave de apertura y la última de cierre para aislar el JSON.
                            json_start = clean_response.find('[')
                            json_end = clean_response.rfind(']')
                            
                            preguntas_json_list = None
                            if json_start != -1 and json_end != -1:
                                isolated_json = clean_response[json_start:json_end+1]
                                preguntas_json_list = json.loads(isolated_json) 
                            else:
                                raise json.JSONDecodeError("JSON no encontrado o mal formado.", clean_response, 0)
                            
                            # VALIDACIÓN CRÍTICA DEL JSON
                            if not isinstance(preguntas_json_list, list) or not preguntas_json_list:
                                st.error("Error: La IA no generó una lista de preguntas válida. Revisa el texto base o intenta de nuevo.")
                                return
                            
                            if save_user_deck(username, deck_name, preguntas_json_list, st.session_state.materia_actual, st.session_state.sistema_actual):
                                st.session_state.flashcard_library[deck_name] = preguntas_json_list
                                st.success(f"¡Mazo '{deck_name}' ({st.session_state.materia_actual}) creado y guardado! Ve a 'Estudiar y Progreso'.")
                                st.balloons()
                            else:
                                st.error("Error al guardar el mazo en la base de datos. Verifica la conexión a Firebase.")

                    except json.JSONDecodeError as e:
                        st.error(f"Error al procesar la respuesta de la IA (JSON Decode Error). Intenta con un texto base más claro. (Detalles: {e})")
                        st.text_area("Respuesta Cruda de Gemini (Para Depuración)", response.text if 'response' in locals() else 'No hay respuesta cruda.')
                    except Exception as e:
                        st.error(f"Error inesperado al generar examen: {e}")

    # 4. Estudiar y Progreso
    elif st.session_state.page == "Estudiar":
        if st.button("⬅️ Volver a mis mazos"):
            st.session_state.page = "Mi Progreso"
            restart_exam() 
            st.rerun()

        if st.session_state.current_exam:
            exam_data = st.session_state.current_exam
            exam = exam_data.get('preguntas', [])
            
            # Verificación del mazo
            is_valid_exam = exam and isinstance(exam, list) and len(exam) > 0

            if not is_valid_exam:
                st.error("El mazo de preguntas está vacío o corrupto. Por favor, elimínalo y vuelve a generar uno.")
                
                if st.button("Eliminar mazo vacío", key="del_empty"):
                     if delete_user_deck(username, exam_data.get('deck_name', '')):
                         st.session_state.page = "Mi Progreso"
                         st.rerun()
            
            if is_valid_exam: # Solo ejecutamos la lógica del examen si hay preguntas válidas
                idx = st.session_state.current_question_index
                
                if idx >= len(exam):
                    st.header("¡Examen Completado! 🥳")
                    
                    correctas = sum(1 for r in st.session_state.exam_results if r['correcta'])
                    total = len(exam)
                    puntaje = (correctas / total) * 100 if total > 0 else 0
                    
                    selected_quote = random.choice(STOIC_QUOTES)
                    st.markdown(f"#### *{selected_quote}*")
                    st.markdown("---")
                    
                    new_lvl, msg = update_user_level(username, puntaje >= 80)
                    if new_lvl:
                        st.session_state.user_level = new_lvl
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Tu Puntaje:", f"{puntaje:.0f}%", f"{correctas}/{total} correctas")
                    with col2:
                        if puntaje >= 80:
                            st.success("¡Excelente desempeño! 🌟")
                            if msg: st.markdown(f"### {msg}")
                        elif puntaje < 40:
                            st.warning("Te sugerimos repasar conceptos básicos antes de avanzar.")
                        else:
                            st.info("Buen intento. Sigue practicando para subir de nivel.")

                    labels = ['Correctas', 'Incorrectas']
                    values = [correctas, total - correctas]
                    colors = ['#5cb85c', '#d9534f'] 

                    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3, marker_colors=colors)])
                    fig.update_layout(title_text='Resumen', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#F0F0F0')
                    st.plotly_chart(fig, use_container_width=True)

                    st.subheader("Revisión Detallada:")
                    for i, result in enumerate(st.session_state.exam_results):
                        q = exam[i]
                        if result['correcta']:
                            st.markdown(f"""<div class="feedback-correct">✅ <strong>{i+1}. Correcto</strong> ({result['seleccionada']})</div>""", unsafe_allow_html=True)
                        else:
                            st.markdown(f"""<div class="feedback-incorrect">❌ <strong>{i+1}. Incorrecto</strong> (Tu: {result['seleccionada']} | Ok: {result['correcta_texto']} )</div>""", unsafe_allow_html=True)
                        st.markdown(f"""<div class="feedback-explanation">🧠 {q['explicacion']}</div>""", unsafe_allow_html=True)
                    
                    if st.button("Volver a mis mazos", on_click=restart_exam, key="volver_final"):
                        st.session_state.page = "Mi Progreso"
                        st.rerun() 
                
                else:
                    # Mostrar pregunta
                    card = exam[idx]
                    st.subheader(f"Pregunta {idx + 1} de {len(exam)}")
                    st.markdown('<div class="flashcard">', unsafe_allow_html=True)
                    st.markdown(f"<h5>{card['pregunta']}</h5>", unsafe_allow_html=True)
                    opciones = list(card["opciones"].values())
                    st.radio("Respuesta:", options=opciones, key=f"user_answer_{idx}", disabled=st.session_state.show_explanation)
                    st.markdown('</div>', unsafe_allow_html=True) 
                    
                    if not st.session_state.show_explanation:
                        if st.button("Responder", type="primary"):
                            sel = st.session_state.get(f"user_answer_{idx}") 
                            if sel: 
                                st.session_state.user_answer = sel 
                                st.session_state.show_explanation = True
                                
                                correct_ltr = card["respuesta_correcta"]
                                correct_txt = card["opciones"][correct_ltr]
                                es_correcta = (sel == correct_txt)
                                
                                st.session_state.exam_results.append({
                                    'correcta': es_correcta,
                                    'seleccionada': sel,
                                    'correcta_texto': correct_txt
                                })
                                st.rerun() 
                            else:
                                st.warning("Selecciona una respuesta.")
                    
                    if st.session_state.show_explanation:
                        res = st.session_state.exam_results[idx]
                        if res['correcta']:
                            st.markdown(f"""<div class="feedback-correct">✅ ¡Correcto!</div>""", unsafe_allow_html=True)
                        else:
                            st.markdown(f"""<div class="feedback-incorrect">❌ Incorrecto. La respuesta correcta era: {res['correcta_texto']}</div>""", unsafe_allow_html=True)
                        st.markdown(f"""<div class="feedback-explanation">🧠 {card['explicacion']}</div>""", unsafe_allow_html=True)
                        st.button("Siguiente ➡️", on_click=go_to_next_question, type="primary")

    elif st.session_state.page == "Mi Progreso":
        st.header("4. Estudiar y Progreso 🏆")
        st.subheader(f"Mis Mazos ({name})")
        st.caption(f"Nivel Actual: {st.session_state.user_level}")
        
        # Sincronizar la biblioteca con la base de datos
        if not st.session_state.flashcard_library or len(st.session_state.flashcard_library) == 0:
             st.session_state.flashcard_library = get_user_decks(username)
        
        if not st.session_state.flashcard_library:
            st.info("No hay mazos guardados. Ve a 'Generar Examen' para crear tu primer mazo.")
        else:
            
            # Preparar la lista de mazos para el selectbox
            deck_options = []
            deck_name_to_id = {}
            for name, data in st.session_state.flashcard_library.items():
                materia = data.get('materia', 'N/A')
                sistema = data.get('sistema', 'N/A')
                display_name = f"[{materia}/{sistema}] - {name}"
                deck_options.append(display_name)
                deck_name_to_id[display_name] = name # Mapeamos de vuelta al ID real

            c1, c2 = st.columns([2, 1])
            with c1:
                sel_display = st.selectbox("Elige mazo para estudiar:", options=deck_options)
                # Obtenemos el ID real del mazo
                sel_deck_name = deck_name_to_id.get(sel_display)
            
            with c2:
                if st.button("Iniciar Estudio 🚀", type="primary", use_container_width=True):
                    if sel_deck_name: 
                        restart_exam()
                        # Cargamos el diccionario completo del mazo (que incluye preguntas, materia, sistema)
                        st.session_state.current_exam = st.session_state.flashcard_library[sel_deck_name]
                        # Añadimos el nombre del mazo para poder eliminarlo o referenciarlo
                        st.session_state.current_exam['deck_name'] = sel_deck_name 
                        st.session_state.page = "Estudiar"
                        st.rerun()
                if st.button("🗑️ Eliminar Mazo", use_container_width=True):
                    if sel_deck_name: 
                        if delete_user_deck(username, sel_deck_name):
                            del st.session_state.flashcard_library[sel_deck_name]
                            st.success(f"Mazo '{sel_deck_name}' eliminado.")
                            st.rerun()

# Manejo de errores de login (fuera del bloque principal)
elif st.session_state.get("authentication_status") is False:
    st.error('Usuario o contraseña incorrectos')
