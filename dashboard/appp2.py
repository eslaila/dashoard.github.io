import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import contextily as ctx
import numpy as np
from io import BytesIO
import io
import os
from matplotlib.animation import FuncAnimation
import rasterio as rio
from pyproj import Transformer 
import folium
from folium import plugins
from branca.colormap import LinearColormap
from streamlit_folium import folium_static
import glob
from PIL import Image, ImageDraw
import imageio
import requests
from io import BytesIO


# Function to read the GeoTIFF file with rasterio
def read_geotiff(folder):
    response = requests.get(folder)
    dataset = rasterio.open(BytesIO(response.content))
    return dataset
# Dossier de sortie pour les timelapses
output_folder = "timelapses"
os.makedirs(output_folder, exist_ok=True)

st.markdown("<h2 style='font-size:32px; text-align:center;'>TIMELAPSE </h2>", unsafe_allow_html=True)

attributs = ['vitesse', 'temperature', 'pression']
selected_attribute = st.radio('Sélectionner un attribut :', attributs)

# Utilisez des colonnes pour centrer la section de la boîte de sélection
col1, col2, col3 = st.columns([1, 3, 1])

def create_timelapse(image_files, DAY_names, duration, output_filename):
    images = []
    for i, file in enumerate(image_files):
        with rio.open(file) as src:
            image_data = src.read()

            # Convertir l'ensemble des bandes en une seule image
            combined_image = np.stack(image_data, axis=-1)

            # Convertir en PIL Image
            pil_image = Image.fromarray(combined_image)

            # Créer un objet de dessin
            draw = ImageDraw.Draw(pil_image)

            # Annoter chaque image avec les noms des jours
            draw.text((10, 10), f'{selected_attribute}_{DAY_names[i]}', fill='white', font=None)

            # Ajouter l'image annotée à la liste
            images.append(np.array(pil_image))

    # Générer le GIF à partir des images annotées
    with imageio.get_writer(output_filename, mode='I', duration=duration, loop=0) as writer:
        for image in images:
            writer.append_data(image)

DAY_names = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
folder = f"dashboard/RASTERSclassifié"


if selected_attribute == 'vitesse':
    vmin = 0
    vmax = 100
elif selected_attribute == "temperature":
    vmin = 0
    vmax = 20
else:
    vmin = 0
    vmax = 50
class_limits1 = np.linspace(vmin, vmax, num=5) 

# Générer la liste des fichiers image
image_files = [os.path.join(folder, f"dashboard/RASTERSclassifié//{selected_attribute}_{day}.tif") for day in DAY_names]


# Utiliser le nom de l'attribut dans le nom du fichier de sortie
output_filename = f'timelapse_{selected_attribute}.gif'

create_timelapse(image_files, DAY_names, duration=5, output_filename=output_filename)
first_image = image_files[0]
with rio.open(first_image) as src:
    bounds = [[src.bounds.bottom, src.bounds.left], [src.bounds.top, src.bounds.right]]

m = folium.Map(location=[28.7917, -9.6026], zoom_start=5)
gif_layer = folium.raster_layers.ImageOverlay(
    output_filename,
    bounds=bounds,
    opacity=0.7,
    name='GIF Layer'
    ).add_to(m)

# Ajouter la possibilité de dessiner sur la carte
draw = plugins.Draw()
draw.add_to(m)

# Ajouter le mode plein écran
plugins.Fullscreen().add_to(m)

# Ajouter la fonctionnalité de position de la souris
plugins.MousePosition().add_to(m)


folium_static(m)

# Définir la plage de couleurs avec 'viridis' au lieu de 'magma'
cmap = plt.get_cmap('viridis')
norm = plt.Normalize(0, 255)

# Modifier la ligne suivante pour ajuster les valeurs affichées sur la colormap
num_classes = 5
colormap = LinearColormap(
    colors=[cmap(norm(value)) for value in np.linspace(0, 255, num=num_classes)],
    vmin=vmin,
    vmax=vmax
)    
cmap.caption = ' Légende'
colormap.add_to(m)
folium.LayerControl().add_to(m)
