import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(
    page_title="Módulo de Consulta INBAL", 
    page_icon="🏛️", 
    layout="wide"
)

# Estilo CSS Corregido
st.markdown("""
    <style>
    /* 1. Fondo general blanco */
    .stApp { 
        background-color: #FFFFFF !important; 
    }
    
    /* 2. TEXTO NEGRO SOLO EN EL CONTENIDO PRINCIPAL (FONDO BLANCO) */
    [data-testid="stMain"] p, 
    [data-testid="stMain"] span, 
    [data-testid="stMain"] label, 
    [data-testid="stMain"] div,
    [data-testid="stMain"] h1,
    [data-testid="stMain"] h2,
    [data-testid="stMain"] h3 {
        color: #1A1A1A !important;
    }

    /* 3. BARRA LATERAL GUINDA CON TEXTO BLANCO */
    [data-testid="stSidebar"] {
        background-color: #4A141C !important;
    }
    
    /* Forzar texto blanco solo dentro de la barra lateral */
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #FFFFFF !important;
    }

    /* 4. AJUSTES ESPECÍFICOS */
    /* Títulos en Guinda para que resalten sobre el blanco */
    [data-testid="stMain"] h1, [data-testid="stMain"] h3 {
        color: #4A141C !important;
    }

    /* Métricas en Dorado */
    [data-testid="stMetricValue"] {
        color: #BC955C !important;
        font-weight: bold !important;
    }
    [data-testid="stMetricLabel"] {
        color: #4A141C !important;
    }

    /* Marca de autor */
    .footer {
        position: fixed;
        right: 15px;
        bottom: 15px;
        text-align: right;
        color: #555555 !important;
        font-size: 12px;
        z-index: 100;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. INICIALIZACIÓN DE DATOS
if 'data' not in st.session_state:
    st.session_state.data = None

# 3. ENCABEZADO
st.title("Módulo de Consulta de Plazas")
st.markdown("### Información de Percepciones y Puestos")
st.write("Seleccione el método de búsqueda y escriba el código correspondiente.")

# 4. PANEL LATERAL
with st.sidebar:
    st.header("Seguridad")
    password = st.text_input("Clave de Administrador", type="password")
    
    if password == "ADMIN2026": 
        st.success("Acceso Autorizado")
        archivo = st.file_uploader("Actualizar Base Excel (.xlsx, .xls)", type=["xlsx", "xls"])
        
        if archivo:
            try:
                engine = 'xlrd' if archivo.name.endswith('.xls') else 'openpyxl'
                df_temp = pd.read_excel(archivo, engine=engine)
                df_temp.columns = df_temp.columns.str.strip()
                st.session_state.data = df_temp
                st.success("Base cargada con éxito")
            except Exception as e:
                st.error(f"Error al leer el archivo: {e}")
    
    st.markdown("---")
    with st.expander("Información del Sistema"):
        st.write("Versión: 1.0")
        st.write("Firma técnica: **Eduardo Eugenio Badillo Melo**")

# 5. LÓGICA DE CONSULTA
if st.session_state.data is not None:
    tipo_busqueda = st.radio(
        "**Paso 1: Seleccione el método de búsqueda**",
        ["Código INBAL", "Código SHCP"],
        horizontal=True
    )

    columna_filtro = "CÓDIGO INBAL" if tipo_busqueda == "Código INBAL" else "CÓDIGO SHCP"
    
    busqueda = st.text_input(f"**Paso 2: Ingrese el {tipo_busqueda} a consultar:**").strip().upper()

    if busqueda:
        df = st.session_state.data
        if columna_filtro in df.columns:
            res = df[df[columna_filtro].astype(str).str.contains(busqueda, na=False)]

            if not res.empty:
                st.markdown("---")
                st.dataframe(res, use_container_width=True, hide_index=True)
                
                st.markdown("### Resumen de la Plaza (Registro más reciente)")
                f = res.iloc[0] 
                c1, c2, c3, c4 = st.columns(4)
                
                c1.metric("Sueldo Base", f"${f.get('SUELDO BASE', 0):,.2f}")
                c2.metric("Despensa", f"${f.get('Despensa mensual', 0):,.2f}")
                c3.metric("Pasajes", f"${f.get('Ayuda para Pasajes', 0):,.2f}")
                c4.metric("TOTAL MENSUAL", f"${f.get('PERCEPCIÓN MENSUAL TOTAL', 0):,.2f}")
                
                st.info(f"**Puesto:** {f.get('DENOMINACIÓN PUESTOS INBAL', 'No especificado')}")
            else:
                st.warning(f"No se encontró información para el {tipo_busqueda}: {busqueda}")
        else:
            st.error(f"La columna '{columna_filtro}' no existe en el Excel cargado.")
else:
    st.info("El sistema está listo. El administrador debe cargar el archivo Excel desde el panel izquierdo.")

# 6. MARCA DE AUTOR
st.markdown("""
    <div class="footer">
        INBAL | EEBM
    </div>
    """, unsafe_allow_html=True)
