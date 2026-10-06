import psycopg

DB_CONFIG = {  
    "dbname": "cinema",  
    "user": "postgres", 
    "password": "root", 
    "host": "localhost",  
    "port": "5432", 
}  


FILAS = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J",] 
COLUNAS = list(
    range(1, 21)
)  


def popular_banco_de_dados():
    try:  
        conn = psycopg.connect(
            **DB_CONFIG
        )  
        cursor = (
            conn.cursor()
        )  

        print(
            "A iniciar o povoamento do banco de dados..."
        )
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS compras (
                id SERIAL PRIMARY KEY,
                sala INT NOT NULL,
                assentos TEXT NOT NULL,
                tipo TEXT NOT NULL,
                data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)  
        
        cursor.execute("SELECT COUNT(*) FROM compras;")  
        if cursor.fetchone()[0] == 0: 
            dados_historico = [  
                (1, "A1, A2, A3", "Reserva"),
                (2, "C10, C11", "Reserva"),
                (1, "A3", "Cancelamento"),
                (3, "E5, E6, E7", "Reserva"),
            ]
            for sala, assentos, tipo in dados_historico:  
                cursor.execute(
                    "INSERT INTO compras (sala, assentos, tipo) VALUES (%s, %s, %s);",
                    (sala, assentos, tipo)
                ) 
            print("[OK] Tabela 'compras' criada e populada com dados de historico iniciais!")
        else:
            print("[OK] Tabela 'compras' ja existente e verificada!")

        
        for num_sala in range(
            1, 6
        ):  
            nome_tabela = f"sala{num_sala}" 

            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {nome_tabela} (
                    id SERIAL PRIMARY KEY,
                    fila CHAR(1) NOT NULL,
                    numero_cadeira INT NOT NULL,
                    ocupado BOOLEAN DEFAULT FALSE,
                    UNIQUE(fila, numero_cadeira)
                );
            """)  

            for fila in FILAS:  
                for coluna in COLUNAS:  
                    cursor.execute(  
                        f"""
                        INSERT INTO {nome_tabela} (fila, numero_cadeira, ocupado)
                        VALUES (%s, %s, FALSE)
                        ON CONFLICT (fila, numero_cadeira) DO NOTHING;
                        """,  
                        (
                            fila,
                            coluna,
                        ),  
                    )

            print(
                f"[OK] Tabela {nome_tabela} verificada e populada com sucesso!"
            )  

        conn.commit() 

        cursor.close()  
        conn.close() 
        print(
            "\n[SUCESSO] Povoamento concluido com sucesso em todas as tabelas e salas!"
        ) 

    except Exception as error:  
        print(
            "\n[ERRO] Erro ao popular a base de dados:", error
        )  


if __name__ == "__main__":
    popular_banco_de_dados()  