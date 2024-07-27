import tkinter as tk
from tkinter import Canvas, messagebox


def cadastrar():
    nome = entry_nome.get()
    email = entry_email.get()
    telefone = entry_telefone.get()
    cidade = entry_cidade.get()
    estado = entry_estado.get()
    empresa = entry_empresa.get()
    cnpj = entry_cnpj.get()
    segmento = entry_segmento.get()

    # Exibir os dados no console (ou salvar em um arquivo, banco de dados, etc.)
    print(f"Nome: {nome}")
    print(f"Email: {email}")
    print(f"Telefone: {telefone}")
    print(f"Cidade: {cidade}")
    print(f"Estado: {estado}")
    print(f"Empresa: {empresa}")
    print(f"CNPJ: {cnpj}")
    print(f"Segmento: {segmento}")


def formatar_telefone(event=None):
    telefone = entry_telefone.get().replace("(", "").replace(")", "").replace("-", "").replace(" ", "").replace("+", "")
    telefone_formatado = ""

    if len(telefone) > 0:
        telefone_formatado = "+"
    if len(telefone) > 2:
        telefone_formatado += telefone[:2] + " "
    if len(telefone) > 4:
        telefone_formatado += "(" + telefone[2:4] + ") "
    if len(telefone) > 9:
        telefone_formatado += telefone[4:9] + "-" + telefone[9:]
    elif len(telefone) > 4:
        telefone_formatado += telefone[4:]

    entry_telefone.delete(0, tk.END)
    entry_telefone.insert(0, telefone_formatado)


def validar_cnpj(event=None):
    cnpj = entry_cnpj.get().replace(".", "").replace("/", "").replace("-", "").replace(" ", "")

    if cnpj == "99999999999999":
        cnpj_formatado = f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
        entry_cnpj.delete(0, tk.END)
        entry_cnpj.insert(0, cnpj_formatado)
        messagebox.showinfo("Informação", "CNPJ 99999999999999 aceito.")
        return

    if len(cnpj) != 14 or not cnpj.isdigit() or not validar_digitos_cnpj(cnpj):
        messagebox.showerror("Erro", "CNPJ inválido")
        entry_cnpj.delete(0, tk.END)
    else:
        cnpj_formatado = f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
        entry_cnpj.delete(0, tk.END)
        entry_cnpj.insert(0, cnpj_formatado)


def validar_digitos_cnpj(cnpj):
    # Verifica se o CNPJ possui todos os dígitos iguais
    if cnpj in (c * 14 for c in "0123456789"):
        return False

    peso1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    peso2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    soma1 = sum(int(cnpj[i]) * peso1[i] for i in range(12))
    digito1 = 11 - soma1 % 11
    digito1 = digito1 if digito1 < 10 else 0

    soma2 = sum(int(cnpj[i]) * peso2[i] for i in range(13))
    digito2 = 11 - soma2 % 11
    digito2 = digito2 if digito2 < 10 else 0

    return cnpj[12] == str(digito1) and cnpj[13] == str(digito2)


# Criação da janela principal
root = tk.Tk()
root.title("Formulário de Registro")

# Criação do canvas
canvas = Canvas(root, width=400, height=700)
canvas.pack()

# Títulos e Entradas do Formulário
label_nome = tk.Label(root, text="Nome:")
canvas.create_window(200, 50, window=label_nome)
entry_nome = tk.Entry(root)
canvas.create_window(200, 70, window=entry_nome)

label_email = tk.Label(root, text="Email:")
canvas.create_window(200, 110, window=label_email)
entry_email = tk.Entry(root)
canvas.create_window(200, 130, window=entry_email)

label_telefone = tk.Label(root, text="Telefone:")
canvas.create_window(200, 170, window=label_telefone)
entry_telefone = tk.Entry(root)
entry_telefone.bind('<FocusOut>', formatar_telefone)
canvas.create_window(200, 190, window=entry_telefone)

label_cidade = tk.Label(root, text="Cidade:")
canvas.create_window(200, 230, window=label_cidade)
entry_cidade = tk.Entry(root)
canvas.create_window(200, 250, window=entry_cidade)

label_estado = tk.Label(root, text="Estado:")
canvas.create_window(200, 290, window=label_estado)
entry_estado = tk.Entry(root)
canvas.create_window(200, 310, window=entry_estado)

label_empresa = tk.Label(root, text="Empresa:")
canvas.create_window(200, 350, window=label_empresa)
entry_empresa = tk.Entry(root)
canvas.create_window(200, 370, window=entry_empresa)

label_cnpj = tk.Label(root, text="CNPJ:")
canvas.create_window(200, 410, window=label_cnpj)
entry_cnpj = tk.Entry(root)
entry_cnpj.bind('<FocusOut>', validar_cnpj)
canvas.create_window(200, 430, window=entry_cnpj)

label_segmento = tk.Label(root, text="Segmento:")
canvas.create_window(200, 470, window=label_segmento)
entry_segmento = tk.Entry(root)
canvas.create_window(200, 490, window=entry_segmento)

# Botão de Cadastro
botao_cadastrar = tk.Button(root, text="Cadastrar", command=cadastrar)
canvas.create_window(200, 540, window=botao_cadastrar)

# Executar o loop principal
root.mainloop()
