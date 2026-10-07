import customtkinter as ctk
from tkinter import messagebox, ttk
import psycopg
from PIL import Image
from pathlib import Path

DB_CONFIG = {
    "dbname": "cinema",
    "user": "postgres",
    "password": "root",
    "host": "localhost",
    "port": "5432"
}

BASE_DIR = Path(__file__).resolve().parent

FILEIRAS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
COLUNAS = list(range(1,21))

ctk.set_appearance_mode("dark")

cinema = ctk.CTk()
cinema.title("cinema ruby")
cinema.geometry("1400x900")

titulo = ctk.CTkLabel(cinema, text="CINEMA RUBY", font=("Bernard MT Condensed", 30, "bold"), bg_color="transparent", fg_color="transparent")
titulo.pack(pady = 20)

frame_imagens = ctk.CTkFrame(cinema, height=550, width=1400)
frame_imagens.pack()

frame_imagens.grid_propagate(False)

imagem = Image.open("a_odisseia.png")
imagem_ctk = ctk.CTkImage(light_image= imagem, dark_image= imagem, size=(300,500)) #no size colocamos primeiro largura depois altura

label_imagem = ctk.CTkLabel(frame_imagens, text="", image=imagem_ctk)
label_imagem.grid(row=0, column= 0, padx = 30, pady = 50)

cinema.mainloop()