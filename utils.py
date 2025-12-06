import pandas as pd
import unicodedata

def normalizar_nombre(nombre):
    nombre = unicodedata.normalize('NFKD', nombre).encode('ascii', errors='ignore').decode()
    nombre = nombre.replace(" ", "_").lower()
    return nombre

def cargar_features_atlas(alcaldia):
    df = pd.read_csv('data/datos_lluvia_con_riesgo_actualizado.csv')
    df['alcaldia_normalizada'] = df['alcaldia'].apply(normalizar_nombre)

    # Normalizar la alcaldía que llega
    alcaldia_normalizada = normalizar_nombre(alcaldia)

    # Filtrar fila
    fila = df[df['alcaldia_normalizada'] == alcaldia_normalizada]

    if fila.empty:
        print(f"⚠️ Alcaldía no encontrada en datos: {alcaldia}")
        # Valores por defecto
        return 3.0, 1.0  # riesgo_promedio, riesgo_std

    fila = fila.iloc[0]
    riesgo_promedio = fila['riesgo_promedio']
    riesgo_std = fila['riesgo_std']

    return riesgo_promedio, riesgo_std