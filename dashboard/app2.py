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
path_to_geoparquet = "C:\\Users\\hp\\Downloads\\OUTPUT1500.geoparquet"
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
folder = "dashboard//RASTERSclassifié"
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

st.write('voici un video de TIMELAPSE ! ')
video_frames = []
for selected_day in range(0, 6):  # Include day 1 in the range
        # Charger le raster correspondant à l'attribut sélectionné
        RASTERPATH = f"dashboard//RASTERSclassifié//{selected_attribute}jour{selected_day}.tif"
        
        ## LC08 RGB Image
        dst_crs = 'EPSG:4326'

        with rio.open(RASTERPATH) as src:

            img = src.read()

            src_crs = src.crs.to_string().upper()
            min_lon, min_lat, max_lon, max_lat = src.bounds

        ## Conversion from UTM to WGS84 CRS
        bounds_orig = [[min_lat, min_lon], [max_lat, max_lon]]

        bounds_fin = []

        for item in bounds_orig:   
        #converting to lat/lon
            lat = item[0]
            lon = item[1]

            proj = Transformer.from_crs(src_crs, dst_crs, always_xy=True)

            lon_n, lat_n = proj.transform(lon, lat)

            bounds_fin.append([lat_n, lon_n])

        colors = [
            (215, 25, 28),   #  la classe 1
            (253, 174, 97),    #  la classe 2
            (255, 255, 191),    #  la classe 3
            (171, 221, 164),     #  la classe 4
            (43, 131, 186) ]      #  la classe 5
        


        # Finding the centre latitude & longitude    
        centre_lon = bounds_fin[0][1] + (bounds_fin[1][1] - bounds_fin[0][1])/2
        centre_lat = bounds_fin[0][0] + (bounds_fin[1][0] - bounds_fin[0][0])/2

        # Create Folium map without specifying tiles
        m = folium.Map(location=[centre_lat, centre_lon], zoom_start=5)

        # Ajout d'une couche de carte de base (par exemple, OpenStreetMap)
        folium.TileLayer('openstreetmap').add_to(m)


        # Overlay raster (RGB) called img using add_child() function (opacity and bounding box set)
        m.add_child(folium.raster_layers.ImageOverlay(img.transpose(1, 2, 0), opacity=.7, 
                        bounds=bounds_fin))
        path = f"dashboard//RASTERSclassifié//{selected_attribute}jour{selected_day}.tif"

        with rio.open(path) as src:
            data = src.read(1, masked=True)
            data = data.astype('float32', casting='same_kind')
            cmap = LinearColormap(colors=colors, vmin = round(data.min(), 2),vmax = round(data.max(), 2))
            cmap.caption = ' Légende'
            cmap.add_to(m)

        # Inside your loop where you append images to video_frames
        img_bytes = m._to_png()
        video_frames.append(np.asarray(Image.open(io.BytesIO(img_bytes)).convert('RGB')))


        # Overlay raster (GeoTIFF) sur la carte
        folium.raster_layers.ImageOverlay(img[0], opacity=0.7, bounds=bounds_fin).add_to(m)



if video_frames:
    # Create a timelapse video
    output_folder = "timelapses"
    video_path = os.path.join(output_folder, f"{attributs}_timelapse.mp4")
    fig, ax = plt.subplots(figsize=(12, 8))
    im = ax.imshow(video_frames[0])

    def update(frame):
        im.set_array(video_frames[frame])
        return [im]

    ani = FuncAnimation(fig, update, frames=len(video_frames), blit=True)
    ani.save(video_path, writer="ffmpeg", fps=1)

    # Display the video
    st.video(video_path)

    # Remove the video file after displaying
    if os.path.exists(video_path):
        os.remove(video_path)
