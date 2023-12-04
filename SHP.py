import geopandas as gpd
import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import folium_static
import pandas as pd
from jenkspy import jenks_breaks
from branca.colormap import LinearColormap
# Chemin vers le fichier SHP
path_to_shapefile = "dashboard/donnees/shp/OUTPUT1500.shp"

# Charger les données à partir du fichier SHP
gdf = gpd.read_file(path_to_shapefile)


st.set_page_config(
    page_title="SHP",
    page_icon="🌍",
    layout="centered",  
)

# Titre de l'application
st.markdown("<h2 style='font-size:32px;text-align:center;'>visualisation SHP</h2>", unsafe_allow_html=True)


def jenks_classifier(data, column, k=5):
    values = data[column].values
    breaks = jenks_breaks(values, k)
    return breaks

# Sidebar pour la sélection de l'option (Attribut/Propriété)
option = st.sidebar.radio("Choisir une option", ("Attribut", "Propriété"))

if option == "Attribut":
    # Liste des attributs pour le choix
    attributs = ['temperat', 'pression', 'pluviome']
    selected_attribute = st.sidebar.selectbox("Sélectionner un attribut", attributs)

    # Liste des jours pour le choix
    jours = [6, 5, 4, 3, 2, 1, 0]
    selected_day = st.sidebar.selectbox("Sélectionner un jour", jours)

    # Filtrer les données en fonction de l'attribut et du jour sélectionnés
    if selected_day!= 0 :
        selected_column_day = f'{selected_attribute}_{selected_day}'
    else:selected_column_day = f'{selected_attribute}*'
    filtered_data = gdf[gdf[selected_column_day] >= 0]

    # Classer les valeurs en utilisant la méthode de Jenks
    breaks = jenks_classifier(filtered_data, selected_column_day, k=5)
    
    # Créer une carte Folium centrée sur la moyenne des coordonnées des géométries
    m = folium.Map(location=[gdf['geometry'].centroid.y.mean(), gdf['geometry'].centroid.x.mean()], zoom_start=4)


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
    

else:
    # Liste des propriétés pour le choix
    proprietes = [ 'humidité', 'Reflectance']
    selected_property = st.sidebar.selectbox("Sélectionner une propriété", proprietes)
    min,max=0,1
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
colors=['#f1eef6','#bdc9e1','#74a9cf','#2b8cbe','#045a8d']    
cmap = LinearColormap(colors=colors, vmin = round(min, 2),vmax = round(max, 2))
cmap.caption = ' Légende'
cmap.add_to(m)
    # Afficher la carte dans Streamlit
folium_static(m ,width=800, height=600)
