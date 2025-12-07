from flask import Flask, render_template, request, jsonify
import pandas as pd
import json
import folium
from api_meteorologia import obtener_datos_meteorologicos
from utils import cargar_probabilidades_riesgo, obtener_riesgo_base, convertir_5_a_3

app = Flask(__name__)

# Cargar GeoJSON de alcaldías
with open('data/alcaldias_cdmx.json', 'r', encoding='utf-8') as f:
    geojson_data = json.load(f)

def crear_mapa_riesgo():
    alcaldias = [feature['properties']['NOMGEO'] for feature in geojson_data['features']]

    # Obtener lluvia actual para cada alcaldía
    lluvias = {}
    for alcaldia in alcaldias:
        # Obtener solo lluvia actual (sin usar atlas para el mapa)
        mm_hora, temperatura, humedad, descripcion_clima, velocidad_viento = obtener_datos_meteorologicos(alcaldia)
        lluvias[alcaldia] = mm_hora

    # Crear mapa base
    mapa = folium.Map(location=[19.4326, -99.1332], zoom_start=11)

    def estilo_lluvia(feature):
        alcaldia_nombre = feature['properties']['NOMGEO']
        mm_hora = lluvias.get(alcaldia_nombre, 0)  # Valor por defecto
        
        # Colorear según intensidad de lluvia (rangos realistas)
        if mm_hora <= 10:
            color = 'green'        # Sin lluvia o muy ligera
        elif mm_hora <= 30:
            color = 'yellow'       # Lluvia moderada
        else:
            color = 'orange'       # Lluvia fuerte o muy fuerte
        
        return {
            'fillColor': color,
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.6
        }

    folium.GeoJson(
        geojson_data,
        style_function=estilo_lluvia,
        tooltip=folium.GeoJsonTooltip(fields=['NOMGEO'], aliases=['Alcaldía'])
    ).add_to(mapa)

    return mapa._repr_html_()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calcular_riesgo', methods=['GET'])
def calcular_riesgo():
    try:
        mapa_html = crear_mapa_riesgo()
        return jsonify({'mapa': mapa_html})
    except Exception as e:
        print(f"Error en calcular_riesgo: {e}")
        return jsonify({'error': str(e)})

@app.route('/predecir', methods=['POST'])
def predecir():
    try:
        data = request.json
        alcaldia = data['alcaldia']
        esta_lloviendo = data['esta_lloviendo']

        # Obtener datos meteorológicos
        mm_hora, temperatura, humedad, descripcion_clima, velocidad_viento = obtener_datos_meteorologicos(alcaldia)
        
        # Obtener riesgo base de la alcaldía (basado en tabla_probabilidad_completa.csv)
        riesgo_base, probabilidades = obtener_riesgo_base(alcaldia)

        # Nueva lógica: si no está lloviendo, riesgo = riesgo base
        if esta_lloviendo == 'no':
            riesgo = riesgo_base
            mensaje = f"Riesgo basado en datos históricos de {alcaldia}."
            recomendaciones = [
                "Mantente informado con autoridades locales.",
                "Sigue monitoreando las condiciones climáticas."
            ]
        else:
            # Si está lloviendo, ajustar riesgo con lluvia
            riesgo = riesgo_base
            
            # Ajustar con intensidad de lluvia (rangos realistas)
            if mm_hora > 30:
                riesgo = min(5, riesgo + 2)  # Sube 2 niveles con mucha lluvia
            elif mm_hora > 10:
                riesgo = min(5, riesgo + 1)  # Sube 1 nivel con lluvia moderada
            else:
                riesgo = max(1, riesgo - 1)  # Baja 1 nivel con poca lluvia
            
            # Ajustar con respuestas del usuario
            if 'condicion_drenaje' in data:
                condicion_drenaje = int(data['condicion_drenaje'])
                if condicion_drenaje == 3:  # Malo
                    riesgo = min(5, riesgo + 1)
                elif condicion_drenaje == 1:  # Bueno
                    riesgo = max(1, riesgo - 1)
            
            if 'inunda_con_lluvia' in data:
                inunda_con_lluvia = data['inunda_con_lluvia']
                if inunda_con_lluvia == 'si':
                    riesgo = min(5, riesgo + 1)

            # Mensaje de riesgo
            if riesgo <= 2:
                mensaje = f"Riesgo bajo en {alcaldia}. Mantente informado."
                recomendaciones = [
                    "Sigue monitoreando las condiciones climáticas.",
                    "Mantente informado con autoridades locales."
                ]
            elif riesgo <= 3:
                mensaje = f"Riesgo moderado en {alcaldia}. Mantente alerta."
                recomendaciones = [
                    "Evita transitar por calles con acumulación de agua.",
                    "Revisa que las coladeras estén despejadas.",
                    "Ten a la mano documentos importantes en lugar seguro."
                ]
            elif riesgo <= 4:
                mensaje = f"Riesgo alto en {alcaldia}. Toma precauciones."
                recomendaciones = [
                    "Evita salir si no es necesario.",
                    "Ten a la mano documentos importantes en lugar seguro.",
                    "Verifica que las salidas de emergencia estén despejadas."
                ]
            else:
                mensaje = f"¡Riesgo muy alto en {alcaldia}! Extrema precaución."
                recomendaciones = [
                    "Permanece en un lugar seguro.",
                    "Evita salir bajo ninguna circunstancia.",
                    "Contacta a autoridades si es necesario."
                ]

        # Convertir riesgo 1-5 a nivel 1-3 para la interfaz
        nivel_interfaz = convertir_5_a_3(riesgo)

        # Devolver JSON con todo
        return jsonify({
            'riesgo': nivel_interfaz,  # 1, 2 o 3 para la interfaz
            'riesgo_detalle': riesgo,  # 1-5 para el backend
            'mensaje': mensaje,
            'recomendaciones': recomendaciones,
            'datos_meteorologicos': {
                'mm_hora': mm_hora,
                'temperatura': temperatura,
                'humedad': humedad,
                'descripcion_clima': descripcion_clima,
                'velocidad_viento': velocidad_viento
            },
            'alcaldia': alcaldia,  # Mostrar alcaldía en la respuesta
            'probabilidades': probabilidades,  # Mostrar probabilidades usadas
            'contactos': {
                '911': 'Llama al 911 en caso de emergencia.',
                'proteccion_civil_cdmx': '55 56 83 17 17'
            },
            'redes_sociales': {
                'conagua': '@conagua_clima',
                'proteccion_civil_cdmx': '@PC_CDMX'
            }
        })
    except Exception as e:
        print(f"Error en predecir: {e}")
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)