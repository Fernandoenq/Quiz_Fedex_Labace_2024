import tkinter as tk
import tkinter.font as tkFont
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
current_hits = 0
time_left = 60  # Tempo inicial de 1 minuto (60 segundos)
is_paused = False

inactivity_timer = None
inactivity_timeout = 15000
time_remaining = inactivity_timeout // 1000  # Tempo restante em segundos


#------------------------- ociosidade --------------------
def update_inactivity_timer():
    global time_remaining, inactivity_timer, inactivity_timeout
    if time_remaining > 0:
        print(f"Tempo restante para inatividade: {time_remaining} segundos")
        time_remaining -= 1
        inactivity_timer = root.after(1000, update_inactivity_timer)
    else:
        show_rest_screen()

def reset_timer():
    global inactivity_timer, time_remaining
    time_remaining = inactivity_timeout // 1000  # Reiniciar o tempo restante
    if inactivity_timer is not None:
        root.after_cancel(inactivity_timer)
    inactivity_timer = root.after(1000, update_inactivity_timer)


#---------------------------------------------------------

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

def change_answer_bg_color(answer_index, temp_color):
    canvas.itemconfig(answer_bg_ids[answer_index], fill=temp_color)
    delay(2000)
    show_overlay_message(current_message, current_sub_message, current_is_correct)

def update_timer():
    global time_left, is_paused
    if not is_paused:
        print("tempo normal")
        if time_left > 0:
            time_left -= 1
            canvas.itemconfig(timer_text_id, text=f'Tempo: {time_left}s')
            root.after(1000, update_timer)
        else:
            show_final_message(in_time=False)
    else:
        print("Pausado")
def delay(ms):
    root.after(ms)
    root.update()


def resume_timer():
    global is_paused
    is_paused = False
    update_timer()

def show_correct_message(question_index):
    global current_message, current_sub_message, current_is_correct
    global is_paused
    is_paused = True
    current_message = correct_messages[question_index]
    current_sub_message = message_after_reply[question_index]
    current_is_correct = True
    change_answer_bg_color(current_answer - 1, "#4D148C")  # Mudar a cor para verde

def show_incorrect_message(question_index):
    global current_message, current_sub_message, current_is_correct
    global is_paused
    is_paused = True
    current_message = incorrect_messages[question_index]
    current_sub_message = message_after_reply[question_index]
    current_is_correct = False
    change_answer_bg_color(current_answer - 1, "red")  # Mudar a cor para vermelho

def read_rfid():
    global rfid_data, current_question, current_answer, current_hits
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
                    print("current_hits")
                    print(current_hits)

                    if current_question < len(correct_answers) and current_answer == correct_answers[current_question]:
                        print(f"Resposta correta: {rfid_data}")
                        rfid_data = ""
                        current_hits += 1
                        print(current_hits)
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
    global logo_img, logo_photo, background_photo, question_text_id, answer_text_ids, answer_bg_ids, timer_text_id
    is_paused = False
    canvas.delete("all")
    answer_text_ids = []  # Resetar a lista de IDs das respostas
    answer_bg_ids = []  # Resetar a lista de IDs dos fundos das respostas

    canvas.create_image(0, 0, image=background_photo, anchor="nw")

    logo_img = Image.open("fedexLogo.png").convert("RGBA")
    logo_img = logo_img.resize((550, 275), Image.Resampling.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_img)
    canvas.create_image(screen_width // 2, 100, image=logo_photo, anchor="center")

    custom_font1 = tkFont.Font(family="FedEx Sans", size=18)
    custom_font2 = tkFont.Font(family="FedEx Sans", size=24)

    timer_text_id = canvas.create_text(screen_width - 200, 152, text=f'Tempo: {time_left}s', font=custom_font1, width=900, fill="white")

    x1, y1 = 50, screen_height // 5  # inicio do preto
    x2, y2 = screen_width - 50, screen_height // 3  # Final do preto
    create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=20, outline='black', width=2, fill='black')

    question_text_id = canvas.create_text(screen_width - (screen_width - 70), screen_height // 4, text=question, font=custom_font2, width=900,
                       fill="white", anchor="w")
    for idx, answer in enumerate(possible_answers):
        x1, y1 = 50, screen_height // 4 + 250 + idx * 150  # inicio do preto
        x2, y2 = screen_width - 50, screen_height // 4 + 350 + idx * 150  # Final do preto
        bg_id = create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=20, outline='black', width=2, fill='black')
        answer_bg_ids.append(bg_id)

        answer_text_id = canvas.create_text(screen_width - (screen_width - 70), screen_height // 4 + 300 + idx * 150, text=answer, font=custom_font2,
                           width=900, fill="white", anchor="w")
        answer_text_ids.append(answer_text_id)
def show_overlay_message(message, sub_message, is_correct):

    overlay = tk.Toplevel(root)
    overlay.geometry(f'{screen_width}x{screen_height}+0+0')
    overlay.overrideredirect(1)
    overlay.attributes("-topmost", True)
    overlay.attributes("-alpha", 0.7)
    overlay_canvas = tk.Canvas(overlay, width=screen_width, height=screen_height, bg='black')
    overlay_canvas.pack(fill="both", expand=True)
    text_width = screen_width - 100

    custom_font1 = tkFont.Font(family="FedEx Sans", size=80)
    custom_font2 = tkFont.Font(family="FedEx Sans", size=40)

    overlay_canvas.create_text(screen_width // 2, screen_height // 4 - 50, text=message, font=custom_font1,
                               fill=f'#4D148C' if is_correct else f'red', width=text_width)
    overlay_canvas.create_text(screen_width // 2, screen_height // 2, text=sub_message, font=custom_font2,
                               fill="white", width=text_width)
    root.after(5000, next_question)
    root.after(5000, overlay.destroy)
    root.after(5000, resume_timer)

def show_final_message(in_time):
    global logo_img, logo_photo
    canvas.delete("all")
    if current_hits > 3 and in_time is True:
        main_message_pt = "Parabéns!"
        main_message_en = "Congratulations!"
        sub_message_pt = f"Desempenho {current_hits}/5"
        sub_message_en = f"Performance {current_hits}/5"
        last_message_pt = f"RETIRE SEU BRINDE"
        last_message_en = f"COLLECT YOUR GIFT"
    elif in_time is False:
        main_message_pt = "Que pena!"
        main_message_en = "What a pity!"
        sub_message_pt = f"Desempenho {current_hits}/5"
        sub_message_en = f"Performance {current_hits}/5"
        last_message_pt = f"O TEMPO ACABOU"
        last_message_en = f"THE TIME IS OVER"
    else:
        main_message_pt = "Que pena!"
        main_message_en = "What a pity!"
        sub_message_pt = f"Desempenho {current_hits}/5"
        sub_message_en = f"Performance {current_hits}/5"
        last_message_pt = f"NÂO FOI DESSA VEZ"
        last_message_en = f"IT WAS NOT THIS TIME"

    canvas.create_image(0, 0, image=background_photo, anchor="nw")

    logo_img = Image.open("fedexLogo.png").convert("RGBA")
    logo_img = logo_img.resize((550, 275), Image.Resampling.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_img)
    canvas.create_image(screen_width // 2, 100, image=logo_photo, anchor="center")

    custom_font1 = tkFont.Font(family="FedEx Sans", size=60)
    custom_font2 = tkFont.Font(family="FedEx Sans", size=24)
    custom_font3 = tkFont.Font(family="FedEx Sans", size=70)

    if selected_language == "pt":
        canvas.create_text(screen_width // 2, screen_height // 2 - 180, text=main_message_pt, font=custom_font1, fill="white")
        canvas.create_text(screen_width // 2, screen_height // 2 - 100, text=sub_message_pt, font=custom_font2, fill="white")
        canvas.create_text(screen_width // 2, screen_height // 2 + 60, text=last_message_pt, font=custom_font3, fill="white")
    else:
        canvas.create_text(screen_width // 2, screen_height // 2 - 180, text=main_message_en, font=custom_font1, fill="white")
        canvas.create_text(screen_width // 2, screen_height // 2 - 100, text=sub_message_en, font=custom_font2, fill="white")
        canvas.create_text(screen_width // 2, screen_height // 2 + 60, text=last_message_en, font=custom_font3, fill="white")

def next_question():
    global current_question
    if current_question < len(questions) - 1:
        current_question += 1
        show_question(questions[current_question], answers[current_question], current_question)
    else:
        show_final_message(in_time=True)

def start_quiz(language):
    global questions, answers, correct_answers, correct_messages, incorrect_messages, message_after_reply, time_left
    current_question = 0
    time_left = 60  # Reinicia o temporizador para 60 segundos
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
            "Incorreto!",
            "Incorreto!",
            "Incorreto!",
            "Incorreto!",
            "Incorreto!"
        ]

        message_after_reply = [
            "A FedEx Express é a empresa privada com a maior combinação de infraestrutura de transporte aéreo e rodoviário do país. Além de conectar mais de 220 países e territórios no mundo com os serviços internacionais, ela oferece também serviços domésticos e de logística para todo o território nacional, conectando mais de 5.300 localidades.",
            "Para atender as entregas urgentes dos clientes, a Fedex oferece o International Priority e International Priority Freight. No International Priority podem ser embarcadas mercadorias até 68kg e no International Priority Freight mercadorias acima de 68kg.",
            "A FedEx oferece diversas soluções para cada perfil de cliente, tanto nos serviços internacionais, quanto nos serviços domésticos e de logística. Para conhecer mais sobre o portfólio da Fedex, converse com a nossa equipe comercial.",
            "A FedEx possui especialistas em carga perigosa para orientar e responder todas as dúvidas sobre como preparar cargas perigosas adequadamente para envio e documentação necessária para o transporte, para assegurar que as entregas sejam feitas no prazo e com segurança.",
            "A meta da FedEx é tornar as operações neutras em carbono até 2040, por meio de diversas iniciativas que inclui: eletrificação de veículos, combustíveis sustentáveis, instalações eficientes, entre outras."
        ]
        correct_answers = [4, 1, 4, 4, 3]
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

        correct_answers = [4, 1, 4, 4, 3]

    show_question(questions[current_question], answers[current_question], current_question)
    update_timer()

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

    if os.path.exists(file_path):
        existing_df = pd.read_excel(file_path)
        new_df = pd.concat([existing_df, pd.DataFrame([data])], ignore_index=True)
    else:
        new_df = pd.DataFrame([data])

    new_df.to_excel(file_path, index=False)
    start_quiz(selected_language)

def on_entry_click(event, placeholder_text):
    global active_entry
    active_entry = event.widget
    if event.widget.get() == placeholder_text:
        event.widget.delete(0, "end")
        event.widget.config(fg="black")

def on_focusout(event, placeholder_text):
    if event.widget.get() == "":
        event.widget.insert(0, placeholder_text)
        event.widget.config(fg="grey")

def key_pressed(char):
    if char != None:
        active_entry.insert(tk.END, char)
    else:
        pass

def backspace_pressed():
    if active_entry and len(active_entry.get()) > 0:
        active_entry.delete(len(active_entry.get()) - 1, tk.END)
    else:
        pass

def create_keyboard(root, canvas):
    keys = [
        '1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
        'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P',
        'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L',
        'Z', 'X', 'C', 'V', 'B', 'N', 'M', '-', '_', '@',
        'Backspace'
    ]
    x_offset = screen_width // 8 + 10
    y_offset = screen_height // 4
    button_width = 7
    button_height = 2
    button_bg = '#d3d3d3'
    button_fg = 'black'
    button_font = tkFont.Font(family="FedEx Sans", size=12, weight='bold')

    for i, key in enumerate(keys):
        row = i // 10
        col = i % 10
        x = x_offset + col * (button_width + 1) * 11
        y = y_offset + row * (button_height + 1) * 20
        if key == 'Backspace':
            command = backspace_pressed
            key = "\u2190"
        else:
            command = lambda k=key: key_pressed(k)
        button = tk.Button(root, text=key, font=button_font, command=command,
                           width=button_width, height=button_height,
                           bg=button_bg, fg=button_fg, bd=1, relief='raised')
        canvas.create_window(x, y, window=button)
    space_button = tk.Button(root, text="Espaço", font=button_font,
                             command=lambda: key_pressed(' '),
                             width=86, height=button_height,
                             bg=button_bg, fg=button_fg, bd=1, relief='raised')
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
    custom_font = tkFont.Font(family="FedEx Sans", size=16)
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
            entry = tk.Entry(root, font=custom_font, width=50, fg="grey", bg='white', bd=0)
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
                entry = tk.Entry(root, font=custom_font, width=26, fg="grey", bg='white', bd=0)
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
                entry = tk.Entry(root, font=custom_font, width=22, fg="grey", bg='white', bd=0)
                entry.insert(0, placeholder_text)
                entry.bind("<FocusIn>", lambda event, placeholder=placeholder_text: on_entry_click(event, placeholder))
                entry.bind("<FocusOut>", lambda event, placeholder=placeholder_text: on_focusout(event, placeholder))
                canvas.create_window((x1 + x2) // 2 - 10, (y1 + y2) // 2, window=entry)
                entries.append(entry)
    name_entry, email_entry, phone_entry, city_entry, uf_entry, company_entry, cnpj_entry, segment_entry = entries
    x1, y1 = screen_width // 3 - 24 - 25, 1150 - 65  # Inicio do preto
    x2, y2 = screen_width // 2 + 205 + 25, 1150 + 66  # Final do preto
    create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=20, outline='black', width=2, fill='black')
    custom_font = tkFont.Font(family="FedEx Sans", size=35)
    register_button = tk.Button(root, text="INICIAR" if language == "pt" else "START", font=custom_font,
                                command=save_registration_data, fg="white", bd=0, bg="black", width=15, height=1)
    canvas.create_window(screen_width // 2, 1150, window=register_button, anchor="center")
    create_keyboard(root, canvas)

def show_rest_screen():
    canvas.delete("all")
    canvas.create_image(0, 0, image=background_photo, anchor="nw")
    canvas.unbind("<Button-1>")
    logo_img = Image.open("fedexLogo.png").convert("RGBA")
    logo_img = logo_img.resize((600, 300), Image.Resampling.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_img)
    canvas.create_image(screen_width // 2, screen_height // 2, image=logo_photo, anchor="center")
    canvas.bind("<Button-1>", lambda event: show_language_selection())
    root.mainloop()


def show_language_selection():
    global inactivity_timer

    def on_interaction(event):
        reset_timer()

    canvas.delete("all")
    canvas.create_image(0, 0, image=background_photo, anchor="nw")
    canvas.unbind("<Button-1>")
    logo_img = Image.open("fedexLogo.png").convert("RGBA")
    logo_img = logo_img.resize((450, 225), Image.Resampling.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_img)
    canvas.create_image(screen_width // 2, 200, image=logo_photo, anchor="center")
    x1, y1 = screen_width // 6 - 20, screen_height // 4 + 30  # Inicio do preto
    x2, y2 = screen_width // 2 + 375, screen_height // 4 + 170  # Final do preto
    create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=20, outline='black', width=2, fill='black')
    custom_font = tkFont.Font(family="FedEx Sans", size=45)
    pt_button = tk.Button(root, text="PORTUGUÊS", font=custom_font, bd=0, command=lambda: show_registration_form("pt"),
                          fg="white", bg="black", width=20, height=1)
    pt_button_window = canvas.create_window(screen_width // 2, screen_height // 4 + 100, anchor="center",
                                            window=pt_button)
    x1, y1 = screen_width // 6 - 20, screen_height // 4 + 230  # Inicio do preto
    x2, y2 = screen_width // 2 + 375, screen_height // 4 + 370  # Final do preto
    create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=20, outline='black', width=2, fill='black')
    en_button = tk.Button(root, text="ENGLISH", font=custom_font, bd=0, command=lambda: show_registration_form("en"),
                          fg="white", bg="black", width=20, height=1)
    en_button_window = canvas.create_window(screen_width // 2, screen_height // 4 + 300, anchor="center",
                                            window=en_button)

    # Adicionar evento de interação para resetar o temporizador
    canvas.bind_all("<Motion>", on_interaction)
    canvas.bind_all("<Key>", on_interaction)
    pt_button.bind("<Button-1>", on_interaction)
    en_button.bind("<Button-1>", on_interaction)

    reset_timer()
    root.mainloop()


# Configuração da interface gráfica
root = tk.Tk()
root.title("Quiz")
place_on_first_monitor(root)
root.attributes('-fullscreen', True)
background_image = Image.open("background.png")
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
background_image = background_image.resize((screen_width, screen_height), Image.LANCZOS)
background_photo = ImageTk.PhotoImage(background_image)
canvas = tk.Canvas(root, width=screen_width, height=screen_height)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=background_photo, anchor="nw")
rfid_text = canvas.create_text(screen_width//2, screen_height - 50, text="RFID Data: ", font=("FedEx Sans", 24), fill="black")
timer_text_id = canvas.create_text(screen_width - 200, 152, text=f'Tempo: {time_left}s', font=("FedEx Sans", 18), fill="white")
questions = []
answers = []
correct_answers = []
threading.Thread(target=read_rfid, daemon=True).start()
root.after(1000, update_rfid_label)
show_rest_screen()
