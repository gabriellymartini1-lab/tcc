import customtkinter as ctk  # Importa a biblioteca CustomTkinter para criar a interface gráfica
from tkinter import messagebox  # Importa as caixas de mensagem do Tkinter
import psycopg  # Importa a biblioteca para conectar o Python ao PostgreSQL
from PIL import Image  # Importa o módulo Image do Pillow para manipulação de imagens
from pathlib import Path  # Importa o Path para trabalhar com caminhos de arquivos do sistema

DB_CONFIG = {  # Cria um dicionário com as configurações de conexão com o banco de dados
    "dbname": "cinema",  # Define o nome do banco de dados
    "user": "postgres",  # Define o usuário do PostgreSQL
    "password": "root",  # Define a senha do banco de dados
    "host": "localhost",  # Define que o banco está no próprio computador
    "port": "5432"  # Define a porta padrão utilizada pelo PostgreSQL
}

BASE_DIR = Path(__file__).resolve().parent  # Define o diretório base raiz onde o arquivo Python está localizado

# Estruturas para armazenar os assentos selecionados e os botões de cada uma das 5 salas
assentos_selecionados = {i: [] for i in range(1, 6)}
botoes_assentos = {i: {} for i in range(1, 6)}

filas = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]  # Cria as filas de A até J
colunas = list(range(1, 21))  # Cria os números das cadeiras de 1 até 20

ctk.set_appearance_mode("dark")  # Define o tema da interface como escuro

def buscar_assentos_ocupados(num_sala):  # Busca no banco quais assentos estão ocupados para uma sala específica
    status_assentos = {}
    try:
        conn = psycopg.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(f"SELECT fila, numero_cadeira, ocupado FROM sala{num_sala};")

        for fila, numero, ocupado in cursor.fetchall():
            status_assentos[f"{fila}{numero}"] = ocupado

        cursor.close()
        conn.close()
    except Exception as error:
        print(f"Erro ao buscar assentos da Sala {num_sala}:", error)

    return status_assentos

def alternar_assento(btn, num_sala):  # Seleciona ou desseleciona uma cadeira
    assento = btn.cget("text")
    lista = assentos_selecionados[num_sala]

    if assento in lista:
        lista.remove(assento)
        btn.configure(fg_color="#E4C6D0", text_color="black")
    else:
        lista.append(assento)
        btn.configure(fg_color="#C05A9D", text_color="white")

def reservar(num_sala):  # Reserva os assentos selecionados da sala correspondente
    lista = assentos_selecionados[num_sala]
    if not lista:
        messagebox.showwarning("Atenção", "Selecione pelo menos um assento para reservar.")
        return

    try:
        conn = psycopg.connect(**DB_CONFIG)
        cursor = conn.cursor()

        for assento in lista:
            fila = assento[0]
            numero = int(assento[1:])

            cursor.execute(
                f"""
                UPDATE sala{num_sala}
                SET ocupado = TRUE
                WHERE fila = %s AND numero_cadeira = %s;
                """,
                (fila, numero)
            )

        conn.commit()
        cursor.close()
        conn.close()

        messagebox.showinfo("Reserva realizada", f"Assentos reservados na Sala {num_sala}:\n{', '.join(lista)}")
        lista.clear()
        atualizar_assentos(num_sala)

    except Exception as error:
        messagebox.showerror("Erro", f"Não foi possível realizar a reserva:\n{error}")

def atualizar_assentos(num_sala):  # Atualiza os botões de acordo com o estado do banco
    assentos_no_banco = buscar_assentos_ocupados(num_sala)
    mapa_botoes = botoes_assentos[num_sala]

    for fila in filas:
        for coluna in colunas:
            nome_assento = f"{fila}{coluna}"
            ocupado = assentos_no_banco.get(nome_assento, False)
            btn = mapa_botoes.get(nome_assento)

            if btn is None:
                continue

            if ocupado:
                btn.configure(fg_color="#D19AB4", text_color="white", state="disabled")
            else:
                btn.configure(fg_color="#E4C6D0", text_color="black", state="normal")

def mostrar_tela(frame_desejado):  # Oculta todas as telas e exibe apenas a desejada
    frame_inicial.pack_forget()
    for f in frames_salas.values():
        f.pack_forget()
    frame_desejado.pack(fill="both", expand=True)

app = ctk.CTk()
app.title("CINEMA RUBY")
app.geometry("1400x900")

# --- TELA INICIAL ---
frame_inicial = ctk.CTkFrame(app, fg_color="#1A1518")
frame_inicial.pack(fill="both", expand=True)

frame_topo = ctk.CTkFrame(frame_inicial, fg_color="transparent")
frame_topo.pack(fill="x", padx=65, pady=(25, 10))

ctk.CTkLabel(frame_topo, text="CINEMA RUBY", font=("Arial", 32, "bold"), text_color="#D19ABE").pack(side="left")
ctk.CTkLabel(frame_topo, text="INÍCIO", font=("Arial", 14, "bold"), text_color="#F7D9ED").pack(side="right", padx=15)

# Banners dos Filmes (Centralizados)
frame_banner = ctk.CTkFrame(frame_inicial, fg_color="#2B2026", corner_radius=18, height=500)
frame_banner.pack(fill="x", padx=65, pady=(20, 25))
frame_banner.pack_propagate(False)

# Sub-container interno para permitir o alinhamento das imagens exatamente ao centro
frame_banner_center = ctk.CTkFrame(frame_banner, fg_color="transparent")
frame_banner_center.pack(expand=True, anchor="center")

filmes_imagens = [
    "a_odisseia.png",
    "obsessao.png.png",
    "toy_story_5.png",
    "um_cabra_bom_de_bola.png",
    "homem_aranha.png."
]

for img_nome in filmes_imagens:
    try:
        img_path = BASE_DIR / img_nome
        pil_img = Image.open(img_path)
        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(180, 320))
        card = ctk.CTkButton(frame_banner_center, text="", image=ctk_img, fg_color="transparent", hover=False)
        card.pack(side="left", padx=15, pady=20)
    except Exception as e:
        print(f"Erro ao carregar a imagem {img_nome}: {e}")

# Seção de seleção de Salas
ctk.CTkLabel(frame_inicial, text="Escolha seu filme", font=("Arial", 24, "bold"), text_color="white").pack(anchor="w", padx=65, pady=(0, 15))

frame_salas_container = ctk.CTkFrame(frame_inicial, fg_color="transparent")
frame_salas_container.pack(fill="x", padx=65)

# --- CONSTRUÇÃO DAS 5 SALAS COM OS NOMES DOS FILMES ---
frames_salas = {}

# Informações de personalização para os botões das 5 salas contendo os títulos dos filmes
info_salas = [
    {"num": 1, "titulo": "A ODISSEIA", "icone": "🎬", "cor": "#D19ABE"},
    {"num": 2, "titulo": "OBSESSÃO", "icone": "🍿", "cor": "#CC91AE"},
    {"num": 3, "titulo": "TOY STORY 5", "icone": "📹", "cor": "#B8789C"},
    {"num": 4, "titulo": "UM CABRA BOM DE BOLA", "icone": "🎞️", "cor": "#A4608A"},
    {"num": 5, "titulo": "HOMEM-ARANHA", "icone": "🎥", "cor": "#8F4B77"}
]

for sala in info_salas:
    i = sala["num"]
    titulo_filme = sala["titulo"]
    
    # 1. Botão/Card de seleção na Tela Inicial
    card_sala = ctk.CTkFrame(frame_salas_container, fg_color=sala["cor"], corner_radius=15, height=170)
    card_sala.pack(side="left", fill="both", expand=True, padx=5)
    card_sala.pack_propagate(False)

    ctk.CTkLabel(card_sala, text=sala["icone"], font=("Arial", 28), text_color="white").pack(anchor="w", padx=15, pady=(12, 0))
    ctk.CTkLabel(card_sala, text=titulo_filme, font=("Arial", 14, "bold"), text_color="white", wraplength=160, justify="left").pack(anchor="w", padx=15, pady=(2, 2))
    
    btn_entrar = ctk.CTkButton(
        card_sala, text="ENTRAR", width=100, height=30,
        fg_color="#8F4D75", hover_color="#713A5D", text_color="white", corner_radius=7,
        command=lambda num=i: (atualizar_assentos(num), mostrar_tela(frames_salas[num]))
    )
    btn_entrar.pack(anchor="w", padx=15, pady=5)

    # 2. Tela / Frame da Sala correspondente
    frame_sala = ctk.CTkFrame(app, fg_color="#FFF7FB")
    frames_salas[i] = frame_sala

    ctk.CTkLabel(frame_sala, text=f"{titulo_filme} (SALA {i})", font=("Arial", 28, "bold"), text_color="#F7D9ED").pack(pady=(15, 5))
    ctk.CTkLabel(frame_sala, text="🎬 TELA DO CINEMA 🎬", font=("Arial", 18, "bold")).pack()

    frame_assentos = ctk.CTkFrame(frame_sala, fg_color="transparent")
    frame_assentos.pack(pady=20)

    assentos_no_banco = buscar_assentos_ocupados(i)

    for r_idx, fila in enumerate(filas):
        for c_idx, coluna in enumerate(colunas):
            nome_assento = f"{fila}{coluna}"
            ocupado = assentos_no_banco.get(nome_assento, False)

            cor = "#D19AB4" if ocupado else "#E4C6D0"
            cor_texto = "white" if ocupado else "black"
            estado = "disabled" if ocupado else "normal"

            btn = ctk.CTkButton(
                frame_assentos, text=nome_assento, width=55, height=40,
                fg_color=cor, text_color=cor_texto, state=estado
            )
            botoes_assentos[i][nome_assento] = btn

            if not ocupado:
                btn.configure(command=lambda b=btn, num=i: alternar_assento(b, num))

            btn.grid(row=r_idx, column=c_idx, padx=3, pady=3)

    # Botões de Ação na Sala
    frame_botoes = ctk.CTkFrame(frame_sala, fg_color="transparent")
    frame_botoes.pack(pady=20)

    ctk.CTkButton(
        frame_botoes, text="🎟 Reservar", width=280, height=55,
        fg_color="#D19ABE", hover_color="#C05A9D",
        command=lambda num=i: reservar(num)
    ).pack(pady=8)

    ctk.CTkButton(
        frame_botoes, text="🏠 Voltar", width=280, height=55,
        fg_color="#CC91AE", hover_color="#B77A99", text_color="white",
        command=lambda: mostrar_tela(frame_inicial)
    ).pack(pady=8)

ctk.CTkLabel(
    frame_inicial,
    text="CINEMA RUBY  •  FILMES  •  SESSÕES  •  RESERVAS",
    font=("Arial", 12), text_color="#8F7C85"
).pack(pady=(25, 10))

mostrar_tela(frame_inicial)  # Exibe a tela inicial quando o programa começa
app.mainloop()  # Mantém a aplicação aberta