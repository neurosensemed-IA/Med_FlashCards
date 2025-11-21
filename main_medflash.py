# CÓDIGO FINAL DE MED-FLASH AI (Versión Optimizada Dr. David)
import streamlit as st
import time
import json
import random 
import yaml
from yaml.loader import SafeLoader

try:
    # --- Importaciones Críticas ---
    from PIL import Image
    import fitz  # PyMuPDF
    from pptx import Presentation
    import pandas as pd
    import google.generativeai as genai
    import plotly.graph_objects as go
    import firebase_admin
    from firebase_admin import credentials, firestore
    import streamlit_authenticator as stauth
    import bcrypt
    # Importación específica para compatibilidad con versión 0.3.3
    from streamlit_authenticator.utilities.hasher import Hasher 
except ImportError as e:
    st.error("Error crítico de dependencias.")
    st.code(f"Error: {e}")
    st.stop()

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Med-Flash AI",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed", 
)

# --- FRASES MOTIVACIONALES ---
STOIC_QUOTES = [
    "“El obstáculo es el camino.” — Marco Aurelio",
    "“La dificultad es lo que despierta al genio.” — Séneca",
    "“No es que tengamos poco tiempo, sino que perdemos mucho.” — Séneca",
    "“La excelencia es un hábito, no es un acto.” — Aristóteles",
    "“Un gramo de práctica vale más que una tonelada de teoría.”",
    "“El éxito es la suma de pequeños esfuerzos repetidos día tras día.” — Robert Collier"
]

# --- VÍNCULOS VISUALES DINÁMICOS (EXPANDIDO) ---
# Define iconos y colores para sistemas y temas moleculares
SYSTEM_VISUALS = {
    # Sistemas Corporales
    "Cardiovascular": {"icon": "❤️", "color": "#FF5757"},
    "Respiratorio": {"icon": "🫁", "color": "#46B9C7"},
    "Nervioso Central": {"icon": "🧠", "color": "#A67CEF"},
    "Nervioso Periférico": {"icon": "⚡", "color": "#FFD700"},
    "Digestivo": {"icon": "🍔", "color": "#FFB347"},
    "Renal (Urinario)": {"icon": "💧", "color": "#5C94FF"},
    "Musculoesquelético": {"icon": "💪", "color": "#90EE90"},
    "Endocrino": {"icon": "🧬", "color": "#FF69B4"},
    "Hematológico": {"icon": "🩸", "color": "#DC143C"},
    "Inmunológico": {"icon": "🛡️", "color": "#1E90FF"},
    "Reproductivo": {"icon": "🤰", "color": "#F5A6C1"},
    # Bioquímica y Celular
    "Metabolismo": {"icon": "🔥", "color": "#FF8C00"},
    "Enzimas/Proteínas": {"icon": "🧩", "color": "#32CD32"},
    "Genética/ADN": {"icon": "🧬", "color": "#8A2BE2"},
    "Biología Celular": {"icon": "🦠", "color": "#20B2AA"},
    # Farmacología
    "Farmacocinética": {"icon": "📈", "color": "#FFD700"},
    "Farmacodinámica": {"icon": "🎯", "color": "#FF4500"},
    "Antibióticos": {"icon": "💊", "color": "#00CED1"},
    # General
    "General": {"icon": "📚", "color": "#E0E0E0"},
    "Otro": {"icon": "❓", "color": "#4A4A4A"},
    "Seleccionar Sistema": {"icon": "🩺", "color": "#F5A6C1"},
}

# --- LÓGICA DE DEPENDENCIAS (MATERIA -> TEMAS) ---
MATERIAS = [
    "Seleccionar Materia", "Anatomía", "Fisiología", "Patología", "Semiología", # Clínicas
    "Bioquímica", "Genética", "Biología Celular", # Moleculares
    "Farmacología", "Microbiología", # Terapéutica/Bugs
    "Pediatría", "Neurología", "Cardiología", "Medicina Interna" # Especialidades
]

# Listas base
SISTEMAS_CUERPO = [
    "Cardiovascular", "Respiratorio", "Nervioso Central", "Nervioso Periférico", 
    "Digestivo", "Renal (Urinario)", "Musculoesquelético", "Endocrino", 
    "Hematológico", "Inmunológico", "Reproductivo", "General"
]

# Diccionario de mapeo: Qué temas mostrar según la materia
TOPICOS_POR_MATERIA = {
    "Bioquímica": ["Metabolismo", "Enzimas/Proteínas", "Genética/ADN", "General"],
    "Genética": ["Genética/ADN", "Biología Celular", "General"],
    "Biología Celular": ["Biología Celular", "Genética/ADN", "Metabolismo"],
    "Farmacología": ["Farmacocinética", "Farmacodinámica", "Antibióticos"] + SISTEMAS_CUERPO,
    "Microbiología": ["Antibióticos", "Inmunológico", "General"],
    # Para las demás (Anatomía, Fisiología, etc.) usamos los sistemas del cuerpo por defecto
    "DEFAULT": SISTEMAS_CUERPO
}

# --- ESTILOS CSS ---
st.markdown("""
<style>
    :root {
        --primary-color: #F5A6C1; 
        --accent-gold: #FFD700; 
        --delete-color: #DC143C; 
        --text-color: #4A4A4A; 
        --dark-bg: #1A1A1A; 
        --dark-text: #F0F0F0; 
    }
    body { background-color: var(--dark-bg); color: var(--dark-text); }
    .stApp { background-color: var(--dark-bg); }
    
    /* Tarjetas */
    .flashcard {
        background-color: #2F2F2F; 
        border-radius: 16px;
        padding: 24px;
        margin: 20px 0;
        box-shadow: 0 8px 16px rgba(0,0,0,0.6);
        border: 2px solid var(--accent-gold);
        color: var(--dark-text); 
    }
    
    /* Feedback Visual Rico */
    .feedback-correct {
        background-color: #384238; border: 2px solid #5cb85c; border-radius: 12px; padding: 16px; margin-top: 10px; color: #E6F7E6;
    }
    .feedback-incorrect {
        background-color: #423838; border: 2px solid #d9534f; border-radius: 12px; padding: 16px; margin-top: 10px; color: #F7E6E6;
    }
    .feedback-explanation {
        background-color: #2D333B; /* Tono gris azulado técnico */
        border-left: 4px solid #5bc0de; 
        border-radius: 8px;
        padding: 20px;
        margin-top: 15px;
        color: #E6F7F7;
        font-family: 'Segoe UI', sans-serif;
    }
    
    /* Doodle Container */
    .doodle-container {
        width: 100%; height: 150px; background-color: #2F2F2F; 
        border-radius: 16px; display: flex; flex-direction: column; 
        align-items: center; justify-content: center; margin-bottom: 20px; padding: 10px;
        border: 4px solid var(--system-color, var(--accent-gold));
    }
    .doodle-container .system-icon { font-size: 4rem; line-height: 1; text-shadow: 0 0 5px rgba(255, 215, 0, 0.8); }
    .doodle-container .system-text { color: var(--dark-text); font-weight: bold; font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

# --- Funciones de Extracción ---
def extraer_texto_pdf(file_stream):
    try:
        doc = fitz.open(stream=file_stream.read(), filetype="pdf")
        texto = ""
        for page in doc: texto += page.get_text()
        doc.close()
        return texto
    except Exception as e: return f"Error PDF: {e}"

def extraer_texto_pptx(file_stream):
    try:
        prs = Presentation(file_stream)
        texto = ""
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"): texto += shape.text + "\n"
        return texto
    except Exception as e: return f"Error PPTX: {e}"

# --- Lógica de Estado ---
if 'page' not in st.session_state: st.session_state.page = "Cargar Contenido"
if 'extracted_content' not in st.session_state: st.session_state.extracted_content = None
if 'current_exam' not in st.session_state: st.session_state.current_exam = None
if 'current_question_index' not in st.session_state: st.session_state.current_question_index = 0
if 'user_answer' not in st.session_state: st.session_state.user_answer = None
if 'show_explanation' not in st.session_state: st.session_state.show_explanation = False
if 'exam_results' not in st.session_state: st.session_state.exam_results = []
if "authentication_status" not in st.session_state: st.session_state.authentication_status = None
if "user_level" not in st.session_state: st.session_state.user_level = "Nivel 1 (Novato)"
if "materia_actual" not in st.session_state: st.session_state.materia_actual = MATERIAS[0]
if "sistema_actual" not in st.session_state: st.session_state.sistema_actual = "General"

def restart_exam():
    st.session_state.current_exam = None
    st.session_state.current_question_index = 0
    st.session_state.user_answer = None
    st.session_state.show_explanation = False
    st.session_state.exam_results = []

def go_to_next_question():
    st.session_state.current_question_index += 1
    st.session_state.user_answer = None
    st.session_state.show_explanation = False

# --- API & Database ---
@st.cache_resource
def init_firebase():
    try:
        if "FIREBASE_SERVICE_ACCOUNT" not in st.secrets: return None
        cred_json = json.loads(st.secrets["FIREBASE_SERVICE_ACCOUNT"])
        cred = credentials.Certificate(cred_json)
        if not firebase_admin._apps: firebase_admin.initialize_app(cred)
        return firestore.client()
    except Exception as e: return None

db = init_firebase()

def check_api_key():
    return "GOOGLE_API_KEY" in st.secrets and st.secrets["GOOGLE_API_KEY"]

api_key_disponible = check_api_key()
gemini_model = None
if api_key_disponible:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    gemini_model = genai.GenerativeModel(model_name="gemini-2.5-flash-preview-09-2025")

# --- Funciones Usuario (Simplificadas) ---
def get_all_users_credentials():
    if not db: return {} # Retorno vacío si no hay DB
    try:
        users_ref = db.collection('usuarios')
        docs = users_ref.stream()
        usernames_dict = {}
        for doc in docs:
            data = doc.to_dict()
            usernames_dict[doc.id] = data
        return {'usernames': usernames_dict}
    except: return {}

def register_new_user(name, email, username, password):
    if not db: return "Error DB"
    try:
        doc_ref = db.collection('usuarios').document(username)
        if doc_ref.get().exists: return "exists"
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        doc_ref.set({'name': name, 'email': email, 'password': hashed_pw, 'level': "Nivel 1 (Novato)", 'xp': 0})
        return "success"
    except Exception as e: return str(e)

def get_user_progress(username):
    if not db: return "Nivel 1 (Novato)", 0
    try:
        doc = db.collection('usuarios').document(username).get()
        if doc.exists: return doc.get('level'), doc.get('xp')
    except: pass
    return "Nivel 1 (Novato)", 0

def update_user_level(username, passed):
    if not db: return None, None
    try:
        doc_ref = db.collection('usuarios').document(username)
        data = doc_ref.get().to_dict()
        lvl = data.get('level', "Nivel 1 (Novato)")
        xp = data.get('xp', 0)
        levels = ["Nivel 1 (Novato)", "Nivel 2 (Estudiante)", "Nivel 3 (Interno)", "Nivel 4 (Residente)", "Nivel 5 (Especialista)"]
        new_lvl = lvl
        msg = ""
        if passed:
            xp += 10
            idx = levels.index(lvl) if lvl in levels else 0
            if idx < 4: 
                new_lvl = levels[idx+1]
                msg = f"¡Nivel UP! Ahora eres: {new_lvl} 🌟"
        doc_ref.update({'level': new_lvl, 'xp': xp})
        return new_lvl, msg
    except: return None, None

def get_user_decks(username):
    if not db: return {}
    try:
        decks = db.collection('usuarios').document(username).collection('mazos').stream()
        return {d.id: d.to_dict() for d in decks}
    except: return {}

def save_user_deck(username, name, content, mat, sis):
    if not db: return False
    try:
        db.collection('usuarios').document(username).collection('mazos').document(name).set({
            'preguntas': content, 'materia': mat, 'sistema': sis, 'creado': firestore.SERVER_TIMESTAMP
        })
        return True
    except: return False

def delete_user_deck(username, name):
    if not db: return False
    try:
        db.collection('usuarios').document(username).collection('mazos').document(name).delete()
        return True
    except: return False

# --- AUTHENTICATOR SETUP ---
credentials_data = get_all_users_credentials()
# IMPORTANTE: Configuración compatible con versión 0.3.3
config = {
    'credentials': credentials_data,
    'cookie': {'expiry_days': 30, 'key': 'medflash_key', 'name': 'medflash_cookie'},
    'preauthorized': {'emails': []}
}
authenticator = stauth.Authenticate(
    config['credentials'], config['cookie']['name'], config['cookie']['key'], 
    config['cookie']['expiry_days'], config['preauthorized']['emails']
)


# --- MAIN APP ---
if st.session_state["authentication_status"] is None:
    st.title("Med-Flash AI 🧬")
    tab1, tab2 = st.tabs(["Login", "Registro"])
    with tab1: authenticator.login('main')
    with tab2:
        with st.form("reg"):
            u = st.text_input("Usuario"); p = st.text_input("Pass", type="password"); n = st.text_input("Nombre"); e = st.text_input("Email")
            if st.form_submit_button("Registrar"):
                res = register_new_user(n, e, u, p)
                if res == "success": st.success("¡Registrado! Inicia sesión."); st.rerun()
                else: st.error(res)

elif st.session_state["authentication_status"]:
    username = st.session_state.get("username")
    name = st.session_state.get("name")
    
    # Sync inicial
    if st.session_state.get("last_login") != username:
        l, x = get_user_progress(username)
        st.session_state.user_level = l
        st.session_state.flashcard_library = get_user_decks(username)
        st.session_state.last_login = username

    # Iconos Dinámicos Seguros
    current_system = st.session_state.sistema_actual
    visuals = SYSTEM_VISUALS.get(current_system, SYSTEM_VISUALS["Otro"])
    
    with st.sidebar:
        st.title("Med-Flash AI")
        st.write(f"Dr. {name} | {st.session_state.user_level}")
        authenticator.logout('Salir', 'sidebar')
        st.markdown("---")
        st.markdown(f"""
        <div class="doodle-container" style="--system-color: {visuals['color']};">
            <span class="system-icon">{visuals['icon']}</span>
            <span class="system-text">{st.session_state.materia_actual}</span>
            <span class="system-text">{current_system}</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        if st.button("1. Cargar Contenido", use_container_width=True): st.session_state.page = "Cargar Contenido"
        if st.button("2. Generar Examen", use_container_width=True): st.session_state.page = "Generar Examen"
        if st.button("3. Estudiar", use_container_width=True): st.session_state.page = "Mi Progreso"

    # --- PÁGINAS ---
    
    if st.session_state.page == "Cargar Contenido":
        st.header("1. Contexto Clínico 📚")
        c1, c2 = st.columns(2)
        with c1:
            mat = st.selectbox("Materia:", MATERIAS)
            st.session_state.materia_actual = mat
        with c2:
            # LOGICA DE CASCADA: Filtrar temas según materia
            if mat in TOPICOS_POR_MATERIA: ops = TOPICOS_POR_MATERIA[mat]
            elif mat == "Seleccionar Materia": ops = ["Selecciona Materia Primero"]
            else: ops = TOPICOS_POR_MATERIA["DEFAULT"]
            
            sis = st.selectbox("Tema/Sistema:", ops)
            st.session_state.sistema_actual = sis
            
        st.divider()
        f = st.file_uploader("Sube PDF/PPTX/TXT", ["pdf", "pptx", "txt"])
        if st.button("Procesar Archivo", type="primary"):
            if f:
                with st.spinner("Leyendo..."):
                    if f.type == "application/pdf": t = extraer_texto_pdf(f)
                    elif "presentation" in f.type: t = extraer_texto_pptx(f)
                    else: t = f.read().decode("utf-8")
                    st.session_state.extracted_content = t
                    st.success("Texto extraído. Ve a 'Generar Examen'.")

    elif st.session_state.page == "Generar Examen":
        st.header("2. Generar Flashcards Visuales 🧠")
        if not st.session_state.extracted_content: st.warning("Carga un archivo primero."); st.stop()
        
        d_name = st.text_input("Nombre del Mazo (ej. Parcial Bioquímica)")
        num = st.slider("Preguntas", 1, 10, 5)
        
        if st.button("🚀 Crear con Feedback Visual", type="primary"):
            if not d_name: st.error("Pon un nombre al mazo."); st.stop()
            restart_exam()
            
            # PROMPT AVANZADO PARA RESPUESTAS VISUALES
            prompt = [
                f"Eres profesor experto en {st.session_state.materia_actual} y diseñador instruccional médico.",
                f"Tema: {st.session_state.sistema_actual}. Nivel: {st.session_state.user_level}.",
                f"Texto base:\n{st.session_state.extracted_content[:10000]}...", # Limitamos caracteres por si acaso
                f"Crea {num} preguntas de opción múltiple.",
                "IMPORTANTE - FEEDBACK VISUAL:",
                "En el campo 'explicacion', NO uses texto plano.",
                "Usa MARKDOWN para crear:",
                "- Tablas comparativas.",
                "- Listas con emojis (🦠, 💊, ⚡).",
                "- Diagramas de flujo de texto (A -> B -> C).",
                "- Esquemas anatómicos simples ( [Órgano] === [Tejido] ).",
                "Formato JSON array estricto:",
                """[{"pregunta": "...", "opciones": {"A": "...", "B": "...", "C": "...", "D": "..."}, "respuesta_correcta": "A", "explicacion": "Markdown rico aquí..."}]"""
            ]
            
            with st.spinner("Generando explicaciones gráficas..."):
                try:
                    res = gemini_model.generate_content(prompt)
                    txt = res.text.replace('```json', '').replace('```', '')
                    data = json.loads(txt[txt.find('['):txt.rfind(']')+1])
                    
                    if save_user_deck(username, d_name, data, st.session_state.materia_actual, st.session_state.sistema_actual):
                        st.session_state.flashcard_library[d_name] = data
                        st.success("Mazo creado. Vamos a estudiar."); st.balloons()
                except Exception as e: st.error(f"Error IA: {e}")

    elif st.session_state.page == "Mi Progreso":
        st.header("3. Biblioteca de Estudio 🏆")
        decks = st.session_state.get("flashcard_library", {})
        
        if not decks: st.info("No tienes mazos."); st.stop()
        
        opts = [f"{k} [{v.get('materia','?')}]" for k,v in decks.items()]
        sel = st.selectbox("Selecciona Mazo", opts)
        real_name = sel.split(" [")[0]
        
        c1, c2 = st.columns([1, 4])
        if c1.button("Estudiar"):
            st.session_state.current_exam = decks[real_name]
            st.session_state.current_exam['name'] = real_name
            st.session_state.page = "Estudiar"
            st.rerun()
        if c1.button("Borrar"):
             delete_user_deck(username, real_name)
             del st.session_state.flashcard_library[real_name]
             st.rerun()

    elif st.session_state.page == "Estudiar":
        exam = st.session_state.current_exam.get('preguntas', [])
        idx = st.session_state.current_question_index
        
        if st.button("⬅ Volver"): st.session_state.page = "Mi Progreso"; restart_exam(); st.rerun()
        
        if idx < len(exam):
            q = exam[idx]
            st.markdown(f"### Pregunta {idx+1}/{len(exam)}")
            st.markdown(f'<div class="flashcard"><h5>{q["pregunta"]}</h5></div>', unsafe_allow_html=True)
            
            ops = list(q['opciones'].values())
            sel = st.radio("Tu respuesta:", ops, key=f"q{idx}", disabled=st.session_state.show_explanation)
            
            if st.button("Responder") and sel:
                st.session_state.show_explanation = True
                cor_ltr = q['respuesta_correcta']
                cor_txt = q['opciones'][cor_ltr]
                is_ok = (sel == cor_txt)
                if len(st.session_state.exam_results) <= idx:
                    st.session_state.exam_results.append({'ok': is_ok, 'sel': sel, 'cor': cor_txt})
                st.rerun()

            if st.session_state.show_explanation:
                res = st.session_state.exam_results[idx]
                if res['ok']: st.markdown('<div class="feedback-correct">✅ Correcto</div>', unsafe_allow_html=True)
                else: st.markdown(f'<div class="feedback-incorrect">❌ Error. Era: {res["cor"]}</div>', unsafe_allow_html=True)
                
                # AQUÍ SE MUESTRA EL CONTENIDO RICO GENERADO POR IA
                st.markdown(f'<div class="feedback-explanation">{q["explicacion"]}</div>', unsafe_allow_html=True)
                
                if st.button("Siguiente ➡"): go_to_next_question(); st.rerun()
        
        else:
            st.balloons()
            score = sum(1 for r in st.session_state.exam_results if r['ok'])
            final = (score / len(exam)) * 100
            st.metric("Resultado Final", f"{final:.0f}%")
            nl, msg = update_user_level(username, final >= 80)
            if msg: st.success(msg)
            st.session_state.user_level = nl if nl else st.session_state.user_level

elif st.session_state["authentication_status"] is False:
    st.error("Credenciales inválidas")
