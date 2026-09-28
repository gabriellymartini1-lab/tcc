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

ctk.set_appearance_mode("light")


def buscar_assentos_ocupados():
    status_assentos = {}

    try:
        conn = psycopg.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT fila, numero_cadeira, ocupado FROM sala1;"
        )

        linhas = cursor.fetchall()

        for fila, numero, ocupado in linhas:
            chave = f"{fila}{numero}"
            status_assentos[chave] = ocupado

    except Exception as error:
        print(f"Erro ao consultar o banco de dados: {error}")

    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass

    return status_assentos


def alternar_assento(btn):
    global nome

    if btn.cget("fg_color") == "#ffffff":

        btn.configure(
            fg_color="#4CAF50",
            text_color="white"
        )

        nome.append(btn.cget("text"))

    else:

        btn.configure(
            fg_color="#ffffff",
            text_color="black"
        )

        nome.remove(btn.cget("text"))


def reservar(a):

    messagebox.showinfo(
        "Reserva Concluída",
        f"Os seguintes assentos foram reservados com sucesso:\n{nome}"
    )

    conn = psycopg.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:

        for elemento in a:

            letra = elemento[0]
            numero = int(elemento[1:])

            cursor.execute("""
                UPDATE sala1
                SET ocupado = TRUE
                WHERE fila = %s
                AND numero_cadeira = %s;
            """, (letra, numero))

        conn.commit()

    except Exception as error:

        print(error)
        conn.rollback()

def cancelamento(a):

    messagebox.showinfo(
        "Cancelamento Concluído",
        f"Os seguintes assentos foram cancelados com sucesso:\n{nome}"
    )

    conn = psycopg.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:

        for elemento in a:

            letra = elemento[0]
            numero = elemento[1]

            query = """
            UPDATE assentos
            SET ocupado = false
            WHERE fila = %s
            AND numero_cadeira = %s;
            """

            cursor.execute(query, (letra, numero))
            conn.commit()

    except Exception as error:

        print(f"Erro ao operar no banco: {error}")
        conn.rollback()

    cursor.close()
    conn.close()


root = ctk.CTk()
root.title("Sistema de Reserva - Cinema")
root.geometry("350x550")

assentos_no_banco = buscar_assentos_ocupados()

lbl_tela = ctk.CTkLabel(
    root,
    text="TELA DO CINEMA",
    font=("Arial", 11, "bold")
)

lbl_tela.grid(
    row=0,
    column=0,
    columnspan=5,
    padx=10,
    pady=10
)

filas = ["A", "B", "C", "D", "E", "F", "G", "H"]
colunas = [1, 2, 3, 4, 5]

for r_idx in range(len(filas)):

    fila = filas[r_idx]

    for c_idx in range(len(colunas)):

        coluna = colunas[c_idx]

        nome_assento = f"{fila}{coluna}"

        esta_ocupado = assentos_no_banco.get(nome_assento)

        if esta_ocupado:

            cor_fundo = "#f44336"
            estado_botao = "disabled"

        else:

            cor_fundo = "#ffffff"
            estado_botao = "normal"

        btn = ctk.CTkButton(
            root,
            text=nome_assento,
            width=40,
            height=40,
            font=("Arial", 9, "bold"),
            fg_color=cor_fundo,
            text_color="white" if esta_ocupado else "black",
            state=estado_botao
        )

        if estado_botao == "normal":
            btn.configure(
                command=lambda b=btn: alternar_assento(b)
            )

        btn.grid(
            row=r_idx + 1,
            column=c_idx,
            padx=4,
            pady=4
        )

btn_reservar = ctk.CTkButton(
    root,
    text="Reservar",
    height=40,
    font=("Arial", 14, "bold"),
    fg_color="#0d761f",
    text_color="black",
    command=lambda: reservar(nome)
)

btn_reservar.grid(
    row=9,
    column=0,
    columnspan=5,
    sticky="ew",
    padx=4,
    pady=4
)

root.mainloop()