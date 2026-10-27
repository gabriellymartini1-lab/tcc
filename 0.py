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

nome = []  

FILEIRAS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
COLUNAS = list(range(1,21))

ctk.set_appearance_mode("dark")

cinema = ctk.CTk()
cinema.title("cinema ruby")
cinema.geometry("1600x800")

titulo = ctk.CTkLabel(
    cinema, 
    text="CINEMA RUBY", 
    font=("Bernard MT Condensed", 46, "bold"), 
    bg_color="transparent", 
    fg_color="transparent", 
    text_color="#fffdfd"
)
titulo.pack(pady = 20)

#def mostrar_sala_1():
    #fazer   
      
frame_imagens = ctk.CTkFrame(cinema, height=550, width=1500, fg_color="transparent")
frame_imagens.pack()

frame_imagens.grid_propagate(False)

#odisseia
imagem_odisseia = Image.open("a_odisseia.png")
imagem_ctk = ctk.CTkImage(light_image= imagem_odisseia, dark_image= imagem_odisseia, size=(280,500)) #no size colocamos primeiro largura depois altura

label_odisseia_imagem = ctk.CTkLabel(frame_imagens, text="", image=imagem_ctk)
label_odisseia_imagem.grid(row=0, column= 0, padx = 10, pady = 20)

#obsessao
imagem_obsessao_imagem = Image.open("obsessao.png")
imagem_ctk = ctk.CTkImage(light_image= imagem_obsessao_imagem, dark_image= imagem_obsessao_imagem, size=(280,500))

label_obsessao_imagem = ctk.CTkLabel(frame_imagens, text="", image=imagem_ctk)
label_obsessao_imagem.grid(row=0, column= 1, padx = 10, pady = 20)

#homem aranha 
imagem_homem_aranha = Image.open("homem_aranha.png")
imagem_ctk = ctk.CTkImage(light_image= imagem_homem_aranha, dark_image= imagem_homem_aranha, size=(280,500))

label_homem_aranha_imagem = ctk.CTkLabel(frame_imagens, text="", image=imagem_ctk)
label_homem_aranha_imagem.grid(row=0, column= 2, padx = 10, pady = 20)

#toy story 5
imagem_toy_story_5 = Image.open("toy_story_5.png")
imagem_ctk = ctk.CTkImage(light_image= imagem_toy_story_5, dark_image= imagem_toy_story_5, size=(280,500))

label_toy_story_5_imagem = ctk.CTkLabel(frame_imagens, text="", image=imagem_ctk)
label_toy_story_5_imagem.grid(row=0, column= 3, padx = 10, pady = 20)

#um cabra bom de bola
imagem_um_cabra_bom_de_bola = Image.open("um_cabra_bom_de_bola.png")
imagem_ctk = ctk.CTkImage(light_image= imagem_um_cabra_bom_de_bola, dark_image= imagem_um_cabra_bom_de_bola, size=(280,500))

label_um_cabra_bom_de_bola_imagem = ctk.CTkLabel(frame_imagens, text="", image=imagem_ctk)
label_um_cabra_bom_de_bola_imagem.grid(row=0, column= 4, padx = 10, pady = 20)

#frame odisseia
frame_odisseia = ctk.CTkFrame(cinema, height=130, width=270, fg_color="#f38989")
frame_odisseia.place(x=75, y=640) 

frame_odisseia.pack_propagate(False)

label_odisseia = ctk.CTkLabel(frame_odisseia, text="🎬\nA ODISSEIA", font=("Arial", 18, "bold"), justify="left")
label_odisseia.place(x=15, y=15)

botao_odisseia = ctk.CTkButton(
    frame_odisseia, 
    text="ENTRAR", 
    font=("Arial", 12, "bold"),
    fg_color="#e25757",
    hover_color="#aa4c4c",
    width=100, 
    height=35 
)
botao_odisseia.place(x=15, y=70)

#frame obsessao
frame_obsessao = ctk.CTkFrame(cinema, height=130, width=270, fg_color="#f16969")
frame_obsessao.place(x=370, y=640) 

frame_obsessao.pack_propagate(False)

label_obsessao = ctk.CTkLabel(frame_obsessao, text="🎬\nA OBSESSAO", font=("Arial", 18, "bold"), justify="left")
label_obsessao.place(x=15, y=15)

botao_obsessao = ctk.CTkButton(
    frame_obsessao, 
    text="ENTRAR", 
    font=("Arial", 12, "bold"),
    fg_color="#e24c4c",
    hover_color="#9c3b3b",
    width=100, 
    height=35 
)
botao_obsessao.place(x=15, y=70)

#frame homem aranha
frame_homem_aranha = ctk.CTkFrame(cinema, height=130, width=270, fg_color="#e64949")
frame_homem_aranha.place(x=670, y=640) 

frame_homem_aranha.pack_propagate(False)

label_homem_aranha = ctk.CTkLabel(frame_homem_aranha, text="🎬\n HOMEM ARANHA", font=("Arial", 18, "bold"), justify="left")
label_homem_aranha.place(x=15, y=15)

botao_homem_aranha = ctk.CTkButton(
    frame_homem_aranha, 
    text="ENTRAR", 
    font=("Arial", 12, "bold"),
    fg_color="#c92b2b",
    hover_color="#a33030",
    width=100, 
    height=35 
)
botao_homem_aranha.place(x=15, y=70)

#frame toy story
frame_toy_story_5 = ctk.CTkFrame(cinema, height=130, width=270, fg_color="#db3434")
frame_toy_story_5.place(x=970, y=640) 

frame_toy_story_5.pack_propagate(False)

label_toy_story_5 = ctk.CTkLabel(frame_toy_story_5, text="🎬\n TOY STORY 5", font=("Arial", 18, "bold"), justify="left")
label_toy_story_5.place(x=15, y=15)

botao_toy_story_5 = ctk.CTkButton(
    frame_toy_story_5, 
    text="ENTRAR", 
    font=("Arial", 12, "bold"),
    fg_color="#D11E1E",
    hover_color="#8d2929",
    width=100, 
    height=35 
)
botao_toy_story_5.place(x=15, y=70)

#frame um cabra bom de bola
frame_um_cabra_bom_de_cabra = ctk.CTkFrame(cinema, height=130, width=270, fg_color="#e63535")
frame_um_cabra_bom_de_cabra.place(x=1270, y=640) 

frame_um_cabra_bom_de_cabra.pack_propagate(False)

label_um_cabra_bom_de_cabra = ctk.CTkLabel(frame_um_cabra_bom_de_cabra, text="🎬\n UM CABRA BOM DE BOLA", font=("Arial", 18, "bold"), justify="left")
label_um_cabra_bom_de_cabra.place(x=15, y=15)

botao_um_cabra_bom_de_cabra = ctk.CTkButton(
    frame_um_cabra_bom_de_cabra, 
    text="ENTRAR", 
    font=("Arial", 12, "bold"),
    fg_color="#D11E1E",
    hover_color="#8d2929",
    width=100, 
    height=35 
)
botao_um_cabra_bom_de_cabra.place(x=15, y=70)

cinema.mainloop()