import streamlit as st
import pandas as pd
import base64
import requests
import os

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
    /* Pie de página */
    .footer { 
        position: fixed; 
        right: 150px; 
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

# SINCRONIZAR CON GITHUB
def actualizar_en_github(archivo_objeto):
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{DB_FILE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    res_get = requests.get(url, headers=headers)
    sha = res_get.json().get('sha') if res_get.status_code == 200 else None
    
    contenido_b64 = base64.b64encode(archivo_objeto.getvalue()).decode()
    
    payload = {
        "message": "Actualización de base de datos",
        "content": contenido_b64,
        "branch": "main"
    }
    if sha:
        payload["sha"] = sha
        
    res_put = requests.put(url, json=payload, headers=headers)
    return res_put.status_code in [200, 201]

# CARGAR DATOS
def cargar_datos(ruta):
    try:
        df = pd.read_excel(ruta)
        df.columns = df.columns.str.strip()
        return df.fillna("N/A")
    except:
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
                with open(DB_FILE, "wb") as f:
                    f.write(archivo_nuevo.getbuffer())
                
                if actualizar_en_github(archivo_nuevo):
                    st.success("Base guardada.")
                    st.rerun()
    
    st.markdown("---")
    with st.expander("Información"):
        st.write("Versión: 2.0")
        st.write("Firma técnica: ")
        st.write("**INBAL | EEBM**")

# LÓGICA DE CONSULTA
st.title("Módulo de Consulta de Plazas")

if os.path.exists(DB_FILE):
    data = cargar_datos(DB_FILE)
    st.caption(f"Archivo: **{DB_FILE}**")
    
    tipo_busqueda = st.radio("**Seleccione el método de búsqueda:**", ["Código INBAL", "Código SHCP"], horizontal=True)
    col_filtro = "CÓDIGO INBAL" if tipo_busqueda == "Código INBAL" else "CÓDIGO SHCP"
    
    busqueda = st.text_input(f" Ingrese el {tipo_busqueda}:").strip().upper()

    if busqueda:
        if col_filtro in data.columns:
            res = data[data[col_filtro].astype(str).str.contains(busqueda, na=False)]
            if not res.empty:
                st.markdown("---")
                st.dataframe(res, use_container_width=True, hide_index=True)
            else:
                st.warning("No se encontró información.")
else:
    st.info("El sistema no tiene datos cargados.")

# Pie de página 
st.markdown('<div class="footer">INBAL</div>', unsafe_allow_html=True)

