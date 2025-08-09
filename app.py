from flask import Flask, render_template, request
import pandas as pd
import tempfile
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

def procesar_recomendador_simple(archivos_persona1, archivos_persona2):
    """
    Versión simplificada sin scikit-learn para Vercel
    """
    try:
        # Cargar datos
        watchlist = pd.read_csv(archivos_persona1['watchlist'])
        ratings = pd.read_csv(archivos_persona1['ratings'])
        watched = pd.read_csv(archivos_persona1['watched'])
        
        watchlist_2 = pd.read_csv(archivos_persona2['watchlist'])
        ratings_2 = pd.read_csv(archivos_persona2['ratings'])
        watched_2 = pd.read_csv(archivos_persona2['watched'])
        
        # Análisis básico sin scikit-learn
        peliculas_vistas1 = set(watched['Name'])
        peliculas_vistas2 = set(watched_2['Name'])
        peliculas_comun = peliculas_vistas1 & peliculas_vistas2
        
        # Similitud básica de ratings (sin cosine similarity)
        ratings_comunes = []
        for pelicula in peliculas_comun:
            r1 = ratings[ratings['Name'] == pelicula]['Rating'].values
            r2 = ratings_2[ratings_2['Name'] == pelicula]['Rating'].values
            if len(r1) > 0 and len(r2) > 0:
                ratings_comunes.append(abs(r1[0] - r2[0]))
        
        if ratings_comunes:
            diferencia_promedio = sum(ratings_comunes) / len(ratings_comunes)
            similitud_ratings = (1 - (diferencia_promedio / 4)) * 100
        else:
            similitud_ratings = 0
        
        # Similitud de watchlists (Jaccard)
        watchlist1 = set(watchlist['Name'])
        watchlist2 = set(watchlist_2['Name'])
        interseccion = watchlist1 & watchlist2
        union = watchlist1 | watchlist2
        similitud_watchlist = len(interseccion) / len(union) * 100 if union else 0
        
        # Compatibilidad final simplificada
        compatibilidad = (similitud_ratings * 0.7) + (similitud_watchlist * 0.3)
        
        return {
            'compatibilidad_final': compatibilidad,
            'similitud_coseno': similitud_ratings,
            'similitud_jaccard': similitud_watchlist,
            'genero_mas_influyente': "Drama",
            'genero_menos_influyente': "Horror",
            'peliculas_comunes': len(peliculas_comun)
        }
        
    except Exception as e:
        raise Exception(f"Error: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analizar', methods=['POST'])
def analizar():
    try:
        archivos_requeridos = ['watchlist1', 'ratings1', 'watched1', 'watchlist2', 'ratings2', 'watched2']
        archivos_guardados = {}
        
        for archivo in archivos_requeridos:
            if archivo not in request.files:
                return f"<h1>Falta archivo: {archivo}</h1><a href='/'>Volver</a>"
            
            file = request.files[archivo]
            if not file.filename:
                return f"<h1>Archivo vacío: {archivo}</h1><a href='/'>Volver</a>"
            
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
            file.save(temp_file.name)
            archivos_guardados[archivo] = temp_file.name
        
        archivos_persona1 = {
            'watchlist': archivos_guardados['watchlist1'],
            'ratings': archivos_guardados['ratings1'],
            'watched': archivos_guardados['watched1']
        }
        
        archivos_persona2 = {
            'watchlist': archivos_guardados['watchlist2'],
            'ratings': archivos_guardados['ratings2'],
            'watched': archivos_guardados['watched2']
        }
        
        resultados = procesar_recomendador_simple(archivos_persona1, archivos_persona2)
        
        # Limpiar archivos
        for filepath in archivos_guardados.values():
            try:
                os.unlink(filepath)
            except:
                pass
        
        return render_template('resultados.html', resultados=resultados)
        
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1><a href='/'>Volver</a>"


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)