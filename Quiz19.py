import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import serial
import threading
from screeninfo import get_monitors
import pandas as pd
import os

# Configuração da porta serial
port = 'COM5'
baud_rate = 9600
rfid_data = ""
current_question = 0
current_answer = 0
answers = []

def place_on_first_monitor(root):
    monitors = get_monitors()
    if len(monitors) > 0:
        first_monitor = monitors[0]
        root.geometry(f'{first_monitor.width}x{first_monitor.height}+{first_monitor.x}+{first_monitor.y}')
    else:
        print("Nenhum monitor detectado. Não é possível colocar a janela no primeiro monitor.")

def place_on_second_monitor(root):
    monitors = get_monitors()
    if len(monitors) > 1:
        second_monitor = monitors[1]
        root.geometry(f'{second_monitor.width}x{second_monitor.height}+{second_monitor.x}+{second_monitor.y}')
    else:
        print("Apenas um monitor detectado. Não é possível colocar a janela no segundo monitor.")

def read_rfid():
    global rfid_data, current_question, current_answer
    try:
        with serial.Serial(port, baud_rate, timeout=1) as ser:
            while True:
                if ser.in_waiting > 0:
                    rfid_data = ser.readline().decode('utf-8').strip().upper()
                    print(f"Tag RFID detectada: {rfid_data}")
                    cleaned_rfid_data = rfid_data.replace(" ", "").upper()
                    print(cleaned_rfid_data)

                    if cleaned_rfid_data == "UIDTAG:0429D495BE2A81":
                        print("Resposta 1")
                        current_answer = 1

                    elif cleaned_rfid_data == "UIDTAG:0448CD95BE2A81":
                        print("Resposta 2")
                        current_answer = 2

                    elif cleaned_rfid_data == "UIDTAG:0417DA95BE2A81":
                        print("Resposta 3")
                        current_answer = 3

                    elif cleaned_rfid_data == "UIDTAG:04FFDF95BE2A81":
                        print("Resposta 4")
                        current_answer = 4

                    print(current_question)
                    print(correct_answers)
                    print(rfid_data)

                    if current_question < len(correct_answers) and current_answer == correct_answers[current_question]:
                        print(f"Resposta correta: {rfid_data}")
                        rfid_data = ""
                        show_correct_message(current_question)
                    elif current_question < len(correct_answers) and current_answer != correct_answers[current_question]:
                        print(f"Resposta incorreta: {rfid_data}")
                        show_incorrect_message(current_question)
                        rfid_data = ""

    except serial.SerialException as e:
        print(f"Erro na comunicação serial: {e}")

def update_rfid_label():
    global rfid_data
    if rfid_data:
        canvas.itemconfig(rfid_text, text=f"RFID Data: {rfid_data}")
    root.after(1000, update_rfid_label)


def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=25, **kwargs):
    """Cria um retângulo arredondado no canvas."""
    points = [x1+radius, y1,
              x1+radius, y1,
              x2-radius, y1,
              x2-radius, y1,
              x2, y1,
              x2, y1+radius,
              x2, y1+radius,
              x2, y2-radius,
              x2, y2-radius,
              x2, y2,
              x2-radius, y2,
              x2-radius, y2,
              x1+radius, y2,
              x1+radius, y2,
              x1, y2,
              x1, y2-radius,
              x1, y2-radius,
              x1, y1+radius,
              x1, y1+radius,
              x1, y1]
    return canvas.create_polygon(points, **kwargs, smooth=True)


def show_question(question, possible_answers, current_question):
    global logo_img, logo_photo, background_photo

    canvas.delete("all")

    canvas.create_image(0, 0, image=background_photo, anchor="nw")

    canvas.create_text(200, 152,text=f'Pergunta {current_question + 1}' if selected_language == "pt" else f'Question {current_question + 1}',font=("Helvetica", 18),
                       width=900, fill="white")

    logo_img = Image.open("fedexLogo.png").convert("RGBA")
    logo_img = logo_img.resize((550, 275), Image.Resampling.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_img)
    canvas.create_image(screen_width // 2, 100, image=logo_photo, anchor="center")

    canvas.create_text(screen_width - 200, 152, text=f'Tempo: 20s', font=("Helvetica", 18),
                       width=900, fill="white")

    x1, y1 = 50, screen_height // 5  # inicio do preto
    x2, y2 = screen_width - 50, screen_height // 3  # Final do preto
    create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=20, outline='black', width=2, fill='black')

    canvas.create_text(screen_width - (screen_width - 70), screen_height // 4, text=question, font=("Helvetica", 24), width=900,
                       fill="white", anchor="w")
    for idx, answer in enumerate(possible_answers):

        x1, y1 = 50, screen_height // 4 + 250 + idx * 150  # inicio do preto
        x2, y2 = screen_width - 50, screen_height // 4 + 350 + idx * 150  # Final do preto
        create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=20, outline='black', width=2, fill='black')

        canvas.create_text(screen_width - (screen_width - 70), screen_height // 4 + 300 + idx * 150, text=answer, font=("Helvetica", 24),
                           width=900, fill="white", anchor="w")

def show_overlay_message(message, sub_message, is_correct):
    # Cria uma nova janela superior (Toplevel) que será usada como overlay
    overlay = tk.Toplevel(root)

    # Define a geometria da nova janela para cobrir toda a largura e altura da tela
    overlay.geometry(f'{screen_width}x{screen_height}+0+0')

    # Remove a barra de título e bordas da janela para dar a aparência de overlay
    overlay.overrideredirect(1)

    # Mantém o overlay no topo de todas as outras janelas
    overlay.attributes("-topmost", True)

    # Define a transparência da janela para 70%
    overlay.attributes("-alpha", 0.7)

    # Cria um canvas dentro da janela overlay com a mesma largura e altura, e define o fundo como preto
    overlay_canvas = tk.Canvas(overlay, width=screen_width, height=screen_height, bg='black')

    # Expande o canvas para preencher toda a janela overlay
    overlay_canvas.pack(fill="both", expand=True)

    # Define um limite de largura para o texto
    text_width = screen_width - 100  # 50 pixels de margem de cada lado

    # Adiciona o texto da mensagem principal no centro do canvas
    overlay_canvas.create_text(screen_width // 2, screen_height // 4 - 50, text=message, font=("Helvetica", 80),
                               fill=f'#ff6200' if is_correct  else f'red', width=text_width)

    # Adiciona o texto da mensagem secundária abaixo da mensagem principal
    overlay_canvas.create_text(screen_width // 2, screen_height // 2, text=sub_message, font=("Helvetica", 40),
                               fill="white", width=text_width)

    # Define para destruir (fechar) a janela overlay após 5 segundos
    root.after(5000, overlay.destroy)



def show_correct_message(question_index):
    show_overlay_message(correct_messages[question_index], message_after_reply[question_index], is_correct=True)
    root.after(5000, next_question)

def show_incorrect_message(question_index):
    show_overlay_message(incorrect_messages[question_index], message_after_reply[question_index], is_correct=False)
    root.after(5000, next_question)


def show_final_message():
    canvas.delete("all")
    canvas.create_image(0, 0, image=background_photo, anchor="nw")
    canvas.create_text(screen_width//2, screen_height//2, text="Quiz Finished! / Quiz Finalizado!", font=("Helvetica", 24), width=700, fill="black")

def next_question():
    global current_question
    if current_question < len(questions) - 1:
        current_question += 1
        show_question(questions[current_question], answers[current_question], current_question)
    else:
        show_final_message()

def start_quiz(language):
    global questions, answers, correct_answers, correct_messages, incorrect_messages, message_after_reply
    current_question = 0  # Reset the current question index
    if language == "pt":
        questions = [
            "1. A FedEx Express é hoje a maior empresa de entregas rápidas do planeta. Quais serviços ela oferece no Brasil?",
            "2. Pensando na agilidade da entrega internacional, a FedEx oferece o serviço International Priority e International Priority Freight aos clientes. Qual o tempo de trânsito médio destes serviços?",
            "3. Para o mercado de aviação, algumas soluções de entrega são extremamente importantes. Qual das soluções abaixo a FedEx oferece para as importações e exportações?",
            "4. A FedEx transporta mercadorias de diversos perfis, valores, tamanhos e pesos. Para o serviço internacional, dos itens abaixo qual tipo de produto a FedEx também transporta?",
            "5. A FedEx vem trabalhando para entregar um futuro mais sustentável. A meta é neutralizar as emissões de carbono em suas operações até 2040 em quantos por cento?"
        ]
        answers = [
            ["Transporte internacional", "Transporte nacional", "Serviços de logística", "Todos os anteriores"],
            ["1 a 3 dias úteis", "1 a 5 dias úteis", "2 a 4 dias úteis", "2 a 5 dias úteis"],
            ["Alto nível de segurança das cargas", "Integração de sistemas para automação do processo",
             "Rastreamento em tempo real", "Todas as anteriores"],
            ["Produtos de tabaco", "Produtos perigosos ", "Bilhetes de loteria", "Correspondência"],
            ["30%", "50%", "100%", "70%"]
        ]
        correct_messages = [
            "Correto!",
            "Correto!",
            "Correto!",
            "Correto!",
            "Correto!"
        ]

        incorrect_messages = [
            "Incorreto! Não era essa a resposta da pergunta 1.",
            "Incorreto! Não era essa a resposta da pergunta 2.",
            "Incorreto! Não era essa a resposta daa pergunta 3.",
            "Incorreto! Não era essa a resposta da pergunta 4.",
            "Incorreto! Não era essa a resposta da pergunta 5."
        ]

        message_after_reply = [
            "A FedEx Express é a empresa privada com a maior combinação de infraestrutura de transporte aéreo e rodoviário do país. Além de conectar mais de 220 países e territórios no mundo com os serviços internacionais, ela oferece também serviços domésticos e de logística para todo o território nacional, conectando mais de 5.300 localidades.",
            "Para atender as entregas urgentes dos clientes, a Fedex oferece o International Priority e International Priority Freight. No International Priority podem ser embarcadas mercadorias até 68kg e no International Priority Freight mercadorias acima de 68kg.",
            "A FedEx oferece diversas soluções para cada perfil de cliente, tanto nos serviços internacionais, quanto nos serviços domésticos e de logística. Para conhecer mais sobre o portfólio da Fedex, converse com a nossa equipe comercial.",
            "A FedEx possui especialistas em carga perigosa para orientar e responder todas as dúvidas sobre como preparar cargas perigosas adequadamente para envio e documentação necessária para o transporte, para assegurar que as entregas sejam feitas no prazo e com segurança.",
            "A meta da FedEx é tornar as operações neutras em carbono até 2040, por meio de diversas iniciativas que inclui: eletrificação de veículos, combustíveis sustentáveis, instalações eficientes, entre outras."
        ]
        correct_answers = [4, 1, 4, 4, 3]  # Corrected answer indices
    else:
        questions = [
            "1. FedEx Express is currently the largest express delivery company on the planet. What services does FedEx offer in Brazil?",
            "2. For efficient international delivery, FedEx provides its customers with two services: International Priority and International Priority Freight. What is the average transit time for these services?",
            "3. Some delivery solutions are extremely important for the transportation market. Which of the following solutions does FedEx offer for imports and exports?",
            "4. FedEx provides transportation services to goods of various types, values, sizes and weights. Which of the options below does FedEx also transport in its international service? ",
            "5. FedEx has been working towards a more sustainable future. In percentage, what is FedEx´s goal to reduce carbon emissions in its operations by 2040?"
        ]
        answers = [
            ["International transportation", "Domestic transportation", "Logistics services",
             "All of the above (correct)"],
            ["1 to 3 business days ", "1 to 5 business days", "2 to 4 business days", "2 to 5 business days"],
            ["High-level cargo security", "System integration for process automation", "Real-time tracking",
             "All of the above "],
            ["Tobacco products", "Dangerous goods ", "Lottery tickets", "Correspondence"],
            ["30%", "50%", "100%", "70%"]
        ]
        correct_messages = [
            "Correct!",
            "Correct!",
            "Correct!",
            "Correct!",
            "Correct!"
        ]

        incorrect_messages = [
            "Incorrect!",
            "Incorrect!",
            "Incorrect!",
            "Incorrect!",
            "Incorrect!"
        ]

        message_after_reply = [
            "FedEx Express is the private company with the largest combination of air and ground transportation infrastructure in the country. In addition to connecting more than 220 countries and territories worldwide through its international services, FedEx also offers domestic and logistics services throughout the country, connecting more than 5,300 locations.",
            "To address customers’ urgent delivery requirements, FedEx provides two distinct services: International Priority, for packages weighing up to 68 kg, and International Priority Freight for packages exceeding 68 kg.",
            "FedEx offers a variety of solutions for each customer profile, both in international and domestic services, as well as in the entire logistics process. To learn more about FedEx´s portfolio, talk to our sales team.",
            "FedEx has a team of dangerous goods specialists to guide customers and to answer all questions about how to properly prepare dangerous goods shipments and the necessary documentation to ensure that deliveries are made on time and safely.",
            "FedEx's goal is to achieve carbon-neutral operations by 2040 through several initiatives, including vehicle electrification, sustainable fuels, efficient facilities, among others."
        ]

        correct_answers = [4, 1, 4, 4, 3]  # Corrected answer indices

    show_question(questions[current_question], answers[current_question], current_question)


def save_registration_data():
    data = {
        "Nome": name_entry.get(),
        "Email": email_entry.get(),
        "Celular": phone_entry.get(),
        "Cidade": city_entry.get(),
        "UF": uf_entry.get(),
        "Empresa": company_entry.get(),
        "CNPJ": cnpj_entry.get(),
        "Segmento": segment_entry.get()
    }
    file_path = "registration_data.xlsx"

    # Verifica se o arquivo já existe
    if os.path.exists(file_path):
        # Carrega o conteúdo existente
        existing_df = pd.read_excel(file_path)
        # Adiciona o novo registro
        new_df = pd.concat([existing_df, pd.DataFrame([data])], ignore_index=True)
    else:
        # Cria um novo DataFrame se o arquivo não existir
        new_df = pd.DataFrame([data])

    # Salva o DataFrame atualizado no arquivo Excel
    new_df.to_excel(file_path, index=False)

    #messagebox.showinfo("Cadastro", "Cadastro realizado com sucesso!")
    start_quiz(selected_language)
def on_entry_click(event, placeholder_text):
    """Remove placeholder text when entry is clicked."""
    global active_entry
    active_entry = event.widget  # Atualiza o campo de entrada ativo
    if event.widget.get() == placeholder_text:
        event.widget.delete(0, "end")
        event.widget.config(fg="black")


def on_focusout(event, placeholder_text):
    """Add placeholder text quando o campo perde o foco e está vazio."""
    if event.widget.get() == "":
        event.widget.insert(0, placeholder_text)
        event.widget.config(fg="grey")


def key_pressed(char):
    """Insere o caractere no campo de entrada ativo"""
    print(char)
    if char != None:
        active_entry.insert(tk.END, char)
    else:
        pass

def backspace_pressed():
    """Remove o último caractere do campo de entrada ativo"""
    if active_entry and len(active_entry.get()) > 0:
        active_entry.delete(len(active_entry.get()) - 1, tk.END)
    else:
        pass


def create_keyboard(root, canvas):
    """Cria um teclado virtual"""
    # Lista de teclas que aparecerão no teclado virtual, incluindo o Backspace no final
    keys = [
        '1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
        'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P',
        'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L',
        'Z', 'X', 'C', 'V', 'B', 'N', 'M', '-', '_', '@',
        'Backspace'
    ]

    # Define o deslocamento inicial para a posição X e Y
    x_offset = screen_width // 8 + 10
    y_offset = screen_height // 4

    # Define a largura e a altura dos botões
    button_width = 7
    button_height = 2

    # Define a cor de fundo e a cor do texto dos botões
    button_bg = '#d3d3d3'
    button_fg = 'black'

    # Define a fonte dos botões
    button_font = ("Helvetica", 12, "bold")

    # Itera sobre a lista de teclas para criar os botões do teclado
    for i, key in enumerate(keys):
        # Calcula a linha e a coluna da tecla atual
        row = i // 10
        col = i % 10

        # Calcula a posição X e Y do botão
        x = x_offset + col * (button_width + 1) * 11
        y = y_offset + row * (button_height + 1) * 20

        # Define o comando do botão
        if key == 'Backspace':
            command = backspace_pressed
            key = "\u2190"  # Substitui o texto "Backspace" pelo símbolo de seta para a esquerda
        else:
            command = lambda k=key: key_pressed(k)

        # Cria o botão com as propriedades definidas
        button = tk.Button(root, text=key, font=button_font,
                           command=command,
                           width=button_width, height=button_height,
                           bg=button_bg, fg=button_fg, bd=1, relief='raised')

        # Adiciona o botão ao canvas
        canvas.create_window(x, y, window=button)

    # Adiciona o botão de espaço
    space_button = tk.Button(root, text="Espaço", font=button_font,
                             command=lambda: key_pressed(' '),
                             width=86, height=button_height,
                             bg=button_bg, fg=button_fg, bd=1, relief='raised')
    # Posiciona o botão de espaço no centro do canvas
    canvas.create_window(screen_width // 2, y_offset + 245, window=space_button)



def show_registration_form(language):
    global selected_language, name_entry, email_entry, phone_entry, city_entry, uf_entry
    global company_entry, cnpj_entry, segment_entry, logo_img, logo_photo, active_entry

    selected_language = language
    canvas.delete("all")
    canvas.create_image(0, 0, image=background_photo, anchor="nw")

    logo_img = Image.open("fedexLogo.png").convert("RGBA")
    logo_img = logo_img.resize((300, 150), Image.Resampling.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_img)
    canvas.create_image(screen_width // 2, 100, image=logo_photo, anchor="center")

    labels = ["Nome e Sobrenome:", "Email:", "Celular:", "Cidade:", "UF:", "Empresa:", "Segmento:", "CNPJ:"]
    labels_en = ["Name and Last Name:", "Email:", "Phone:", "City:", "State:", "Company:", "Segment:", "CNPJ:"]
    y_positions = [200, 250, 300, 350, 350, 400, 400, 450]

    entries = []
    for idx, label in enumerate(labels):
        placeholder_text = labels[idx] if language == "pt" else labels_en[idx]

        if idx != 3 and idx != 4 and idx != 5 and idx != 6:
            x1, y1 = screen_width // 5 - 60, y_positions[idx] - 15  # inicio do preto
            x2, y2 = screen_width // 2 + 380, y_positions[idx] + 25  # Final do preto
            create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=20, outline='black', width=2, fill='black')

            x1, y1 = screen_width // 5 - 57, y_positions[idx] - 12  # ponto inicial
            x2, y2 = screen_width // 2 + 377, y_positions[idx] + 22  # ponto finaal
            create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=20, outline='black', width=1, fill='white')

            entry = tk.Entry(root, font=("Helvetica", 18), width=50, fg="grey", bg='white', bd=0)
            entry.insert(0, placeholder_text)
            entry.bind("<FocusIn>", lambda event, placeholder=placeholder_text: on_entry_click(event, placeholder))
            entry.bind("<FocusOut>", lambda event, placeholder=placeholder_text: on_focusout(event, placeholder))

            canvas.create_window((x1 + x2) // 2 - 40, (y1 + y2) // 2, window=entry)
            entries.append(entry)
        else:
            if idx == 3 or idx == 5:
                x1, y1 = screen_width // 5 - 60, y_positions[idx] - 15  # ponto inicial
                x2, y2 = screen_width // 2 + 25, y_positions[idx] + 25  # Final do preto
                create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=20, outline='black', width=3, fill='black')

                x1, y1 = screen_width // 5 - 57, y_positions[idx] - 12  # ponto inicial
                x2, y2 = screen_width // 2 + 22, y_positions[idx] + 22  # ponto finaal
                create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=20, outline='black', width=1, fill='white')

                entry = tk.Entry(root, font=("Helvetica", 18), width=26, fg="grey", bg='white', bd=0)
                entry.insert(0, placeholder_text)
                entry.bind("<FocusIn>", lambda event, placeholder=placeholder_text: on_entry_click(event, placeholder))
                entry.bind("<FocusOut>", lambda event, placeholder=placeholder_text: on_focusout(event, placeholder))

                canvas.create_window((x1 + x2) // 2 - 20, (y1 + y2) // 2, window=entry)
                entries.append(entry)
            else:
                x1, y1 = screen_width // 2 + 45, y_positions[idx] - 15
                x2, y2 = screen_width // 2 + 380, y_positions[idx] + 25  # Final do preto
                create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=20, outline='black', width=2, fill='black')

                x1, y1 = screen_width // 2 + 48, y_positions[idx] - 12  # ponto inicial
                x2, y2 = screen_width // 2 + 377, y_positions[idx] + 22  # ponto finaal
                create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=20, outline='black', width=1, fill='white')

                entry = tk.Entry(root, font=("Helvetica", 18), width=22, fg="grey", bg='white', bd=0)
                entry.insert(0, placeholder_text)
                entry.bind("<FocusIn>", lambda event, placeholder=placeholder_text: on_entry_click(event, placeholder))
                entry.bind("<FocusOut>", lambda event, placeholder=placeholder_text: on_focusout(event, placeholder))


                canvas.create_window((x1 + x2) // 2 - 10, (y1 + y2) // 2, window=entry)
                entries.append(entry)

    name_entry, email_entry, phone_entry, city_entry, uf_entry, company_entry, cnpj_entry, segment_entry = entries

    x1, y1 = screen_width // 3 - 24 - 15, 1150 - 55  # Inicio do preto
    x2, y2 = screen_width // 2 + 205 + 15, 1150 + 56  # Final do preto
    create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=20, outline='black', width=2, fill='black')

    register_button = tk.Button(root, text="INICIAR" if language == "pt" else "START", font=("Helvetica", 35),
                                command=save_registration_data, fg="white", bd=0, bg="black", width=15, height=1)
    canvas.create_window(screen_width // 2, 1150, window=register_button, anchor="center")

    # Adiciona o teclado virtual
    create_keyboard(root, canvas)

def show_rest_screen():
    canvas.delete("all")
    canvas.create_image(0, 0, image=background_photo, anchor="nw")

    # Desvincula todos os eventos de clique
    canvas.unbind("<Button-1>")

    logo_img = Image.open("fedexLogo.png").convert("RGBA")
    logo_img = logo_img.resize((600, 300), Image.Resampling.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_img)
    canvas.create_image(screen_width // 2, screen_height // 2, image=logo_photo, anchor="center")

    # Vincula o evento de clique do mouse para chamar a função show_language_selection
    canvas.bind("<Button-1>", lambda event: show_language_selection())

    root.mainloop()


def show_language_selection():
    canvas.delete("all")
    canvas.create_image(0, 0, image=background_photo, anchor="nw")

    # Desvincula todos os eventos de clique
    canvas.unbind("<Button-1>")

    logo_img = Image.open("fedexLogo.png").convert("RGBA")
    logo_img = logo_img.resize((450, 225), Image.Resampling.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_img)
    canvas.create_image(screen_width // 2, 200, image=logo_photo, anchor="center")

    x1, y1 = screen_width // 6 - 20, screen_height // 4 + 30  # Inicio do preto
    x2, y2 = screen_width // 2 + 365, screen_height // 4 + 170  # Final do preto
    create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=20, outline='black', width=2, fill='black')

    pt_button = tk.Button(root, text="PORTUGUÊS", font=("Helvetica", 45), bd=0, command=lambda: show_registration_form("pt"), fg="white", bg="black", width=20, height=1)
    pt_button_window = canvas.create_window(screen_width//2, screen_height//4 + 100, anchor="center", window=pt_button)

    x1, y1 = screen_width // 6 - 20, screen_height // 4 + 230  # Inicio do preto
    x2, y2 = screen_width // 2 + 365, screen_height // 4 + 370  # Final do preto
    create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=20, outline='black', width=2, fill='black')

    en_button = tk.Button(root, text="ENGLISH", font=("Helvetica", 45), bd=0, command=lambda: show_registration_form("en"), fg="white", bg="black", width=20, height=1)
    en_button_window = canvas.create_window(screen_width//2, screen_height//4 + 300, anchor="center", window=en_button)
    root.mainloop()

# Configuração da interface gráfica
root = tk.Tk()
root.title("Quiz")

# Escolha o monitor apropriado
place_on_first_monitor(root)
# place_on_second_monitor(root)
root.attributes('-fullscreen', True)

# Carregar a imagem de fundo
background_image = Image.open("background.png")

# Obter a largura e a altura da tela
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Redimensionar a imagem de fundo
background_image = background_image.resize((screen_width, screen_height), Image.LANCZOS)
background_photo = ImageTk.PhotoImage(background_image)

# Configurar o canvas com a imagem de fundo
canvas = tk.Canvas(root, width=screen_width, height=screen_height)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=background_photo, anchor="nw")

# Adicionar texto RFID no canvas
rfid_text = canvas.create_text(screen_width//2, screen_height - 50, text="RFID Data: ", font=("Helvetica", 24), fill="black")

# Lista de perguntas, respostas e respostas corretas (vazio inicialmente)
questions = []
answers = []
correct_answers = []

# Iniciar a leitura do RFID em um thread separado
threading.Thread(target=read_rfid, daemon=True).start()

# Atualizar o rótulo de RFID periodicamente
root.after(1000, update_rfid_label)

# Mostrar a tela de descanso ao iniciar o programa
show_rest_screen()
