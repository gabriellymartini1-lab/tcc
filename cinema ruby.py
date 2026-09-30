import customtkinter as ctk  # Importa a biblioteca CustomTkinter para criar a interface gráfica moderna
from tkinter import messagebox  # Importa o módulo de caixas de texto/mensagem do Tkinter
import psycopg  # Importa a biblioteca para conectar o Python ao banco de dados PostgreSQL
from PIL import Image  # Importa o módulo Image do Pillow para abrir e manipular as imagens dos pôsteres
from pathlib import Path  # Importa Path para manipular os caminhos de ficheiros de forma compatível com o sistema

DB_CONFIG = {  # Cria um dicionário com as credenciais e configurações de acesso ao PostgreSQL
    "dbname": "cinema",  # Define o nome da base de dados que será utilizada
    "user": "postgres",  # Define o nome de utilizador do PostgreSQL
    "password": "root",  # Define a palavra-passe do utilizador do banco de dados
    "host": "localhost",  # Define o endereço do servidor (localhost indica que o banco está no mesmo PC)
    "port": "5432"  # Define a porta de comunicação padrão do PostgreSQL
}  # Fecha a estrutura do dicionário de configuração

BASE_DIR = Path(__file__).resolve().parent  # Obtém o caminho absoluto do diretório onde este ficheiro .py está guardado

assentos_selecionados = {i: [] for i in range(1, 6)}  # Inicializa um dicionário com listas vazias para os assentos marcados de 5 salas
botoes_assentos = {i: {} for i in range(1, 6)}  # Inicializa um dicionário para mapear os objetos de botão de cada uma das 5 salas

filas = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]  # Define a lista com as letras correspondentes às 10 filas de assentos
colunas = list(range(1, 21))  # Cria uma lista numérica de 1 a 20 para as colunas de cada fila

ctk.set_appearance_mode("dark")  # Configura a aparência global da aplicação Tkinter para o modo escuro (Dark Mode)

def buscar_assentos_ocupados(num_sala):  # Define a função que consulta no PostgreSQL quais lugares já estão reservados
    status_assentos = {}  # Cria um dicionário vazio para guardar o estado final dos lugares (ex: {"A1": True})
    try:  # Inicia o bloco de tratamento de exceções para conexões de rede/banco
        conn = psycopg.connect(**DB_CONFIG)  # Abre a conexão com a base de dados PostgreSQL usando o dicionário DB_CONFIG
        cursor = conn.cursor()  # Cria um objeto cursor para executar os comandos SQL na base de dados
        cursor.execute(f"SELECT fila, numero_cadeira, ocupado FROM sala{num_sala};")  # Executa a consulta SQL na tabela da sala especificada

        for fila, numero, ocupado in cursor.fetchall():  # Percorre cada registo retornado da consulta SQL
            status_assentos[f"{fila}{numero}"] = ocupado  # Mapeia a identificação do assento com o seu estado de ocupação (True/False)

        cursor.close()  # Encerra o cursor da base de dados para libertar recursos do sistema
        conn.close()  # Fecha a conexão ativa com o servidor PostgreSQL
    except Exception as error:  # Captura qualquer falha que ocorra durante a tentativa de conexão ou consulta SQL
        print(f"Erro ao buscar assentos da Sala {num_sala}:", error)  # Exibe no terminal a mensagem de erro identificada

    return status_assentos  # Retorna o dicionário contendo o estado de todos os assentos da sala informada

def alternar_assento(btn, num_sala):  # Define a função de clique para marcar/desmarcar o assento desejado
    assento = btn.cget("text")  # Lê o texto do botão (ex: "A1") para identificar o lugar clicado
    lista = assentos_selecionados[num_sala]  # Obtém a lista temporária de assentos selecionados da sala atual

    if assento in lista:  # Verifica se o lugar clicado já se encontra na lista de seleção
        lista.remove(assento)  # Remove a identificação do assento da lista de seleção
        btn.configure(fg_color="#E4C6D0", text_color="black")  # Restaura a cor do botão para o estado padrão (Rosa claro)
    else:  # Caso o lugar não estivesse selecionado anteriormente
        lista.append(assento)  # Adiciona a identificação do assento à lista de seleção
        btn.configure(fg_color="#C05A9D", text_color="white")  # Modifica a cor do botão para assento marcado (Rosa escuro)

def reservar(num_sala):  # Define a função para gravar a reserva dos assentos marcados na base de dados
    lista = assentos_selecionados[num_sala]  # Obtém a lista de lugares selecionados para a respetiva sala
    if not lista:  # Valida se o utilizador clicou no botão sem selecionar nenhum assento
        messagebox.showwarning("Atenção", "Selecione pelo menos um assento para reservar.")  # Exibe alerta na ecrã
        return  # Interrompe a execução da função de reserva

    try:  # Inicia o bloco de tratamento de exceções para a atualização no PostgreSQL
        conn = psycopg.connect(**DB_CONFIG)  # Estabelece a conexão com a base de dados
        cursor = conn.cursor()  # Cria o cursor para envio das instruções SQL

        for assento in lista:  # Itera sobre cada código de assento selecionado (ex: "B12")
            fila = assento[0]  # Extrai a letra da fila (primeiro caractere da string)
            numero = int(assento[1:])  # Extrai e converte para número o restante da string do assento

            cursor.execute(  # Executa a instrução SQL de atualização do estado da cadeira
                f"""
                UPDATE sala{num_sala}
                SET ocupado = TRUE
                WHERE fila = %s AND numero_cadeira = %s;
                """,
                (fila, numero)  # Substitui os marcadores de posição (%s) de forma segura contra injeção SQL
            )  # Fim da execução da query SQL

        conn.commit()  # Confirma e consolida todas as alterações efetuadas na base de dados
        cursor.close()  # Encerra o cursor do banco de dados
        conn.close()  # Encerra a conexão com o PostgreSQL

        messagebox.showinfo("Reserva realizada", f"Assentos reservados na Sala {num_sala}:\n{', '.join(lista)}")  # Mostra mensagem de sucesso
        lista.clear()  # Limpa a lista temporária de seleção da sala
        atualizar_assentos(num_sala)  # Atualiza o estado e cor visual dos botões na ecrã

    except Exception as error:  # Captura eventuais erros ocorridos no processo de gravação
        messagebox.showerror("Erro", f"Não foi possível realizar a reserva:\n{error}")  # Apresenta mensagem de erro ao utilizador

def atualizar_assentos(num_sala):  # Define a função para re-sincronizar os botões com a base de dados
    assentos_no_banco = buscar_assentos_ocupados(num_sala)  # Consulta os estados mais recentes do banco
    mapa_botoes = botoes_assentos[num_sala]  # Obtém o dicionário com as instâncias dos botões dessa sala

    for fila in filas:  # Ciclo pelas filas (A a J)
        for coluna in colunas:  # Ciclo pelas colunas (1 a 20)
            nome_assento = f"{fila}{coluna}"  # Monta a chave da cadeira (ex: "A1")
            ocupado = assentos_no_banco.get(nome_assento, False)  # Obtém o estado de ocupação do banco
            btn = mapa_botoes.get(nome_assento)  # Procura a referência do botão correspondente

            if btn is None:  # Se por algum motivo o botão não for localizado
                continue  # Avança para a próxima iteração do ciclo

            if ocupado:  # Se o lugar constar como ocupado na base de dados
                btn.configure(fg_color="#D19AB4", text_color="white", state="disabled")  # Desativa o botão e muda para cor de ocupado
            else:  # Se o lugar estiver livre
                btn.configure(fg_color="#E4C6D0", text_color="black", state="normal")  # Habilita o botão e aplica a cor padrão

def mostrar_tela(frame_desejado):  # Define a função responsável pela alternância de ecrãs na interface
    frame_inicial.pack_forget()  # Oculta o painel/frame da ecrã inicial
    for f in frames_salas.values():  # Iterar por todas as telas de salas criadas
        f.pack_forget()  # Oculta a ecrã de sala correspondente
    frame_desejado.pack(fill="both", expand=True)  # Exibe a ecrã solicitada preenchendo a janela por completo

app = ctk.CTk()  # Cria a janela principal da aplicação através do CustomTkinter
app.title("CINEMA RUBY")  # Define o título da janela do sistema
app.geometry("1400x900")  # Define a dimensão inicial da janela em pixels (Largura x Altura)

# --- TELA INICIAL ---
frame_inicial = ctk.CTkFrame(app, fg_color="#1A1518")  # Cria o container principal da ecrã inicial com fundo escuro
frame_inicial.pack(fill="both", expand=True)  # Ajusta o container para ocupar todo o espaço da janela

frame_topo = ctk.CTkFrame(frame_inicial, fg_color="transparent")  # Cria o painel superior/cabeçalho transparente
frame_topo.pack(fill="x", padx=65, pady=(25, 10))  # Posiciona o cabeçalho no topo com espaçamentos

ctk.CTkLabel(frame_topo, text="CINEMA RUBY", font=("Arial", 32, "bold"), text_color="#D19ABE").pack(side="left")  # Adiciona a marca do cinema à esquerda
ctk.CTkLabel(frame_topo, text="INÍCIO", font=("Arial", 14, "bold"), text_color="#F7D9ED").pack(side="right", padx=15)  # Adiciona a indicação do menu à direita

# Banners dos Filmes (Centralizados)
frame_banner = ctk.CTkFrame(frame_inicial, fg_color="#2B2026", corner_radius=18, height=500)  # Cria a secção dos cartazes com cantos arredondados
frame_banner.pack(fill="x", padx=65, pady=(20, 25))  # Exibe o container da galeria na ecrã inicial
frame_banner.pack_propagate(False)  # Impede que o container mude de tamanho de acordo com os elementos filhos

frame_banner_center = ctk.CTkFrame(frame_banner, fg_color="transparent")  # Sub-container invisível para alinhamento
frame_banner_center.pack(expand=True, anchor="center")  # Centraliza o sub-container no meio exato do painel superior

filmes_imagens = [  # Lista contendo os ficheiros das imagens dos filmes no diretório
    "a_odisseia.png",  # Imagem do filme 1
    "obsessao.png.png",  # Imagem do filme 2
    "toy_story_5.png",  # Imagem do filme 3
    "um_cabra_bom_de_bola.png",  # Imagem do filme 4
    "homem_aranha.png."  # Imagem do filme 5
]  # Fim da lista de ficheiros

for img_nome in filmes_imagens:  # Percorre a lista com o nome das imagens
    try:  # Bloco para prevenção de erros na leitura dos ficheiros
        img_path = BASE_DIR / img_nome  # Define o caminho completo até a imagem
        pil_img = Image.open(img_path)  # Abre o ficheiro de imagem utilizando a biblioteca PIL (Pillow)
        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(180, 320))  # Redimensiona a imagem para exibição gráfica
        card = ctk.CTkButton(frame_banner_center, text="", image=ctk_img, fg_color="transparent", hover=False)  # Cria o botão de exibição da capa
        card.pack(side="left", padx=15, pady=20)  # Posiciona o cartaz lado a lado no centro
    except Exception as e:  # Captura falha se algum ficheiro de imagem não for encontrado
        print(f"Erro ao carregar a imagem {img_nome}: {e}")  # Imprime mensagem de erro com o nome da imagem com falha

# Seção de seleção de Salas
ctk.CTkLabel(frame_inicial, text="Escolha seu filme", font=("Arial", 24, "bold"), text_color="white").pack(anchor="w", padx=65, pady=(0, 15))  # Rótulo de instrução

frame_salas_container = ctk.CTkFrame(frame_inicial, fg_color="transparent")  # Container para abrigar os cartões de seleção das salas
frame_salas_container.pack(fill="x", padx=65)  # Posiciona o container na ecrã inicial

# --- CONSTRUÇÃO DAS 5 SALAS COM OS NOMES DOS FILMES ---
frames_salas = {}  # Dicionário onde serão salvos os quadros completos de cada ecrã de sala

info_salas = [  # Estrutura com as definições de filmes, salas, ícones e esquemas de cor
    {"num": 1, "titulo": "A ODISSEIA", "icone": "🎬", "cor": "#D19ABE"},  # Dados da Sala 1
    {"num": 2, "titulo": "OBSESSÃO", "icone": "🍿", "cor": "#CC91AE"},  # Dados da Sala 2
    {"num": 3, "titulo": "TOY STORY 5", "icone": "📹", "cor": "#B8789C"},  # Dados da Sala 3
    {"num": 4, "titulo": "UM CABRA BOM DE BOLA", "icone": "🎞️", "cor": "#A4608A"},  # Dados da Sala 4
    {"num": 5, "titulo": "HOMEM-ARANHA", "icone": "🎥", "cor": "#8F4B77"}  # Dados da Sala 5
]  # Fim da lista de informações das salas

for sala in info_salas:  # Loop para construir dinamicamente as salas e ecrãs do sistema
    i = sala["num"]  # Guarda o número identificador da sala
    titulo_filme = sala["titulo"]  # Guarda o nome/título do filme

    # 1. Botão/Card de seleção na Tela Inicial
    card_sala = ctk.CTkFrame(frame_salas_container, fg_color=sala["cor"], corner_radius=15, height=170)  # Instancia o cartão visual da sala
    card_sala.pack(side="left", fill="both", expand=True, padx=5)  # Empacota horizontalmente com preenchimento responsivo
    card_sala.pack_propagate(False)  # Mantém fixo o tamanho do cartão de seleção

    ctk.CTkLabel(card_sala, text=sala["icone"], font=("Arial", 28), text_color="white").pack(anchor="w", padx=15, pady=(12, 0))  # Ícone do cartão
    ctk.CTkLabel(card_sala, text=titulo_filme, font=("Arial", 14, "bold"), text_color="white", wraplength=160, justify="left").pack(anchor="w", padx=15, pady=(2, 2))  # Título do filme com quebra automática
    
    btn_entrar = ctk.CTkButton(  # Cria o botão de entrada na sala correspondente
        card_sala, text="ENTRAR", width=100, height=30,  # Define o texto e as dimensões do botão
        fg_color="#8F4D75", hover_color="#713A5D", text_color="white", corner_radius=7,  # Configuração de cores e raio do canto
        command=lambda num=i: (atualizar_assentos(num), mostrar_tela(frames_salas[num]))  # Define a ação de carregar os dados e mudar de ecrã
    )  # Fim da construção do botão
    btn_entrar.pack(anchor="w", padx=15, pady=5)  # Exibe o botão "ENTRAR" dentro do cartão da sala

    # 2. Tela / Frame da Sala correspondente
    frame_sala = ctk.CTkFrame(app, fg_color="#FFF7FB")  # Cria a janela/quadro da sala
    frames_salas[i] = frame_sala  # Guarda a referência no dicionário de ecrãs

    ctk.CTkLabel(frame_sala, text=f"{titulo_filme} (SALA {i})", font=("Arial", 28, "bold"), text_color="#F7D9ED").pack(pady=(15, 5))  # Título da sala
    ctk.CTkLabel(frame_sala, text="🎬 TELA DO CINEMA 🎬", font=("Arial", 18, "bold")).pack()  # Representação da tela do cinema

    frame_assentos = ctk.CTkFrame(frame_sala, fg_color="transparent")  # Container da grelha de assentos da sala
    frame_assentos.pack(pady=20)  # Posiciona o container com espaçamento vertical

    assentos_no_banco = buscar_assentos_ocupados(i)  # Executa a busca inicial na base de dados das cadeiras ocupadas

    for r_idx, fila in enumerate(filas):  # Iteração sobre a lista de filas obtendo índice e letra
        for c_idx, coluna in enumerate(colunas):  # Iteração sobre a lista de colunas obtendo índice e número
            nome_assento = f"{fila}{coluna}"  # Gera o identificador do lugar (ex: "A1")
            ocupado = assentos_no_banco.get(nome_assento, False)  # Obtém o estado no banco de dados

            cor = "#D19AB4" if ocupado else "#E4C6D0"  # Determina a cor com base na ocupação
            cor_texto = "white" if ocupado else "black"  # Determina a cor da letra
            estado = "disabled" if ocupado else "normal"  # Habilita ou desabilita o botão

            btn = ctk.CTkButton(  # Cria o botão do assento individual na grelha
                frame_assentos, text=nome_assento, width=55, height=40,  # Especifica texto do assento e tamanho
                fg_color=cor, text_color=cor_texto, state=estado  # Aplica o estilo de acordo com o estado do banco
            )  # Fim da criação do botão do assento
            botoes_assentos[i][nome_assento] = btn  # Mapeia a referência do botão no dicionário para atualizações futuras

            if not ocupado:  # Adiciona a ação de clique se a cadeira estiver livre
                btn.configure(command=lambda b=btn, num=i: alternar_assento(b, num))  # Vincula a função de marcar/desmarcar

            btn.grid(row=r_idx, column=c_idx, padx=3, pady=3)  # Posiciona o botão na matriz usando a grelha Tkinter

    # Botões de Ação na Sala
    frame_botoes = ctk.CTkFrame(frame_sala, fg_color="transparent")  # Container para botões de comandos inferiores
    frame_botoes.pack(pady=20)  # Exibe o container com espaçamento na ecrã da sala

    ctk.CTkButton(  # Cria o botão de envio para efetivar as reservas selecionadas
        frame_botoes, text="🎟 Reservar", width=280, height=55,  # Texto e tamanhos do botão
        fg_color="#D19ABE", hover_color="#C05A9D",  # Cores de preenchimento e estado sobreposto (hover)
        command=lambda num=i: reservar(num)  # Chama a função de gravação no banco de dados
    ).pack(pady=8)  # Exibe o botão na ecrã da sala

    ctk.CTkButton(  # Cria o botão para regressar ao ecrã inicial
        frame_botoes, text="🏠 Voltar", width=280, height=55,  # Texto e tamanho do botão de navegação
        fg_color="#CC91AE", hover_color="#B77A99", text_color="white",  # Configurações visuais do botão
        command=lambda: mostrar_tela(frame_inicial)  # Executa a troca para o ecrã inicial
    ).pack(pady=8)  # Exibe o botão na ecrã

ctk.CTkLabel(  # Rótulo de rodapé na ecrã inicial
    frame_inicial,  # Pertence ao container principal
    text="CINEMA RUBY  •  FILMES  •  SESSÕES  •  RESERVAS",  # Texto descritivo
    font=("Arial", 12), text_color="#8F7C85"  # Fonte e cor cinza discreta
).pack(pady=(25, 10))  # Posiciona o rodapé no fim da ecrã

mostrar_tela(frame_inicial)  # Define a ecrã inicial como a primeira a ser exibida
app.mainloop()  # Inicia o ciclo de eventos principal da aplicação gráfica