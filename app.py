import pandas as pd
import streamlit as st
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import base64
import folium
import json
from streamlit_folium import st_folium
# Configuración de la página en Streamlit
st.set_page_config(page_title="Residuos Municipales Generados Anualmente", page_icon="🇵🇪")  # Nombre para configurar la página web
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
st.markdown('<div class="custom-header">Residuos Municipales Generados Anualmente</div>', unsafe_allow_html=True)  # Título de la página
# Ruta del archivo CSV
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
# Cargar los datos
df = load_data()
# Limpiar espacios en blanco en la columna DEPARTAMENTO
df['DEPARTAMENTO'] = df['DEPARTAMENTO'].str.strip()
# Función para contar residuos por departamento y graficar
def contar_residuos():
    # Agrupar los datos por DEPARTAMENTO y contar los residuos
    df_personas = df.groupby(['DEPARTAMENTO'], as_index=False)['QRESIDUOS_MUN'].count()
    # Mostrar el DataFrame completo y el resumen por departamento
    st.dataframe(df)  # Mostrar todo el DataFrame
    st.write(df_personas)  # Mostrar el resumen agrupado
    # Crear un gráfico de torta (pie chart)
    pie_chart = px.pie(df_personas, 
                       title='Residuos por departamento',
                       values='QRESIDUOS_MUN', 
                       names='DEPARTAMENTO')
    st.plotly_chart(pie_chart)  # Mostrar el gráfico en Streamlit
# Menú con opciones en la barra lateral
st.sidebar.image('https://www.precayetanovirtual.pe/moodle/pluginfile.php/1/theme_mb2nl/loadinglogo/1692369360/logo-cayetano.png', use_column_width=True)
option = st.sidebar.selectbox('Seleccione una opción:', ('Acerca', ' Departamental', ' Regional', ' Domic./No Domic. y  Urbanos/Rural', 'Gráfico Anual', 'lugar en especifico','Mapa del Perú', 'Nosotros'))
# Crear listas únicas de las columnas (esto no es condicional, simplemente extraemos los valores únicos)
ciudad = df['REG_NAT'].unique().tolist()  # Lista única de regiones naturales
calificacion = df['POB_TOTAL'].unique().tolist()  # Lista única de población total
edad = df['QRESIDUOS_MUN'].unique().tolist()  # Lista única de residuos

#crear multiselectores
def residuos_region():
    ciudad_selector = st.multiselect('Región:', ciudad, default = ciudad)                              
    #Ahora necesito que esos selectores y slider me filtren la informacion
    mask = (df['REG_NAT'].isin(ciudad_selector))&(df['POB_TOTAL'])
    numero_resultados = df[mask].shape[0] ##number of availables rows
    st.markdown(f'*Resultados Disponibles:{numero_resultados}*') ## sale como un titulo que dice cuantos resultados tiene para ese filtro
    # Aplicar el filtro y agrupar por REGION_NATURAL contando DISPOSICION_FINAL_ADECUADA
    df_agrupado = df[mask].groupby(by=['REG_NAT']).count()[['QRESIDUOS_MUN']]
    df_agrupado = df_agrupado.rename(columns={'QRESIDUOS_MUN': 'Residuos municipales generados anualmente'})
    df_agrupado = df_agrupado.reset_index()
    # Crear un gráfico de barras con diferentes colores
    colors = px.colors.qualitative.Plotly  # Puedes usar cualquier secuencia de colores predefinida de Plotly
    bar_chart = px.bar(df_agrupado, 
                    x='REG_NAT',
                    y='Residuos municipales generados anualmente',
                    text='Residuos municipales generados anualmente',
                    color='REG_NAT',  # Usar REGION_NATURAL para asignar colores diferentes
                    color_discrete_sequence=colors,
                    template='plotly_white',
                    title="Residuos Municipales Generados por Región Natural (Toneladas)"  # Título del gráfico
                      )
    # Mostrar el gráfico en Streamlit
    st.plotly_chart(bar_chart)
def residuos_departamento():
    # Agrupar por DEPARTAMENTO y sumar QRESIDUOS_MUN
    data_agrupada = df.groupby('DEPARTAMENTO')['QRESIDUOS_MUN'].sum().reset_index()
    
    # Aplicación Streamlit
    st.markdown('**Gráfico Circular de Cantidad de Residuos Sólidos Generados a Nivel Municipal en cada Departamento**')
    
    # Crear el gráfico circular (Pie chart) con Plotly para residuos municipales
    fig = px.pie(data_agrupada, values='QRESIDUOS_MUN', names='DEPARTAMENTO', title='CANTIDAD DE RESIDUOS SÓLIDOS GENERADOS A NIVEL MUNICIPAL')
    
    # Configuración del gráfico circular
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    # Mostrar el gráfico circular en Streamlit
    st.plotly_chart(fig)
    
    # Ahora agregar gráfico comparativo de residuos domiciliarios y no domiciliarios por DEPARTAMENTO
    st.markdown('**Gráfico de Comparación de Residuos Rural y Urbana por Departamento**')
    
    # Agrupar por DEPARTAMENTO y sumar los residuos domiciliarios y no domiciliarios
    data_comparativa = df.groupby('DEPARTAMENTO')[['POB_RURAL', 'POB_URBANA']].sum().reset_index()
    
    # Gráfico de barras apiladas para comparar residuos domiciliarios y no domiciliarios
    fig_comparativa_apilada = px.bar(data_comparativa, 
                                     x='DEPARTAMENTO', 
                                     y=['POB_RURAL', 'POB_URBANA'], 
                                     title='Comparación de Residuos Domiciliarios y No Domiciliarios por Departamento',
                                     labels={'POB_RURAL': 'Residuos Rurales', 
                                             'POB_URBANA': 'Residuos Urbanos', 
                                             'DEPARTAMENTO': 'Departamento'},
                                     color_discrete_sequence=["#636EFA", "#EF553B"],  # Colores para cada tipo de residuo
                                     barmode='stack')  # Para apilar las barras
    
    # Configuración del gráfico de barras apiladas
    fig_comparativa_apilada.update_layout(
        xaxis_title="Departamento", 
        yaxis_title="Cantidad de Residuos (Toneladas)",
        title="Residuos Rurales y Urbanos por Departamento "
    )
    
    # Mostrar el gráfico de barras apiladas en Streamlit
    st.plotly_chart(fig_comparativa_apilada)
    data_comparativa2 = df.groupby('DEPARTAMENTO')[['QRESIDUOS_DOM', 'QRESIDUOS_NO_DOM']].sum().reset_index()
    # Gráfico de barras agrupadas para comparar residuos domiciliarios y no domiciliarios
    fig_comparativa_grupo = px.bar(data_comparativa2, 
                                   x='DEPARTAMENTO', 
                                   y=['QRESIDUOS_DOM', 'QRESIDUOS_NO_DOM'], 
                                   title='Comparación de Residuos Domiciliarios y No Domiciliarios por Departamento (Barras Agrupadas)',
                                   labels={'QRESIDUOS_DOM': 'Residuos Domiciliarios', 
                                           'QRESIDUOS_NO_DOM': 'Residuos No Domiciliarios', 
                                           'DEPARTAMENTO': 'Departamento'},
                                   color_discrete_sequence=["#28a745", "#ffc107"],  # Colores para cada tipo de residuo
                                   barmode='group')  # Para mostrar las barras lado a lado
    st.write('DataFrame Comparativo de Residuos Rurales y Urbanos:', data_comparativa2)
    # Configuración del gráfico de barras agrupadas
    fig_comparativa_grupo.update_layout(
        xaxis_title="Departamento", 
        yaxis_title="Cantidad de Residuos (Toneladas)",
        title="Residuos Domiciliarios y No Domiciliarios por Departamento (Barras Agrupadas)"
    )
    
    # Mostrar el gráfico de barras agrupadas en Streamlit
    st.plotly_chart(fig_comparativa_grupo)
    
    # Mostrar el DataFrame comparativo (opcional)
    st.write('DataFrame Comparativo de Residuos Domiciliarios y No Domiciliarios:', data_comparativa)
    
def residuos_departamento_anio():
    # Agrupar por DEPARTAMENTO y ANIO, y sumar DISPOSICION_FINAL_ADECUADA
    data_agrupada = df.groupby(['PERIODO', 'DEPARTAMENTO'])['QRESIDUOS_MUN'].sum().reset_index()

    # Definir una lista de colores oscuros y sólidos
    dark_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

    # Aplicación Streamlit
    st.markdown('**Gráfico de Líneas de Disposición Final Adecuada por Año y Departamento**')

   # Crear subplots por cada año
    anios = data_agrupada['PERIODO'].unique()
    fig = make_subplots(rows=len(anios), cols=1, shared_xaxes=True, vertical_spacing=0.1, subplot_titles=[f'Año {anio}' for anio in anios])

    # Añadir trazos para cada año
    for i, anio in enumerate(anios, start=1):
        data_anio = data_agrupada[data_agrupada['PERIODO'] == anio]
        fig.add_trace(
            go.Scatter(
                x=data_anio['DEPARTAMENTO'], 
                y=data_anio['QRESIDUOS_MUN'], 
                mode='lines+markers',
                name=f'Año {anio}',
                line=dict(color=dark_colors[i % len(dark_colors)])
            ),
            row=i, col=1
        )
        # Configurar etiquetas del eje x para cada subplot
        # fig.update_xaxes(title_text='Departamento', row=i, col=1)
    # Ajustes finales
    fig.update_layout(
        height=200*len(anios), 
        title_text='Disposición Final Adecuada por Año y Departamento',
        showlegend=True
    )
    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig)

def total_sitios_disposicion_final():
    # Título de la aplicación
    st.markdown('**Filtrar y Sumar Residuos Generados por Provincia y Distrito**')
    # Cargar y limpiar los datos
    df = load_data()  # Asumiendo que ya tienes la función load_data() para cargar el archivo CSV
    # Filtrar por DEPARTAMENTO
    departamento_seleccionado = st.selectbox('Seleccione el Departamento', df['DEPARTAMENTO'].unique())
    df_filtrado = df[df['DEPARTAMENTO'] == departamento_seleccionado]
    # Filtrar por PROVINCIA
    provincia_seleccionada = st.selectbox('Seleccione la Provincia', df_filtrado['PROVINCIA'].unique())
    df_filtrado = df_filtrado[df_filtrado['PROVINCIA'] == provincia_seleccionada]
    # Filtrar por DISTRITO
    distrito_seleccionado = st.selectbox('Seleccione el Distrito', df_filtrado['DISTRITO'].unique())
    df_filtrado = df_filtrado[df_filtrado['DISTRITO'] == distrito_seleccionado]
    # Asegurar que los valores de NOMBRE_SITIO_DISPOSICION_FINAL_ADECUADA sean únicos y sumar QRESIDUOS_MUN
    suma_residuos = df_filtrado.groupby('DISTRITO')['QRESIDUOS_MUN'].sum().reset_index()
    # Crear el gráfico de barras con Plotly
    fig = px.bar(
        suma_residuos,
        x='DISTRITO',
        y='QRESIDUOS_MUN',
        color='DISTRITO',
        title=f'Total de Residuos Generados por Distrito en la Provincia de {provincia_seleccionada} - Departamento de {departamento_seleccionado}',
        labels={'QRESIDUOS_MUN': 'Total de Residuos Municipales Generados (Toneladas)', 'DISTRITO': 'Distrito'}
    )

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig)

    # Información adicional sobre la gráfica
    st.info("Esta gráfica muestra la cantidad de residuos sólidos generados en un distrito específico de la provincia y departamento seleccionados.", icon='😍')

    # Mostrar el DataFrame filtrado
    st.write('DataFrame Filtrado:', df_filtrado)

def mapa_residuos():
    st.header('Distribucion Geopolitica sobre Residuos Municipales ')
    # Cargar el archivo GeoJSON (asegúrate de que esté en la misma carpeta o pasa la ruta correcta)
    with open('peru_departamental_simple.geojson', 'r') as f:
        peru_departamentos = json.load(f)

    # Cargar el dataset con los datos de residuos (asegúrate de tener el archivo CSV)
    dataset = pd.read_csv('Residuos municipales generados anualmente.csv', sep=';', encoding='latin1')

    # Extraer los nombres de los departamentos para mostrarlos en el selectbox
    # Normalizar los nombres de los departamentos para evitar diferencias en mayúsculas/minúsculas o acentos
    departamentos = [feature['properties']['NOMBDEP'].strip().lower() for feature in peru_departamentos['features']]

    # Crear un mapa centrado en Perú
    m = folium.Map(location=[-9.19, -75.0152], zoom_start=5)

    # Crear un FeatureGroup para los límites departamentales
    fg = folium.FeatureGroup(name="Departamentos de Perú")

    # Función para crear un Popup dinámico para cada departamento
    def popup_info(feature):
        return folium.Popup(f"Departamento: {feature['properties']['NOMBDEP']}", max_width=300)

    # Seleccionar un departamento de la lista
    selected_department = st.selectbox("Selecciona un departamento", departamentos)

    # Función para cambiar el color del departamento seleccionado
    def style_function(feature):
        # Normalizar el nombre del departamento para evitar problemas de capitalización
        department_name = feature['properties']['NOMBDEP'].strip().lower()
        
        if department_name == selected_department:
            return {
                'fillColor': 'green',  # Color cuando el departamento está seleccionado
                'color': 'black',
                'weight': 2,
                'fillOpacity': 0.7
            }
        else:
            # Si no está seleccionado, usar un color predeterminado
            return {
                'fillColor': 'blue',  # Color predeterminado
                'color': 'black',
                'weight': 2,
                'fillOpacity': 0.4
            }

    # Agregar el archivo GeoJSON de los departamentos al mapa
    fg.add_child(folium.GeoJson(
        peru_departamentos,
        name='Departamentos',
        tooltip=folium.GeoJsonTooltip(fields=['NOMBDEP'], aliases=['Departamento'], localize=True),
        popup=popup_info,  # Usamos la función para el popup dinámico
        style_function=style_function  # Usamos la función de estilo dinámica
    ))

    # Agregar el FeatureGroup al mapa
    m.add_child(fg)

    # Agregar controles de capa para poder activar o desactivar la capa
    folium.LayerControl().add_to(m)

    # Renderizar el mapa con Streamlit usando st_folium
    out = st_folium(
        m,
        width=1200,
        height=500
    )

    # Asegurarse de que el nombre del departamento seleccionado esté en formato correcto
    # Convertir a minúsculas para evitar problemas de coincidencia
    selected_department_normalized = selected_department.strip().lower()

    # Filtrar los datos del dataset según el departamento seleccionado
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
    st.markdown('<div class="espacio-arriba"></div>', unsafe_allow_html=True)  # Espacio personalizado
    # Introducción del proyecto
    st.write("""
    Bienvenidos a nuestra página web, donde presentaremos información relevante sobre la generación y disposición de los residuos sólidos municipales en Perú, mediante gráficos y análisis detallados de los datos.
    """)
    st.markdown('<div class="espacio-arriba"></div>', unsafe_allow_html=True)  # Espacio personalizado
    # Textito primera columna
    st.header('Introducción a los Residuos Municipales')
    st.write("""
    Los residuos sólidos municipales comprenden todos los desechos generados por las actividades urbanas, que incluyen materiales desechados de hogares, comercios, instituciones públicas y privadas, y espacios públicos en general. En Perú, la generación de residuos municipales ha experimentado un aumento considerable debido al crecimiento poblacional y a la expansión de las áreas urbanas.
    """)
    st.write("""
    El manejo adecuado de los residuos municipales es un desafío clave para la sostenibilidad y la salud pública en el país. A través de este proyecto, analizamos la cantidad y distribución de los residuos generados anualmente en diversas regiones de Perú, con el objetivo de proporcionar datos relevantes para mejorar las políticas de gestión y reciclaje, y así contribuir a un entorno más limpio y saludable.
    """)
    st.markdown('<div class="espacio-arriba"></div>', unsafe_allow_html=True)  # Espacio personalizado
    # Imagen segunda columna
    st.image('plan_manejo.png', caption='Extraído de Google', use_column_width=True)
    st.markdown('<div class="espacio-arriba"></div>', unsafe_allow_html=True)  # Espacio personalizado
    # Texto horizontal después de las columnas
    st.write("""
    Este proyecto busca mostrar cómo la generación de residuos municipales varía a lo largo de los años en Perú, analizando tendencias y factores que influyen en la cantidad de residuos generados anualmente. Utilizamos Streamlit para crear una interfaz interactiva que permita visualizar estos datos de manera clara.
    """)
    st.markdown('<div class="espacio-arriba"></div>', unsafe_allow_html=True)  # Espacio personalizado
    # División en tres columnas para los objetivos
    st.header('Generación Anual de Residuos Sólidos Municipales')
    st.write("""
    Los residuos sólidos municipales se generan de manera constante en todas las ciudades del país. La cantidad de residuos generados depende de varios factores como el crecimiento poblacional, el consumo, y las prácticas de manejo de residuos en las distintas regiones. Es importante entender cómo varía esta generación anual para poder mejorar las políticas de manejo, reciclaje y disposición final.
    """)
    # Columnas para los objetivos
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
elif option == ' Departamental':
    contar_residuos()
elif option == ' Regional':
    residuos_region()
elif option == ' Domic./No Domic. y  Urbanos/Rural':
    residuos_departamento()
elif option == 'Gráfico Anual':
    residuos_departamento_anio()
elif option == 'lugar en especifico':
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

