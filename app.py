import streamlit as st
import pandas as pd

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
    [data-testid="stMetricValue"] { color: #BC955C !important; font-weight: bold !important; }
    [data-testid="stMetricLabel"] { color: #4A141C !important; }
    .footer { position: fixed; right: 15px; bottom: 15px; text-align: right; color: #555555 !important; font-size: 12px; z-index: 100; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

if 'data' not in st.session_state:
    st.session_state.data = None

# 2. ENCABEZADO
st.title("Módulo de Consulta de Plazas")
st.markdown("### Información de Percepciones y Puestos")

# 3. PANEL LATERAL (ADMINISTRACIÓN)
with st.sidebar:
    st.header("Seguridad")
    password = st.text_input("Clave de Administrador", type="password")
    
    if password == "ADMIN2026": 
        st.success("Acceso Autorizado")
        archivo = st.file_uploader("Actualizar Base Excel", type=["xlsx", "xls"])
        
        if archivo:
            try:
                engine = 'xlrd' if archivo.name.endswith('.xls') else 'openpyxl'
                df_temp = pd.read_excel(archivo, engine=engine)
                # Limpiar espacios en los nombres de las columnas
                df_temp.columns = df_temp.columns.str.strip()
                
                # --- LIMPIEZA DE NaN ---
                # Rellenar textos vacíos con "N/A" y números vacíos con 0
                columnas_numericas = ['Sueldo Base', 'Comp. Garant.', 'Despensa mensual', 
                                     'Ayuda para pasajes', 'Ayuda para activ. Sociocult.', 
                                     'Percepción mensual total']
                for col in columnas_numericas:
                    if col in df_temp.columns:
                        df_temp[col] = pd.to_numeric(df_temp[col], errors='coerce').fillna(0)
                
                df_temp = df_temp.fillna("N/A")
                st.session_state.data = df_temp
                st.success(" Datos actualizados y limpios")
            except Exception as e:
                st.error(f"Error al procesar el Excel: {e}")
    
    st.markdown("---")
    with st.expander("Información"):
        st.write("Versión: 1.1")
        st.write("Firma técnica: **Eduardo Eugenio Badillo Melo**")

# 4. LÓGICA DE CONSULTA
if st.session_state.data is not None:
    tipo_busqueda = st.radio(
        "**Paso 1: Seleccione el método de búsqueda**",
        ["Código INBAL", "Código SHCP"],
        horizontal=True
    )

    col_filtro = "CÓDIGO INBAL" if tipo_busqueda == "Código INBAL" else "CÓDIGO SHCP"
    busqueda = st.text_input(f"**Paso 2: Ingrese el {tipo_busqueda}:**").strip().upper()

    if busqueda:
        df = st.session_state.data
        if col_filtro in df.columns:
            # Filtrado exacto o parcial
            res = df[df[col_filtro].astype(str).str.contains(busqueda, na=False)]

            if not res.empty:
                st.markdown("---")
                st.dataframe(res, use_container_width=True, hide_index=True)
                
                st.markdown("### Resumen Detallado de la Plaza")
                f = res.iloc[0] # Tomamos el primer resultado encontrado
                
                # Función para mostrar moneda sin errores
                def m(v): return f"${v:,.2f}"

                # Fila 1 de métricas
                c1, c2, c3 = st.columns(3)
                c1.metric("Sueldo Base", m(f.get('Sueldo Base', 0)))
                c2.metric("Comp. Garant.", m(f.get('Comp. Garant.', 0)))
                c3.metric("Despensa Mensual", m(f.get('Despensa mensual', 0)))

                # Fila 2 de métricas
                c4, c5, c6 = st.columns(3)
                c4.metric("Ayuda Pasajes", m(f.get('Ayuda para pasajes', 0)))
                c5.metric("Ayuda Sociocult.", m(f.get('Ayuda para activ. Sociocult.', 0)))
                c6.metric("TOTAL MENSUAL", m(f.get('Percepción mensual total', 0)))
                
                st.info(f"**Puesto:** {f.get('Denominación Puestos INBAL', 'N/A')} | **Nivel:** {f.get('Nivel Salarial', 'N/A')}")
            else:
                st.warning(f"No se encontró información para el {tipo_busqueda}: {busqueda}")
        else:
            st.error(f"Error: No se encuentra la columna '{col_filtro}' en el Excel.")
else:
    st.info("Sistema listo. Por favor, cargue el archivo Excel en el panel lateral.")

# 5. MARCA DE AUTOR
st.markdown("""
    <div class="footer">
        INBAL | EEBM
    </div>
    """, unsafe_allow_html=True)
