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
filas = ["A", "B", "C", "D", "E", "F", "G", "H"]
colunas = [1, 2, 3, 4, 5]

ctk.set_appearance_mode("dark")

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

def mostrar_sala_inicial():
    esconder_todas_as_telas()
    frame_inicial.pack(fill="both", expand=True)

def mostrar_sala1():
    esconder_todas_as_telas()
    frame_sala1.pack(fill="both", expand=True)

def mostrar_sala2():
    esconder_todas_as_telas()
    frame_sala2.pack(fill="both", expand=True)

def esconder_todas_as_telas():
    frame_inicial.pack_forget()
    frame_sala1.pack_forget()
    frame_sala2.pack_forget()

app = ctk.CTk()
app.title("CINEMA RUBY")
app.geometry("800x700")

frame_inicial = ctk.CTkFrame(app, fg_color="#f8e5f7")

lbl_inicial = ctk.CTkLabel(frame_inicial, text="CINEMA RUBY", font=("Arial", 16, "bold"))
lbl_inicial.pack(pady=20)

btn_ir_sala1 = ctk.CTkButton(frame_inicial, text="SALA 1", command=mostrar_sala1)
btn_ir_sala1.pack(pady=20)

btn_ir_sala2 = ctk.CTkButton(frame_inicial, text="SALA 2", command=mostrar_sala2)
btn_ir_sala2.pack(pady=20)

frame_sala1 = ctk.CTkFrame(app, fg_color="#f7e7f3")

lbl_sala1 = ctk.CTkLabel(frame_sala1, text="SALA 1", font=("Arial", 16, "bold"))
lbl_sala1.pack(pady=20)

btn_voltar_sala1 = ctk.CTkButton(frame_sala1, text="Voltar", command=mostrar_sala_inicial)
btn_voltar_sala1.pack(pady=10)

frame_sala2 = ctk.CTkFrame(app, fg_color="#fae9f8")

lbl_sala2 = ctk.CTkLabel(frame_sala2, text="SALA 2", font=("Arial", 16, "bold"))
lbl_sala2.pack(pady=20)

btn_voltar_sala2 = ctk.CTkButton(frame_sala2, text="Voltar", command=mostrar_sala_inicial)
btn_voltar_sala2.pack(pady=10)

frame_sala1 = ctk.CTkFrame(app, fg_color="#db5ad5")

lbl_tela = ctk.CTkLabel(
    frame_sala1,
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

assentos_no_banco = buscar_assentos_ocupados()

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
            frame_sala1,
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
    frame_sala1,
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

mostrar_sala_inicial()
app.mainloop()