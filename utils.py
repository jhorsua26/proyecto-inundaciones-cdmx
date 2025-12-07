import pandas as pd

def cargar_probabilidades_riesgo(alcaldia):
    """
    Carga la probabilidad de cada nivel de riesgo para una alcaldía
    desde tabla_probabilidad_completa.csv
    """
    try:
        # Cargar tabla de probabilidades
        df = pd.read_csv('tabla_probabilidad_completa.csv')
        
        # Filtrar datos para la alcaldía específica
        datos_alcaldia = df[df['Alcaldia'] == alcaldia]
        
        if datos_alcaldia.empty:
            print(f"⚠️ Alcaldía no encontrada: {alcaldia}")
            # Valores por defecto si no se encuentra la alcaldía
            return {
                'riesgo_1': 0.2,
                'riesgo_2': 0.2,
                'riesgo_3': 0.2,
                'riesgo_4': 0.2,
                'riesgo_5': 0.2,
                'riesgo_promedio': 3.0
            }
        
        # Crear diccionario con probabilidades
        probabilidades = {}
        for nivel in [1, 2, 3, 4, 5]:
            fila = datos_alcaldia[datos_alcaldia['Nivel de riesgo (k)'] == nivel]
            if not fila.empty:
                probabilidad = fila.iloc[0]['Probabilidad p(riesgo k)']
            else:
                probabilidad = 0.0  # Valor por defecto si no hay datos
            probabilidades[f'riesgo_{nivel}'] = probabilidad
        
        # Calcular riesgo promedio
        riesgo_promedio = datos_alcaldia['riesgo_promedio'].iloc[0] if 'riesgo_promedio' in datos_alcaldia.columns else 3.0
        
        resultado = probabilidades.copy()
        resultado['riesgo_promedio'] = riesgo_promedio
        
        return resultado
    except Exception as e:
        print(f"Error al cargar probabilidades: {e}")
        # Valores por defecto
        return {
            'riesgo_1': 0.2,
            'riesgo_2': 0.2,
            'riesgo_3': 0.2,
            'riesgo_4': 0.2,
            'riesgo_5': 0.2,
            'riesgo_promedio': 3.0
        }

def obtener_riesgo_base(alcaldia):
    """
    Obtiene el riesgo base de una alcaldía basado en la probabilidad más alta
    """
    probabilidades = cargar_probabilidades_riesgo(alcaldia)
    
    # Determinar el nivel de riesgo base (el más probable)
    max_prob = 0
    riesgo_base = 3  # Valor por defecto
    
    for nivel in [1, 2, 3, 4, 5]:
        prob = probabilidades[f'riesgo_{nivel}']
        if prob > max_prob:
            max_prob = prob
            riesgo_base = nivel
    
    return riesgo_base, probabilidades

def convertir_5_a_3(nivel_5):
    """
    Convierte nivel de riesgo 1-5 a 1-3 para interfaz
    """
    if nivel_5 <= 2:
        return 1  # Bajo
    elif nivel_5 == 3:
        return 2  # Medio
    else:
        return 3  # Alto