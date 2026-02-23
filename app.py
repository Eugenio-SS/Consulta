import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN E IDENTIDAD VISUAL
st.set_page_config(
    page_title="Módulo de Consulta INBAL", 
    page_icon="🏛️", 
    layout="wide"
)

# Estilo CSS
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #4A141C !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    [data-testid="stMetricValue"] { color: #BC955C !important; }
    .footer {
        position: fixed;
        right: 10px;
        bottom: 10px;
        text-align: right;
        color: #888888;
        font-size: 11px;
        z-index: 100;
        font-family: sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. INICIALIZACIÓN
if 'data' not in st.session_state:
    st.session_state.data = None

# 3. ENCABEZADO
st.title("🏛️ Módulo de Consulta de Plazas")
st.subheader("Información de Percepciones y Puestos")
st.markdown("---")

# 4. PANEL LATERAL (ADMINISTRACIÓN)
with st.sidebar:
    st.header("Seguridad")
    password = st.text_input("Clave de Administrador", type="password")
    
    if password == "ADMIN2026": 
        st.success("Acceso Autorizado")
        archivo = st.file_uploader("Cargar Base Excel (.xlsx, .xls)", type=["xlsx", "xls"])
        
        if archivo:
            try:
                engine = 'xlrd' if archivo.name.endswith('.xls') else 'openpyxl'
                df_temp = pd.read_excel(archivo, engine=engine)
                df_temp.columns = df_temp.columns.str.strip()
                st.session_state.data = df_temp
                st.success("✅ Datos actualizados")
            except Exception as e:
                st.error(f"Error al leer: {e}")
    
    st.markdown("---")
    with st.expander("Información del Sistema"):
        st.write("Versión: 2.1")
        st.write("Firma técnica: **EEBM**")

# 5. LÓGICA DE CONSULTA (CON SELECCIÓN DE TIPO DE CÓDIGO)
if st.session_state.data is not None:
    # CUADROS DE SELECCIÓN PARA EL TIPO DE BÚSQUEDA
    tipo_busqueda = st.radio(
        "Seleccione el método de búsqueda:",
        ["Código INBAL", "Código SHCP"],
        horizontal=True
    )

    # El placeholder del buscador cambia según la opción seleccionada
    etiqueta = "CÓDIGO INBAL" if tipo_busqueda == "Código INBAL" else "CÓDIGO SHCP"
    
    busqueda = st.text_input(f"🔍 Ingrese el {etiqueta}:").strip().upper()

    if busqueda:
        df = st.session_state.data
        
        # Filtrado dinámico según la opción seleccionada
        # Buscamos en la columna exacta (asegúrate que en el Excel se llamen así)
        columna_a_buscar = "CÓDIGO INBAL" if tipo_busqueda == "Código INBAL" else "CÓDIGO SHCP"
        
        if columna_a_buscar in df.columns:
            res = df[df[columna_a_buscar].astype(str).str.contains(busqueda, na=False)]

            if not res.empty:
                st.dataframe(res, use_container_width=True, hide_index=True)
                
                st.markdown("### Resumen de la Plaza")
                f = res.iloc[0] 
                c1, c2, c3, c4 = st.columns(4)
                
                c1.metric("Sueldo Base", f"${f.get('SUELDO BASE', 0):,.2f}")
                c2.metric("Despensa", f"${f.get('Despensa mensual', 0):,.2f}")
                c3.metric("Pasajes", f"${f.get('Ayuda para Pasajes', 0):,.2f}")
                c4.metric("TOTAL MENSUAL", f"${f.get('PERCEPCIÓN MENSUAL TOTAL', 0):,.2f}")
                
                st.info(f"**Puesto:** {f.get('DENOMINACIÓN PUESTOS INBAL', 'No especificado')}")
            else:
                st.warning(f"No se encontraron registros para ese {etiqueta}.")
        else:
            st.error(f"Error: No se encontró la columna '{columna_a_buscar}' en el archivo Excel cargado.")
else:
    st.warning("⚠️ Sistema vacío. El administrador debe cargar el archivo en el panel lateral.")

# 6. MARCA DE AUTOR FIJA
st.markdown("""
    <div class="footer">
        Eduardo Eugenio Badillo Melo para el INBAL
    </div>
    """, unsafe_allow_html=True)