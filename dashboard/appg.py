import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import folium_static
import numpy as np
st.set_page_config(
    page_title="REQUETES",
    page_icon="🖇",
    layout="centered",  
)

st.markdown("<h2 style='font-size:32px; text-align:center;'>REQUETES </h2>", unsafe_allow_html=True)
st.markdown("<h2 style='font-size:15px; text-align:center;'>veuiller composer vos requetes ci dessous :</h2>", unsafe_allow_html=True)
# Charger les données géospatiales depuis le fichier GeoParquet
path_to_geoparquet = "donnees\geoparquet\OUTPUT1500.geoparquet"
gdf = gpd.read_parquet(path_to_geoparquet)
filtered_data=[]
# Fonction pour filtrer les données
def filter_data(gdf, filters, ):
    filtered_data = gdf.copy()
    final_filtered_data = gdf.iloc[0:0]  # Crée un DataFrame vide avec les mêmes colonnes
    i=0
    for col, op, val ,logical_operator in filters:
        
        if op == "contains":
            temp_filtered = filtered_data[filtered_data[col].str.contains(val)]
        else:
            if op == "==":
                temp_filtered = filtered_data[filtered_data[col] == val]
            elif op == "!=":
                temp_filtered = filtered_data[filtered_data[col] != val]
            elif op == ">":
                temp_filtered = filtered_data[filtered_data[col] > val]
            elif op == "<":
                temp_filtered = filtered_data[filtered_data[col] < val]
            elif op == ">=":
                temp_filtered = filtered_data[filtered_data[col] >= val]
            elif op == "<=":
                temp_filtered = filtered_data[filtered_data[col] <= val]
               
        if i>0:
            final_filtered_data=RESULTAT
            if logical_operator == "ET" :
                RESULTAT = final_filtered_data.merge(temp_filtered, how='inner')
            elif logical_operator == "OU":
                RESULTAT = final_filtered_data.merge(temp_filtered, how='outer')
        else:RESULTAT=temp_filtered    
        i=i+1
    return RESULTAT   
# Sidebar pour le choix des filtres
filters = []
col = st.selectbox("Propriété", gdf.columns)
op = st.selectbox("Opérateur", ["==", "!=", ">", "<", ">=", "<=", "contains"])
if col in ["date", "nom"]:
    val = st.text_input("Valeur")
else:
    val = st.number_input("Valeur")
logical_operator=None
filters.append((col, op, val,logical_operator))
add_filter = st.checkbox("Ajouter un filtre",key=0)
i = 1
while add_filter:
    logical_operator = st.radio("Choisir l'opérateur logique entre les filtres", ["ET", "OU"], key=f"operator_{i}")
    col = st.selectbox("Propriété", gdf.columns, key=f"property_{i}")
    op = st.selectbox("Opérateur", ["==", "!=", ">", "<", ">=", "<=", "contains"], key=f"operator_type_{i}")
    if col in ["nom", "date"]:
        val = st.text_input("Valeur", key=f"value_text_{i}")
    else:
        val = st.number_input("Valeur", key=f"value_number_{i}")

    filters.append((col, op, val, logical_operator))
    add_filter = st.checkbox("Ajouter un filtre", key=f"add_filter_{i}")
    i += 1

button_clicked = st.button("Filtrer les données")

if button_clicked:
    if add_filter:
       filtered_data = filter_data(gdf, filters)
    else:filtered_data = filter_data(gdf, filters)
    st.write(f"Nombre de points : {len(filtered_data)}")
    
if filtered_data is not None and not isinstance(filtered_data, list) and not filtered_data.empty:
    # Calculer les coordonnées moyennes pour la carte à partir des données filtrées
    map_center = [filtered_data['geometry'].centroid.y.mean(), filtered_data['geometry'].centroid.x.mean()]

    # Vérifier si le centre est valide
    if all(map(lambda x: x is not None and not np.isnan(x), map_center)):
        # Créer la carte avec le centre calculé
        m = folium.Map(location=map_center, zoom_start=4)
        
    else:
        st.error("Les coordonnées du centre de la carte ne sont pas valides.")
    for idx, row in filtered_data.iterrows():
       
        folium.CircleMarker(
            location=[row['geometry'].y, row['geometry'].x],
            radius=10,  # Ajuster l'échelle pour la taille des symboles
        
            color='blue',
            fill=True,
            fill_color='blue',
            fill_opacity=0.6,
        ).add_to(m)    
    # Affichage de la carte uniquement si les données sont valides
    folium_static(m)
elif isinstance(filtered_data, list) or filtered_data is None or filtered_data.empty:
    m = folium.Map(location=[0, 0], zoom_start=2)

# Affichage de la carte sans aucune couche
    folium_static(m)