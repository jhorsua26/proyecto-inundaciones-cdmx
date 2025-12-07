import pandas as pd

def cargar_probabilidades_riesgo(alcaldia):
    """
    Carga la probabilidad de cada nivel de riesgo para una alcaldía
    desde data/tabla_probabilidad_completa.csv
    """
    try:
        # Cargar tabla de probabilidades desde la carpeta data/
        df = pd.read_csv('data/tabla_probabilidad_completa.csv')
        
        # Buscar alcaldía
        fila = df[df['alcaldia'] == alcaldia]
        
        if fila.empty:
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
        
        fila = fila.iloc[0]
        return {
            'riesgo_1': fila['riesgo_1'],
            'riesgo_2': fila['riesgo_2'],
            'riesgo_3': fila['riesgo_3'],
            'riesgo_4': fila['riesgo_4'],
            'riesgo_5': fila['riesgo_5'],
            'riesgo_promedio': fila['riesgo_promedio']
        }
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