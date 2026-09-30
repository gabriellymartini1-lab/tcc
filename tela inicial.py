import customtkinter as ctk  # Importa a biblioteca CustomTkinter para criar a interface gráfica
from tkinter import messagebox  # Importa as caixas de mensagem do Tkinter
import psycopg  # Importa a biblioteca para conectar o Python ao PostgreSQL

DB_CONFIG = {  # Cria um dicionário com as configurações de conexão com o banco de dados
    "dbname": "cinema",  # Define o nome do banco de dados
    "user": "postgres",  # Define o usuário do PostgreSQL
    "password": "root",  # Define a senha do banco de dados
    "host": "localhost",  # Define que o banco está no próprio computador
    "port": "5432"  # Define a porta padrão utilizada pelo PostgreSQL
}

nome = []  # Cria uma lista para armazenar os assentos selecionados pelo usuário
filas = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]  # Cria as filas de A até J
colunas = list(range(1, 21))  # Cria os números das cadeiras de 1 até 20


ctk.set_appearance_mode("dark")  # Define o tema da interface como escuro

def buscar_assentos_ocupados():  # Cria uma função para buscar no banco quais assentos estão ocupados
    status_assentos = {}  # Cria um dicionário para armazenar o status de cada assento

    try:  # Inicia um bloco para tentar executar a conexão com o banco
        conn = psycopg.connect(**DB_CONFIG)  # Abre uma conexão com o banco usando as configurações acima
        cursor = conn.cursor()  # Cria um cursor para executar comandos SQL

        cursor.execute(  # Executa um comando SQL no banco de dados
            "SELECT fila, numero_cadeira, ocupado FROM sala1;"  # Busca fila, número e situação de cada cadeira
        )

        for fila, numero, ocupado in cursor.fetchall():  # Percorre todos os registros retornados pelo banco
            status_assentos[f"{fila}{numero}"] = ocupado  # Guarda o assento e seu status no dicionário

        cursor.close()  # Fecha o cursor do banco de dados
        conn.close()  # Fecha a conexão com o banco de dados

    except Exception as error:  # Captura qualquer erro que aconteça durante a consulta
        print("Erro ao buscar assentos:", error)  # Mostra o erro no terminal

    return status_assentos  # Retorna o dicionário contendo os assentos e seus status

def alternar_assento(btn):  # Cria uma função para selecionar ou desselecionar uma cadeira
    assento = btn.cget("text")  # Obtém o texto do botão, por exemplo A1

    if assento in nome:  # Verifica se o assento já está selecionado
        nome.remove(assento)  # Remove o assento da lista de selecionados

        btn.configure(  # Altera a aparência do botão
            fg_color="#E4C6D0",  # Define novamente a cor de fundo original
            text_color="black"  # Define a cor do texto como preta
        )

    else:  # Executa caso o assento ainda não esteja selecionado
        nome.append(assento)  # Adiciona o assento à lista de selecionados

        btn.configure(  # Altera a aparência do botão
            fg_color="#C05A9D",  # Define a cor rosa escura para indicar seleção
            text_color="white"  # Define o texto do botão como branco
        )

def reservar(lista):  # Cria uma função para reservar os assentos selecionados
    if not lista:  # Verifica se a lista está vazia
        messagebox.showwarning(  # Mostra uma mensagem de aviso
            "Atenção",  # Define o título da mensagem
            "Selecione pelo menos um assento para reservar."  # Define o texto do aviso
        )
        return  # Interrompe a função porque nenhum assento foi selecionado

    try:  # Inicia o bloco que tentará realizar a reserva
        conn = psycopg.connect(**DB_CONFIG)  # Abre uma conexão com o banco
        cursor = conn.cursor()  # Cria um cursor para executar comandos SQL

        for assento in lista:  # Percorre todos os assentos selecionados
            fila = assento[0]  # Pega a primeira letra do assento, que representa a fila
            numero = int(assento[1:])  # Pega o número do assento e transforma em inteiro

            cursor.execute(  # Executa o comando SQL de atualização
                """
                UPDATE sala1
                SET ocupado = TRUE
                WHERE fila = %s
                AND numero_cadeira = %s;
                """,  # Define o SQL que marca a cadeira como ocupada
                (fila, numero)  # Envia os valores da fila e do número para o SQL
            )

        conn.commit()  # Confirma e salva as alterações no banco de dados

        cursor.close()  # Fecha o cursor
        conn.close()  # Fecha a conexão com o banco

        messagebox.showinfo(  # Mostra uma mensagem informando que a reserva foi realizada
            "Reserva realizada",  # Define o título da mensagem
            f"Assentos reservados:\n{', '.join(lista)}"  # Mostra os assentos que foram reservados
        )

        lista.clear()  # Limpa a lista de assentos selecionados

        atualizar_assentos()  # Atualiza a aparência dos botões na tela

    except Exception as error:  # Captura qualquer erro ocorrido durante a reserva
        messagebox.showerror(  # Mostra uma mensagem de erro
            "Erro",  # Define o título da mensagem
            f"Não foi possível realizar a reserva:\n{error}"  # Mostra o erro ocorrido
        )

def atualizar_assentos():  # Cria uma função para atualizar os assentos na tela
    """
    Atualiza a aparência dos botões de acordo com o banco de dados.
    """  # Explica o objetivo da função

    assentos_no_banco = buscar_assentos_ocupados()  # Busca novamente os assentos ocupados no banco

    for r_idx, fila in enumerate(filas):  # Percorre todas as filas e guarda o índice de cada uma
        for c_idx, coluna in enumerate(colunas):  # Percorre todas as colunas e guarda o índice de cada uma

            nome_assento = f"{fila}{coluna}"  # Cria o nome do assento, por exemplo A1

            ocupado = assentos_no_banco.get(  # Procura no dicionário se o assento está ocupado
                nome_assento,  # Informa qual assento deve ser procurado
                False  # Caso não encontre, considera o assento livre
            )

            btn = botoes_assentos.get(nome_assento)  # Busca o botão correspondente ao assento

            if btn is None:  # Verifica se o botão não existe
                continue  # Pula para o próximo assento

            if ocupado:  # Verifica se o assento está ocupado
                btn.configure(  # Altera a aparência e o estado do botão
                    fg_color="#D19AB4",  # Define a cor do assento ocupado
                    text_color="white",  # Define a cor do texto como branca
                    state="disabled"  # Desabilita o botão
                )

            else:  # Executa caso o assento esteja livre
                btn.configure(  # Altera a aparência do botão
                    fg_color="#E4C6D0",  # Define a cor do assento livre
                    text_color="black",  # Define a cor do texto como preta
                    state="normal"  # Deixa o botão habilitado
                )

def mostrar_sala_inicial():  # Cria uma função para mostrar a tela inicial
    frame_sala1.pack_forget()  # Esconde a tela da Sala 1
    frame_inicial.pack(fill="both", expand=True)  # Mostra a tela inicial ocupando toda a janela


def mostrar_sala1():  # Cria uma função para mostrar a Sala 1
    frame_inicial.pack_forget()  # Esconde a tela inicial
    frame_sala1.pack(fill="both", expand=True)  # Mostra a Sala 1 ocupando toda a janela

app = ctk.CTk()  # Cria a janela principal da aplicação

app.title("CINEMA RUBY")  # Define o título da janela
app.geometry("1300x780")  # Define o tamanho da janela

frame_inicial = ctk.CTkFrame(  # Cria o quadro que representa a tela inicial
    app,  # Define a janela principal como pai do quadro
    fg_color="#FFF7FB"  # Define a cor de fundo do quadro
)

frame_inicial.pack(  # Adiciona o quadro à janela
    fill="both",  # Faz o quadro ocupar largura e altura disponíveis
    expand=True  # Permite que o quadro se expanda
)

ctk.CTkLabel(  # Cria um texto na tela
    frame_inicial,  # Coloca o texto dentro do quadro inicial
    text="CINEMA RUBY",  # Define o texto exibido
    font=("Arial", 36, "bold"),  # Define fonte, tamanho e estilo
    text_color="#F8C4E6"  # Define a cor do texto
).pack(pady=(80, 30))  # Posiciona o texto com espaçamento vertical

ctk.CTkButton(  # Cria um botão
    frame_inicial,  # Coloca o botão no quadro inicial
    text="🎬 SALA 1",  # Define o texto do botão
    width=250,  # Define a largura do botão
    height=50,  # Define a altura do botão
    command=mostrar_sala1  # Define a função executada ao clicar
).pack(pady=10)  # Adiciona espaçamento ao redor do botão

ctk.CTkButton(  # Cria outro botão
    frame_inicial,  # Coloca o botão no quadro inicial
    text="🍿 SALA 2",  # Define o texto do botão
    width=250,  # Define a largura do botão
    height=50  # Define a altura do botão
).pack(pady=10)  # Adiciona espaçamento ao redor do botão


frame_sala1 = ctk.CTkFrame(  # Cria o quadro da Sala 1
    app,  # Define a janela principal como pai
    fg_color="#FFF7FB"  # Define a cor de fundo da Sala 1
)

ctk.CTkLabel(  # Cria o título da Sala 1
    frame_sala1,  # Coloca o título dentro do quadro da Sala 1
    text="SALA 1",  # Define o texto do título
    font=("Arial", 30, "bold"),  # Define fonte, tamanho e estilo
    text_color="#F7D9ED"  # Define a cor do título
).pack(pady=(15, 5))  # Posiciona o título com espaçamento

ctk.CTkLabel(  # Cria um texto para representar a tela do cinema
    frame_sala1,  # Coloca o texto dentro da Sala 1
    text="🎬 TELA DO CINEMA 🎬",  # Define o texto exibido
    font=("Arial", 18, "bold")  # Define fonte, tamanho e estilo
).pack()  # Posiciona o texto

frame_assentos = ctk.CTkFrame(  # Cria um quadro para armazenar os assentos
    frame_sala1,  # Coloca o quadro dentro da Sala 1
    fg_color="transparent"  # Deixa o fundo transparente
)

frame_assentos.pack(pady=20)  # Posiciona o quadro com espaçamento vertical

assentos_no_banco = buscar_assentos_ocupados()  # Consulta o banco para descobrir os assentos ocupados

botoes_assentos = {}  # Cria um dicionário para guardar os botões dos assentos

for r_idx, fila in enumerate(filas):  # Percorre todas as filas da Sala 1

    for c_idx, coluna in enumerate(colunas):  # Percorre todas as colunas de cada fila

        nome_assento = f"{fila}{coluna}"  # Cria o nome do assento, como A1, A2, B1 etc.

        ocupado = assentos_no_banco.get(  # Verifica no dicionário se o assento está ocupado
            nome_assento,  # Informa o nome do assento
            False  # Considera livre caso não esteja no banco
        )

        if ocupado:  # Verifica se o assento está ocupado
            cor = "#D19AB4"  # Define a cor para assento ocupado
            cor_texto = "white"  # Define a cor do texto como branca
            estado = "disabled"  # Desabilita o botão

        else:  # Executa caso o assento esteja livre
            cor = "#E4C6D0"  # Define a cor para assento livre
            cor_texto = "black"  # Define a cor do texto como preta
            estado = "normal"  # Mantém o botão habilitado

        btn = ctk.CTkButton(  # Cria o botão do assento
            frame_assentos,  # Coloca o botão dentro do quadro dos assentos
            text=nome_assento,  # Mostra o nome do assento no botão
            width=55,  # Define a largura do botão
            height=40,  # Define a altura do botão
            fg_color=cor,  # Define a cor de fundo do botão
            text_color=cor_texto,  # Define a cor do texto
            state=estado  # Define se o botão está habilitado ou desabilitado
        )

        botoes_assentos[nome_assento] = btn  # Guarda o botão no dicionário usando o nome do assento

        if not ocupado:  # Verifica se o assento está livre

            btn.configure(  # Configura o comando do botão
                command=lambda b=btn: alternar_assento(b)  # Chama a função para selecionar o assento
            )

        btn.grid(  # Posiciona o botão utilizando o sistema de grade
            row=r_idx,  # Define a linha do botão
            column=c_idx,  # Define a coluna do botão
            padx=3,  # Define o espaçamento horizontal
            pady=3  # Define o espaçamento vertical
        )

frame_botoes = ctk.CTkFrame(  # Cria um quadro para os botões de ação
    frame_sala1,  # Coloca o quadro dentro da Sala 1
    fg_color="transparent"  # Deixa o fundo transparente
)

frame_botoes.pack(pady=20)  # Posiciona o quadro com espaçamento vertical

ctk.CTkButton(  # Cria o botão de reservar
    frame_botoes,  # Coloca o botão dentro do quadro de botões
    text="🎟 Reservar",  # Define o texto do botão
    width=280,  # Define a largura
    height=55,  # Define a altura
    fg_color="#D19ABE",  # Define a cor de fundo
    hover_color="#C05A9D",  # Define a cor quando o mouse passa por cima
    command=lambda: reservar(nome)  # Chama a função reservar usando a lista de assentos
).pack(pady=8)  # Posiciona o botão com espaçamento

ctk.CTkButton(  # Cria o botão para voltar à tela inicial
    frame_botoes,  # Coloca o botão dentro do quadro de botões
    text="🏠 Voltar",  # Define o texto do botão
    width=280,  # Define a largura
    height=55,  # Define a altura
    fg_color="#CC91AE",  # Define a cor de fundo
    hover_color="#B77A99",  # Define a cor quando o mouse passa por cima
    text_color="white",  # Define a cor do texto
    command=mostrar_sala_inicial  # Chama a função para voltar à tela inicial
).pack(pady=8)  # Posiciona o botão com espaçamento

mostrar_sala_inicial()  # Exibe a tela inicial quando o programa começa
app.mainloop()  # Mantém a aplicação aberta e esperando ações do usuário
