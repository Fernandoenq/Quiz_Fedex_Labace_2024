import tkinter as tk
from PIL import Image, ImageTk

# Função para criar a janela principal
def create_window():
    root = tk.Tk()
    root.title("Aplicação com Logo Transparente")

    # Carregar a imagem com fundo transparente
    img_path = "fedexLogo.png"
    img = Image.open(img_path)
    logo = ImageTk.PhotoImage(img)

    # Criar um rótulo e adicionar a imagem
    logo_label = tk.Label(root, image=logo, bg="black")
    logo_label.image = logo  # Necessário para evitar que a imagem seja recolhida pelo garbage collector
    logo_label.pack()

    root.mainloop()

# Executar a aplicação
create_window()
