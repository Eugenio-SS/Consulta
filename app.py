import streamlit as st
import pandas as pd
import base64
import requests
import io

# 1. CONFIGURACIÓN E IDENTIDAD VISUAL
st.set_page_config(page_title="Módulo de Consulta INBAL", page_icon="🏛️", layout="wide")

st.markdown("""
    <style>

    .stApp { background-color: #FFFFFF !important; }
    
    /* Forzar texto oscuro en área principal para que sea visible */
    [data-testid="stMain"] p, [data-testid="stMain"] span, [data-testid="stMain"] label, 
    [data-testid="stMain"] div, [data-testid="stMain"] h1, [data-testid="stMain"] h2, [data-testid="stMain"] h3 {
        color: #1A1A1A !important;
    }


    [data-testid="stSidebar"] { background-color: #4A141C !important; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    
    /* Botón Guinda con texto blanco */
    div.stButton > button {
        background-color: #4A141C !important;
        color: white !important;
        border: 1px solid #4A141C !important;
        border-radius: 5px;
        font-weight: bold !important;
    }
    div.stButton > button p { color: white !important; }
    
    .footer { 
        position: fixed; left: 20px; bottom: 20px; text-align: left; 
        color: #555555 !important; font-size: 12px; font-weight: bold; 
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CONFIGURACIÓN DE ACCESO
try:
    G_TOKEN = st.secrets["GITHUB_TOKEN"]
    ADMIN_PWD = st.secrets["ADMIN_PASSWORD"]
except:
    st.error("Error: Configura GITHUB_TOKEN y ADMIN_PASSWORD en Secrets.")
    st.stop()

GITHUB_USER = "Eugenio-SS"
GITHUB_REPO = "Consulta"
DB_FILE = "COMPENDIO.xlsx"

# 3. FUNCIONES DE DATOS 
@st.cache_data(show_spinner=False)
def cargar_datos_por_hoja():
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{DB_FILE}"
    headers = {"Authorization": f"Bearer {G_TOKEN}"}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            content = base64.b64decode(res.json()['content'])
            return pd.read_excel(io.BytesIO(content), sheet_name=None)
    except:
        return None
    return None

def actualizar_en_github(archivo_objeto):
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{DB_FILE}"
    headers = {"Authorization": f"Bearer {G_TOKEN}"}
    res_get = requests.get(url, headers=headers)
    sha = res_get.json().get('sha') if res_get.status_code == 200 else None
    contenido_b64 = base64.b64encode(archivo_objeto.getvalue()).decode()
    payload = {"message": "Update DB", "content": contenido_b64, "branch": "main"}
    if sha: payload["sha"] = sha
    res_put = requests.put(url, json=payload, headers=headers)
    return res_put.status_code in [200, 201]

# 4. LÓGICA DE RESETEO 
if "query_text" not in st.session_state:
    st.session_state.query_text = ""

def borrar_busqueda():
    st.session_state.query_text = ""

# 5. PANEL LATERAL
with st.sidebar:
    st.header("Seguridad")
    pwd = st.text_input("Clave de Administrador", type="password")
    if pwd == ADMIN_PWD:
        st.success("Acceso Autorizado")
        archivo_nuevo = st.file_uploader("Actualizar Base Excel", type=["xlsx", "xls"])
        if archivo_nuevo:
            with st.spinner("Sincronizando..."):
                if actualizar_en_github(archivo_nuevo):
                    st.success("¡Base cargada!")
                    st.cache_data.clear()
                    st.rerun()
    elif pwd:
        st.error("Contraseña Incorrecta")
    
    st.markdown("---")
    # Expander recuperado
    with st.expander("Información"):
        st.write("Versión: 2.2.2")
        st.write("Firma técnica: ")
        st.write("**INBAL | EEBM**")

# 6. INTERFAZ DE CONSULTA
st.title("Módulo de Consulta de Plazas")

dict_hojas = cargar_datos_por_hoja()

if dict_hojas:
    st.caption(f"Archivo: {DB_FILE}")
    
    metodo = st.radio("**Seleccione el método:**", ["Código INBAL", "Código SHCP"], horizontal=True)
    col_busqueda = "CÓDIGO INBAL" if metodo == "Código INBAL" else "CÓDIGO SHCP"

    # Input controlado
    texto_usuario = st.text_input(f"Ingrese el {metodo}:", key="query_text").strip().upper()

    # Botón Limpiar 
    st.button("Limpiar datos", on_click=borrar_busqueda)

    if texto_usuario:
        encontrado = False
        for nombre_hoja, df in dict_hojas.items():
            if col_busqueda in df.columns:
                filtro = df[df[col_busqueda].astype(str).str.contains(texto_usuario, na=False)]
                if not filtro.empty:
                    st.markdown(f"**Resultados en pestaña: {nombre_hoja}**")
                    # Mostrar tabla sin columnas extra de otras hojas
                    st.dataframe(filtro.fillna("N/A"), use_container_width=True, hide_index=True)
                    encontrado = True
        
        if not encontrado:
            st.warning(f"No se encontró el código '{texto_usuario}'.")
else:
    st.info("Cargue el archivo Excel para iniciar.")

st.markdown('<div class="footer">INBAL</div>', unsafe_allow_html=True)

