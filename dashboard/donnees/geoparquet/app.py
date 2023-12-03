import streamlit as st
import geopandas as gpd
import folium

# Charger les données géospatiales depuis le fichier GeoParquet
path_to_geoparquet = "data.geoparquet"
gdf = gpd.read_parquet(path_to_geoparquet)

# Afficher les données géospatiales sur une carte Folium
m = folium.Map(location=[gdf['geometry'].centroid.y.mean(), gdf['geometry'].centroid.x.mean()], zoom_start=8)

# Ajouter les données à la carte en tant que couches GeoJSON
for idx, row in gdf.iterrows():
    popup = f"ID: {idx}"
    folium.GeoJson(row['geometry'].__geo_interface__, popup=popup).add_to(m)

# Afficher la carte dans Streamlit
st.write(m)
