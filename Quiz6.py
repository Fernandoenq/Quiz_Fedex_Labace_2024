import tkinter as tk
from PIL import Image, ImageTk
import serial
import threading
from screeninfo import get_monitors

# Configuração da porta serial
port = 'COM4'
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
        if rfid_label.winfo_exists():
            rfid_label.config(text=f"RFID Data: {rfid_data}")
    root.after(1000, update_rfid_label)

def show_question(question, possible_answers):
    for widget in frame.winfo_children():
        if widget != rfid_label and widget != background_label:
            widget.destroy()
    question_label = tk.Label(frame, text=question, font=("Helvetica", 24), wraplength=700, justify="center", bg="white")
    question_label.pack(pady=20)
    for idx, answer in enumerate(possible_answers):
        answer_button = tk.Button(frame, text=answer, font=("Helvetica", 18), wraplength=600, justify="center", bg="white")
        answer_button.pack(pady=10)

def show_correct_message(question_index):
    for widget in frame.winfo_children():
        if widget != rfid_label and widget != background_label:
            widget.destroy()
    message_label = tk.Label(frame, text=correct_messages[question_index], font=("Helvetica", 24), wraplength=700, justify="center", bg="white")
    message_label.pack(pady=20)
    message_label = tk.Label(frame, text=message_after_reply[question_index], font=("Helvetica", 24), wraplength=700, justify="center", bg="white")
    message_label.pack(pady=20)
    root.after(5000, next_question)  # Wait for 5 seconds before moving to the next question

def show_incorrect_message(question_index):
    for widget in frame.winfo_children():
        if widget != rfid_label and widget != background_label:
            widget.destroy()
    message_label = tk.Label(frame, text=incorrect_messages[question_index], font=("Helvetica", 24), wraplength=700, justify="center", bg="white")
    message_label.pack(pady=20)
    message_label = tk.Label(frame, text=message_after_reply[question_index], font=("Helvetica", 24), wraplength=700, justify="center", bg="white")
    message_label.pack(pady=20)
    root.after(5000, next_question)  # Wait for 5 seconds before moving to the next question

def next_question():
    global current_question
    if current_question < len(questions) - 1:
        current_question += 1
        show_question(questions[current_question], answers[current_question])
    else:
        show_final_message()

def start_quiz(language):
    global questions, answers, correct_answers, correct_messages, incorrect_messages, message_after_reply
    if language == "pt":
        questions = [
            "Pergunta 1: A FedEx Express é hoje a maior empresa de entregas rápidas do planeta. Quais serviços ela oferece no Brasil?",
            "Pergunta 2: Pensando na agilidade da entrega internacional, a FedEx oferece o serviço International Priority e International Priority Freight aos clientes. Qual o tempo de trânsito médio destes serviços?",
            "Pergunta 3: Para o mercado de aviação, algumas soluções de entrega são extremamente importantes. Qual das soluções abaixo a FedEx oferece para as importações e exportações?",
            "Pergunta 4: A FedEx transporta mercadorias de diversos perfis, valores, tamanhos e pesos. Para o serviço internacional, dos itens abaixo qual tipo de produto a FedEx também transporta?",
            "Pergunta 5: A FedEx vem trabalhando para entregar um futuro mais sustentável. A meta é neutralizar as emissões de carbono em suas operações até 2040 em quantos por cento?"
        ]
        answers = [
            ["Transporte internacional", "Transporte nacional", "Serviços de logística", "Todos os anteriores"],
            ["1 a 3 dias úteis", "1 a 5 dias úteis", "2 a 4 dias úteis", "2 a 5 dias úteis"],
            ["Alto nível de segurança das cargas", "Integração de sistemas para automação do processo", "Rastreamento em tempo real", "Todas as anteriores"],
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
            "Question 1: FedEx Express is currently the largest express delivery company on the planet. What services does FedEx offer in Brazil?",
            "Question 2: For efficient international delivery, FedEx provides its customers with two services: International Priority and International Priority Freight. What is the average transit time for these services?",
            "Question 3: Some delivery solutions are extremely important for the transportation market. Which of the following solutions does FedEx offer for imports and exports?",
            "Question 4: FedEx provides transportation services to goods of various types, values, sizes and weights. Which of the options below does FedEx also transport in its international service? ",
            "Question 5: FedEx has been working towards a more sustainable future. In percentage, what is FedEx´s goal to reduce carbon emissions in its operations by 2040?"
        ]
        answers = [
            ["International transportation", "Domestic transportation", "Logistics services", "All of the above (correct)"],
            ["1 to 3 business days ", "1 to 5 business days", "2 to 4 business days", "2 to 5 business days"],
            ["High-level cargo security", "System integration for process automation", "Real-time tracking", "All of the above "],
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

    show_question(questions[current_question], answers[current_question])

def show_language_selection():
    for widget in frame.winfo_children():
        if widget != background_label:
            widget.destroy()
    language_label = tk.Label(frame, text="Choose Language / Escolha a Língua", font=("Helvetica", 24), wraplength=700, justify="center", bg="white")
    language_label.pack(pady=20)
    pt_button = tk.Button(frame, text="Português", font=("Helvetica", 18), command=lambda: start_quiz("pt"), bg="white")
    pt_button.pack(pady=10)
    en_button = tk.Button(frame, text="English", font=("Helvetica", 18), command=lambda: start_quiz("en"), bg="white")
    en_button.pack(pady=10)

def show_final_message():
    for widget in frame.winfo_children():
        if widget != rfid_label and widget != background_label:
            widget.destroy()
    final_label = tk.Label(frame, text="Quiz Finished! / Quiz Finalizado!", font=("Helvetica", 24), wraplength=700, justify="center", bg="white")
    final_label.pack(pady=20)

def resize_image(event):
    new_width = event.width
    new_height = event.height
    image = bg_image_copy.resize((new_width, new_height))
    photo = ImageTk.PhotoImage(image)
    background_label.config(image=photo)
    background_label.image = photo  # Atualiza a referência da imagem

# Configuração da interface gráfica
root = tk.Tk()
root.title("Quiz")

# Escolha o monitor apropriado
place_on_first_monitor(root)
# place_on_second_monitor(root)
root.attributes('-fullscreen', True)

# Carregar a imagem de fundo
background_image = Image.open("fedex.jpg")

# Obter a largura e a altura da tela
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Redimensionar a imagem de fundo
#background_image = background_image.resize((screen_width, screen_height), Image.LANCZOS)
background_photo = ImageTk.PhotoImage(background_image)

# Configurar o frame com a imagem de fundo
frame = tk.Frame(root, height=screen_height, width=screen_width)
frame.pack(expand=True, fill="both")

background_label = tk.Label(frame, image=background_photo)
background_label.image = background_photo  # Manter uma referência da imagem
background_label.place(x=0, y=0, relwidth=1, relheight=1)

rfid_label = tk.Label(frame, text="RFID Data: ", font=("Helvetica", 24), bg="white")
rfid_label.pack(side=tk.BOTTOM, pady=10)

# Lista de perguntas, respostas e respostas corretas (vazio inicialmente)
questions = []
answers = []
correct_answers = []

# Iniciar a leitura do RFID em um thread separado
threading.Thread(target=read_rfid, daemon=True).start()

# Atualizar o rótulo de RFID periodicamente
root.after(1000, update_rfid_label)

# Mostrar a tela de seleção de idioma
show_language_selection()

root.mainloop()
