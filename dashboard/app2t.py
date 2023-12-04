import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import folium_static
import pandas as pd
from jenkspy import jenks_breaks

# Charger les données géospatiales depuis le fichier GeoParquet
path_to_geoparquet = "C:\\Users\\hp\\Downloads\\OUTPUT1500.geoparquet"
gdf = gpd.read_parquet(path_to_geoparquet)

st.set_page_config(
    page_title="Visualisation",
    page_icon="🌍",
    layout="wide",  
)


# Titre de l'application
st.markdown("<h1 style='font-size:24px;'>Une Carte de MAROC</h1>", unsafe_allow_html=True)


def jenks_classifier(data, column, k=5):
    values = data[column].values
    breaks = jenks_breaks(values, k)
    return breaks

# Sidebar pour la sélection de l'option (Attribut/Propriété)
option = st.sidebar.radio("Choisir une option", ("Attribut", "Propriété"))
# Récupérer les paramètres d'URL actuels
params = st.experimental_get_query_params()
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
    # Convertir les valeurs de la colonne en nombres flottants
    gdf[selected_column_day] = gdf[selected_column_day].astype(float)

    # Diviser les données en 5 classes
    nb_classes = 5
    class_bins = [gdf[selected_column_day].quantile(i / nb_classes) for i in range(nb_classes + 1)]
    colors = ['#f1eef6', '#bdc9e1', '#74a9cf', '#2b8cbe', '#045a8d']  # Autre jeu de couleurs

    
    # Définir la colormap
    colormap = folium.LinearColormap(colors=colors, vmin=gdf[selected_column_day].min(), vmax=gdf[selected_column_day].max())
    
    # Ajouter manuellement les classes à la carte Folium
    colormap.add_to(m)

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
    # Convertir les valeurs de la colonne en nombres flottants
    gdf[selected_property] = gdf[selected_property].astype(float)

    # Diviser les données en 5 classes
    nb_classes = 5
    class_bins = [gdf[selected_property].quantile(i / nb_classes) for i in range(nb_classes + 1)]
    colors = ['#f1eef6', '#bdc9e1', '#74a9cf', '#2b8cbe', '#045a8d']  # Autre jeu de couleurs

    
    # Définir la colormap
    colormap = folium.LinearColormap(colors=colors, vmin=gdf[selected_property].min(), vmax=gdf[selected_property].max())
    
    # Ajouter manuellement les classes à la carte Folium
    colormap.add_to(m)
    
# Afficher la carte dans Streamlit
folium_static(m ,width=1000, height=600)

# Tkinter application for capturing a screenshot
from tkinter import Tk, Frame, Button,Canvas
from PIL import ImageGrab, Image, ImageTk, ImageDraw
import pyautogui
from tkinter import Tk, Frame, Canvas, Button
from PIL import ImageGrab, Image, ImageTk, ImageDraw
import os
import streamlit as st
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import base64
import time
from datetime import datetime
from io import BytesIO

# Function to capture a screenshot using Tkinter
def capture_screenshot():
    with st.spinner("Capture a screenshot by clicking the button below"):
        # Invoke the Tkinter application and return the screenshot path
        screenshot_path = app.run_application()
    return screenshot_path

def create_pdf(title, image_path, description, pdf_output="output.pdf"):
    # Récupérer le répertoire de travail actuel
     current_directory = os.getcwd()

    # Construire le chemin complet du fichier PDF
     pdf_path = os.path.join(current_directory, pdf_output)

     c = canvas.Canvas(pdf_path, pagesize=letter)

    # Largeur de la page
     page_width, _ = letter

    # Ajout du titre (taille 15, police différente)
     c.setFont("Times-Bold", 15)
    
    # Positionnement du titre au centre de la page
     title_x_position = page_width / 2
     title_y_position = 750
     c.drawCentredString(title_x_position, title_y_position, title)

    # Ajout de l'image (centrée horizontalement, taille plus grande)
     image_width, image_height = 600, 400
     c.drawInlineImage(image_path, (page_width - image_width) / 2, title_y_position - image_height - 30, width=image_width, height=image_height)

    # Ajout de la description (au-dessous de l'image)
     c.setFont("Helvetica", 12)
     text_object = c.beginText((page_width - 500) / 2, title_y_position - image_height - 60)  # Ajustez la position selon vos besoins
    
    # Mise en forme de la description pour ajuster la mise en page
     lines = description.split("\n")
     for line in lines:
          text_object.textLine(line)
    
     c.drawText(text_object)

     c.save()
     print(f"PDF généré sous : {pdf_path}")
     return pdf_path
    
class Application():
    def __init__(self, master):
        self.snip_surface = None
        self.master = master
        self.start_x = None
        self.start_y = None
        self.current_x = None
        self.current_y = None
        self.image_path = None

        root.geometry('400x50+200+200')  # set new geometry
        root.title('choisir votre image !')

        self.menu_frame = Frame(master)
        self.menu_frame.pack()

        self.buttonBar = Frame(self.menu_frame)
        self.buttonBar.pack()

        self.snipButton = Button(self.buttonBar, text="Snip", command=self.create_screen_canvas)
        self.snipButton.pack()

        self.canvas = Canvas(self.master, bg="white")
        self.canvas.pack(fill="both", expand=True)

        self.create_rectangle_button = Button(self.master, text="Create Rectangle", command=self.create_rectangle)
        self.create_rectangle_button.pack()

        self.master.bind("<ButtonPress-1>", self.on_button_press)
        self.master.bind("<B1-Motion>", self.on_snip_drag)
        self.master.bind("<ButtonRelease-1>", self.on_button_release)

        self.master_screen = Tk()
        self.master_screen.withdraw()

    def create_screen_canvas(self):
        self.master_screen.deiconify()
        root.withdraw()

        self.snip_surface = Frame(self.master_screen, cursor="cross", bg=None)
        self.snip_surface.pack(fill="both", expand= True)
        self.master_screen.attributes('-fullscreen', True)
        self.master_screen.attributes('-alpha', .3)
        self.master_screen.lift()
        self.master_screen.attributes("-topmost", True)

        self.master_screen.bind("<ButtonPress-1>", self.on_button_press)
        self.master_screen.bind("<B1-Motion>", self.on_snip_drag)
        self.master_screen.bind("<ButtonRelease-1>", self.on_button_release)

    def create_rectangle(self):
        if self.start_x is not None and self.start_y is not None and self.current_x is not None and self.current_y is not None:
            self.canvas.create_rectangle(self.start_x, self.start_y, self.current_x, self.current_y, outline="red", width=2)


    def on_button_release(self, event):
        self.create_rectangle()
        self.display_rectangle_position()

        if self.start_x <= self.current_x and self.start_y <= self.current_y:
            print("right down")
            screenshot_data = self.take_bounded_screenshot(self.start_x, self.start_y, self.current_x, self.current_y)

        elif self.start_x >= self.current_x and self.start_y <= self.current_y:
            print("left down")
            screenshot_data = self.take_bounded_screenshot(self.current_x, self.start_y, self.start_x, self.current_y)

        elif self.start_x <= self.current_x and self.start_y >= self.current_y:
            print("right up")
            screenshot_data = self.take_bounded_screenshot(self.start_x, self.current_y, self.current_x, self.start_y)

        elif self.start_x >= self.current_x and self.start_y >= self.current_y:
            print("left up")
            screenshot_data = self.take_bounded_screenshot(self.current_x, self.current_y, self.start_x, self.start_y)


        self.exit_screenshot_mode()
        # Now 'screenshot_data' contains the captured screenshot data (PIL Image)
        screenshot_data.show()
        screenshot_path = "screenshot.png"
        screenshot_data.save(screenshot_path)

        self.exit_screenshot_mode()
        return event

    def exit_screenshot_mode(self):
        self.snip_surface.destroy()
        self.master_screen.withdraw()
        root.deiconify()

    def on_button_press(self, event):
        # save mouse drag start position
        self.start_x = self.master_screen.winfo_pointerx()
        self.start_y = self.master_screen.winfo_pointery()
        self.overlay_image = Image.new("RGBA", (self.master_screen.winfo_screenwidth(), self.master_screen.winfo_screenheight()), (0, 0, 0, 0))
        self.overlay_image_draw = ImageDraw.Draw(self.overlay_image)
        self.snip_surface.create_rectangle(0, 0, 1, 1, outline='red', width=3, fill="maroon3")

        return event

    def on_snip_drag(self, event):
        self.current_x = self.master_screen.winfo_pointerx()
        self.current_y = self.master_screen.winfo_pointery()

        # Update the overlay image on the snip_surface
        img_tk = ImageTk.PhotoImage(self.overlay_image)
        self.snip_surface.configure(bg="")
        self.snip_surface.img_tk = img_tk
        self.snip_surface.create_image(0, 0, anchor="nw", image=img_tk)

        return event

    def display_rectangle_position(self):
        print(self.start_x)
        print(self.start_y)
        print(self.current_x)
        print(self.current_y)

    def run_application(self):
        self.master.deiconify()
        self.master.attributes('-fullscreen', True)
        self.master.lift()
        self.master.attributes("-topmost", True)
        self.master.mainloop()

    def take_bounded_screenshot(self, x1, y1, x2, y2, image_filename="screenshot.png"):
        screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        current_directory = os.getcwd()  # Use os.getcwd() to get the current working directory
        image_path = os.path.join(current_directory, image_filename)
        screenshot.save(image_path)
        return screenshot
    

import aspose.pdf as pdf

st.markdown("<h2 style='font-size:25px;'>delimiter votre image ! </h2>", unsafe_allow_html=True)

st.write("Cliquez sur le bouton ci-dessous.")
pdf_path = None
# Step 1: Choose the image for the PDF
if st.button("Choisir l'image de PDF"):
    # Create a Tkinter root window
    root = Tk()
    app = Application(root)
    root.mainloop()
    root.deletecommand

st.write("Delimiter votre image en utilisant L'onglet affiché au dessous")

st.title("telecharger pdf")

st.write("Cliquez sur le bouton ci-dessous.")

if st.button("preparer votre pdf"):
    current_directory = os.getcwd()  
    image_filename="screenshot.png"
    image_path = os.path.join(current_directory, image_filename)
    # Step 2: Generate and download the PDF
    title = "Visualisation Des Donnees"
    description = (
            "L'application innovante que nous avons développée offre une expérience immersive de \n"
            "visualisation des données géographiques classifiées par couleur, extraites d'un fichier \n"
            "GeoParquet comprenant 1500 points répartis à travers tout le Maroc. \n\n"
            "Grâce à une interface conviviale, les utilisateurs peuvent explorer facilement les nuances  \n"
            "subtiles des informations géospatiales, représentées de manière visuellement attrayante. \n\n"
            "Que vous soyez intéressé par des attributs climatiques tels que la température, \n"
            "la pression atmosphérique et la pluviométrie, ou par des propriétés environnementales comme \n"
            " l'humidité et la réflectance, notre application offre une vue détaillée des données. \n\n"
        )
    # Générer le PDF
    pdf_path = create_pdf(title, image_path, description, "output.pdf")

    st.download_button(
            label="Téléchargez le PDF",
            data=open(pdf_path, "rb").read(),
            key="pdf_download_button",
            file_name="output.pdf"
    )