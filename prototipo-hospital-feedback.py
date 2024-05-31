import sqlite3
from datetime import datetime

def criar_conexao():
    conn = sqlite3.connect('feedbacks_hospitais.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hospitais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            localizacao TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedbacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hospital_id INTEGER,
            feedback TEXT NOT NULL,
            tempo_espera INTEGER,
            hora TEXT,
            FOREIGN KEY (hospital_id) REFERENCES hospitais (id)
        )
    ''')

    conn.commit()
    return conn

def inserir_hospital(conn, nome, localizacao):
    cursor = conn.cursor()
    cursor.execute('INSERT INTO hospitais (nome, localizacao) VALUES (?, ?)', (nome, localizacao))
    conn.commit()

def listar_hospitais(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM hospitais')
    hospitais = cursor.fetchall()
    return hospitais

def inserir_feedback(conn, hospital_id, feedback):
    cursor = conn.cursor()

    # Verifica se a coluna 'hora' já existe
    cursor.execute('PRAGMA table_info(feedbacks)')
    columns = cursor.fetchall()
    hora_existe = any(column[1] == 'hora' for column in columns)

    # Adiciona a coluna 'hora' se não existir
    if not hora_existe:
        cursor.execute('ALTER TABLE feedbacks ADD COLUMN hora TEXT')

    # Verifica se a coluna 'tempo_espera' já existe
    cursor.execute('PRAGMA table_info(feedbacks)')
    columns = cursor.fetchall()
    tempo_espera_existe = any(column[1] == 'tempo_espera' for column in columns)

    # Adiciona a coluna 'tempo_espera' se não existir
    if not tempo_espera_existe:
        cursor.execute('ALTER TABLE feedbacks ADD COLUMN tempo_espera INTEGER')

    # Salvando a data e hora atual
    data_hora_atual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('INSERT INTO feedbacks (hospital_id, feedback, hora) VALUES (?, ?, ?)', (hospital_id, feedback, data_hora_atual))
    
    # Solicitar e inserir tempo de espera
    try:
        tempo_espera = int(input("Digite o tempo de espera em minutos: "))
        cursor.execute('UPDATE feedbacks SET tempo_espera = ? WHERE hospital_id = ? AND hora = ?', (tempo_espera, hospital_id, data_hora_atual))
    except ValueError:
        print("Tempo de espera inválido. Não foi inserido.")

    conn.commit()

def listar_feedbacks(conn, hospital_id):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM feedbacks WHERE hospital_id = ?', (hospital_id,))
    feedbacks = cursor.fetchall()
    return feedbacks

def obter_tempo_espera(conn, hospital_id):
    cursor = conn.cursor()
    cursor.execute('SELECT tempo_espera FROM hospitais WHERE id = ?', (hospital_id,))
    tempo_espera = cursor.fetchone()
    return tempo_espera[0] if tempo_espera else None

def processar_resultados(conn):
    hospitais = listar_hospitais(conn)

    for idx, hospital in enumerate(hospitais, start=1):
        print(f"{idx}. Hospital: {hospital[1]} - Localização: {hospital[2]}")

    print("\n0. Voltar ao menu principal")

    escolha_hospital = input("Escolha o número do hospital para ver os feedbacks ou 0 para voltar: ")

    try:
        escolha_hospital = int(escolha_hospital)

        if escolha_hospital == 0:
            print("Voltando ao menu principal. Essa opção é válida.")
            return

        if 1 <= escolha_hospital <= len(hospitais):
            hospital_id = hospitais[escolha_hospital - 1][0]
            feedbacks = listar_feedbacks(conn, hospital_id)
            tempo_espera = obter_tempo_espera(conn, hospital_id)

            if not feedbacks:
                print(f"Nenhum feedback disponível para o hospital '{hospitais[escolha_hospital - 1][1]}'. Essa opção é válida.")
            else:
                print(f"\nVocê escolheu o hospital '{hospitais[escolha_hospital - 1][1]}'. Essa opção é válida.")
                print(f"Tempo de espera: {tempo_espera} minutos")

                print("\nFeedbacks:")
                for idx, feedback in enumerate(feedbacks, start=1):
                    print(f"{idx}. {feedback[2]} - Postado em: {feedback[3]}")  # Inclui a data e hora
        else:
            print("Escolha inválida. Tente novamente.")
    except ValueError:
        print("Opção inválida. Tente novamente.")

def main():
    conn = criar_conexao()

    while True:
        print("\n1. Inserir novo hospital")
        print("2. Inserir feedback para hospital")
        print("3. Verificar feedbacks por hospital")
        print("4. Sair")

        escolha = input("Escolha uma opção: ")

        try:
            escolha = int(escolha)

            if escolha == 1:
                nome_hospital = input("Digite o nome do hospital: ")
                localizacao_hospital = input("Digite a localização do hospital: ")
                inserir_hospital(conn, nome_hospital, localizacao_hospital)
                print(f"Hospital '{nome_hospital}' inserido com sucesso. Essa opção é válida.")
            elif escolha == 2:
                hospitais = listar_hospitais(conn)

                if not hospitais:
                    print("Nenhum hospital cadastrado. Por favor, cadastre um hospital primeiro.")
                else:
                    print("Escolha um hospital para inserir o feedback:")
                    for idx, hospital in enumerate(hospitais, start=1):
                        print(f"{idx}. {hospital[1]} - {hospital[2]}")

                    print("\n0. Voltar ao menu principal")

                    escolha_hospital = input("Escolha o número do hospital para ver os feedbacks ou 0 para voltar: ")

                    try:
                        escolha_hospital = int(escolha_hospital)

                        if escolha_hospital == 0:
                            print("Voltando ao menu principal. Essa opção é válida.")
                            continue

                        if 1 <= escolha_hospital <= len(hospitais):
                            hospital_id = hospitais[escolha_hospital - 1][0]
                            feedback = input("Digite o feedback ('cheio', 'vazio' ou 'moderado'): ")
                            inserir_feedback(conn, hospital_id, feedback)
                            print(f"Feedback inserido com sucesso para o hospital '{hospitais[escolha_hospital - 1][1]}'. Essa opção é válida.")
                        else:
                            print("Escolha inválida. Tente novamente.")
                    except ValueError:
                        print("Opção inválida. Tente novamente.")
            elif escolha == 3:
                processar_resultados(conn)
            elif escolha == 4:
                print("Saindo... Essa opção é válida.")
                break
            else:
                print("Opção inválida. Tente novamente.")
        except ValueError:
            print("Opção inválida. Tente novamente.")

    conn.close()

if __name__ == "__main__":
    main()
