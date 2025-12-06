from flask import Flask, render_template, request, jsonify
import joblib
import pandas as pd
import json
import folium
from api_meteorologia import obtener_datos_meteorologicos
from utils import cargar_features_atlas

app = Flask(__name__)

# Cargar modelo
modelo = joblib.load('modelo_riesgo_inundacion_con_atlas.pkl')

# Cargar GeoJSON de alcaldías
with open('data/alcaldias_cdmx.json', 'r', encoding='utf-8') as f:
    geojson_data = json.load(f)

def crear_mapa_riesgo():
    alcaldias = [feature['properties']['NOMGEO'] for feature in geojson_data['features']]

    riesgos = {}
    for alcaldia in alcaldias:
        mm_hora, _, _, _, _ = obtener_datos_meteorologicos(alcaldia)
        riesgo_promedio, riesgo_std = cargar_features_atlas(alcaldia)

        # Crear DataFrame con los mismos nombres de columnas que el modelo
        X = pd.DataFrame([[mm_hora, riesgo_promedio, riesgo_std]], 
                         columns=['mm_hora', 'riesgo_promedio', 'riesgo_std'])
        riesgo = modelo.predict(X)[0]
        riesgos[alcaldia] = int(riesgo)

    # Crear mapa base
    mapa = folium.Map(location=[19.4326, -99.1332], zoom_start=11)

    def estilo_riesgo(feature):
        alcaldia_nombre = feature['properties']['NOMGEO']
        riesgo = riesgos.get(alcaldia_nombre, 1)
        riesgo = int(riesgo)
        if riesgo == 1:
            color = 'green'
        elif riesgo == 2:
            color = 'orange'
        else:
            color = 'red'
        return {
            'fillColor': color,
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.6
        }

    folium.GeoJson(
        geojson_data,
        style_function=estilo_riesgo,
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

        mm_hora, temperatura, humedad, descripcion_clima, velocidad_viento = obtener_datos_meteorologicos(alcaldia)
        riesgo_promedio, riesgo_std = cargar_features_atlas(alcaldia)

        # Nueva lógica: si no está lloviendo, riesgo = 1
        if esta_lloviendo == 'no':
            riesgo = 1
            mensaje = "Riesgo bajo. No se reporta lluvia en este momento."
            recomendaciones = [
                "Mantente informado con autoridades locales.",
                "Sigue monitoreando las condiciones climáticas."
            ]
        else:
            # Crear DataFrame con los mismos nombres de columnas que el modelo
            X = pd.DataFrame([[mm_hora, riesgo_promedio, riesgo_std]], 
                             columns=['mm_hora', 'riesgo_promedio', 'riesgo_std'])
            
            riesgo = modelo.predict(X)[0]

            # Leer respuestas del usuario (solo si están presentes)
            condicion_drenaje = int(data.get('condicion_drenaje', 2))  # Por defecto: regular
            inunda_con_lluvia = data.get('inunda_con_lluvia', 'no')

            # Ajustar con respuestas del usuario
            if condicion_drenaje == 3:  # Malo
                riesgo = min(3, riesgo + 1)
            elif condicion_drenaje == 1:  # Bueno
                riesgo = max(1, riesgo - 1)

            if inunda_con_lluvia == 'si':
                riesgo = min(3, riesgo + 1)

            # Mensaje de riesgo
            if riesgo == 1:
                mensaje = "Riesgo bajo. Mantente informado."
                recomendaciones = [
                    "Sigue monitoreando las condiciones climáticas.",
                    "Mantente informado con autoridades locales."
                ]
            elif riesgo == 2:
                mensaje = "Riesgo moderado. Mantente alerta."
                recomendaciones = [
                    "Evita transitar por calles con acumulación de agua.",
                    "Revisa que las coladeras estén despejadas.",
                    "Ten a la mano documentos importantes en lugar seguro."
                ]
            else:
                mensaje = "¡Riesgo alto! Toma precauciones."
                recomendaciones = [
                    "Evita salir si no es necesario.",
                    "Ten a la mano documentos importantes en lugar seguro.",
                    "Verifica que las salidas de emergencia estén despejadas."
                ]

        # Devolver JSON con todo
        return jsonify({
            'riesgo': int(riesgo),
            'mensaje': mensaje,
            'recomendaciones': recomendaciones,
            'datos_meteorologicos': {
                'mm_hora': mm_hora,
                'temperatura': temperatura,
                'humedad': humedad,
                'descripcion_clima': descripcion_clima,
                'velocidad_viento': velocidad_viento
            },
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