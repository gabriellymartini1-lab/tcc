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

assentos_selecionados = {i: [] for i in range(1, 6)}
assentos_cancelar = {i: [] for i in range(1, 6)}
botoes_assentos = {i: {} for i in range(1, 6)}

filas = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
colunas = list(range(1, 21))

ctk.set_appearance_mode("dark")


def testar_conexao():
    try:
        conn = psycopg.connect(**DB_CONFIG)
        conn.close()
        print("Conexão com o PostgreSQL via pgAdmin 4 realizada com sucesso!")
    except Exception as error:
        print("Erro ao conectar à base de dados pgAdmin 4:", error)


def registar_historico(num_sala, assentos, tipo):
    try:
        conn = psycopg.connect(**DB_CONFIG)
        cursor = conn.cursor()
        assentos_str = ", ".join(assentos)

        cursor.execute(
            "INSERT INTO compras (sala, assentos, tipo) VALUES (%s, %s, %s);",
            (num_sala, assentos_str, tipo)
        )

        conn.commit()
        cursor.close()
        conn.close()

    except Exception as error:
        print("Erro ao registar no histórico:", error)


def buscar_assentos_ocupados(num_sala):
    status_assentos = {}

    try:
        conn = psycopg.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute(
            f"SELECT fila, numero_cadeira, ocupado FROM sala{num_sala};"
        )

        for fila, numero, ocupado in cursor.fetchall():
            status_assentos[f"{fila.strip()}{numero}"] = ocupado

        cursor.close()
        conn.close()

    except Exception as error:
        print(f"Erro ao buscar assentos da Sala {num_sala}:", error)

    return status_assentos


def alternar_assento_livre(btn, num_sala):
    assento = btn.cget("text")
    lista = assentos_selecionados[num_sala]

    if assento in lista:
        lista.remove(assento)
        btn.configure(
            fg_color="#E4C6D0",
            text_color="black"
        )
    else:
        lista.append(assento)
        btn.configure(
            fg_color="#C05A9D",
            text_color="white"
        )


def alternar_assento_ocupado(btn, num_sala):
    assento = btn.cget("text")
    lista = assentos_cancelar[num_sala]

    if assento in lista:
        lista.remove(assento)
        btn.configure(
            fg_color="#D19AB4",
            text_color="white"
        )
    else:
        lista.append(assento)
        btn.configure(
            fg_color="#A32A2A",
            text_color="white"
        )


def reservar(num_sala):
    lista = assentos_selecionados[num_sala]

    if not lista:
        messagebox.showwarning(
            "Atenção",
            "Selecione pelo menos um assento livre para reservar."
        )
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

        registar_historico(num_sala, lista, "Reserva")

        messagebox.showinfo(
            "Reserva Realizada",
            f"Assentos reservados na Sala {num_sala}:\n{', '.join(lista)}"
        )

        lista.clear()
        atualizar_assentos(num_sala)

    except Exception as error:
        messagebox.showerror(
            "Erro",
            f"Não foi possível realizar a reserva:\n{error}"
        )


def cancelar_reserva(num_sala):
    lista = assentos_cancelar[num_sala]

    if not lista:
        messagebox.showwarning(
            "Atenção",
            "Clique em um assento ocupado (rosa escuro) para selecioná-lo e cancelar."
        )
        return

    confirmar = messagebox.askyesno(
        "Confirmar Cancelamento",
        f"Tem certeza que deseja cancelar a reserva dos assentos:\n{', '.join(lista)}?"
    )

    if not confirmar:
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
                SET ocupado = FALSE
                WHERE fila = %s AND numero_cadeira = %s;
                """,
                (fila, numero)
            )

        conn.commit()
        cursor.close()
        conn.close()

        registar_historico(num_sala, lista, "Cancelamento")

        messagebox.showinfo(
            "Cancelamento Concluído",
            f"Reservas canceladas na Sala {num_sala}:\n{', '.join(lista)}"
        )

        lista.clear()
        atualizar_assentos(num_sala)

    except Exception as error:
        messagebox.showerror(
            "Erro",
            f"Não foi possível cancelar a reserva:\n{error}"
        )


def atualizar_assentos(num_sala):
    assentos_no_banco = buscar_assentos_ocupados(num_sala)
    mapa_botoes = botoes_assentos[num_sala]

    assentos_selecionados[num_sala].clear()
    assentos_cancelar[num_sala].clear()

    for fila in filas:
        for coluna in colunas:
            nome_assento = f"{fila}{coluna}"
            ocupado = assentos_no_banco.get(nome_assento, False)
            btn = mapa_botoes.get(nome_assento)

            if btn is None:
                continue

            if ocupado:
                btn.configure(
                    fg_color="#D19AB4",
                    text_color="white",
                    state="normal",
                    command=lambda b=btn, num=num_sala:
                    alternar_assento_ocupado(b, num)
                )
            else:
                btn.configure(
                    fg_color="#E4C6D0",
                    text_color="black",
                    state="normal",
                    command=lambda b=btn, num=num_sala:
                    alternar_assento_livre(b, num)
                )


def carregar_historico():
    for item in tabela_historico.get_children():
        tabela_historico.delete(item)

    try:
        conn = psycopg.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, sala, assentos, tipo, data_hora "
            "FROM compras ORDER BY id DESC;"
        )

        registos = cursor.fetchall()

        for reg in registos:
            id_compra, sala, assentos, tipo, data_hora = reg

            data_formatada = (
                data_hora.strftime("%d/%m/%Y %H:%M:%S")
                if data_hora
                else "-"
            )

            tabela_historico.insert(
                "",
                "end",
                values=(
                    id_compra,
                    f"Sala {sala}",
                    assentos,
                    tipo,
                    data_formatada
                )
            )

        cursor.close()
        conn.close()

    except Exception as error:
        messagebox.showerror(
            "Erro",
            f"Erro ao carregar o histórico:\n{error}"
        )


def mostrar_tela(frame_desejado):
    frame_inicial.pack_forget()
    frame_historico.pack_forget()

    for f in frames_salas.values():
        f.pack_forget()

    frame_desejado.pack(
        fill="both",
        expand=True
    )


def abrir_historico():
    carregar_historico()
    mostrar_tela(frame_historico)


testar_conexao()

app = ctk.CTk()
app.title("CINEMA RUBY")
app.geometry("1400x900")

frame_inicial = ctk.CTkFrame(
    app,
    fg_color="#1A1518"
)

frame_inicial.pack(
    fill="both",
    expand=True
)

frame_topo = ctk.CTkFrame(
    frame_inicial,
    fg_color="transparent"
)

frame_topo.pack(
    fill="x",
    padx=65,
    pady=(25, 10)
)

ctk.CTkLabel(
    frame_topo,
    text="CINEMA RUBY",
    font=("Arial", 32, "bold"),
    text_color="#D19ABE"
).pack(side="left")

btn_historico = ctk.CTkButton(
    frame_topo,
    text="📜 HISTÓRICO",
    font=("Arial", 13, "bold"),
    fg_color="#8F4D75",
    hover_color="#713A5D",
    text_color="white",
    width=140,
    height=35,
    command=abrir_historico
)

btn_historico.pack(
    side="right",
    padx=10
)

ctk.CTkLabel(
    frame_topo,
    text="INÍCIO",
    font=("Arial", 14, "bold"),
    text_color="#F7D9ED"
).pack(
    side="right",
    padx=15
)

frame_banner = ctk.CTkFrame(
    frame_inicial,
    fg_color="#2B2026",
    corner_radius=18,
    height=500
)

frame_banner.pack(
    fill="x",
    padx=65,
    pady=(20, 25)
)

frame_banner.pack_propagate(False)

frame_banner_center = ctk.CTkFrame(
    frame_banner,
    fg_color="transparent"
)

frame_banner_center.pack(
    expand=True,
    anchor="center"
)

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

        ctk_img = ctk.CTkImage(
            light_image=pil_img,
            dark_image=pil_img,
            size=(180, 320)
        )

        card = ctk.CTkButton(
            frame_banner_center,
            text="",
            image=ctk_img,
            fg_color="transparent",
            hover=False
        )

        card.pack(
            side="left",
            padx=15,
            pady=20
        )

    except Exception as e:
        print(
            f"Erro ao carregar a imagem {img_nome}: {e}"
        )

ctk.CTkLabel(
    frame_inicial,
    text="Escolha seu filme",
    font=("Arial", 24, "bold"),
    text_color="white"
).pack(
    anchor="w",
    padx=65,
    pady=(0, 15)
)

frame_salas_container = ctk.CTkFrame(
    frame_inicial,
    fg_color="transparent"
)

frame_salas_container.pack(
    fill="x",
    padx=65
)

frames_salas = {}

info_salas = [
    {
        "num": 1,
        "titulo": "A ODISSEIA",
        "icone": "🎬",
        "cor": "#D19ABE"
    },
    {
        "num": 2,
        "titulo": "OBSESSÃO",
        "icone": "🍿",
        "cor": "#CC91AE"
    },
    {
        "num": 3,
        "titulo": "TOY STORY 5",
        "icone": "📹",
        "cor": "#B8789C"
    },
    {
        "num": 4,
        "titulo": "UM CABRA BOM DE BOLA",
        "icone": "🎞️",
        "cor": "#A4608A"
    },
    {
        "num": 5,
        "titulo": "HOMEM-ARANHA",
        "icone": "🎥",
        "cor": "#8F4B77"
    }
]

for sala in info_salas:
    i = sala["num"]
    titulo_filme = sala["titulo"]

    card_sala = ctk.CTkFrame(
        frame_salas_container,
        fg_color=sala["cor"],
        corner_radius=15,
        height=170
    )

    card_sala.pack(
        side="left",
        fill="both",
        expand=True,
        padx=5
    )

    card_sala.pack_propagate(False)

    ctk.CTkLabel(
        card_sala,
        text=sala["icone"],
        font=("Arial", 28),
        text_color="white"
    ).pack(
        anchor="w",
        padx=15,
        pady=(12, 0)
    )

    ctk.CTkLabel(
        card_sala,
        text=titulo_filme,
        font=("Arial", 14, "bold"),
        text_color="white",
        wraplength=160,
        justify="left"
    ).pack(
        anchor="w",
        padx=15,
        pady=(2, 2)
    )

    btn_entrar = ctk.CTkButton(
        card_sala,
        text="ENTRAR",
        width=100,
        height=30,
        fg_color="#8F4D75",
        hover_color="#713A5D",
        text_color="white",
        corner_radius=7,
        command=lambda num=i: (
            atualizar_assentos(num),
            mostrar_tela(frames_salas[num])
        )
    )

    btn_entrar.pack(
        anchor="w",
        padx=15,
        pady=5
    )

    frame_sala = ctk.CTkFrame(
        app,
        fg_color="#FFF7FB"
    )

    frames_salas[i] = frame_sala

    ctk.CTkLabel(
        frame_sala,
        text=f"{titulo_filme} (SALA {i})",
        font=("Arial", 28, "bold"),
        text_color="#F7D9ED"
    ).pack(
        pady=(15, 5)
    )

    ctk.CTkLabel(
        frame_sala,
        text="🎬 TELA DO CINEMA 🎬",
        font=("Arial", 18, "bold")
    ).pack()

    frame_assentos = ctk.CTkFrame(
        frame_sala,
        fg_color="transparent"
    )

    frame_assentos.pack(
        pady=15
    )

    for r_idx, fila in enumerate(filas):
        for c_idx, coluna in enumerate(colunas):
            nome_assento = f"{fila}{coluna}"

            btn = ctk.CTkButton(
                frame_assentos,
                text=nome_assento,
                width=55,
                height=40
            )

            botoes_assentos[i][nome_assento] = btn

            btn.grid(
                row=r_idx,
                column=c_idx,
                padx=3,
                pady=3
            )

    frame_botoes = ctk.CTkFrame(
        frame_sala,
        fg_color="transparent"
    )

    frame_botoes.pack(
        pady=10
    )

    ctk.CTkButton(
        frame_botoes,
        text="🎟 Reservar Assentos Selecionados",
        width=280,
        height=45,
        fg_color="#D19ABE",
        hover_color="#C05A9D",
        text_color="white",
        font=("Arial", 14, "bold"),
        command=lambda num=i: reservar(num)
    ).pack(
        side="left",
        padx=10
    )

    ctk.CTkButton(
        frame_botoes,
        text="❌ Cancelar Reserva",
        width=280,
        height=45,
        fg_color="#A32A2A",
        hover_color="#802020",
        text_color="white",
        font=("Arial", 14, "bold"),
        command=lambda num=i: cancelar_reserva(num)
    ).pack(
        side="left",
        padx=10
    )

    ctk.CTkButton(
        frame_botoes,
        text="🏠 Voltar ao Início",
        width=200,
        height=45,
        fg_color="#CC91AE",
        hover_color="#B77A99",
        text_color="white",
        font=("Arial", 14, "bold"),
        command=lambda: mostrar_tela(frame_inicial)
    ).pack(
        side="left",
        padx=10
    )


frame_historico = ctk.CTkFrame(
    app,
    fg_color="#1A1518"
)

ctk.CTkLabel(
    frame_historico,
    text="📜 HISTÓRICO DE COMPRAS E CANCELAMENTOS",
    font=("Arial", 26, "bold"),
    text_color="#D19ABE"
).pack(
    pady=25
)

frame_tabela = ctk.CTkFrame(
    frame_historico,
    fg_color="#2B2026",
    corner_radius=15
)

frame_tabela.pack(
    fill="both",
    expand=True,
    padx=65,
    pady=10
)

style = ttk.Style()
style.theme_use("default")

style.configure(
    "Treeview",
    background="#2B2026",
    foreground="white",
    fieldbackground="#2B2026",
    rowheight=30,
    font=("Arial", 11)
)

style.configure(
    "Treeview.Heading",
    background="#8F4D75",
    foreground="white",
    font=("Arial", 12, "bold")
)

style.map(
    "Treeview",
    background=[("selected", "#C05A9D")]
)

colunas_hist = (
    "ID",
    "Sala",
    "Assentos",
    "Tipo",
    "Data / Hora"
)

tabela_historico = ttk.Treeview(
    frame_tabela,
    columns=colunas_hist,
    show="headings"
)

tabela_historico.heading(
    "ID",
    text="ID"
)

tabela_historico.heading(
    "Sala",
    text="SALA"
)

tabela_historico.heading(
    "Assentos",
    text="ASSENTOS"
)

tabela_historico.heading(
    "Tipo",
    text="TIPO DE OPERAÇÃO"
)

tabela_historico.heading(
    "Data / Hora",
    text="DATA E HORA"
)

tabela_historico.column(
    "ID",
    width=60,
    anchor="center"
)

tabela_historico.column(
    "Sala",
    width=120,
    anchor="center"
)

tabela_historico.column(
    "Assentos",
    width=300,
    anchor="center"
)

tabela_historico.column(
    "Tipo",
    width=180,
    anchor="center"
)

tabela_historico.column(
    "Data / Hora",
    width=220,
    anchor="center"
)

scrollbar = ttk.Scrollbar(
    frame_tabela,
    orient="vertical",
    command=tabela_historico.yview
)

tabela_historico.configure(
    yscrollcommand=scrollbar.set
)

tabela_historico.pack(
    side="left",
    fill="both",
    expand=True,
    padx=(15, 0),
    pady=15
)

scrollbar.pack(
    side="right",
    fill="y",
    padx=(0, 15),
    pady=15
)

ctk.CTkButton(
    frame_historico,
    text="🏠 Voltar ao Início",
    width=220,
    height=45,
    fg_color="#CC91AE",
    hover_color="#B77A99",
    text_color="white",
    font=("Arial", 14, "bold"),
    command=lambda: mostrar_tela(frame_inicial)
).pack(
    pady=20
)

ctk.CTkLabel(
    frame_inicial,
    text="CINEMA RUBY  •  FILMES  •  SESSÕES  •  RESERVAS",
    font=("Arial", 12),
    text_color="#8F7C85"
).pack(
    pady=(25, 10)
)

mostrar_tela(frame_inicial)

app.mainloop()
