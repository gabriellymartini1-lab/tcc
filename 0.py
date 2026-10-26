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

label_odisseia = ctk.CTkLabel(frame_imagens, text="", image=imagem_ctk)
label_odisseia.grid(row=0, column= 0, padx = 10, pady = 20)

#obsessao
imagem_obsessao = Image.open("obsessao.png")
imagem_ctk = ctk.CTkImage(light_image= imagem_obsessao, dark_image= imagem_obsessao, size=(280,500))

label_obsessao = ctk.CTkLabel(frame_imagens, text="", image=imagem_ctk)
label_obsessao.grid(row=0, column= 1, padx = 10, pady = 20)

#homem aranha 
imagem_homem_aranha = Image.open("homem_aranha.png")
imagem_ctk = ctk.CTkImage(light_image= imagem_homem_aranha, dark_image= imagem_homem_aranha, size=(280,500))

label_homem_aranha = ctk.CTkLabel(frame_imagens, text="", image=imagem_ctk)
label_homem_aranha.grid(row=0, column= 2, padx = 10, pady = 20)

#toy story 5
imagem_toy_story_5 = Image.open("toy_story_5.png")
imagem_ctk = ctk.CTkImage(light_image= imagem_toy_story_5, dark_image= imagem_toy_story_5, size=(280,500))

label_toy_story_5 = ctk.CTkLabel(frame_imagens, text="", image=imagem_ctk)
label_toy_story_5.grid(row=0, column= 3, padx = 10, pady = 20)

#um cabra bom de bola
imagem_um_cabra_bom_de_bola = Image.open("um_cabra_bom_de_bola.png")
imagem_ctk = ctk.CTkImage(light_image= imagem_um_cabra_bom_de_bola, dark_image= imagem_um_cabra_bom_de_bola, size=(280,500))

label_um_cabra_bom_de_bola = ctk.CTkLabel(frame_imagens, text="", image=imagem_ctk)
label_um_cabra_bom_de_bola.grid(row=0, column= 4, padx = 10, pady = 20)

#frame botoes
frame_botoes = ctk.CTkFrame(cinema, height=200, width=1500, fg_color="transparent")
frame_botoes.pack(pady = 20)

frame_botoes.grid_propagate(False)

#botao odisseia
btn_odisseia = ctk.CTkButton(frame_botoes,
        text="SALA 1\n Odisseia",
        width=260,
        height=100,
        fg_color="#C42525",
        hover_color="#7A0505",
        text_color="white",
        font=("Broadway", 20, "bold"))
btn_odisseia.grid(row=0, column= 0, padx = 20, pady = 0)

#botao obsessao
btn_obsessao = ctk.CTkButton(frame_botoes,
        text="SALA 2\n Obsessao",
        width=260,
        height=100,
        fg_color="#C42525",
        hover_color="#7A0505",
        text_color="white",
        font=("Broadway", 20, "bold"))
btn_obsessao.grid(row=0, column= 1, padx = 20, pady = 0)

#botao homem aranha
btn_Homem_Aranha = ctk.CTkButton(frame_botoes,
        text="SALA 3\n Homem Aranha",
        width=260,
        height=100,
        fg_color="#C42525",
        hover_color="#7A0505",
        text_color="white",
        font=("Broadway", 20, "bold"))
btn_Homem_Aranha.grid(row=0, column= 3, padx = 20, pady = 0)

#botao toy story
btn_Toy_Story_5 = ctk.CTkButton(frame_botoes,
        text="SALA 4\n Toy Story 5",
        width=260,
        height=100,
        fg_color="#C42525",
        hover_color="#7A0505",
        text_color="white",
        font=("Broadway", 20, "bold"))
btn_Toy_Story_5.grid(row=0, column= 4, padx = 15, pady = 0)

#botao um cabra bom de bola
btn_Um_Cabra_bom_de_bola = ctk.CTkButton(frame_botoes,
        text="SALA 5\n Um Cabra bom de bola",
        width=260,
        height=100,
        fg_color="#C42525",
        hover_color="#7A0505",
        text_color="white",
        font=("Broadway", 20, "bold"))
btn_Um_Cabra_bom_de_bola.grid(row=0, column= 5, padx = 15, pady = 0)

cinema.mainloop()