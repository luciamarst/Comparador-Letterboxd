import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# Datos de la persona 1
watchlist = pd.read_csv('archivos/watchlist.csv')
ratings = pd.read_csv('archivos/ratings.csv')
#reviews = pd.read_csv('archivos/reviews.csv')
watched = pd.read_csv('archivos/watched.csv')

# Datos de la persona 2
watchlist_2 = pd.read_csv('archivos/watchlist-2.csv')
ratings_2 = pd.read_csv('archivos/ratings-2.csv')
#reviews_2 = pd.read_csv('archivos/reviews_2.csv')
watched_2 = pd.read_csv('archivos/watched-2.csv')


# Primeramente, realizaremos un primer análisis en funcion de las películas que ambas personas han visto,
#  es decir, la intersección de los dos conjuntos de datos.

peliculas_vistas1 = set(watched['Name'])
peliculas_vistas2 = set(watched_2['Name'])

peliculas_comun = peliculas_vistas1 & peliculas_vistas2 #& simboliza la intersección de conjuntos

# Ahora que tenemos las peliculas que ambas personas vieron, podemos crear una tabla con cada pelicula
# donde las columnas serán el rating de cada persona y la película en cuestión.
# Usar una lista para recolectar los datos y luego crear el DataFrame
comparacion_rows = []
for pelicula in peliculas_comun:
    rating1 = ratings.loc[ratings['Name'] == pelicula, 'Rating'].values
    rating2 = ratings_2.loc[ratings_2['Name'] == pelicula, 'Rating'].values

    comparacion_rows.append({
        'Movie': pelicula,
        'Rating_Person1': rating1[0] if len(rating1) > 0 else None,
        'Rating_Person2': rating2[0] if len(rating2) > 0 else None
    })

comparacion = pd.DataFrame(comparacion_rows, columns=['Movie', 'Rating_Person1', 'Rating_Person2'])

# Una vez tenemos la tabla comparativa, podemos analizar la compatibilidad entre las dos personas.
compatibilidad = comparacion.dropna()  # Eliminar filas con NaN

# Para calcular la similitud entre ratings de peliculas vistas, vamos a usar una combinacion de la
# diferencia absoluta promecio

# DIFERENCIA ABSOLUTA PROMEDIO
diferencia_promedio = np.mean(abs(compatibilidad['Rating_Person1'] - compatibilidad['Rating_Person2']))
diferencia_maxima  = 4 # Porque el raintg de Letterboxd varía entre 0 y 5
similitud_ratings_dif_abs = (1 - (diferencia_promedio / diferencia_maxima)) * 100


# SIMILITUD COSENO
from sklearn.metrics.pairwise import cosine_similarity
ratings1 = comparacion['Rating_Person1'].values.reshape(1, -1)
ratings2 = comparacion['Rating_Person2'].values.reshape(1, -1)
similitud_coseno = cosine_similarity(ratings1, ratings2)[0][0]
similitud_coseno = similitud_coseno * 100


peliculas_watchlist1 = set(watchlist['Name'].values)
peliculas_watchlist2 = set(watchlist_2['Name'].values)

# Ahora que tenemos ambos conjutnos, vamos a utilizar el coeficiente de Jaccard para ver 
# cual es la similitud entre las dos listas de seguimiento.
intersection = peliculas_watchlist1.intersection(peliculas_watchlist2)
union = peliculas_watchlist1.union(peliculas_watchlist2)
similitud_jaccard = len(intersection) / len(union) * 100


peliculas_watched = set(watched['Name'].values)
peliculas_watchlist = set(watchlist_2['Name'].values)

# Una vez tenemos estos datos, aplicamos el coeficiente de Jaccard para ver la similitud entre las películas vistas por la persona 1 y la watchlist de la persona 2.
intersection = peliculas_watched.intersection(peliculas_watchlist)  
union = peliculas_watched.union(peliculas_watchlist)
similitud_jaccard_watched_watchlist = len(intersection) / len(union) * 100

# Ahora tenemos que realizar el mismo proceso pero de manera inversa ya que ambas personas no han visto las mismas peliculas ni tienen la misma watchlist.
peliculas_watched_2 = set(watched_2['Name'].values)
peliculas_watchlist_2 = set(watchlist['Name'].values)

# Aplicamos el coeficiente de Jaccard para ver la similitud entre las películas vistas por la persona 2 y la watchlist de la persona 1.
intersection = peliculas_watched_2.intersection(peliculas_watchlist_2)
union = peliculas_watched_2.union(peliculas_watchlist_2)
similitud_jaccard_watched_watchlist_2 = len(intersection) / len(union) * 100


import re
movies = pd.read_csv('archivos/movies.csv')

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



    # Similitud ponderada por frecuencia
def calcular_similitud_ponderada():
    similitud_total = 0
    peso_total = 0
    
    for genero in generos:
        count1 = 0
        for titulo_pelicula, año_pelicula in intersecion_1:
            try:
                mask = movies['title_clean'] == titulo_pelicula
                if mask.any():
                    generos_pelicula = movies[mask]['genres'].iloc[0]
                    if pd.notna(generos_pelicula) and genero in generos_pelicula:
                        count1 += 1
            except (IndexError, KeyError):
                continue
                
        count2 = 0
        for titulo_pelicula, año_pelicula in intersecion_2:
            try:
                mask = movies['title_clean'] == titulo_pelicula
                if mask.any():
                    generos_pelicula = movies[mask]['genres'].iloc[0]
                    if pd.notna(generos_pelicula) and genero in generos_pelicula:
                        count2 += 1
            except (IndexError, KeyError):
                continue
        
        if count1 > 0 and count2 > 0:
            peso = count1 + count2
            similitud = min(count1, count2) / max(count1, count2) * 100
            similitud_total += similitud * peso
            peso_total += peso
    
    return similitud_total / peso_total if peso_total > 0 else 0

similitud_ponderada_genero = calcular_similitud_ponderada()


# Utilizamos las metricas anteriores para calcular la compatibilidad final.
compatibilidad_final = (
    (similitud_coseno * 0.35) +
    (similitud_jaccard * 0.1) +
    (similitud_jaccard_watched_watchlist * 0.1) +
    (similitud_jaccard_watched_watchlist_2 * 0.1) +
    (similitud_ponderada_genero * 0.35)
)

print("Basado en las valoraciones de películas vistas, las watchlists y los géneros de las películas vistas.")
print("Donde se ha dado más peso a la similitud de ratings y géneros, y menos a las watchlists.")


print(f"\n=== COMPATIBILIDAD FINAL ENTRE LAS DOS PERSONAS ===")
print(f"Compatibilidad final: {compatibilidad_final:.2f}%")



# Encontrar el género con mayor similitud ponderada
print()
genero_mas_influyente = max(similitud_generos, key=similitud_generos.get)
print(f"Género más influyente: {genero_mas_influyente} con {similitud_generos[genero_mas_influyente]:.2f}%")


# Obtener la intersección de títulos limpios y películas vistas por ambas personas
peliculas_mismo_genero = set(movies['title_clean']) & set(watched['Name'].values) & set(watched_2['Name'].values) & set(movies[movies['genres'].str.contains(genero_mas_influyente, na=False)]['title_clean'].values)

print(f"En películas como: {list(peliculas_mismo_genero)[:5]}")  # Muestra las primeras 5 películas del conjunto

# Encontrar el género con menor similitud ponderada
print()
genero_menos_influyente = min(similitud_generos, key=similitud_generos.get)
print(f"Género menos influyente: {genero_menos_influyente} con {similitud_generos[genero_menos_influyente]:.2f}%")


# Obtener la intersección de títulos limpios y películas vistas por ambas personas
peliculas_mismo_genero = set(movies['title_clean']) & set(watched['Name'].values) & set(watched_2['Name'].values) & set(movies[movies['genres'].str.contains(genero_menos_influyente, na=False)]['title_clean'].values)
print(f"Películas de {genero_menos_influyente} en común: {list(peliculas_mismo_genero)[:5]}")  # Muestra las primeras 5 películas del conjunto