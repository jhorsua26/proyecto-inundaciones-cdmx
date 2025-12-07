import requests

# Clave de API de OpenWeather
API_KEY = "3c5e5740311fde42201d81d3f818a098"

def obtener_datos_meteorologicos(alcaldia):
    # Coordenadas de las alcaldías
    coordenadas = {
        'Azcapotzalco': (19.4833, -99.1833),
        'Benito_Juarez': (19.4000, -99.1500),
        'Coyoacan': (19.3333, -99.1667),
        'Cuajimalpa_de_Morelos': (19.3333, -99.2833),
        'Cuauhtemoc': (19.4326, -99.1332),
        'Gustavo_A._Madero': (19.4833, -99.1000),
        'Iztacalco': (19.4000, -99.0833),
        'Iztapalapa': (19.3333, -99.0667),
        'La_Magdalena_Contreras': (19.3000, -99.2000),
        'Miguel_Hidalgo': (19.4333, -99.2000),
        'Milpa_Alta': (19.2167, -99.0333),
        'Tlalpan': (19.2667, -99.1333),
        'Tlahuac': (19.2833, -98.9833),
        'Venustiano_Carranza': (19.4667, -99.0833),
        'Xochimilco': (19.2500, -99.1000),
        'Alvaro_Obregon': (19.3833, -99.2167)
    }
    
    coords = coordenadas.get(alcaldia, (19.4326, -99.1332))  # Por defecto CDMX
    lat, lon = coords
    
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=es"
    try:
        response = requests.get(url)
        data = response.json()
        
        # Obtener datos
        mm_hora = data.get('rain', {}).get('1h', 0)  # Lluvia en la última hora
        temperatura = data.get('main', {}).get('temp', 0)
        humedad = data.get('main', {}).get('humidity', 0)
        descripcion_clima = data.get('weather', [{}])[0].get('description', 'Desconocido')
        velocidad_viento = data.get('wind', {}).get('speed', 0)
        
        return mm_hora, temperatura, humedad, descripcion_clima, velocidad_viento
    except Exception as e:
        print(f"Error obteniendo datos meteorológicos: {e}")
        return 0, 0, 0, 'Desconocido', 0  # Valores por defecto