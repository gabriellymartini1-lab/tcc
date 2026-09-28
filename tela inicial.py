import customtkinter as ctk

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

mostrar_sala_inicial()
app.mainloop()