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
from branca.colormap import LinearColormap
from streamlit_folium import folium_static
import glob
from PIL import Image, ImageDraw
import imageio

# Charger les données géospatiales depuis le fichier GeoParquet
path_to_geoparquet = "dashboard/donnees/geoparquet/OUTPUT1500.geoparquet"
gdf = gpd.read_parquet(path_to_geoparquet)

from branca.colormap import LinearColormap
st.set_page_config(
    page_title="TIMELAPSE",
    page_icon="⏳",
    layout="wide",  
)

# Dossier de sortie pour les timelapses
output_folder = "timelapses"
os.makedirs(output_folder, exist_ok=True)


st.markdown("<h2 style='font-size:32px; text-align:center;'>TIMELAPSE </h2>", unsafe_allow_html=True)
st.write('voici le GIF 🎞️ ')
attributs = ['temperature', 'pression_atmosph', 'pluviometrie']
selected_attribute = st.sidebar.selectbox("Sélectionner un attribut", attributs)
def create_timelapse(image_files, DAY_names, duration):
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
            draw.text((10, 10), f'{selected_attribute}jour{DAY_names[i]}', fill='black', font=None)

            # Ajouter l'image annotée à la liste
            images.append(np.array(pil_image))

    # Générer le GIF à partir des images annotées
    with imageio.get_writer('timelapse.gif', mode='I', duration=duration, loop=0) as writer:
        for image in images:
            writer.append_data(image)


DAY_names = ['0', '1', '2', '3', '4', '5', '6']
folder = "dashboard/RASTERSclassifié"
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
    # Générer la liste des fichiers image

image_files = sorted(glob.glob(f"{folder}//{selected_attribute.lower()}jour*.tif"))

create_timelapse(image_files, DAY_names, duration=1)
first_image = image_files[0]
with rio.open(first_image) as src:
        bounds = [[src.bounds.bottom, src.bounds.left], [src.bounds.top, src.bounds.right]]


m = folium.Map(location=[28.7917, -9.6026], zoom_start=5)
gif_filename = 'timelapse.gif'
gif_layer = folium.raster_layers.ImageOverlay(
    gif_filename,
    bounds=bounds,
    opacity=0.7,
    name='GIF Layer'
    ).add_to(m)
colors = [
    (215, 25, 28),   #  la classe 1
    (253, 174, 97),    #  la classe 2
    (255, 255, 191),    #  la classe 3
    (171, 221, 164),     #  la classe 4
    (43, 131, 186) ] 
cmap = LinearColormap(colors=colors, vmin = round(min, 2),vmax = round(max, 2))
cmap.caption = ' Légende'
cmap.add_to(m)
folium.LayerControl().add_to(m)
folium_static(m ,width=1050, height=600)
