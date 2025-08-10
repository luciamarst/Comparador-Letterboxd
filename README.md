# Comparador de compatibilidad basado en perfiles de Letterboxd

El comparador ha sido desarrollado teniendo en cuenta los datos disponibles sobre películas vistas, puntuación de películas vistas y las watchlists de ambas personas.
A partir de estos datos, se aplican diferentes métricas para obtener un resultado final que refleja el nivel de compatibilidad cinematográfica.

Dado que los archivos .csv exportables desde Letterboxd contienen información limitada, ha sido necesario incorporar un archivo auxiliar — [movies.csv](https://grouplens.org/datasets/movielens) — con datos adicionales como el género de cada película.
Este archivo, obtenido del portal GroupLens, permite enriquecer el análisis y realizar los cálculos necesarios para una comparación más completa.
