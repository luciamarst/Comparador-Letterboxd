from flask import Flask, render_template, request
import pandas as pd
import tempfile
import os
import re
from collections import Counter

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
        
         # Cargar movies.csv para géneros
        try:
            movies = pd.read_csv('movies.csv')
            print("movies.csv cargado exitosamente")
        except FileNotFoundError:
            print("movies.csv no encontrado, usando géneros por defecto")
            movies = None

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
        

        #Nombres de las peliculas
        # Nombres de las películas - LIMPIEZA COMPLETA
        def limpiar_titulo(titulo):
            if pd.notna(titulo):
                # Extraer año primero
                lanzamiento = re.search(r'\((\d{4})\)', titulo)
                año = lanzamiento.group(1) if lanzamiento else None
                
                # Quitar fecha entre paréntesis y espacios finales
                titulo_limpio = re.sub(r'\s*\(\d{4}\)$', '', titulo.strip())
                
                return (titulo_limpio, año)
            return (None, None)

        # Aplicar la limpieza a todos los títulos
        movies_data = []
        for titulo in movies['title'].values:
            titulo_limpio, año = limpiar_titulo(titulo)
            movies_data.append((titulo_limpio, año))

        # También crear una versión limpia del DataFrame para usar después
        # Crear columnas separadas en el DataFrame
        movies['title_clean'] = [data[0] for data in movies_data]
        movies['year'] = [data[1] for data in movies_data]

        # Crear conjuntos con tuplas (titulo, año) para comparaciones más precisas
        peliculas_con_anyo = set((titulo, año) for titulo, año in movies_data if titulo is not None)

        peliculas_letterboxd_1 = set()
        for _, row in watched.iterrows():
            if pd.notna(row['Name']) and pd.notna(row['Year']):
                # Convertir año a string para que coincida con movies_data
                año_str = str(int(row['Year'])) if isinstance(row['Year'], (int, float)) else str(row['Year'])
                peliculas_letterboxd_1.add((row['Name'], año_str))

        peliculas_letterboxd_2 = set()
        for _, row in watched_2.iterrows():
            if pd.notna(row['Name']) and pd.notna(row['Year']):
                año_str = str(int(row['Year'])) if isinstance(row['Year'], (int, float)) else str(row['Year'])
                peliculas_letterboxd_2.add((row['Name'], año_str))

        # AHORA SÍ PUEDES HACER LA INTERSECCIÓN CON TÍTULO + AÑO
        intersecion_1 = peliculas_con_anyo & peliculas_letterboxd_1
        intersecion_2 = peliculas_con_anyo & peliculas_letterboxd_2



        generos = set(movies['genres'].values)

        # En el dataset los generos vienen separados por pipe (|), por lo que vamos a separarlos y quedarnos con los únicos.
        todos_los_generos = []
        for generos_fila in movies['genres'].values:
            if pd.notna(generos_fila):  # Verificar que no sea NaN
                generos_individuales = generos_fila.split('|')
                todos_los_generos.extend([genero.strip() for genero in generos_individuales])


        # Crear set de géneros únicos, excluyendo vacíos
        generos = set(genero for genero in todos_los_generos if genero and genero != '(no genres listed)')

        # Calculamos la similitud entre géneros de las películas vistas por ambas personas
        similitud_generos = {}

        for genero in generos:
            # Filtrar películas vistas por persona 1 y contar cuántas tienen el género actual
            contador_genero_1 = 0
            for titulo_pelicula, año_pelicula in intersecion_1:
                # Buscar la película en el DataFrame por título limpio
                try:
                    mask = movies['title_clean'] == titulo_pelicula
                    if mask.any():
                        generos_pelicula = movies[mask]['genres'].iloc[0]
                        if pd.notna(generos_pelicula) and genero in generos_pelicula:
                            contador_genero_1 += 1
                except (IndexError, KeyError):
                    continue
            
            contador_genero_2 = 0
            for titulo_pelicula, año_pelicula in intersecion_2:
                try:
                    mask = movies['title_clean'] == titulo_pelicula
                    if mask.any():
                        generos_pelicula = movies[mask]['genres'].iloc[0]
                        if pd.notna(generos_pelicula) and genero in generos_pelicula:
                            contador_genero_2 += 1
                except (IndexError, KeyError):
                    continue
            
            if contador_genero_1 > 0 and contador_genero_2 > 0:
                similitud_generos[genero] = min(contador_genero_1, contador_genero_2) / max(contador_genero_1, contador_genero_2) * 100

        
        genero_menos_influyente = min(similitud_generos, key=similitud_generos.get)
        print(f"Género menos influyente: {genero_menos_influyente} con {similitud_generos[genero_menos_influyente]:.2f}%")

        genero_mas_influyente = max(similitud_generos, key=similitud_generos.get)
        print(f"Género más influyente: {genero_mas_influyente} con {similitud_generos[genero_mas_influyente]:.2f}%")

        return {
            'compatibilidad_final': compatibilidad,
            'similitud_coseno': similitud_ratings,
            'similitud_jaccard': similitud_watchlist,
            'genero_mas_influyente': genero_mas_influyente,
            'genero_menos_influyente': genero_menos_influyente,
            'peliculas_comunes': len(peliculas_comun)
        }
        
    except Exception as e:
        print(f"Error en procesar_recomendador_simple: {str(e)}")
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
          
            # CAMBIO PARA VERCEL: usar /tmp/
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv', dir='/tmp')
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


# IMPORTANTE: Para Vercel, exportar la app
app_handler = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)