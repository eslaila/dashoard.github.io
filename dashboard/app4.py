import folium
from streamlit_folium import folium_static
import pandas as pd
import altair as alt
import geopandas as gpd
from folium.plugins import MarkerCluster
import streamlit as st

# Charger les données géospatiales depuis le fichier GeoParquet
path_to_geoparquet = "dashboard/donnees/geoparquet/OUTPUT1500.geoparquet"
gdf = gpd.read_parquet(path_to_geoparquet)

st.set_page_config(
    page_title="POPUP Application",
    page_icon="📈",
    layout="wide",  
)

attributs = ['temperature', 'pression_atmosph', 'pluviometrie']

# Liste des jours pour le choix
jours = [6, 5, 4, 3, 2, 1, 0]


# Create a Folium map centered around the mean of the points
m = folium.Map(location=[gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()], zoom_start=4)
# Ajouter un cluster de marqueurs pour les points
marker_cluster = MarkerCluster().add_to(m)

for index, row in gdf.iterrows():
    marker = folium.Marker(
        location=[row['geometry'].y, row['geometry'].x],
    ).add_to(marker_cluster)

    data = {
        'Jour': list(range(1, 7)),
        'temperature': row[[f'temperaturejour{i}' for i in range(1, 7)]].values,
        'pression_atmosph': row[[f'pression_atmosphjour{i}' for i in range(1, 7)]].values,
        'pluviometrie': row[[f'pluviometriejour{i}' for i in range(1, 7)]].values
    }

    df_chart = pd.DataFrame(data).melt('Jour')
    chart = alt.Chart(df_chart).mark_line().encode(
        x='Jour',
        y='value:Q',
        color='variable:N'
    ).properties(width=300, height=150)

    chart_html = chart.to_html()
    popup = folium.Popup(max_width=350).add_child(folium.VegaLite(chart, width=350, height=150))    
    marker.add_child(popup)
    marker.add_to(marker_cluster)

    # Afficher la carte dans Streamlit
st.markdown('<h2 style="text-align: center;">POPUP</h2>', unsafe_allow_html=True)
folium_static(m ,width=1350, height=600)
