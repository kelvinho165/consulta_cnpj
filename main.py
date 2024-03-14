import tkinter as tk
from tkinter import messagebox, simpledialog
import requests
import re
import sqlite3

class TelaNavegacao:
    def __init__(self, master):
        self.master = master
        master.title("Consulta de CNPJ")
        self.token = "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
        self.conn = sqlite3.connect('clientes.db')
        self.criar_tabela_clientes()

        self.label = tk.Label(master, text="Escolha uma opção:")
        self.label.pack(pady=10)

        self.botao_listar = tk.Button(master, text="Listar CNPJs cadastrados", command=self.listar_cnpjs)
        self.botao_listar.pack(pady=25)

        self.botao_importar = tk.Button(master, text="Importar dados de CNPJ", command=self.importar_cnpj)
        self.botao_importar.pack(pady=25)

        self.botao_sair = tk.Button(master, text="Sair", command=self.fechar_conexao)
        self.botao_sair.pack(pady=10)

    def criar_tabela_clientes(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clientes (
                    cnpj TEXT PRIMARY KEY,
                    nome TEXT,
                    razao_social TEXT,
                    email TEXT
                )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Erro ao criar a tabela: {e}")

    def listar_cnpjs(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM clientes")
            clientes = cursor.fetchall()
            self.mostrar_resultados(clientes)
        except sqlite3.Error as e:
            print(f"Erro ao listar CNPJs: {e}")

    def importar_cnpj(self):
        try:
            cnpj = simpledialog.askstring("CNPJ", "Informe o CNPJ desejado:")

            if cnpj:
                if not self.validar_cnpj(cnpj):
                    messagebox.showerror("Erro", "CNPJ inválido. Por favor, insira um CNPJ válido.")
                    return

                dados_cnpj = consulta_cnpj(cnpj, self.token)

                if dados_cnpj:
                    messagebox.showinfo("Dados do CNPJ",
                                        f"CNPJ: {dados_cnpj['cnpj']}\n"
                                        f"Razão Social: {dados_cnpj.get('nome', '')}\n"
                                        f"E-mail: {dados_cnpj.get('email', '')}")

                    if self.validar_email(dados_cnpj.get('email', '')):
                        confirmacao = messagebox.askquestion("Confirmação", "Deseja criar novo cliente com esses dados?")

                        if confirmacao == 'yes':
                            self.incluir_cliente(dados_cnpj)
                            messagebox.showinfo("Novo Cliente", "Novo cliente adicionado com sucesso!")
        except Exception as e:
            print(f"Erro ao importar CNPJ: {e}")

    def incluir_cliente(self, dados_cnpj):
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO clientes (cnpj, nome, razao_social, email) VALUES (?, ?, ?, ?)",
                           (dados_cnpj['cnpj'], dados_cnpj.get('nome', ''), dados_cnpj.get('razao_social', ''), dados_cnpj.get('email', '')))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Erro ao incluir cliente: {e}")

    def mostrar_resultados(self, resultados):
        resultados_formatados = []
        for result in resultados:
            resultado_str = f"CNPJ: {result[0]}, Nome: {result[1]}, Razão Social: {result[2]}, E-mail: {result[3]}"
            resultados_formatados.append(resultado_str)

        resultado_str = "\n".join(resultados_formatados)
        messagebox.showinfo("Resultados", resultado_str)

    def validar_email(self, email):
        regex_email = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
        return bool(re.match(regex_email, email))

    def validar_cnpj(self, cnpj):
        # Remove caracteres não numéricos
        cnpj = re.sub(r'\D', '', cnpj)

        # Validação simples de CNPJ
        if len(cnpj) != 14 or len(set(cnpj)) == 1:
            return False
        return True

    def fechar_conexao(self):
        try:
            self.conn.close()
            self.master.destroy()
        except Exception as e:
            print(f"Erro ao fechar a conexão: {e}")

def consulta_cnpj(cnpj, token):
    try:
        url = f"https://www.receitaws.com.br/v1/cnpj/{cnpj}"
        querystring = {"token": token, "cnpj": cnpj, "plugin": "RF"}
        response = requests.get(url, params=querystring)

        if response.status_code == 200:
            dados_cnpj = response.json()
            return dados_cnpj
        else:
            return None
    except requests.RequestException as e:
        print(f"Erro na requisição HTTP: {e}")
        return None
    except Exception as e:
        print(f"Erro na consulta CNPJ: {e}")
        return None

# Criar a janela principal
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry('350x350')
    app = TelaNavegacao(root)
    root.mainloop()