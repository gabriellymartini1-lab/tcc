import customtkinter as ctk
from tkinter import messagebox
import psycopg

DB_CONFIG = {
    "dbname": "cinema",
    "user": "postgres",
    "password": "root",
    "host": "localhost",
    "port": "5432"
}

nome = []
filas = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
colunas = list(range(1, 21))

ctk.set_appearance_mode("light")


def buscar_assentos_ocupados():
    status_assentos = {}

    try:
        conn = psycopg.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT fila, numero_cadeira, ocupado FROM sala1;"
        )

        for fila, numero, ocupado in cursor.fetchall():
            status_assentos[f"{fila}{numero}"] = ocupado

        cursor.close()
        conn.close()

    except Exception as error:
        print("Erro ao buscar assentos:", error)

    return status_assentos


def alternar_assento(btn):
    assento = btn.cget("text")

    if assento in nome:
        nome.remove(assento)

        btn.configure(
            fg_color="#E4C6D0",
            text_color="black"
        )

    else:
        nome.append(assento)

        btn.configure(
            fg_color="#C05A9D",
            text_color="white"
        )


def reservar(lista):
    if not lista:
        messagebox.showwarning(
            "Atenção",
            "Selecione pelo menos um assento para reservar."
        )
        return

    try:
        conn = psycopg.connect(**DB_CONFIG)
        cursor = conn.cursor()

        for assento in lista:
            fila = assento[0]
            numero = int(assento[1:])

            cursor.execute(
                """
                UPDATE sala1
                SET ocupado = TRUE
                WHERE fila = %s
                AND numero_cadeira = %s;
                """,
                (fila, numero)
            )

        conn.commit()

        cursor.close()
        conn.close()

        messagebox.showinfo(
            "Reserva realizada",
            f"Assentos reservados:\n{', '.join(lista)}"
        )

        lista.clear()

        # Atualiza a tela
        atualizar_assentos()

    except Exception as error:
        messagebox.showerror(
            "Erro",
            f"Não foi possível realizar a reserva:\n{error}"
        )


def atualizar_assentos():
    """
    Atualiza a aparência dos botões de acordo com o banco de dados.
    """

    assentos_no_banco = buscar_assentos_ocupados()

    for r_idx, fila in enumerate(filas):
        for c_idx, coluna in enumerate(colunas):

            nome_assento = f"{fila}{coluna}"

            ocupado = assentos_no_banco.get(
                nome_assento,
                False
            )

            btn = botoes_assentos.get(nome_assento)

            if btn is None:
                continue

            if ocupado:
                btn.configure(
                    fg_color="#D19AB4",
                    text_color="white",
                    state="disabled"
                )

            else:
                btn.configure(
                    fg_color="#E4C6D0",
                    text_color="black",
                    state="normal"
                )


def mostrar_sala_inicial():
    frame_sala1.pack_forget()
    frame_inicial.pack(fill="both", expand=True)


def mostrar_sala1():
    frame_inicial.pack_forget()
    frame_sala1.pack(fill="both", expand=True)


app = ctk.CTk()

app.title("CINEMA RUBY")
app.geometry("1300x780")

frame_inicial = ctk.CTkFrame(
    app,
    fg_color="#FFF7FB"
)

frame_inicial.pack(
    fill="both",
    expand=True
)


ctk.CTkLabel(
    frame_inicial,
    text="CINEMA RUBY",
    font=("Arial", 36, "bold"),
    text_color="#F8C4E6"
).pack(pady=(80, 30))


ctk.CTkButton(
    frame_inicial,
    text="🎬 SALA 1",
    width=250,
    height=50,
    command=mostrar_sala1
).pack(pady=10)


ctk.CTkButton(
    frame_inicial,
    text="🍿 SALA 2",
    width=250,
    height=50
).pack(pady=10)

frame_sala1 = ctk.CTkFrame(
    app,
    fg_color="#FFF7FB"
)


ctk.CTkLabel(
    frame_sala1,
    text="SALA 1",
    font=("Arial", 30, "bold"),
    text_color="#F7D9ED"
).pack(pady=(15, 5))


ctk.CTkLabel(
    frame_sala1,
    text="🎬 TELA DO CINEMA 🎬",
    font=("Arial", 18, "bold")
).pack()


frame_assentos = ctk.CTkFrame(
    frame_sala1,
    fg_color="transparent"
)

frame_assentos.pack(pady=20)


assentos_no_banco = buscar_assentos_ocupados()

botoes_assentos = {}


for r_idx, fila in enumerate(filas):

    for c_idx, coluna in enumerate(colunas):

        nome_assento = f"{fila}{coluna}"

        ocupado = assentos_no_banco.get(
            nome_assento,
            False
        )

        if ocupado:
            cor = "#D19AB4"
            cor_texto = "white"
            estado = "disabled"

        else:
            cor = "#E4C6D0"
            cor_texto = "black"
            estado = "normal"

        btn = ctk.CTkButton(
            frame_assentos,
            text=nome_assento,
            width=55,
            height=40,
            fg_color=cor,
            text_color=cor_texto,
            state=estado
        )

        botoes_assentos[nome_assento] = btn

        if not ocupado:

            btn.configure(
                command=lambda b=btn: alternar_assento(b)
            )

        btn.grid(
            row=r_idx,
            column=c_idx,
            padx=3,
            pady=3
        )


frame_botoes = ctk.CTkFrame(
    frame_sala1,
    fg_color="transparent"
)

frame_botoes.pack(pady=20)


ctk.CTkButton(
    frame_botoes,
    text="🎟 Reservar",
    width=280,
    height=55,
    fg_color="#D19ABE",
    hover_color="#C05A9D",
    command=lambda: reservar(nome)
).pack(pady=8)


ctk.CTkButton(
    frame_botoes,
    text="🏠 Voltar",
    width=280,
    height=55,
    fg_color="#CC91AE",
    hover_color="#B77A99",
    text_color="white",
    command=mostrar_sala_inicial
).pack(pady=8)

mostrar_sala_inicial()

app.mainloop()
