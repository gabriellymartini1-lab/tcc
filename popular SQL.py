import psycopg

DB_CONFIG = {  # Cria um dicionario com as credenciais e configuracoes de acesso ao PostgreSQL / pgAdmin 4
    "dbname": "cinema",  # Nome da base de dados criada no pgAdmin 4
    "user": "postgres",  # Utilizador padrao do PostgreSQL
    "password": "root",  # Altera para a palavra-passe que definiste na instalacao do pgAdmin
    "host": "localhost",  # Endereco do servidor (localhost para banco local)
    "port": "5432",  # Porta padrao de conexao do PostgreSQL
}  # Fecha a estrutura do dicionario de configuracao


FILAS = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J",]  # Define a lista com as letras correspondentes as 10 filas de assentos
COLUNAS = list(
    range(1, 21)
)  # Cria uma lista numerica de 1 a 20 para representar o numero de cada cadeira


def popular_banco_de_dados():  # Define a funcao responsavel por estruturar e povoar o banco de dados
    try:  # Inicia o bloco de tratamento de excecoes para a conexao e execucao SQL
        conn = psycopg.connect(
            **DB_CONFIG
        )  # Abre a conexao com o servidor PostgreSQL passando o dicionario DB_CONFIG
        cursor = (
            conn.cursor()
        )  # Cria um objeto cursor para enviar os comandos SQL para a base de dados

        print(
            "A iniciar o povoamento do banco de dados..."
        )  # Exibe no terminal a mensagem de inicio de processamento

        # --- CRIAÇÃO E POVOAÇÃO DA TABELA DE HISTÓRICO (COMPRAS) ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS compras (
                id SERIAL PRIMARY KEY,
                sala INT NOT NULL,
                assentos TEXT NOT NULL,
                tipo TEXT NOT NULL,
                data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)  # Cria a tabela compras caso ela ainda nao exista
        
        cursor.execute("SELECT COUNT(*) FROM compras;")  # Verifica a quantidade de registos existentes na tabela
        if cursor.fetchone()[0] == 0:  # Se a tabela de historico estiver vazia
            dados_historico = [  # Lista com registos ficticios para teste
                (1, "A1, A2, A3", "Reserva"),
                (2, "C10, C11", "Reserva"),
                (1, "A3", "Cancelamento"),
                (3, "E5, E6, E7", "Reserva"),
            ]
            for sala, assentos, tipo in dados_historico:  # Percorre os dados ficticios
                cursor.execute(
                    "INSERT INTO compras (sala, assentos, tipo) VALUES (%s, %s, %s);",
                    (sala, assentos, tipo)
                )  # Insere cada registo de historico na tabela compras
            print("[OK] Tabela 'compras' criada e populada com dados de historico iniciais!")
        else:
            print("[OK] Tabela 'compras' ja existente e verificada!")

        # --- CRIAÇÃO E POVOAÇÃO DAS TABELAS DAS SALAS ---
        for num_sala in range(
            1, 6
        ):  # Inicia um loop que vai iterar de 1 ate 5 para processar as 5 salas
            nome_tabela = f"sala{num_sala}"  # Define dinamicamente o nome da tabela (ex: sala1, sala2, ..., sala5)

            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {nome_tabela} (
                    id SERIAL PRIMARY KEY,
                    fila CHAR(1) NOT NULL,
                    numero_cadeira INT NOT NULL,
                    ocupado BOOLEAN DEFAULT FALSE,
                    UNIQUE(fila, numero_cadeira)
                );
            """)  # Executa a instrucao SQL que cria a tabela da sala caso ela ainda nao exista no banco

            for fila in FILAS:  # Percorre a lista de letras das filas (de A ate J)
                for coluna in COLUNAS:  # Percorre a lista de numeros das cadeiras (de 1 ate 20)
                    cursor.execute(  # Prepara o comando SQL de insercao de dados para o assento atual
                        f"""
                        INSERT INTO {nome_tabela} (fila, numero_cadeira, ocupado)
                        VALUES (%s, %s, FALSE)
                        ON CONFLICT (fila, numero_cadeira) DO NOTHING;
                        """,  # Instrucao SQL com protecao contra duplicacao de assentos existentes
                        (
                            fila,
                            coluna,
                        ),  # Passa a letra da fila e o numero da cadeira como parametros seguros
                    )  # Finaliza a execucao da instrucao SQL de insercao do lugar

            print(
                f"[OK] Tabela {nome_tabela} verificada e populada com sucesso!"
            )  # Exibe no terminal a confirmacao de conclusao da sala atual

        conn.commit()  # Confirma e consolida permanentemente todas as alteracoes no PostgreSQL

        cursor.close()  # Fecha o cursor do banco de dados libertando recursos do sistema
        conn.close()  # Encerra a conexao ativa com o servidor PostgreSQL
        print(
            "\n[SUCESSO] Povoamento concluido com sucesso em todas as tabelas e salas!"
        )  # Imprime mensagem de sucesso total no terminal

    except Exception as error:  # Captura qualquer erro de conexao ou de instrucao SQL que ocorra
        print(
            "\n[ERRO] Erro ao popular a base de dados:", error
        )  # Exibe no terminal o erro capturado sem interromper abruptamente


if __name__ == "__main__":  # Verifica se o script esta a ser executado diretamente pelo Python
    popular_banco_de_dados()  # Chama a funcao principal para iniciar o povoamento do banco de dados