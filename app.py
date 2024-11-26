import pandas as pd
import streamlit as st
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import base64
import folium
import json
from streamlit_folium import st_folium
from streamlit_option_menu import option_menu
# Configuración de la página en Streamlit
st.set_page_config(page_title="Residuos Municipales Generados Anualmente", page_icon="🇵🇪") 
st.markdown("""
    <style>
        .custom-header {
            font-size: 40px;  /* Tamaño de fuente */
            font-weight: bold;  /* Negrita */
            color: green;  /* Color de texto verde */
            text-shadow: 
                2px 2px 4px white,  /* Borde blanco en la parte inferior y derecha */
                -2px -2px 4px white,  /* Borde blanco en la parte superior y izquierda */
                2px -2px 4px white,  /* Borde blanco en la parte inferior y izquierda */
                -2px 2px 4px white;  /* Borde blanco en la parte superior y derecha */
            text-align: center;  /* Centrado del texto */
        }
    </style>
""", unsafe_allow_html=True)

# Aplicar la clase CSS personalizada al header
st.markdown('<div class="custom-header">Residuos Municipales Generados Anualmente</div>', unsafe_allow_html=True)
csv_file = 'Residuos municipales generados anualmente.csv'
# Cargar los datos
@st.cache_data
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()
img = get_img_as_base64("ga.jpg")
page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
background-image: url("https://cdn.pixabay.com/photo/2023/10/12/17/56/after-the-rain-8311416_1280.jpg");
background-size: 100%;
background-position: top left;
background-repeat: repeat;
background-attachment: local;
}}
[data-testid="stSidebar"] > div:first-child {{
background-image: url("data:image/png;base64,{img}");
background-position: center; 
background-repeat: no-repeat;
background-attachment: fixed;
}}
[data-testid="stHeader"] {{
background: rgba(0,0,0,0);
}}
[data-testid="stToolbar"] {{
right: 2rem;
}}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)
st.sidebar.header("Configuración")
def load_data():
    df = pd.read_csv(csv_file, sep=';', encoding='latin-1')
    return df
df = load_data()
df['DEPARTAMENTO'] = df['DEPARTAMENTO'].str.strip()
st.sidebar.image('https://www.precayetanovirtual.pe/moodle/pluginfile.php/1/theme_mb2nl/loadinglogo/1692369360/logo-cayetano.png', use_column_width=True)
with st.sidebar:
    option = option_menu("Menú", ["Acerca", 'Departamental', 'Regional', 'Domic./No Domic. y  Urbanos/Rural', 'Gráfico Anual', 'Lugar específico', 'Mapa del Perú', 'Nosotros'],
        icons=['info', 'building', 'map', 'house-door', 'bar-chart-line', 'map', 'globe', 'people'], default_index=0) 
    ciudad = df['REG_NAT'].unique().tolist() 
calificacion = df['POB_TOTAL'].unique().tolist()
edad = df['QRESIDUOS_MUN'].unique().tolist() 
def contar_residuos():
    # Agrupamos los datos por 'DEPARTAMENTO' y contamos los residuos por municipio en cada departamento
    df_personas = df.groupby(['DEPARTAMENTO'], as_index=False)['QRESIDUOS_MUN'].count()

    # Mostrar el dataframe original para que el usuario vea los datos crudos
    st.subheader("Datos de residuos por municipio")
    st.write(
        "A continuación, se presenta el conjunto de datos original, que incluye los residuos generados por cada "
        "municipio en los diferentes departamentos. Cada fila representa el número total de residuos generados en "
        "un municipio específico dentro de su respectivo departamento."
    )
    st.dataframe(df)  # Muestra el dataframe original

    # Mostrar el dataframe resumido, que tiene la cantidad de residuos por departamento
    st.subheader("Resumen de residuos por departamento")
    st.write(
        "En esta tabla, los datos se han agrupado por departamento. Cada fila muestra el total de residuos generados "
        "por municipio dentro de ese departamento. Esto nos permite ver cómo se distribuyen los residuos en un nivel más "
        "alto, permitiendo comparaciones entre diferentes departamentos."
    )
    st.write(df_personas)  # Muestra el resumen por departamento

    # Crear un gráfico de pie para mostrar la distribución de residuos por departamento
    pie_chart = px.pie(df_personas, 
                       title='Distribución de residuos por departamento',
                       values='QRESIDUOS_MUN',  # Los valores serán el número de residuos
                       names='DEPARTAMENTO',  # Los nombres serán los departamentos
                       color='DEPARTAMENTO',   # Añadimos color para diferenciar mejor los departamentos
                       labels={'QRESIDUOS_MUN': 'Número de residuos',  # Etiquetamos los valores
                               'DEPARTAMENTO': 'Departamento'},  # Etiquetamos los departamentos
                       template='plotly_dark')  # Usamos un tema oscuro para mayor visibilidad
    # Explicación breve y clara para el usuario sobre el gráfico
    st.write(
        "Este gráfico muestra cómo se distribuyen los residuos generados por municipio en cada departamento. "
        "Cada segmento representa un departamento y su tamaño es proporcional al número total de residuos generados. "
        "De esta forma, se puede visualizar fácilmente qué departamentos generan más residuos en relación con otros."
    )
    # Mostrar el gráfico de pie con los datos procesados
    st.plotly_chart(pie_chart)

    # Explicación breve y clara para el usuario sobre el gráfico
    st.write(
        "Este gráfico muestra cómo se distribuyen los residuos generados por municipio en cada departamento. "
        "Cada segmento representa un departamento y su tamaño es proporcional al número total de residuos generados. "
        "De esta forma, se puede visualizar fácilmente qué departamentos generan más residuos en relación con otros."
    )

# multiselectores
def residuos_region():
    # Título de la sección
    st.title("Análisis de Residuos por Región Natural")
    
    # Definir las regiones naturales disponibles en el filtro
    ciudad = df['REG_NAT'].unique()  # Asumiendo que REG_NAT es la columna con las regiones naturales
    
    # Filtro interactivo para seleccionar las regiones naturales
    ciudad_selector = st.multiselect('Región:', ciudad, default=ciudad)                              
    
    # Filtro del DataFrame
    mask = (df['REG_NAT'].isin(ciudad_selector)) & (df['POB_TOTAL'].notna())
    numero_resultados = df[mask].shape[0]  # Número de resultados disponibles
    st.markdown(f'*Resultados Disponibles: {numero_resultados}*')  # Mostrar los resultados disponibles
    
    # Agrupar por región natural y contar los residuos generados
    df_agrupado = df[mask].groupby(by=['REG_NAT']).sum()[['QRESIDUOS_MUN']]  # Sumamos los residuos
    df_agrupado = df_agrupado.rename(columns={'QRESIDUOS_MUN': 'Residuos municipales generados anualmente'})
    df_agrupado = df_agrupado.reset_index()

    # Crear un gráfico de barras con diferentes colores
    colors = px.colors.qualitative.Plotly  # Colores predefinidos
    bar_chart = px.bar(df_agrupado, 
                    x='REG_NAT',
                    y='Residuos municipales generados anualmente',
                    text='Residuos municipales generados anualmente',
                    color='REG_NAT',  # Colores basados en la región natural
                    color_discrete_sequence=colors,
                    template='plotly_white',
                    title="Residuos Municipales Generados por Región Natural (Toneladas)"  # Título del gráfico
                      )
    
    # Mejorar formato del eje y (agregar separador de miles)
    bar_chart.update_layout(
        yaxis_tickformat=",.0f"  # Agregar separadores de miles
    )
    
    # Mostrar el gráfico interactivo
    st.plotly_chart(bar_chart)

    # Explicación clara del gráfico
    st.write(
        "Este gráfico de barras interactivo muestra la cantidad de residuos generados anualmente en cada región natural seleccionada. "
        "Cada barra representa una región y su altura refleja la cantidad de residuos generados en toneladas por los municipios de esa región."
    )
    
    # Llamado a la acción para explicar los filtros
    st.write(
        "Puedes seleccionar una o más regiones para comparar la cantidad de residuos generados en esas áreas. "
        "El gráfico se actualizará en tiempo real para mostrarte los resultados de las regiones seleccionadas."
    )
    
    # Información adicional sobre los datos filtrados
    if numero_resultados > 0:
        st.write(
            "Los datos mostrados reflejan los residuos generados por los municipios de cada región natural. "
            "Cada barra representa el total de residuos municipales generados anualmente en los municipios de la región seleccionada."
        )
    
    # Consejos sobre interpretación
    st.write(
        "Recuerda que las regiones con barras más grandes generan una mayor cantidad de residuos. "
        "Esto te ayudará a identificar rápidamente qué regiones están produciendo más residuos a nivel municipal."
    )

def residuos_ruralyurbano():
    st.markdown("### Análisis de Residuos Rurales vs Urbanos por Departamento")
    
    st.markdown("""
    En esta sección, se comparan los residuos generados en áreas rurales y urbanas para cada departamento.
    Los gráficos a continuación ayudan a visualizar la distribución de los residuos en ambas categorías (rural y urbano), permitiendo comprender cómo varía la generación de residuos según el tipo de área (rural vs urbana).
    Puede observar las diferencias en los tipos de residuos generados en los diferentes departamentos seleccionados.
    """)
    
    # Agrupar los datos para residuos rurales y urbanos
    data_comparativa = df.groupby('DEPARTAMENTO')[['POB_RURAL', 'POB_URBANA']].sum().reset_index()

    # Gráfico de áreas apiladas para la comparación rural vs urbano
    st.markdown("**Gráfico 1: Comparación de Residuos Rurales y Urbanos por Departamento**")
    st.markdown("""
    Este gráfico de áreas apiladas muestra la distribución de residuos generados en áreas rurales y urbanas en cada departamento. 
    Las áreas apiladas permiten ver la proporción de residuos en cada categoría (rural/urbano) dentro de cada departamento. 
    Esto facilita la comparación visual de la contribución de residuos en cada área.
    """)

    fig_comparativa_apilada = px.area(data_comparativa, 
                                     x='DEPARTAMENTO', 
                                     y=['POB_RURAL', 'POB_URBANA'], 
                                     title='Comparación de Residuos Rurales y Urbanos por Departamento',
                                     labels={'POB_RURAL': 'Residuos Rurales', 
                                             'POB_URBANA': 'Residuos Urbanos', 
                                             'DEPARTAMENTO': 'Departamento'},
                                     color_discrete_sequence=["#636EFA", "#EF553B"])  
    
    fig_comparativa_apilada.update_layout(
        xaxis_title="Departamento", 
        yaxis_title="Cantidad de Residuos (Toneladas)",
        title="Residuos Rurales y Urbanos por Departamento",
        showlegend=True
    )
    st.plotly_chart(fig_comparativa_apilada)
    st.markdown("""
    A continuacion se muestra el DataFrame en el cual aparece los datos especificos de los departamentos respecto a""")
    st.write('Residuos Rurales y Urbanos:', data_comparativa)
    
    # Agrupar los datos para residuos domiciliarios y no domiciliarios
    data_comparativa2 = df.groupby('DEPARTAMENTO')[['QRESIDUOS_DOM', 'QRESIDUOS_NO_DOM']].sum().reset_index()
    st.markdown("### Análisis de Residuos Domiciliarion y No Domiciliarios por Departamento")
    # Gráfico de barras apiladas para residuos domiciliarios y no domiciliarios
    st.markdown("**Gráfico 2: Comparación de Residuos Domiciliarios y No Domiciliarios por Departamento**")
    st.markdown("""
    Este gráfico de barras apiladas compara los residuos domiciliarios y no domiciliarios generados en cada departamento. 
    Las barras apiladas facilitan la visualización de la proporción de residuos domiciliarios y no domiciliarios en cada departamento, 
    ayudando a observar cómo varían las cantidades de residuos generados por cada tipo en las diferentes zonas.
    """)

    fig_comparativa_grupo = px.bar(data_comparativa2, 
                                   x='DEPARTAMENTO', 
                                   y=['QRESIDUOS_DOM', 'QRESIDUOS_NO_DOM'], 
                                   title='Comparación de Residuos Domiciliarios y No Domiciliarios por Departamento (Barras Apiladas)',
                                   labels={'QRESIDUOS_DOM': 'Residuos Domiciliarios', 
                                           'QRESIDUOS_NO_DOM': 'Residuos No Domiciliarios', 
                                           'DEPARTAMENTO': 'Departamento'},
                                   color_discrete_sequence=["#28a745", "#ffc107"],  
                                   barmode='stack')  

    fig_comparativa_grupo.update_layout(
        xaxis_title="Departamento", 
        yaxis_title="Cantidad de Residuos (Toneladas)",
        title="Residuos Domiciliarios y No Domiciliarios por Departamento (Barras Apiladas)",
        showlegend=True
    )

    st.plotly_chart(fig_comparativa_grupo)
    
    # Agregar gráfico de líneas para comparar residuos domiciliarios y no domiciliarios
    st.markdown("**Gráfico 3: Comparación de Residuos Domiciliarios y No Domiciliarios por Departamento (Líneas)**")
    st.markdown("""
    Este gráfico de líneas compara la cantidad de residuos domiciliarios y no domiciliarios en los departamentos seleccionados. 
    Las líneas muestran cómo evolucionan estos residuos a lo largo de los departamentos, permitiendo visualizar las tendencias de generación de residuos para cada tipo.
    """)
    
    fig_comparativa_lineas = go.Figure()

    # Añadir líneas para residuos domiciliarios
    fig_comparativa_lineas.add_trace(go.Scatter(
        x=data_comparativa2['DEPARTAMENTO'],
        y=data_comparativa2['QRESIDUOS_DOM'],
        mode='lines+markers',
        name='Residuos Domiciliarios',
        line=dict(color='green'),
        hovertemplate='Departamento: %{x}<br>Residuos Domiciliarios: %{y} toneladas<extra></extra>'
    ))

    # Añadir líneas para residuos no domiciliarios
    fig_comparativa_lineas.add_trace(go.Scatter(
        x=data_comparativa2['DEPARTAMENTO'],
        y=data_comparativa2['QRESIDUOS_NO_DOM'],
        mode='lines+markers',
        name='Residuos No Domiciliarios',
        line=dict(color='orange'),
        hovertemplate='Departamento: %{x}<br>Residuos No Domiciliarios: %{y} toneladas<extra></extra>'
    ))

    fig_comparativa_lineas.update_layout(
        title='Comparación de Residuos Domiciliarios y No Domiciliarios por Departamento (Gráfico de Líneas)',
        xaxis_title="Departamento",
        yaxis_title="Cantidad de Residuos (Toneladas)",
        showlegend=True,
        hovermode='closest'
    )

    st.plotly_chart(fig_comparativa_lineas)
    st.markdown("""
    A continuacion se muestra el DataFrame en el cual aparece los datos especificos de los departamentos respecto a  """)
    
    st.write('Residuos Domiciliarios y No Domiciliarios:', data_comparativa2)
    
def residuos_departamento_anio():

    # Agrupar los datos por año y departamento
    data_agrupada = df.groupby(['PERIODO', 'DEPARTAMENTO'])['QRESIDUOS_MUN'].sum().reset_index()

    st.markdown('**Gráfico de Radar y Información de Disposición Final Adecuada por Año y Departamento**')

    # Crear un selector para elegir el año
    anios = sorted(data_agrupada['PERIODO'].unique())
    anio_seleccionado = st.selectbox('Selecciona el Año:', anios)

    # Filtrar los datos para el año seleccionado
    data_anio = data_agrupada[data_agrupada['PERIODO'] == anio_seleccionado]

    # Calcular el total de residuos para ese año
    total_residuos_anio = data_anio['QRESIDUOS_MUN'].sum()

    # Calcular el porcentaje de residuos por departamento
    data_anio['Porcentaje'] = (data_anio['QRESIDUOS_MUN'] / total_residuos_anio) * 100

    # Ordenar los datos por la cantidad de residuos
    data_anio_sorted = data_anio.sort_values(by='QRESIDUOS_MUN', ascending=False)

    # Configurar los colores para cada año
    color_palette = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    color = color_palette[anios.index(anio_seleccionado) % len(color_palette)]  # Asignar un color único por año

    # Configurar el gráfico de radar
    fig = go.Figure()

    # Añadir la traza de radar
    fig.add_trace(go.Scatterpolar(
        r=data_anio['QRESIDUOS_MUN'],  # Valores de residuos
        theta=data_anio['DEPARTAMENTO'],  # Los nombres de los departamentos
        fill='toself',  # Rellenar el área
        name=f'Año {anio_seleccionado}',
        line=dict(color=color),  # Color dinámico para cada año
        hovertemplate='Departamento: %{theta}<br>Residuos: %{r} toneladas<extra></extra>'  # Información al pasar el cursor
    ))

    # Configurar el diseño del gráfico de radar
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(data_anio['QRESIDUOS_MUN']) + 100]  # Ajuste de rango de residuos
            )
        ),
        title=f'Disposición Final Adecuada por Departamento en el Año {anio_seleccionado}',
        showlegend=True
    )

    # Mostrar primero el gráfico en Streamlit
    st.plotly_chart(fig)

    # Mostrar tarjetas con información clave sobre los residuos
    st.markdown("### Resumen de Residuos por Departamento")

    # Tarjetas de información (porcentaje máximo, total de residuos, etc.)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total de Residuos (toneladas)", f"{total_residuos_anio:.2f}")
    
    max_residuo = data_anio_sorted['QRESIDUOS_MUN'].max()
    max_departamento = data_anio_sorted[data_anio_sorted['QRESIDUOS_MUN'] == max_residuo]['DEPARTAMENTO'].values[0]
    
    with col2:
        st.metric("Departamento con más residuos", max_departamento)

    max_porcentaje = data_anio_sorted['Porcentaje'].max()
    max_departamento_porcentaje = data_anio_sorted[data_anio_sorted['Porcentaje'] == max_porcentaje]['DEPARTAMENTO'].values[0]
    
    with col3:
        st.metric("Departamento con mayor porcentaje", max_departamento_porcentaje)

    # **Gráfico de Línea**
    st.markdown("### Distribución de Residuos por Departamento (Gráfico de Línea)")

    line_fig = go.Figure()

    # Añadir las líneas para cada departamento
    line_fig.add_trace(go.Scatter(
        x=data_anio_sorted['DEPARTAMENTO'],
        y=data_anio_sorted['QRESIDUOS_MUN'],
        mode='lines+markers',  # Mostrar líneas con marcadores en cada punto
        name=f'Residuos por Departamento en {anio_seleccionado}',
        marker=dict(color='rgba(50, 171, 96, 0.6)'),
        line=dict(color='rgba(50, 171, 96, 0.6)', width=3),
        hovertemplate='Departamento: %{x}<br>Residuos: %{y} toneladas<extra></extra>'
    ))

    line_fig.update_layout(
        title=f'Distribución de Residuos por Departamento (Línea) - {anio_seleccionado}',
        xaxis_title="Departamento",
        yaxis_title="Cantidad de Residuos (toneladas)",
        xaxis_tickangle=-45,  # Rotar las etiquetas de los departamentos si es necesario
        hovermode='closest'  # Mostrar el valor exacto al pasar el cursor por encima
    )

    st.plotly_chart(line_fig)

    # **Tabla Estilizada con los datos y porcentaje**
    st.markdown("### Detalles de Residuos por Departamento")

    # Estilizar la tabla con colores para facilitar la lectura
    styled_df = data_anio_sorted[['DEPARTAMENTO', 'QRESIDUOS_MUN', 'Porcentaje']].style.format({
        'QRESIDUOS_MUN': '{:.2f}',  # Formato de los residuos
        'Porcentaje': '{:.2f}%'  # Formato del porcentaje
    }).background_gradient(axis=0, cmap='Blues')

    # Mostrar la tabla sin índice
    st.dataframe(styled_df, hide_index=True, use_container_width=True)

    # Explicación para el usuario
    st.write(""" 
        - **Gráfico de Radar**: Muestra la distribución de residuos por departamento en el año seleccionado. Los departamentos con mayor cantidad de residuos estarán más distantes del centro del gráfico.
        - **Tarjetas de Información**: Muestran métricas clave como el total de residuos y el departamento con más residuos.
        - **Gráfico de Línea**: Muestra cómo se distribuyen los residuos por departamento en un formato de línea, útil para ver tendencias y comparar cantidades.
        - **Tabla Estilizada**: Proporciona detalles más precisos sobre los residuos generados por cada departamento, con un formato interactivo para facilitar la lectura.
    """)


def total_sitios_disposicion_final():
    # Título e Introducción
    st.markdown('**Filtrar y Visualizar la Distribución de Residuos Generados por Provincia y Distrito**')
    st.markdown("""
    En esta sección, puedes explorar la distribución de los residuos generados en cada distrito dentro de una provincia específica del departamento seleccionado. 
    Utilizando el gráfico de violín, se muestra cómo se distribuyen los residuos a través de diferentes puntos del distrito seleccionado, 
    ayudando a entender la variabilidad y concentración de los residuos generados en esa área.
    A continuación, selecciona un departamento, provincia y distrito para ver la distribución detallada de los residuos.
    """)

    # Cargar datos
    df = load_data()  
    
    # Filtro por Departamento
    departamento_seleccionado = st.selectbox('Seleccione el Departamento', df['DEPARTAMENTO'].unique())
    df_filtrado = df[df['DEPARTAMENTO'] == departamento_seleccionado]
 
    # Filtro por Provincia
    provincia_seleccionada = st.selectbox('Seleccione la Provincia', df_filtrado['PROVINCIA'].unique())
    df_filtrado = df_filtrado[df_filtrado['PROVINCIA'] == provincia_seleccionada]
 
    # Filtro por Distrito
    distrito_seleccionado = st.selectbox('Seleccione el Distrito', df_filtrado['DISTRITO'].unique())
    df_filtrado = df_filtrado[df_filtrado['DISTRITO'] == distrito_seleccionado]
    
    # Explicación del gráfico
    st.markdown("""
    El siguiente gráfico de violín muestra la **distribución de los residuos sólidos generados** en el distrito seleccionado. 
    Un gráfico de violín es útil para entender cómo se distribuyen los datos y proporciona información sobre la mediana, los cuartiles, 
    y la presencia de valores atípicos en la distribución de los residuos generados. 
    Además, incluye un cuadro que muestra la dispersión de los datos y los puntos individuales para una visualización completa.
    """)

    # Gráfico de violín para la distribución de los residuos
    fig = px.violin(df_filtrado, 
                    y='QRESIDUOS_MUN', 
                    box=True, 
                    points='all', 
                    title=f'Distribución de Residuos Generados por Distrito en la Provincia de {provincia_seleccionada} - Departamento de {departamento_seleccionado}',
                    labels={'QRESIDUOS_MUN': 'Total de Residuos Municipales Generados (Toneladas)', 'DISTRITO': 'Distrito'})
    st.info("""
    **Interpretación del gráfico:**
    - **El violín** muestra la distribución de residuos generados en el distrito. La forma del violín indica la densidad de los residuos, mostrando dónde se concentran más o menos.
    - **La caja** dentro del violín representa el rango intercuartílico (IQR), que incluye el 50% central de los datos.
    - **Los puntos individuales** muestran los datos de residuos generados por cada entidad o punto dentro del distrito.
    - El gráfico te ayuda a ver no solo el total de residuos, sino también cómo varían estos valores dentro del distrito.
    """, icon='📊')

    st.plotly_chart(fig)

    # Mostrar el DataFrame filtrado
    st.markdown("""
    A continuación, se muestra el DataFrame con los datos de residuos filtrados para el distrito seleccionado. Este DataFrame incluye 
    los valores de residuos generados en las diferentes unidades dentro del distrito
    """)
    st.write('**DataFrame Filtrado:**', df_filtrado)
    

def mapa_residuos():
    st.header('Distribución Geopolítica de los Residuos Municipales en Perú')

    # Cargar datos GeoJSON para los departamentos de Perú
    with open('peru_departamental_simple.geojson', 'r') as f:
        peru_departamentos = json.load(f)
    
    # Cargar dataset de residuos
    dataset = pd.read_csv('Residuos municipales generados anualmente.csv', sep=';', encoding='latin1')

    # Extraer los nombres de los departamentos
    departamentos = [feature['properties']['NOMBDEP'].strip().lower() for feature in peru_departamentos['features']]

    # Crear el mapa base
    m = folium.Map(location=[-9, -65], zoom_start=5, control_scale=True)

    # Añadir un grupo de características al mapa
    fg = folium.FeatureGroup(name="Departamentos de Perú")

    # Función para el popup de cada departamento
    def popup_info(feature):
        departamento = feature['properties']['NOMBDEP']
        return folium.Popup(f"<strong>Departamento:</strong> {departamento}", max_width=300)

    # Seleccionar un departamento
    selected_department = st.selectbox("Selecciona un departamento", sorted(departamentos))

    # Filtrar los datos según el departamento seleccionado
    selected_department_normalized = selected_department.strip().lower()
    selected_data = dataset[dataset['DEPARTAMENTO'].str.strip().str.lower() == selected_department_normalized]

    # Obtener la cantidad de residuos para el departamento seleccionado
    residuos_value = selected_data['QRESIDUOS_MUN'].values[0] if not selected_data.empty else None

    # Función de estilo para los departamentos
    def style_function(feature):
        department_name = feature['properties']['NOMBDEP'].strip().lower()
        
        # Resaltar el departamento seleccionado
        if department_name == selected_department:
            return {
                'fillColor': '#33cc33',  # Verde para el seleccionado
                'color': 'black',
                'weight': 2,
                'fillOpacity': 0.7
            }
        else:
            return {
                'fillColor': '#66b3ff',  # Azul para el resto
                'color': 'black',
                'weight': 1.5,
                'fillOpacity': 0.4
            }

    # Añadir los departamentos al mapa
    fg.add_child(folium.GeoJson(
        peru_departamentos,
        name='Departamentos',
        tooltip=folium.GeoJsonTooltip(fields=['NOMBDEP'], aliases=['Departamento'], localize=True),
        popup=popup_info,
        style_function=style_function
    ))

    m.add_child(fg)

    # Añadir un control de capas para poder encender y apagar la capa
    folium.LayerControl().add_to(m)

    # Mostrar el mapa interactivo en Streamlit
    out = st_folium(m, width=1200, height=500)
    st.markdown("""
    ### Leyenda:
    - **Verde**: Departamento seleccionado.
    - **Azul**: Otros departamentos.
    """)
    # Mostrar información sobre los residuos si hay datos disponibles
    if residuos_value is not None:
        st.write(f"**Residuos Municipales en {selected_department.capitalize()}:**")
        st.write(f"La cantidad de residuos generados anualmente en {selected_department.capitalize()} es de {residuos_value} toneladas.")
    else:
        st.write(f"No se encontraron datos para el departamento: {selected_department.capitalize()}")
    selected_data = dataset[dataset['DEPARTAMENTO'].str.strip().str.lower() == selected_department_normalized]
    selected_data = dataset[dataset['DEPARTAMENTO'].str.strip().str.lower() == selected_department_normalized]

    # Mostrar los datos asociados al departamento seleccionado en una tabla de Streamlit
    if not selected_data.empty:
        st.write(f"**Datos para el departamento: {selected_department}**")
        st.write(selected_data[['DEPARTAMENTO', 'POB_TOTAL', 'POB_URBANA', 'POB_RURAL', 'QRESIDUOS_DOM', 'QRESIDUOS_NO_DOM', 'QRESIDUOS_MUN']])
    else:
        st.write(f"No se encontraron datos para el departamento: {selected_department}")
def acerca():
    # Título principal sobre una imagen
    st.image('imagen_titulo.png', use_column_width=True)
    st.markdown('<div class="espacio-arriba"></div>', unsafe_allow_html=True) 

    # Introducción del proyecto
    with st.expander("Introducción del Proyecto", expanded=True):
        st.write("""
        Bienvenidos a nuestra página web, donde presentaremos información relevante sobre la generación y disposición de los residuos sólidos municipales en Perú, mediante gráficos y análisis detallados de los datos.
        """)

    st.markdown('<div class="espacio-arriba"></div>', unsafe_allow_html=True) 
    
    with st.expander("Introducción a los Residuos Municipales", expanded=True):
        st.write("""
        Los residuos sólidos municipales comprenden todos los desechos generados por las actividades urbanas, que incluyen materiales desechados de hogares, comercios, instituciones públicas y privadas, y espacios públicos en general. En Perú, la generación de residuos municipales ha experimentado un aumento considerable debido al crecimiento poblacional y a la expansión de las áreas urbanas.
        """)
        st.write("""
        El manejo adecuado de los residuos municipales es un desafío clave para la sostenibilidad y la salud pública en el país. A través de este proyecto, analizamos la cantidad y distribución de los residuos generados anualmente en diversas regiones de Perú, con el objetivo de proporcionar datos relevantes para mejorar las políticas de gestión y reciclaje, y así contribuir a un entorno más limpio y saludable.
        """)

    st.markdown('<div class="espacio-arriba"></div>', unsafe_allow_html=True)  
    
    st.image('plan_manejo.png', caption='Extraído de Google', use_column_width=True)
    
    st.markdown('<div class="espacio-arriba"></div>', unsafe_allow_html=True)  
    
    with st.expander("Descripción del Proyecto", expanded=True):
        st.write("""
        Este proyecto busca mostrar cómo la generación de residuos municipales varía a lo largo de los años en Perú, analizando tendencias y factores que influyen en la cantidad de residuos generados anualmente. Utilizamos Streamlit para crear una interfaz interactiva que permita visualizar estos datos de manera clara.
        """)

    st.markdown('<div class="espacio-arriba"></div>', unsafe_allow_html=True) 
    
    with st.expander("Generación Anual de Residuos Sólidos Municipales", expanded=True):
        st.write("""
        Los residuos sólidos municipales se generan de manera constante en todas las ciudades del país. La cantidad de residuos generados depende de varios factores como el crecimiento poblacional, el consumo, y las prácticas de manejo de residuos en las distintas regiones. Es importante entender cómo varía esta generación anual para poder mejorar las políticas de manejo, reciclaje y disposición final.
        """)
        st.image("tipos_residuos.png")
        
        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader('Aumento de Residuos por Crecimiento Urbano')
            st.write("""
            El aumento de la población y la expansión de las áreas urbanas han llevado a un incremento en la generación de residuos sólidos. Este fenómeno es particularmente visible en las grandes ciudades como Lima, Arequipa y Trujillo.
            """)

        with col2:
            st.subheader('Factores de Generación Anual')
            st.write("""
            Los patrones de consumo, la actividad comercial y el desarrollo industrial también contribuyen a la cantidad de residuos generados. Analizar estos factores nos permite predecir las tendencias y optimizar el manejo de los residuos.
            """)

        with col3:
            st.subheader('Impacto Ambiental')
            st.write("""
            Un aumento en la generación de residuos implica mayores retos para su disposición adecuada, lo que puede resultar en impactos negativos sobre el medio ambiente. Por ello, es crucial implementar estrategias sostenibles para la gestión de estos residuos.
            """)

    st.write("""
    Este proyecto tiene como objetivo principal demostrar cómo los datos sobre la generación anual de residuos pueden ser utilizados para mejorar la toma de decisiones en políticas públicas y gestión ambiental, promoviendo un Perú más limpio y responsable en la gestión de sus residuos sólidos municipales.
    """)

def nosotros():
    st.write("Somos estudiantes de la Universidad Peruana Cayetano Heredia (UPCH), en la carrera de Ingeniería informatica.")
    st.write("""Este proyecto nace con el objetivo de proporcionar una plataforma interactiva que permita a la ciudadanía, autoridades y organizaciones del sector ambiental entender mejor el manejo y disposición final de residuos sólidos municipales en el Perú.   
    A través de esta herramienta, buscamos visualizar la información crítica sobre la gestión de residuos y promover una discusión sobre las mejores prácticas, políticas públicas y soluciones sostenibles que pueden ser implementadas para mejorar el manejo de los residuos en nuestro país.
    Como futuros ingenieros ambientales, estamos comprometidos con la creación de soluciones que no solo sean tecnológicas, sino que también contribuyan a la preservación de nuestro entorno y al bienestar de las futuras generaciones.
    Nos gustaría agradecer a todos los que han participado en este proyecto, desde los desarrolladores hasta los usuarios que interactúan con los datos. Creemos que este tipo de iniciativas pueden marcar la diferencia en la creación de un futuro más limpio y saludable para todos.
    """)
    st.write("""
    **¡Gracias por tu interés en conocer más sobre la disposición final de residuos en Perú!**
    """)
    st.image('https://media.istockphoto.com/id/1425875523/es/foto/grupo-de-programadores-y-desarrolladores-de-software-trabajando-en-un-nuevo-proyecto-en-la.jpg?s=2048x2048&w=is&k=20&c=Y9xQDMwsINCFPmx9wcMG06xOjBgciq8SBdzVnZUtZtQ=', caption="Grupo de programadores trabajando en un nuevo proyecto", use_column_width=True)
# Mostrar las opciones y ejecutar la función correspondiente
if option =='Acerca':
    acerca()
elif option == 'Departamental':
    contar_residuos()
elif option == 'Regional':
    residuos_region()
elif option == 'Domic./No Domic. y  Urbanos/Rural':
    residuos_ruralyurbano()
elif option == 'Gráfico Anual':
    residuos_departamento_anio()
elif option == 'Lugar específico':
    total_sitios_disposicion_final()
elif option=='Mapa del Perú':
    mapa_residuos()
elif option == 'Nosotros':
    nosotros()
st.sidebar.markdown("""
**Integrantes:**
                    
-Valenzuela Valer Luis Martin

_Lopez Vega Juan Diego                                     
                    
_Pilco Cruz Elvis
                    
_Nunton Fajardo Leonardo
                    
_Roldan Montalvan Jorge Esteban
                                                            
""")
st.sidebar.write("Ingenieria Informatica - 2024")

