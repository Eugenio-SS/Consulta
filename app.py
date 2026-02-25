import streamlit as st
import pandas as pd
import base64
import requests
import os
import io

# CONFIGURACIÓN E IDENTIDAD VISUAL
st.set_page_config(page_title="Módulo de Consulta INBAL", page_icon="🏛️", layout="wide")

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
    .footer { 
        position: fixed; 
        right: 250px; 
        bottom: 20px; 
        text-align: right; 
        color: #555555 !important; 
        font-size: 12px; 
        z-index: 100; 
        font-weight: bold; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURACIÓN DE GITHUB ---
GITHUB_USER = "Eugenio-SS"
GITHUB_REPO = "Consulta"
GITHUB_TOKEN = "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"
DB_FILE = "COMPENDIO.xlsx"

# SINCRONIZAR A GITHUB
def actualizar_en_github(archivo_objeto):
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{DB_FILE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    res_get = requests.get(url, headers=headers)
    sha = res_get.json().get('sha') if res_get.status_code == 200 else None
    contenido_b64 = base64.b64encode(archivo_objeto.getvalue()).decode()
    payload = {"message": "Actualización de base de datos", "content": contenido_b64, "branch": "main"}
    if sha: payload["sha"] = sha
    res_put = requests.put(url, json=payload, headers=headers)
    return res_put.status_code in [200, 201]

# CARGAR DATOS (NUBE Y LOCAL)
def cargar_datos_seguro():
    # Intento 1: Buscar archivo local
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_excel(DB_FILE)
            return df.fillna("N/A")
        except: pass
    
    # Intento 2: Descargar de GitHub si no está local
    try:
        url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{DB_FILE}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            content = base64.b64decode(res.json()['content'])
            df = pd.read_excel(io.BytesIO(content))
            with open(DB_FILE, "wb") as f:
                f.write(content)
            return df.fillna("N/A")
    except:
        return None
    return None

# PANEL LATERAL (ADMINISTRACIÓN)
with st.sidebar:
    st.header("Seguridad")
    password = st.text_input("Clave de Administrador", type="password")
    if password == "ADMIN2026": 
        st.success("Acceso Autorizado")
        archivo_nuevo = st.file_uploader("Actualizar Base Excel", type=["xlsx", "xls"])
        if archivo_nuevo:
            with st.spinner("Guardando permanentemente..."):
                if actualizar_en_github(archivo_nuevo):
                    with open(DB_FILE, "wb") as f:
                        f.write(archivo_nuevo.getbuffer())
                    st.success(f"¡Archivo Base '{archivo_nuevo.name}' cargada!")
                    st.rerun()

    st.markdown("---")
    with st.expander("Información"):
        st.write("Versión: 2.1")
        st.write("Firma técnica: ")
        st.write("**INBAL | EEBM**")

# LÓGICA DE CONSULTA
st.title("Módulo de Consulta de Plazas")

data = cargar_datos_seguro()

if data is not None:
    st.caption(f"Consultando archivo actual: {DB_FILE}")
    tipo_busqueda = st.radio("**Seleccione el método de búsqueda:**", ["Código INBAL", "Código SHCP"], horizontal=True)
    col_filtro = "CÓDIGO INBAL" if tipo_busqueda == "Código INBAL" else "CÓDIGO SHCP"
    busqueda = st.text_input(f"Ingrese el {tipo_busqueda}:").strip().upper()

    if busqueda:
        if col_filtro in data.columns:
            res = data[data[col_filtro].astype(str).str.contains(busqueda, na=False)]
            if not res.empty:
                st.markdown("---")
                st.write(f"### Resultados para: {busqueda}")
                st.dataframe(res, use_container_width=True, hide_index=True)
            else:
                st.warning("No se encontró información.")
else:
    st.info("El sistema no tiene datos cargados.")

st.markdown('<div class="footer">INBAL</div>', unsafe_allow_html=True)
