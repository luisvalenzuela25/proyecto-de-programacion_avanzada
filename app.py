import streamlit as st
import pandas as pd
import numpy as np
# Título de la aplicación
st.title('RESIDUOS MUNICIPALES GENERADOS ANUALMENTE (MINISTERIO DEL AMBIENTE)')
# Widget para cargar el archivo CSV
uploaded_file = st.file_uploader("Residuos municipales generados anualmente.csv", type=["csv"])

if uploaded_file is not None:
    # Leer el archivo CSV usando pandas
    df = pd.read_csv(uploaded_file)

    # Mostrar los primeros 5 registros del DataFrame
    st.write("Vista previa del archivo CSV:")
    st.dataframe(df.head())  # Muestra las primeras 5 filas

