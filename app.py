import streamlit as st
import pandas as pd
import os

# 1. CONFIGURACIÓN E IDENTIDAD VISUAL
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
    .footer { position: fixed; right: 15px; bottom: 15px; text-align: right; color: #555555 !important; font-size: 12px; z-index: 100; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# Nombre del archivo que servirá como base de datos permanente
DB_FILE = "COMPENDIO.xlsx"

# 2. FUNCIÓN PARA CARGAR DATOS
def cargar_datos(camino):
    try:
        df = pd.read_excel(camino)
        df.columns = df.columns.str.strip()
        return df.fillna("N/A")
    except Exception as e:
        return None

# 3. PANEL LATERAL (ADMINISTRACIÓN)
with st.sidebar:
    st.header("Seguridad")
    password = st.text_input("Clave de Administrador", type="password")
    
    if password == "ADMIN2026": 
        st.success("Acceso Autorizado")
        archivo_nuevo = st.file_uploader("Subir nueva base para TODOS los usuarios", type=["xlsx", "xls"])
        
        if archivo_nuevo:
            # ESTA ES LA PARTE CLAVE: Guarda el archivo en el servidor permanentemente
            with open(DB_FILE, "wb") as f:
                f.write(archivo_nuevo.getbuffer())
            st.success(" Base de datos actualizada.")
            # Forzamos recarga de la aplicación para leer el nuevo archivo
            st.rerun()
    
    st.markdown("---")
    with st.expander("Información"):
        st.write("Versión: 1.0")
        st.write("Firma técnica: **Eduardo Eugenio Badillo Melo**")

# 4. LÓGICA DE CONSULTA
st.title("Módulo de Consulta de Plazas")
st.markdown("### Información de Percepciones y Puestos")

# Carga automática del archivo persistente
if os.path.exists(DB_FILE):
    data = cargar_datos(DB_FILE)
    
    tipo_busqueda = st.radio("**Seleccione el método de búsqueda:**", ["Código INBAL", "Código SHCP"], horizontal=True)
    col_filtro = "CÓDIGO INBAL" if tipo_busqueda == "Código INBAL" else "CÓDIGO SHCP"
    
    busqueda = st.text_input(f" Ingrese el {tipo_busqueda}:").strip().upper()

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
    st.info(" El administrador debe cargar el archivo inicial 'COMPENDIO.xlsx' desde el panel lateral.")

st.markdown('<div class="footer">INBAL | EEBM</div>', unsafe_allow_html=True)

