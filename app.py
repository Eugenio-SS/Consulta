import streamlit as st
import pandas as pd
import base64
import requests
import io

# CONFIGURACIÓN E IDENTIDAD VISUAL
st.set_page_config(page_title="Módulo de Consulta INBAL", page_icon="🏛️", layout="wide")

# ESTILOS FORZADOS (Botón Guinda, Texto Blanco y Footer)
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    [data-testid="stMain"] p, [data-testid="stMain"] span, [data-testid="stMain"] label, [data-testid="stMain"] div, [data-testid="stMain"] h1, [data-testid="stMain"] h2, [data-testid="stMain"] h3 {
        color: #1A1A1A !important;
    }
    [data-testid="stSidebar"] { background-color: #4A141C !important; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] div, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #FFFFFF !important;
    }
    
    /* BOTÓN GUINDA CON TEXTO BLANCO FORZADO */
    div.stButton > button {
        background-color: #4A141C !important;
        color: white !important;
        border: 1px solid #4A141C !important;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold !important;
    }
    div.stButton > button p {
        color: white !important; /* Fuerza el color del texto dentro del botón */
    }
    div.stButton > button:hover {
        background-color: #631C26 !important;
        color: white !important;
    }

    .footer { 
        position: fixed; 
        left: 20px; 
        bottom: 20px; 
        text-align: left; 
        color: #555555 !important; 
        font-size: 12px; 
        z-index: 100; 
        font-weight: bold; 
    }
    </style>
    """, unsafe_allow_html=True)

# CARGAR CONFIGURACIÓN DESDE SECRETS
try:
    G_TOKEN = st.secrets["GITHUB_TOKEN"]
    ADMIN_PWD = st.secrets["ADMIN_PASSWORD"]
except:
    st.error("Error: Configura los Secrets en Streamlit.")
    st.stop()

GITHUB_USER = "Eugenio-SS"
GITHUB_REPO = "Consulta"
DB_FILE = "COMPENDIO.xlsx"

# FUNCIÓN CARGAR TODAS LAS HOJAS
def cargar_datos_seguro():
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{DB_FILE}"
    headers = {"Authorization": f"Bearer {G_TOKEN}"}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            content = base64.b64decode(res.json()['content'])
            # LEER TODAS LAS HOJAS
            excel_file = pd.ExcelFile(io.BytesIO(content))
            lista_dfs = []
            for sheet in excel_file.sheet_names:
                temp_df = pd.read_excel(excel_file, sheet_name=sheet)
                lista_dfs.append(temp_df)
            
            # CONCATENAR TODAS LAS HOJAS EN UNA SOLA TABLA
            df_final = pd.concat(lista_dfs, ignore_index=True)
            return df_final.fillna("N/A")
    except Exception as e:
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

# LÓGICA DE RESETEO
if 'termino_busqueda' not in st.session_state:
    st.session_state.termino_busqueda = ""

def limpiar_campos():
    st.session_state.termino_busqueda = ""

# PANEL LATERAL
with st.sidebar:
    st.header("Seguridad")
    password = st.text_input("Clave de Administrador", type="password")
    if password == ADMIN_PWD:
        st.success("Acceso Autorizado")
        archivo_nuevo = st.file_uploader("Actualizar Base Excel", type=["xlsx", "xls"])
        if archivo_nuevo:
            if actualizar_en_github(archivo_nuevo):
                st.success("Base cargada correctamente")
                st.rerun()
    elif password:
        st.error("Contraseña Incorrecta")

    st.markdown("---")
    with st.expander("Información"):
        st.write("Versión: 2.2")
        st.write("**INBAL | EEBM**")

# LÓGICA DE CONSULTA
st.title("Módulo de Consulta de Plazas")

data = cargar_datos_seguro()

if data is not None:
    st.caption(f"Total de registros cargados: {len(data)} (Todas las hojas)")
    tipo = st.radio("**Seleccione el método de búsqueda:**", ["Código INBAL", "Código SHCP"], horizontal=True)
    col_filtro = "CÓDIGO INBAL" if tipo == "Código INBAL" else "CÓDIGO SHCP"
    
    # Input de búsqueda conectado al estado
    busqueda = st.text_input(f"Ingrese el {tipo}:", value=st.session_state.termino_busqueda, key="input_text").strip().upper()
    st.session_state.termino_busqueda = busqueda

    # BOTÓN DE LIMPIAR
    if st.button("Limpiar datos", on_click=limpiar_campos):
        st.rerun()

    if st.session_state.termino_busqueda:
        if col_filtro in data.columns:
            res = data[data[col_filtro].astype(str).str.contains(st.session_state.termino_busqueda, na=False)]
            if not res.empty:
                st.dataframe(res, use_container_width=True, hide_index=True)
            else:
                st.warning("No se encontró información.")
        else:
            st.error(f"La columna '{col_filtro}' no existe en el archivo cargado.")
else:
    st.info("Cargue el archivo Excel para iniciar.")

st.markdown('<div class="footer">INBAL</div>', unsafe_allow_html=True)
