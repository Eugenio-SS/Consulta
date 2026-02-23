import streamlit as st
import pandas as pd
import os
import glob

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

# 2. FUNCIÓN PARA ENCONTRAR Y CARGAR CUALQUIER EXCEL DISPONIBLE
def obtener_base_datos():
    # Busca cualquier archivo .xlsx o .xls en la carpeta actual
    archivos = glob.glob("*.xlsx") + glob.glob("*.xls")
    if archivos:
        # Toma el archivo más reciente (el último que se subió o modificó)
        archivo_reciente = max(archivos, key=os.path.getmtime)
        try:
            df = pd.read_excel(archivo_reciente)
            df.columns = df.columns.str.strip()
            return df.fillna("N/A"), archivo_reciente
        except:
            return None, None
    return None, None

# 3. PANEL LATERAL (ADMINISTRACIÓN)
with st.sidebar:
    st.header("Seguridad")
    password = st.text_input("Clave de Administrador", type="password")
    
    if password == "ADMIN2026": 
        st.success("Acceso Autorizado")
        archivo_nuevo = st.file_uploader("Subir nueva base (cualquier nombre)", type=["xlsx", "xls"])
        
        if archivo_nuevo:
            # Borramos archivos anteriores para que no se mezclen bases viejas
            viejos = glob.glob("*.xlsx") + glob.glob("*.xls")
            for v in viejos:
                try: os.remove(v)
                except: pass
            
            # Guardamos el nuevo con su nombre ORIGINAL
            with open(archivo_nuevo.name, "wb") as f:
                f.write(archivo_nuevo.getbuffer())
            st.success(f" ¡Archivo Base '{archivo_nuevo.name}' cargada !")
            st.rerun()
    
    st.markdown("---")
    with st.expander("Información"):
        st.write("Versión: 1.0")
        st.write(\n \n "INBAL" \n \n)
        st.write("")
        st.write("")
        st.write("Firma técnica: **Eduardo Eugenio Badillo Melo**")
        st.write("**Eduardo Eugenio Badillo Melo**")

# 4. LÓGICA DE CONSULTA
st.title("Módulo de Consulta de Plazas")

data, nombre_archivo = obtener_base_datos()

if data is not None:
    st.caption(f" Consultando archivo actual: **{nombre_archivo}**")
    
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
    st.info(" El sistema no tiene datos cargados. El administrador debe subir un Excel.")

st.markdown('<div class="footer">INBAL | EEBM</div>', unsafe_allow_html=True)



