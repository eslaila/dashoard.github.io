import streamlit as st
import numpy as np
import leafmap.foliumap as leafmap
st.set_page_config(
    page_title="COG",
    page_icon="✂",
    layout="wide",  
)
st.markdown("<h2 style='font-size:32px; text-align:center;'>Split_Map par cog </h2>", unsafe_allow_html=True)

m = leafmap.Map()
# Sidebar pour la sélection de l'attribut
selected_attribute = st.sidebar.selectbox("Sélectionner l'attribut", ['temperature', 'pression_atmosph', 'pluviometrie'])

# Sidebar pour la sélection des jours
selecte_day = st.sidebar.slider("Sélectionner le premier jour", 0, 6, 0 )


# Vérifier si les colonnes attributs existent pour les jours sélectionnés
selected_column_day_1 = f'https://eslaila.github.io/webmapping.github.io//{selected_attribute}jour{selecte_day}.tif'
selected_column_day_2 = f'https://eslaila.github.io/webmapping.github.io//cog{selected_attribute}jour{selecte_day}.tif'
# Configurer et exécuter la boucle d'événements avec asyncio

m.split_map(
        left_layer=selected_column_day_1 , right_layer=selected_column_day_2 ,
        left_label=f'{selected_attribute}jour{selecte_day}',
        right_label=f'cog{selected_attribute}jour{selecte_day}',
        left_position=  "topleft",
        right_position = "topright",
    )


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


labels = [f'{round(class_limits1[0],2)}-{round(class_limits1[1],2)}',f'{round(class_limits1[1],2)}-{round(class_limits1[2],2)}', f'{round(class_limits1[2],2)}-{round(class_limits1[3],2)}',f'{round(class_limits1[3],2)}-{round(class_limits1[4],2)}', f'{round(class_limits1[4],2)}-{round(class_limits1[5],2)}']
# color can be defined using either hex code or RGB (0-255, 0-255, 0-255)
colors = [
    (215, 25, 28),   #  la classe 1
    (253, 174, 97),    #  la classe 2
    (255, 255, 191),    #  la classe 3
    (171, 221, 164),     #  la classe 4
    (43, 131, 186) ]   

m.add_legend(title='Legend', labels=labels, colors=colors)  
m.to_streamlit(height=600)