import customtkinter as ctk 
from tkinter import messagebox, ttk  # Importa caixas de mensagem e o módulo ttk (Treeview/Style) do Tkinter
import psycopg  # Importa a biblioteca para conectar o Python ao banco de dados PostgreSQL/pgAdmin
from PIL import Image  # Importa o módulo Image do Pillow para abrir e manipular as imagens dos pôsteres
from pathlib import Path  # Importa Path para manipular os caminhos de ficheiros de forma compatível com o sistema

DB_CONFIG = {  # Cria um dicionário com as credenciais e configurações de acesso ao PostgreSQL / pgAdmin 4
    "dbname": "cinema",  # Nome da base de dados criada no pgAdmin 4
    "user": "postgres",  # Utilizador padrão do PostgreSQL
    "password": "root",  # Altera para a palavra-passe que definiste na instalação do pgAdmin
    "host": "localhost",  # Endereço do servidor (localhost para banco local)
    "port": "5432"  # Porta padrão do PostgreSQL
}  # Fecha a estrutura do dicionário de configuração

BASE_DIR = Path(__file__).resolve().parent  # Obtém o caminho absoluto do diretório onde este ficheiro .py está guardado

assentos_selecionados = {i: [] for i in range(1, 6)}  # Inicializa um dicionário com listas para os assentos marcados para RESERVA
assentos_cancelar = {i: [] for i in range(1, 6)}  # Inicializa um dicionário com listas para os assentos marcados para CANCELAMENTO
botoes_assentos = {i: {} for i in range(1, 6)}  # Inicializa um dicionário para mapear os objetos de botão de cada uma das 5 salas

filas = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]  # Define a lista com as letras correspondentes às 10 filas de assentos
colunas = list(range(1, 21))  # Cria uma lista numérica de 1 a 20 para as colunas de cada fila

ctk.set_appearance_mode("dark")  # Configura a aparência global da aplicação Tkinter para o modo escuro (Dark Mode)

def testar_conexao():  # Função para validar a conexão com o pgAdmin 4 ao iniciar a aplicação
    try:  # Inicia o bloco de teste de conexão
        conn = psycopg.connect(**DB_CONFIG)  # Tenta conectar ao banco PostgreSQL usando desempacotamento de dicionário
        conn.close()  # Fecha a conexão de teste com sucesso
        print("Conexão com o PostgreSQL via pgAdmin 4 realizada com sucesso!")  # Exibe confirmação no terminal
    except Exception as error:  # Captura falha na conexão com a base de dados
        print("Erro ao conectar à base de dados pgAdmin 4:", error)  # Exibe o erro no terminal

def registar_historico(num_sala, assentos, tipo):  # Regista transações de reserva/cancelamento no banco de dados
    try:  # Inicia bloco de gravação no histórico
        conn = psycopg.connect(**DB_CONFIG)  # Abre conexão com o PostgreSQL
        cursor = conn.cursor()  # Cria o cursor
        assentos_str = ", ".join(assentos)  # Formata a lista de assentos para texto
        cursor.execute(  # Insere a compra/cancelamento na tabela compras
            "INSERT INTO compras (sala, assentos, tipo) VALUES (%s, %s, %s);",  # Instrução SQL
            (num_sala, assentos_str, tipo)  # Parâmetros
        )  # Fim da instrução
        conn.commit()  # Consolida a transação
        cursor.close()  # Fecha cursor
        conn.close()  # Fecha conexão
    except Exception as error:  # Trata erros
        print("Erro ao registar no histórico:", error)  # Exibe o erro no terminal

def buscar_assentos_ocupados(num_sala):  # Define a função que consulta no PostgreSQL quais lugares já estão reservados
    status_assentos = {}  # Cria um dicionário vazio para guardar o estado final dos lugares (ex: {"A1": True})
    try:  # Inicia o bloco de tratamento de exceções para conexões de rede/banco
        conn = psycopg.connect(**DB_CONFIG)  # Abre a conexão com a base de dados PostgreSQL usando o dicionário DB_CONFIG
        cursor = conn.cursor()  # Cria um objeto cursor para executar os comandos SQL na base de dados
        cursor.execute(f"SELECT fila, numero_cadeira, ocupado FROM sala{num_sala};")  # Executa a consulta SQL na tabela da sala especificada

        for fila, numero, ocupado in cursor.fetchall():  # Percorre cada registo retornado da consulta SQL
            status_assentos[f"{fila.strip()}{numero}"] = ocupado  # Mapeia a identificação do assento com o seu estado de ocupação (True/False)

        cursor.close()  # Encerra o cursor da base de dados para libertar recursos do sistema
        conn.close()  # Fecha a conexão ativa com o servidor PostgreSQL
    except Exception as error:  # Captura qualquer falha que ocorra durante a tentativa de conexão ou consulta SQL
        print(f"Erro ao buscar assentos da Sala {num_sala}:", error)  # Exibe no terminal a mensagem de erro identificada

    return status_assentos  # Retorna o dicionário contendo o estado de todos os assentos da sala informada

def alternar_assento_livre(btn, num_sala):  # Seleciona/desseleciona um assento livre para RESERVA
    assento = btn.cget("text")  # Lê o texto do botão (ex: "A1")
    lista = assentos_selecionados[num_sala]  # Lista de reservas temporárias

    if assento in lista:  # Se já estava selecionado para reservar
        lista.remove(assento)  # Remove da seleção
        btn.configure(fg_color="#E4C6D0", text_color="black")  # Cor padrão de assento livre
    else:  # Se não estava selecionado
        lista.append(assento)  # Adiciona à lista de reservas
        btn.configure(fg_color="#C05A9D", text_color="white")  # Cor de assento selecionado para reserva

def alternar_assento_ocupado(btn, num_sala):  # Seleciona/desseleciona um assento ocupado para CANCELAMENTO
    assento = btn.cget("text")  # Lê o texto do botão (ex: "A1")
    lista = assentos_cancelar[num_sala]  # Lista de cancelamentos temporários

    if assento in lista:  # Se já estava marcado para cancelar
        lista.remove(assento)  # Remove da lista de cancelamento
        btn.configure(fg_color="#D19AB4", text_color="white")  # Volta à cor padrão de ocupado
    else:  # Se não estava marcado para cancelar
        lista.append(assento)  # Adiciona à lista de cancelamento
        btn.configure(fg_color="#A32A2A", text_color="white")  # Cor vermelha para indicar seleção de cancelamento

def reservar(num_sala):  # Define a função para gravar a reserva dos assentos marcados na base de dados
    lista = assentos_selecionados[num_sala]  # Obtém a lista de lugares selecionados para a respetiva sala
    if not lista:  # Valida se o utilizador clicou no botão sem selecionar nenhum assento
        messagebox.showwarning("Atenção", "Selecione pelo menos um assento livre para reservar.")  # Exibe alerta no ecrã
        return  # Interrompe a execução da função de reserva

    try:  # Inicia o bloco de tratamento de exceções para a atualização no PostgreSQL
        conn = psycopg.connect(**DB_CONFIG)  # Estabelece a conexão com a base de dados
        cursor = conn.cursor()  # Cria o cursor para envio das instruções SQL

        for assento in lista:  # Itera sobre cada código de assento selecionado (ex: "B12")
            fila = assento[0]  # Extrai a letra da fila
            numero = int(assento[1:])  # Extrai e converte para número o restante da string do assento

            cursor.execute(  # Executa a instrução SQL de atualização do estado da cadeira
                f"""
                UPDATE sala{num_sala}
                SET ocupado = TRUE
                WHERE fila = %s AND numero_cadeira = %s;
                """,  # Query formatada para atualizar o status do assento
                (fila, numero)  # Parâmetros seguros passados para a consulta
            )  # Fim da execução da instrução SQL

        conn.commit()  # Confirma e consolida todas as alterações efetuadas na base de dados
        cursor.close()  # Encerra o cursor
        conn.close()  # Encerra a conexão

        registar_historico(num_sala, lista, "Reserva")  # Regista a reserva na tabela de histórico compras
        messagebox.showinfo("Reserva Realizada", f"Assentos reservados na Sala {num_sala}:\n{', '.join(lista)}")  # Mensagem de sucesso
        lista.clear()  # Limpa a lista temporária de seleção
        atualizar_assentos(num_sala)  # Atualiza a interface gráfica

    except Exception as error:  # Captura eventuais erros ocorridos
        messagebox.showerror("Erro", f"Não foi possível realizar a reserva:\n{error}")  # Apresenta mensagem de erro

def cancelar_reserva(num_sala):  # Nova função para CANCELAR a reserva de assentos ocupados
    lista = assentos_cancelar[num_sala]  # Obtém a lista de lugares marcados para cancelamento
    if not lista:  # Valida se o utilizador selecionou algum lugar ocupado
        messagebox.showwarning("Atenção", "Clique em um assento ocupado (rosa escuro) para selecioná-lo e cancelar.")  # Exibe alerta
        return  # Interrompe a execução

    confirmar = messagebox.askyesno("Confirmar Cancelamento", f"Tem certeza que deseja cancelar a reserva dos assentos:\n{', '.join(lista)}?")  # Confirmação
    if not confirmar:  # Se o utilizador clicar em 'Não'
        return  # Aborta o cancelamento

    try:  # Inicia o bloco de gravação no banco de dados
        conn = psycopg.connect(**DB_CONFIG)  # Abre conexão com o banco
        cursor = conn.cursor()  # Cria o cursor

        for assento in lista:  # Percorre cada assento marcado para cancelamento
            fila = assento[0]  # Extrai a letra da fila
            numero = int(assento[1:])  # Extrai o número do assento

            cursor.execute(  # Executa a query SQL para libertar o assento
                f"""
                UPDATE sala{num_sala}
                SET ocupado = FALSE
                WHERE fila = %s AND numero_cadeira = %s;
                """,  # Query formatada para libertar a cadeira
                (fila, numero)  # Parâmetros seguros para evitar SQL Injection
            )  # Fim do comando SQL

        conn.commit()  # Efetiva as alterações na base de dados
        cursor.close()  # Encerra cursor
        conn.close()  # Encerra conexão

        registar_historico(num_sala, lista, "Cancelamento")  # Regista o cancelamento na tabela de histórico compras
        messagebox.showinfo("Cancelamento Concluído", f"Reservas canceladas na Sala {num_sala}:\n{', '.join(lista)}")  # Mensagem de sucesso
        lista.clear()  # Limpa a lista de cancelamento
        atualizar_assentos(num_sala)  # Atualiza os botões no ecrã

    except Exception as error:  # Trata falhas na conexão/execução
        messagebox.showerror("Erro", f"Não foi possível cancelar a reserva:\n{error}")  # Mensagem de erro

def atualizar_assentos(num_sala):  # Define a função para re-sincronizar os botões com a base de dados
    assentos_no_banco = buscar_assentos_ocupados(num_sala)  # Consulta os estados mais recentes do banco
    mapa_botoes = botoes_assentos[num_sala]  # Obtém o dicionário com as instâncias dos botões dessa sala
    
    assentos_selecionados[num_sala].clear()  # Reseta seleções pendentes de reserva
    assentos_cancelar[num_sala].clear()  # Reseta seleções pendentes de cancelamento

    for fila in filas:  # Ciclo pelas filas (A a J)
        for coluna in colunas:  # Ciclo pelas colunas (1 a 20)
            nome_assento = f"{fila}{coluna}"  # Monta a chave da cadeira (ex: "A1")
            ocupado = assentos_no_banco.get(nome_assento, False)  # Obtém o estado de ocupação do banco
            btn = mapa_botoes.get(nome_assento)  # Procura a referência do botão correspondente

            if btn is None:  # Se o botão não for localizado
                continue  # Avança para a próxima iteração

            if ocupado:  # Se o lugar constar como ocupado na base de dados
                btn.configure(  # Atualiza a configuração do botão para estado ocupado
                    fg_color="#D19AB4", text_color="white", state="normal",  # Deixa ativo para permitir o clique de cancelamento
                    command=lambda b=btn, num=num_sala: alternar_assento_ocupado(b, num)  # Associa à ação de cancelar
                )  # Fim da configuração do botão ocupado
            else:  # Se o lugar estiver livre
                btn.configure(  # Atualiza a configuração do botão para estado livre
                    fg_color="#E4C6D0", text_color="black", state="normal",  # Cor de lugar disponível
                    command=lambda b=btn, num=num_sala: alternar_assento_livre(b, num)  # Associa à ação de reservar
                )  # Fim da configuração do botão livre

def carregar_historico():  # Consulta e carrega os registos de compras do banco para a tabela gráfica
    for item in tabela_historico.get_children():  # Limpa os elementos atuais da tabela visual
        tabela_historico.delete(item)  # Elimina cada linha antiga

    try:  # Bloco de tentativa de leitura do banco
        conn = psycopg.connect(**DB_CONFIG)  # Abre conexão com o banco
        cursor = conn.cursor()  # Cria o cursor
        cursor.execute("SELECT id, sala, assentos, tipo, data_hora FROM compras ORDER BY id DESC;")  # Busca o histórico ordenado pelos mais recentes
        registos = cursor.fetchall()  # Guarda todos os registos retornados

        for reg in registos:  # Percorre cada registo do histórico
            id_compra, sala, assentos, tipo, data_hora = reg  # Desempacota os dados do registo
            data_formatada = data_hora.strftime("%d/%m/%Y %H:%M:%S") if data_hora else "-"  # Formata a data/hora para visualização
            tabela_historico.insert("", "end", values=(id_compra, f"Sala {sala}", assentos, tipo, data_formatada))  # Insere a linha na tabela visual

        cursor.close()  # Fecha cursor
        conn.close()  # Fecha conexão
    except Exception as error:  # Trata exceções de banco
        messagebox.showerror("Erro", f"Erro ao carregar o histórico:\n{error}")  # Exibe aviso em caso de erro

def mostrar_tela(frame_desejado):  # Define a função responsável pela alternância de ecrãs na interface
    frame_inicial.pack_forget()  # Oculta a ecrã inicial
    frame_historico.pack_forget()  # Oculta a ecrã de histórico
    for f in frames_salas.values():  # Iterar por todas as telas de salas
        f.pack_forget()  # Oculta a ecrã de sala correspondente
    frame_desejado.pack(fill="both", expand=True)  # Exibe a ecrã solicitada

def abrir_historico():  # Abre a tela de histórico e atualiza os seus dados
    carregar_historico()  # Executa a busca dos dados no banco de dados
    mostrar_tela(frame_historico)  # Exibe o frame do histórico na janela

testar_conexao()  # Executa o teste de conexão inicial com o banco pgAdmin

app = ctk.CTk()  # Cria a janela principal da aplicação
app.title("CINEMA RUBY")  # Define o título da janela
app.geometry("1400x900")  # Define a dimensão da janela

# --- TELA INICIAL ---
frame_inicial = ctk.CTkFrame(app, fg_color="#1A1518")  # Container da ecrã inicial
frame_inicial.pack(fill="both", expand=True)  # Ajusta o container para preencher toda a janela

frame_topo = ctk.CTkFrame(frame_inicial, fg_color="transparent")  # Cabeçalho transparente da tela inicial
frame_topo.pack(fill="x", padx=65, pady=(25, 10))  # Posiciona o cabeçalho no topo com margens

ctk.CTkLabel(frame_topo, text="CINEMA RUBY", font=("Arial", 32, "bold"), text_color="#D19ABE").pack(side="left")  # Adiciona o título no canto esquerdo

# Botão para abrir a tela de histórico
btn_historico = ctk.CTkButton(  # Instancia o botão do histórico
    frame_topo, text="📜 HISTÓRICO", font=("Arial", 13, "bold"),  # Configura texto e fonte
    fg_color="#8F4D75", hover_color="#713A5D", text_color="white", width=140, height=35,  # Estilização visual
    command=abrir_historico  # Chama a função que abre a tela do histórico
)  # Fim da criação do botão
btn_historico.pack(side="right", padx=10)  # Posiciona o botão à direita no cabeçalho

ctk.CTkLabel(frame_topo, text="INÍCIO", font=("Arial", 14, "bold"), text_color="#F7D9ED").pack(side="right", padx=15)  # Adiciona o indicador de aba à direita

# Banners dos Filmes
frame_banner = ctk.CTkFrame(frame_inicial, fg_color="#2B2026", corner_radius=18, height=500)  # Frame visual para abrigar os pôsteres
frame_banner.pack(fill="x", padx=65, pady=(20, 25))  # Exibe a moldura dos banners na tela inicial
frame_banner.pack_propagate(False)  # Impede que o frame altere de tamanho dinamicamente com os elementos filhos

frame_banner_center = ctk.CTkFrame(frame_banner, fg_color="transparent")  # Container interno para centralizar os banners
frame_banner_center.pack(expand=True, anchor="center")  # Centraliza o conteúdo no meio do banner

filmes_imagens = [  # Lista contendo os nomes dos arquivos de imagem dos pôsteres
    "a_odisseia.png",  # Imagem da sala 1
    "obsessao.png.png",  # Imagem da sala 2
    "toy_story_5.png",  # Imagem da sala 3
    "um_cabra_bom_de_bola.png",  # Imagem da sala 4
    "homem_aranha.png."  # Imagem da sala 5
]  # Fim da lista de caminhos de imagens

for img_nome in filmes_imagens:  # Percorre a lista de nomes de imagens
    try:  # Bloco para tentar carregar e processar a imagem
        img_path = BASE_DIR / img_nome  # Concatena o diretório base com o nome da imagem
        pil_img = Image.open(img_path)  # Abre o arquivo de imagem usando o Pillow
        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(180, 320))  # Converte para formato compatível com CustomTkinter
        card = ctk.CTkButton(frame_banner_center, text="", image=ctk_img, fg_color="transparent", hover=False)  # Cria botão/card para a imagem
        card.pack(side="left", padx=15, pady=20)  # Empacota os cards lado a lado na horizontal
    except Exception as e:  # Captura falha ao tentar carregar imagem
        print(f"Erro ao carregar a imagem {img_nome}: {e}")  # Exibe erro no console caso o arquivo não seja encontrado

# Seção de seleção de Salas
ctk.CTkLabel(frame_inicial, text="Escolha seu filme", font=("Arial", 24, "bold"), text_color="white").pack(anchor="w", padx=65, pady=(0, 15))  # Título da seção de seleção

frame_salas_container = ctk.CTkFrame(frame_inicial, fg_color="transparent")  # Frame horizontal para organizar as opções de salas
frame_salas_container.pack(fill="x", padx=65)  # Exibe o container das salas com margem lateral

# --- CONSTRUÇÃO DAS 5 SALAS ---
frames_salas = {}  # Dicionário que guardará os frames/telas de cada sala

info_salas = [  # Lista com as informações detalhadas e estilização das 5 salas
    {"num": 1, "titulo": "A ODISSEIA", "icone": "🎬", "cor": "#D19ABE"},  # Dados da sala 1
    {"num": 2, "titulo": "OBSESSÃO", "icone": "🍿", "cor": "#CC91AE"},  # Dados da sala 2
    {"num": 3, "titulo": "TOY STORY 5", "icone": "📹", "cor": "#B8789C"},  # Dados da sala 3
    {"num": 4, "titulo": "UM CABRA BOM DE BOLA", "icone": "🎞️", "cor": "#A4608A"},  # Dados da sala 4
    {"num": 5, "titulo": "HOMEM-ARANHA", "icone": "🎥", "cor": "#8F4B77"}  # Dados da sala 5
]  # Fim da lista de informações das salas

for sala in info_salas:  # Loop para construir a interface de cada uma das salas
    i = sala["num"]  # Extrai o número da sala
    titulo_filme = sala["titulo"]  # Extrai o título do filme correspondente

    # Cartão na Tela Inicial
    card_sala = ctk.CTkFrame(frame_salas_container, fg_color=sala["cor"], corner_radius=15, height=170)  # Cria o card representativo da sala
    card_sala.pack(side="left", fill="both", expand=True, padx=5)  # Adiciona o card lado a lado
    card_sala.pack_propagate(False)  # Trava as dimensões do card para manter padrão visual

    ctk.CTkLabel(card_sala, text=sala["icone"], font=("Arial", 28), text_color="white").pack(anchor="w", padx=15, pady=(12, 0))  # Adiciona o ícone visual
    ctk.CTkLabel(card_sala, text=titulo_filme, font=("Arial", 14, "bold"), text_color="white", wraplength=160, justify="left").pack(anchor="w", padx=15, pady=(2, 2))  # Rótulo com título do filme
    
    btn_entrar = ctk.CTkButton(  # Cria o botão para entrar na sala correspondente
        card_sala, text="ENTRAR", width=100, height=30,  # Define texto e dimensões do botão
        fg_color="#8F4D75", hover_color="#713A5D", text_color="white", corner_radius=7,  # Define o estilo visual do botão
        command=lambda num=i: (atualizar_assentos(num), mostrar_tela(frames_salas[num]))  # Atualiza assentos e navega para a tela da sala
    )  # Fim da criação do botão de entrar
    btn_entrar.pack(anchor="w", padx=15, pady=5)  # Posiciona o botão dentro do card da sala

    # Frame da Sala
    frame_sala = ctk.CTkFrame(app, fg_color="#FFF7FB")  # Cria a tela específica para exibição do mapa de assentos da sala
    frames_salas[i] = frame_sala  # Guarda a referência da tela criada no dicionário

    ctk.CTkLabel(frame_sala, text=f"{titulo_filme} (SALA {i})", font=("Arial", 28, "bold"), text_color="#F7D9ED").pack(pady=(15, 5))  # Cabeçalho da sala
    ctk.CTkLabel(frame_sala, text="🎬 TELA DO CINEMA 🎬", font=("Arial", 18, "bold")).pack()  # Representação visual da tela do cinema

    frame_assentos = ctk.CTkFrame(frame_sala, fg_color="transparent")  # Container para a grade/matriz de assentos
    frame_assentos.pack(pady=15)  # Posiciona o container com margem vertical

    for r_idx, fila in enumerate(filas):  # Itera pelas linhas (A a J)
        for c_idx, coluna in enumerate(colunas):  # Itera pelas colunas (1 a 20)
            nome_assento = f"{fila}{coluna}"  # Gera o nome do assento (ex: "A1", "B5")
            btn = ctk.CTkButton(  # Instancia o botão para o assento
                frame_assentos, text=nome_assento, width=55, height=40  # Define o tamanho e texto do botão
            )  # Fim da criação do botão de assento
            botoes_assentos[i][nome_assento] = btn  # Mapeia o objeto botão no dicionário da sala
            btn.grid(row=r_idx, column=c_idx, padx=3, pady=3)  # Posiciona o botão na grade usando o layout grid

    # Botões de Ação na Sala (Reservar, Cancelar e Voltar)
    frame_botoes = ctk.CTkFrame(frame_sala, fg_color="transparent")  # Frame inferior para abrigar os botões de ação
    frame_botoes.pack(pady=10)  # Posiciona o frame de botões na tela da sala

    # Botão de Reservar
    ctk.CTkButton(  # Cria o botão de confirmação de reservas
        frame_botoes, text="🎟 Reservar Assentos Selecionados", width=280, height=45,  # Texto e tamanho
        fg_color="#D19ABE", hover_color="#C05A9D", text_color="white", font=("Arial", 14, "bold"),  # Estilização de cores
        command=lambda num=i: reservar(num)  # Dispara a função de reserva para a sala atual
    ).pack(side="left", padx=10)  # Alinha o botão à esquerda com margem

    # Botão de Cancelar Reserva
    ctk.CTkButton(  # Cria o botão para cancelar reservas existentes
        frame_botoes, text="❌ Cancelar Reserva", width=280, height=45,  # Texto e dimensões do botão
        fg_color="#A32A2A", hover_color="#802020", text_color="white", font=("Arial", 14, "bold"),  # Estilo vermelho de cancelamento
        command=lambda num=i: cancelar_reserva(num)  # Dispara a função de cancelamento para a sala atual
    ).pack(side="left", padx=10)  # Alinha o botão ao lado do anterior

    # Botão de Voltar
    ctk.CTkButton(  # Cria o botão de navegação para retornar ao menu principal
        frame_botoes, text="🏠 Voltar ao Início", width=200, height=45,  # Texto e tamanho
        fg_color="#CC91AE", hover_color="#B77A99", text_color="white", font=("Arial", 14, "bold"),  # Estilização visual
        command=lambda: mostrar_tela(frame_inicial)  # Volta para a tela inicial ao ser clicado
    ).pack(side="left", padx=10)  # Alinha o botão à esquerda

# --- TELA DE HISTÓRICO DE COMPRAS ---
frame_historico = ctk.CTkFrame(app, fg_color="#1A1518")  # Frame da tela de histórico

ctk.CTkLabel(frame_historico, text="📜 HISTÓRICO DE COMPRAS E CANCELAMENTOS", font=("Arial", 26, "bold"), text_color="#D19ABE").pack(pady=25)  # Título da tela

frame_tabela = ctk.CTkFrame(frame_historico, fg_color="#2B2026", corner_radius=15)  # Container visual para abrigar a tabela
frame_tabela.pack(fill="both", expand=True, padx=65, pady=10)  # Posiciona o frame da tabela

# Estilização da Treeview (Tabela)
style = ttk.Style()  # Instancia o gestor de estilos do Tkinter via ttk
style.theme_use("default")  # Aplica o tema padrão como base
style.configure("Treeview", background="#2B2026", foreground="white", fieldbackground="#2B2026", rowheight=30, font=("Arial", 11))  # Configura cores das linhas
style.configure("Treeview.Heading", background="#8F4D75", foreground="white", font=("Arial", 12, "bold"))  # Configura cores do cabeçalho
style.map("Treeview", background=[("selected", "#C05A9D")])  # Define a cor de seleção das linhas

colunas_hist = ("ID", "Sala", "Assentos", "Tipo", "Data / Hora")  # Define as colunas da tabela de histórico
tabela_historico = ttk.Treeview(frame_tabela, columns=colunas_hist, show="headings")  # Cria a tabela Treeview

tabela_historico.heading("ID", text="ID")  # Define cabeçalho da coluna ID
tabela_historico.heading("Sala", text="SALA")  # Define cabeçalho da coluna Sala
tabela_historico.heading("Assentos", text="ASSENTOS")  # Define cabeçalho da coluna Assentos
tabela_historico.heading("Tipo", text="TIPO DE OPERAÇÃO")  # Define cabeçalho da coluna Tipo
tabela_historico.heading("Data / Hora", text="DATA E HORA")  # Define cabeçalho da coluna Data/Hora

tabela_historico.column("ID", width=60, anchor="center")  # Largura e alinhamento da coluna ID
tabela_historico.column("Sala", width=120, anchor="center")  # Largura e alinhamento da coluna Sala
tabela_historico.column("Assentos", width=300, anchor="center")  # Largura e alinhamento da coluna Assentos
tabela_historico.column("Tipo", width=180, anchor="center")  # Largura e alinhamento da coluna Tipo
tabela_historico.column("Data / Hora", width=220, anchor="center")  # Largura e alinhamento da coluna Data/Hora

scrollbar = ttk.Scrollbar(frame_tabela, orient="vertical", command=tabela_historico.yview)  # Cria barra de rolagem vertical
tabela_historico.configure(yscrollcommand=scrollbar.set)  # Conecta a barra de rolagem à tabela

tabela_historico.pack(side="left", fill="both", expand=True, padx=(15, 0), pady=15)  # Empacota a tabela à esquerda
scrollbar.pack(side="right", fill="y", padx=(0, 15), pady=15)  # Empacota a barra de rolagem à direita

# Botão de Voltar na tela de Histórico
ctk.CTkButton(  # Botão para regressar ao menu inicial
    frame_historico, text="🏠 Voltar ao Início", width=220, height=45,  # Texto e dimensões
    fg_color="#CC91AE", hover_color="#B77A99", text_color="white", font=("Arial", 14, "bold"),  # Estilo do botão
    command=lambda: mostrar_tela(frame_inicial)  # Ação ao clicar
).pack(pady=20)  # Posiciona o botão com margem inferior

ctk.CTkLabel(  # Adiciona a barra de rodapé na tela inicial
    frame_inicial,  # Frame onde será desenhado o rodapé
    text="CINEMA RUBY  •  FILMES  •  SESSÕES  •  RESERVAS",  # Texto informativo do rodapé
    font=("Arial", 12), text_color="#8F7C85"  # Estilo de fonte e cor discreta
).pack(pady=(25, 10))  # Exibe o rodapé com margem no fundo da página

mostrar_tela(frame_inicial)  # Exibe a tela inicial no lançamento da aplicação
app.mainloop()  # Inicia o loop principal de eventos da interface do Tkinter