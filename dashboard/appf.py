import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import folium_static
import jenkspy
from branca.colormap import LinearColormap
import numpy as np
st.set_page_config(
    page_title="RECHERCHE PAR COORDS",
    page_icon="🔍",
    layout="centered",  
)

st.markdown("<h2 style='font-size:32px; text-align:center;'>recherche par coordonnées </h2>", unsafe_allow_html=True)
# Charger les données géospatiales depuis le fichier GeoParquet
path_to_geoparquet = "dashboard/donnees/geoparquet/OUTPUT1500.geoparquet"
gdf = gpd.read_parquet(path_to_geoparquet)

def jenks_classifier(data, column, k=5):
    values = data[column].values
    breaks = jenkspy.jenks_breaks(values, k)
    return breaks

option = st.sidebar.radio("Choisir une option", ("Attribut", "Propriété"))

search_coords = st.sidebar.text_input("Coordonnées du point à rechercher (par exemple: -4.67836,33.39132)")
search_button = st.sidebar.button("Rechercher")

if option == "Attribut":
    # Liste des attributs pour le choix
    attributs = ['temperature', 'pression_atmosph', 'pluviometrie']
    selected_attribute = st.sidebar.selectbox("Sélectionner un attribut", attributs)

    # Liste des jours pour le choix
    jours = [6, 5, 4, 3, 2, 1, 0]
    selected_day = st.sidebar.selectbox("Sélectionner un jour", jours)

    # Filtrer les données en fonction de l'attribut et du jour sélectionnés
    selected_column_day = f'{selected_attribute}jour{selected_day}'
    filtered_data = gdf[gdf[selected_column_day] >= 0]

    # Classer les valeurs en utilisant la méthode de Jenks
    breaks = jenks_classifier(filtered_data, selected_column_day, k=5)

    # Créer une carte Folium centrée sur la moyenne des coordonnées des géométries
    m = folium.Map(location=[gdf['geometry'].centroid.y.mean(), gdf['geometry'].centroid.x.mean()], zoom_start=4)

    # Définir l'échelle pour les symboles proportionnels
    scale = filtered_data[selected_column_day].max()

    # Ajouter les données à la carte en tant que symboles proportionnels
    for idx, row in filtered_data.iterrows():
        popup = f"{selected_column_day}: {row[selected_column_day]}"
        
        # Assigner une couleur en fonction de la classe Jenks
        color = '#f1eef6' if row[selected_column_day] <= breaks[1] else \
                '#bdc9e1' if row[selected_column_day] <= breaks[2] else \
                '#74a9cf' if row[selected_column_day] <= breaks[3] else \
                '#2b8cbe' if row[selected_column_day] <= breaks[4] else \
                '#045a8d'  

        folium.CircleMarker(
            location=[row['geometry'].y, row['geometry'].x],
            radius= 5,  # Ajuster l'échelle pour la taille des symboles
            popup=popup,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.6,
        ).add_to(m)
    if selected_attribute=='temperature':
      min=0
      max=100
    elif selected_attribute=="pression_atmosph":
      min=0
      max=20
    else:
      min=0
      max=50
    class_limits1 = np.linspace(min, max, num=6) 
    
    # Afficher la carte dans Streamlit


else:
    # Liste des propriétés pour le choix
    proprietes = [ 'humidité', 'Reflectance']
    selected_property = st.sidebar.selectbox("Sélectionner une propriété", proprietes)

    # Classer les valeurs en utilisant la méthode de Jenks
    breaks = jenks_classifier(gdf, selected_property, k=5)

    # Créer une carte Folium centrée sur la moyenne des coordonnées des géométries
    m = folium.Map(location=[gdf['geometry'].centroid.y.mean(), gdf['geometry'].centroid.x.mean()], zoom_start=4)

      # Définir les couleurs pour les classes
    colors = ['#f1eef6', '#bdc9e1', '#74a9cf', '#2b8cbe', '#045a8d']
    
    # Ajouter les données à la carte avec des couleurs pour les classes
    for idx, row in gdf.iterrows():
        popup = f"{selected_property}: {row[selected_property]}"
        
        # Assigner une couleur en fonction de la classe Jenks
        color = '#f1eef6' if row[selected_property] <= breaks[1] else \
                '#bdc9e1' if row[selected_property] <= breaks[2] else \
                '#74a9cf' if row[selected_property] <= breaks[3] else \
                '#2b8cbe' if row[selected_property] <= breaks[4] else \
                '#045a8d'
       
        value = row[selected_property]

        folium.CircleMarker(
            location=[row['geometry'].y, row['geometry'].x],
            radius=5,
            popup=popup,
            color=color,
            fill=True, 
            fill_color=color,
            fill_opacity=0.6,
        ).add_to(m)
        min,max=0,1
if search_button:
    point_found = False

    if search_coords:
        search_longitude, search_latitude = map(float, search_coords.split(','))

        for idx, row in gdf.iterrows():
            if round(row['geometry'].x, 3) == round(search_longitude, 3) and round(row['geometry'].y, 3) == round(search_latitude, 3):
                point_found = True
                popup = f"Point trouvé aux coordonnées: {row['geometry'].x}, {row['geometry'].y}"
                folium.Marker(
                    location=[row['geometry'].y, row['geometry'].x],
                    popup=popup,
                    icon=folium.Icon(color='green', icon='info-sign')
                ).add_to(m)

        if not point_found:
            st.sidebar.write("Le point spécifié n'existe pas dans les données.")
colors=['#f1eef6','#bdc9e1','#74a9cf','#2b8cbe','#045a8d']    
cmap = LinearColormap(colors=colors, vmin = round(min, 2),vmax = round(max, 2))
cmap.caption = ' Légende'
cmap.add_to(m)

folium_static(m)
