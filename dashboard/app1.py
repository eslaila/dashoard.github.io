import rasterio as rio
import streamlit as st
from pyproj import Transformer 
import folium
from streamlit_folium import folium_static
import pandas as pd
import geopandas as gpd
import numpy as np
from branca.colormap import LinearColormap
st.set_page_config(
    page_title="SLIDER",
    page_icon="📅",
    layout="centered",  
)

st.markdown("<h2 style='font-size:32px; text-align:center;'>SLIDER </h2>", unsafe_allow_html=True)
# Charger les données géospatiales depuis le fichier GeoParquet
path_to_geoparquet = "dashboard/donnees/geoparquet/OUTPUT1500.geoparquet"
gdf = gpd.read_parquet(path_to_geoparquet)
# Sidebar pour la sélection de l'attribut
selected_attribute = st.sidebar.selectbox("Sélectionner l'attribut", ['temperature', 'pression_atmosph', 'pluviometrie'])

# Slider pour choisir le jour
selected_day = st.slider("Sélectionner le jour", 0, 6, 0)

# Vérifier si la colonne attribut existe pour le jour sélectionné
for attribut in ['temperature', 'pression_atmosph', 'pluviometrie']:
    if selected_attribute == attribut:
        selected_column_day = f'{attribut}jour{selected_day}'
        if selected_column_day in gdf.columns:
            # Check if the selected column contains non-numeric values
            if not pd.api.types.is_numeric_dtype(gdf[selected_column_day].dtype):
                st.warning(f"La colonne sélectionnée ne contient pas des valeurs numériques. Choisissez une colonne numérique.")
                break
            else:
                # Filtrer les données pour le jour sélectionné
                filtered_data = gdf[gdf[selected_column_day] >= 0]

                # Create a grid for interpolation
                x_min, x_max, y_min, y_max = filtered_data.total_bounds
                x_res, y_res = 0.1, 0.1  # Adjust resolution as needed
                x_steps, y_steps = int((x_max - x_min) / x_res), int((y_max - y_min) / y_res)

                x_vals = np.linspace(x_min, x_max, x_steps)
                y_vals = np.linspace(y_min, y_max, y_steps)

        else:
            st.warning(f"Column '{selected_column_day}' not found in the GeoDataFrame.")

# Charger le raster correspondant à l'attribut sélectionné
RASTERPATH = f"RASTERSclassifié\{selected_attribute}jour{selected_day}.tif"
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

# Overlay raster (RGB) called img using add_child() function (opacity and bounding box set)
m.add_child(folium.raster_layers.ImageOverlay(img.transpose(1, 2, 0), opacity=.7, 
                                              bounds=bounds_fin))
path=f"raster\{selected_attribute}jour{selected_day}.tif"
with rio.open(path) as src:
    data = src.read(1, masked=True)
    data = data.astype('float32', casting='same_kind')
cmap = LinearColormap(colors=colors, vmin = round(data.min(), 2),vmax = round(data.max(), 2))
cmap.caption = ' Légende'
cmap.add_to(m)

# Afficher la carte avec Streamlit
folium_static(m)
