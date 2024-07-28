import tkinter as tk
import tkinter.font as tkFont
from PIL import Image, ImageTk
import serial
import threading
from screeninfo import get_monitors
import pandas as pd
import os
import re
import time

# Configuração da porta serial
port = 'COM8'
baud_rate = 9600
rfid_data = ""
current_question = 0
current_answer = 0
answers = []
current_hits = 0
time_left = 120  # Tempo inicial
is_paused = False
stop_time_var = False

inactivity_timer = None
inactivity_timeout = 15000
time_remaining = inactivity_timeout // 1000  # Tempo restante em segundos

rfid_allowed = False

# ------------------------- ociosidade --------------------
def update_inactivity_timer():
    global time_remaining, inactivity_timer, inactivity_timeout, stop_time_var
    if stop_time_var is False:
        if time_remaining > 0:
            print(f"Tempo restante para inatividade: {time_remaining} segundos")
            time_remaining -= 1
            inactivity_timer = root.after(1000, update_inactivity_timer)
        else:
            show_rest_screen()
    else:
        pass

def reset_timer():
    global inactivity_timer, time_remaining
    time_remaining = inactivity_timeout // 1000  # Reiniciar o tempo restante
    if inactivity_timer is not None:
        root.after_cancel(inactivity_timer)
    inactivity_timer = root.after(1000, update_inactivity_timer)

def stop_time():
    global inactivity_timer, time_remaining, stop_time_var
    stop_time_var = True

def Start_time_after_all():
    global inactivity_timer, time_remaining, stop_time_var
    inactivity_timer = None
    inactivity_timeout = 15000
    time_remaining = inactivity_timeout // 1000  # Tempo restante em segundos
    stop_time_var = False

# ---------------------------------------------------------

def place_on_second_monitor(root):
    monitors = get_monitors()
    if len(monitors) > 1:
        second_monitor = monitors[0]
        root.geometry(f'{second_monitor.width}x{second_monitor.height}+{second_monitor.x}+{second_monitor.y}')
        root.update_idletasks()
    else:
        print("Apenas um monitor detectado. Não é possível colocar a janela no segundo monitor.")




def place_on_first_monitor(root):
    monitors = get_monitors()
    if len(monitors) > 0:
        first_monitor = monitors[0]
        root.geometry(f'{first_monitor.width}x{first_monitor.height}+{first_monitor.x}+{first_monitor.y}')
    else:
        print("Nenhum monitor detectado. Não é possível colocar a janela no primeiro monitor.")


def change_answer_bg_color(answer_index, temp_color):
    # Altera a cor de fundo do item de resposta específico no canvas
    canvas.itemconfig(answer_bg_ids[answer_index], fill=temp_color)

    # Adiciona um atraso de 2000 milissegundos (2 segundos) antes de executar a próxima linha
    delay(8000)

    # Exibe uma mensagem sobreposta com a mensagem atual, sub-mensagem e se a resposta está correta ou não
    show_overlay_message(current_message, current_sub_message, current_is_correct)


def update_timer():
    global time_left, is_paused
    if not is_paused:
        if time_left > 0:
            time_left -= 1
            print(time_left)
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
    # Declaração de variáveis globais usadas na função
    global current_message, current_sub_message, current_is_correct
    global is_paused

    # Define a variável is_paused como True para pausar o timer ou outras atividades dependentes desse estado
    is_paused = True

    # Define a mensagem principal que será mostrada ao usuário, com base no índice da pergunta correta
    current_message = correct_messages[question_index]

    # Define a mensagem secundária, que pode conter informações adicionais, com base no índice da pergunta
    current_sub_message = message_after_reply[question_index]

    # Marca que a resposta atual é correta, alterando o estado da variável global
    current_is_correct = True

    # Muda a cor de fundo da resposta correta para um tom específico (#4D148C)
    change_answer_bg_color(current_answer - 1, "#4D148C")  # Mudar a cor para verde


def show_incorrect_message(question_index):
    # Declaração de variáveis globais usadas na função
    global current_message, current_sub_message, current_is_correct
    global is_paused

    # Define a variável is_paused como True para pausar o timer ou outras atividades dependentes desse estado
    is_paused = True

    # Define a mensagem principal que será mostrada ao usuário, com base no índice da pergunta incorreta
    current_message = incorrect_messages[question_index]

    # Define a mensagem secundária, que pode conter informações adicionais, com base no índice da pergunta
    current_sub_message = message_after_reply[question_index]

    # Marca que a resposta atual é incorreta, alterando o estado da variável global
    current_is_correct = False

    # Muda a cor de fundo da resposta incorreta para vermelho
    change_answer_bg_color(current_answer - 1, "red")  # Mudar a cor para vermelho


def read_rfid():
    global rfid_data, current_question, current_answer, current_hits, rfid_allowed
    rfid_readings = []  # Lista para armazenar as leituras de RFID
    max_readings = 5  # Número de leituras necessárias
    reading_interval = 2  # Intervalo máximo entre leituras em segundos (2 segundos)
    last_read_time = time.time()  # Tempo da última leitura

    def reset_readings():
        nonlocal rfid_readings
        rfid_readings.clear()  # Limpar as leituras acumuladas
        print("Leituras de RFID reiniciadas devido ao intervalo de tempo sem leitura")

    try:
        with serial.Serial(port, baud_rate, timeout=1) as ser:
            while True:
                if ser.in_waiting > 0:
                    rfid_data = ser.readline().decode('utf-8').strip().upper()
                    print(f"Tag RFID detectada: {rfid_data}")
                    cleaned_rfid_data = rfid_data.replace(" ", "").upper()

                    current_time = time.time()
                    if current_time - last_read_time > reading_interval:
                        reset_readings()  # Reiniciar leituras se o intervalo for excedido

                    last_read_time = current_time

                    if rfid_allowed:  # Verificar se a leitura é permitida
                        rfid_readings.append(cleaned_rfid_data)
                        if len(rfid_readings) > max_readings:
                            rfid_readings.pop(0)  # Mantém apenas as últimas 'max_readings' leituras

                        if len(rfid_readings) == max_readings and all(r == rfid_readings[0] for r in rfid_readings):
                            # Todas as leituras são iguais
                            if cleaned_rfid_data == "UIDTAG:0429D495BE2A81":
                                current_answer = 1
                            elif cleaned_rfid_data == "UIDTAG:0448CD95BE2A81":
                                current_answer = 2
                            elif cleaned_rfid_data == "UIDTAG:0417DA95BE2A81":
                                current_answer = 3
                            elif cleaned_rfid_data == "UIDTAG:04FFDF95BE2A81":
                                current_answer = 4

                            if current_question < len(correct_answers) and current_answer == correct_answers[
                                current_question]:
                                current_hits += 1
                                show_correct_message(current_question)
                            elif current_question < len(correct_answers) and current_answer != correct_answers[
                                current_question]:
                                show_incorrect_message(current_question)

                            rfid_data = ""  # Limpar a leitura após processar
                            rfid_readings.clear()  # Limpar as leituras acumuladas
                            rfid_allowed = False  # Bloquear leituras adicionais até a próxima pergunta
    except serial.SerialException as e:
        print(f"Erro na comunicação serial: {e}")

    root.after(int(reading_interval * 1000), reset_readings)  # Programar o reinício das leituras após o intervalo

def update_rfid_label():
    global rfid_data
    if rfid_data:
        canvas.itemconfig(rfid_text, text=f"RFID Data: {rfid_data}")
    root.after(1000, update_rfid_label)

def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=25, **kwargs):
    """Cria um retângulo arredondado no canvas."""
    points = [x1 + radius, y1,
              x1 + radius, y1,
              x2 - radius, y1,
              x2 - radius, y1,
              x2, y1,
              x2, y1 + radius,
              x2, y1 + radius,
              x2, y2 - radius,
              x2, y2 - radius,
              x2, y2,
              x2 - radius, y2,
              x2 - radius, y2,
              x1 + radius, y2,
              x1 + radius, y2,
              x1, y2,
              x1, y2 - radius,
              x1, y2 - radius,
              x1, y1 + radius,
              x1, y1 + radius,
              x1, y1]
    return canvas.create_polygon(points, **kwargs, smooth=True)


def show_question(question, possible_answers, current_question, in_weight):
    # Declaração de variáveis globais usadas na função
    global logo_img, logo_photo, background_photo, question_text_id, answer_text_ids, answer_bg_ids, timer_text_id, rfid_allowed, boximg, logo_photo_boximg

    # Para o temporizador de inatividade
    stop_time()

    # Inicializa a variável de pausa como falsa
    is_paused = False

    # Limpa todos os elementos do canvas
    canvas.delete("all")

    # Reseta as listas de IDs das respostas e fundos das respostas
    answer_text_ids = []
    answer_bg_ids = []

    # Define a imagem de fundo do canvas
    canvas.create_image(0, 0, image=background_photo, anchor="nw")

    # Carrega o logo da FedEx, redimensiona e converte para o formato necessário.
    logo_img = Image.open("fedexLogo.png").convert("RGBA")
    logo_img = logo_img.resize((480, 133), Image.Resampling.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_img)

    # Posiciona o logo da FedEx no centro da tela.
    canvas.create_image(screen_width // 2, screen_height // 8, image=logo_photo, anchor="center")

    # Define diferentes fontes personalizadas
    custom_font1 = tkFont.Font(family="Sans Light", size=28) #fonte temporizador
    custom_font2 = tkFont.Font(family="Sans Light", size=54) #fonte das perguntas

    # Adiciona o temporizador ao canvas
    timer_text_id = canvas.create_text(screen_width - 400, screen_height // 8 + int(133 / 4) + 5, text=f'Tempo: {time_left}s', font=custom_font1,
                                       width=900, fill="black")

    y_offset = 100  # Ajuste este valor para descer as perguntas e respostas
    x1, y1 = screen_width // 10, screen_height // 5 + y_offset  # Início do retângulo a 1/10 da largura
    x2, y2 = screen_width * 9 // 10, screen_height // 3 + y_offset  # Fim do retângulo a 9/10 da largura
    create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=65, outline='white', width=2, fill='white')

    # Calcula a largura do texto da pergunta com base nas coordenadas do retângulo de fundo
    text_width = x2 - x1 - 20  # Ajuste o valor conforme necessário para garantir que o texto não ultrapasse os limites

    # Adiciona o texto da pergunta ao canvas
    question_text_id = canvas.create_text(x1 + 10, (y1 + y2) // 2, text=question,
                                          font=custom_font2, width=text_width, fill="black", anchor="w")

    # Define as coordenadas do retângulo de fundo da questão
    px1, py1 = screen_width // 10 + 15, int(screen_height // 5 + 20 + (y_offset * 5.5))  # Início do retângulo a 1/10 da largura
    px2, py2 = screen_width // 3.5, int(screen_height // 5 + 40 + (y_offset * 5.5))  # Fim do retângulo a 9/10 da largura
    create_rounded_rectangle(canvas, px1, py1, px2, py2, radius=0, outline='#4d148c', width=2, fill='#4d148c')


    # Loop para criar os textos das respostas e seus fundos
    for idx, answer in enumerate(possible_answers):
        # Define as coordenadas dos retângulos de fundo das respostas
        y_answer_offset = y_offset + 200  # Ajuste adicional para as respostas
        Y_difference_beetwen_question = 160
        x1, y1 = screen_width // 10, screen_height // 4 + 200 + idx * Y_difference_beetwen_question + y_answer_offset  # Início do retângulo a 1/10 da largura
        x2, y2 = screen_width * 9 // 10, screen_height // 4 + 300 + idx * Y_difference_beetwen_question + y_answer_offset  # Fim do retângulo a 9/10 da largura
        bg_id = create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=65, outline='white', width=2, fill='white')
        answer_bg_ids.append(bg_id)

        # Criação do texto em duas partes: peso e resposta
        answer_text = canvas.create_text(x1 + 10, y1 + 50,
                                         text=answer, font=custom_font2, fill="black", anchor="w", width=text_width)

        # Adiciona os IDs dos textos de resposta à lista
        answer_text_ids.append(answer_text)

    # Define um atraso de 5 segundos para permitir a leitura RFID
    root.after(5000, lambda: set_rfid_allowed(True))

    # Define um atraso adicional de 0.1 segundos para mostrar a imagem da caixa
    root.after(5100, show_box_image)


def show_box_image():
    print()
    global boximg, logo_photo_boximg
    try:
        boximg = Image.open("Box.png").convert("RGBA")
        boximg = boximg.resize((500, 600), Image.Resampling.LANCZOS)
        logo_photo_boximg = ImageTk.PhotoImage(boximg)
        canvas.create_image(screen_width // 2, screen_height // 2 + (screen_height // 4), image=logo_photo_boximg, anchor="center")
    except Exception as e:
        print(f"Erro ao carregar a imagem: {e}")


def set_rfid_allowed(state):
    global rfid_allowed
    rfid_allowed = state

def show_overlay_message(message, sub_message, is_correct):
    global overlay_photo  # Adiciona a referência global para manter a imagem viva
    # Limpa a sobreposição existente, se houver
    canvas.delete("overlay")

    # Cria uma imagem semi-transparente
    overlay_img = Image.new("RGBA", (screen_width - screen_width // 12, screen_height // 2 + screen_height // 4), (0, 0, 0, int(255 * 0.7)))
    overlay_photo = ImageTk.PhotoImage(overlay_img)

    # Adiciona a imagem semi-transparente ao canvas
    canvas.create_image(90, 90, image=overlay_photo, anchor="nw", tags="overlay")

    text_width = screen_width - 250
    text_width_title = screen_width // 2

    # Define as fontes personalizadas para o texto
    custom_font1 = tkFont.Font(family="Sans Light", size=160)
    custom_font2 = tkFont.Font(family="Sans Light", size=60)

    # Cria o texto principal na sobreposição
    canvas.create_text(screen_width // 2, screen_height // 4 - 50, text=message, font=custom_font1,
                               fill=f'#4D148C' if is_correct else f'red', width=text_width_title, anchor="center", justify="center")

    # Cria o texto secundário na sobreposição
    canvas.create_text(screen_width // 2, screen_height // 2, text=sub_message, font=custom_font2,
                               fill="white", width=text_width)

    # Configura para chamar a função next_question após 5000 milissegundos (5 segundos)
    root.after(15000, next_question)

    # Configura para limpar a sobreposição após 5000 milissegundos (5 segundos)
    root.after(15000, lambda: canvas.delete("overlay"))

    # Verifica se a pergunta atual é menor que 4 para continuar o jogo
    if current_question < 4:
        print("AINDA DENTRO DO GAME")

        # Configura para chamar a função resume_timer após 5000 milissegundos (5 segundos)
        root.after(15000, resume_timer)

def show_final_message(in_time):
    global logo_img, logo_photo, current_hits, current_question, time_left, is_paused
    is_paused = True  # Pausar o tempo ao entrar na tela da mensagem final
    stop_time()  # Parar o temporizador de inatividade
    canvas.delete("all")

    if current_hits > 3 and in_time is True:
        main_message_pt = "PARABÉNS!"
        main_message_en = "CONGRATULATIONS!"
        sub_message_pt = f"Desempenho {current_hits}/5"
        sub_message_en = f"Performance {current_hits}/5"
        last_message_pt = f"RETIRE SEU BRINDE"
        last_message_en = f"COLLECT YOUR GIFT"
    else:
        main_message_pt = "QUE PENA, NÂO FOI DESSA VEZ"
        main_message_en = "What a pity, IT WAS NOT THIS TIME"
        sub_message_pt = f"Desempenho {current_hits}/5"
        sub_message_en = f"Performance {current_hits}/5"
        last_message_pt = None
        last_message_en = None

    canvas.create_image(0, 0, image=background_photo, anchor="nw")

    logo_img = Image.open("fedexLogo.png").convert("RGBA")
    logo_img = logo_img.resize((550, 152), Image.Resampling.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_img)
    canvas.create_image(screen_width // 2, 100, image=logo_photo, anchor="center")

    custom_font1 = tkFont.Font(family="Sans Light", size=40)
    custom_font2 = tkFont.Font(family="Sans Light", size=24)
    custom_font3 = tkFont.Font(family="Sans Light", size=70)

    if selected_language == "pt":
        canvas.create_text(screen_width // 2, screen_height // 2 - 180, text=main_message_pt, font=custom_font1,
                           fill="black")
        canvas.create_text(screen_width // 2, screen_height // 2 - 100, text=sub_message_pt, font=custom_font2,
                           fill="black")

        if current_hits > 3 and in_time is True:
            x1, y1 = screen_width // 2 - (screen_width // 4) + 100, screen_height // 2 + 125  # Inicio do preto
            x2, y2 = screen_width // 2 + (screen_width // 4) - 100, screen_height // 2 + 150  # Final do preto
            create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=65, outline='#4D148C', width=2, fill='#4D148C')

            canvas.create_text(screen_width // 2, screen_height // 2 + 160, text=last_message_pt, font=custom_font3,
                               fill="black")
    else:
        canvas.create_text(screen_width // 2, screen_height // 2 - 180, text=main_message_en, font=custom_font1,
                           fill="black")
        canvas.create_text(screen_width // 2, screen_height // 2 - 100, text=sub_message_en, font=custom_font2,
                           fill="black")

        if current_hits > 3 and in_time is True:
            x1, y1 = screen_width // 2 - (screen_width // 4) + 100, screen_height // 2 + 125  # Inicio do preto
            x2, y2 = screen_width // 2 + (screen_width // 4) - 100, screen_height // 2 + 150  # Final do preto
            create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=65, outline='#4D148C', width=2, fill='#4D148C')

            canvas.create_text(screen_width // 2, screen_height // 2 + 160, text=last_message_en, font=custom_font3,
                               fill="black")

    # Adiciona um evento para reiniciar o quiz ao clicar em qualquer parte da tela
    canvas.bind("<Button-1>", restart_quiz)

def restart_quiz(event=None):
    global current_question, current_hits, time_left, rfid_data, is_paused, stop_time_var, rfid_allowed
    current_question = 0
    current_hits = 0
    time_left = 120  # Reinicia o temporizador para 120 segundos
    rfid_data = ""
    is_paused = False
    stop_time_var = False
    rfid_allowed = False

    reset_timer()  # Reiniciar o temporizador de inatividade
    show_language_selection()  # Mostrar a tela de seleção de idioma

def next_question():
    global current_question
    if current_question < len(questions) - 1:
        current_question += 1
        show_question(questions[current_question], answers[current_question], current_question, in_weight)
    else:
        show_final_message(in_time=True)

def start_quiz(language):
    global questions, answers, correct_answers, correct_messages, incorrect_messages, message_after_reply, time_left, in_weight, current_question, current_hits
    current_question = 0
    current_hits = 0
    time_left = 120  # Reinicia o temporizador para 120 segundos
    if language == "pt":
        questions = [
            "A FedEx Express é hoje a maior empresa de entregas rápidas do planeta. Quais serviços ela oferece no Brasil?",
            "Pensando na agilidade da entrega internacional, a FedEx oferece o serviço International Priority e International Priority Freight aos clientes. Qual o tempo de trânsito médio destes serviços?",
            "Para o mercado de aviação, algumas soluções de entrega são extremamente importantes. Qual das soluções abaixo a FedEx oferece para as importações e exportações?",
            "A FedEx transporta mercadorias de diversos perfis, valores, tamanhos e pesos. Para o serviço internacional, dos itens abaixo qual tipo de produto a FedEx também transporta?",
            "A FedEx vem trabalhando para entregar um futuro mais sustentável. A meta é neutralizar as emissões de carbono em suas operações até 2040 em quantos por cento?"
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
            "RESPOSTA CORRETA!",
            "RESPOSTA CORRETA!",
            "RESPOSTA CORRETA!",
            "RESPOSTA CORRETA!",
            "RESPOSTA CORRETA!"
        ]

        incorrect_messages = [
            "RESPOSTA ERRADA!",
            "RESPOSTA ERRADA!",
            "RESPOSTA ERRADA!",
            "RESPOSTA ERRADA!",
            "RESPOSTA ERRADA!"
        ]

        message_after_reply = [
            "A FedEx Express é a empresa privada com a maior combinação de infraestrutura de transporte aéreo e rodoviário do país. \n\n"
            "Além de conectar mais de 220 países e territórios no mundo com os serviços internacionais, ela oferece também serviços domésticos "
            "e de logística para todo o território nacional, conectando mais de 5.300 localidades.",

            "Para atender as entregas urgentes dos clientes, a Fedex oferece o International Priority e International Priority Freight. \n\n"
            "No International Priority podem ser embarcadas mercadorias até 68kg e no International Priority Freight mercadorias acima de 68kg.",

            "A FedEx oferece diversas soluções para cada perfil de cliente, tanto nos serviços internacionais, quanto nos serviços domésticos e de logística. \n\n"
            "Para conhecer mais sobre o portfólio da Fedex, converse com a nossa equipe comercial.",

            "A FedEx possui especialistas em carga perigosa para orientar e responder todas as dúvidas sobre como "
            "preparar cargas perigosas adequadamente para envio e documentação necessária para o transporte, para"
            " assegurar que as entregas sejam feitas no prazo e com segurança.",

            "A meta da FedEx é tornar as operações neutras em carbono até 2040, por meio de diversas iniciativas que inclui: "
            "eletrificação de veículos, combustíveis sustentáveis, instalações eficientes, entre outras."
        ]
        correct_answers = [4, 1, 4, 4, 3]

        in_weight = [
            "Box FedEx 1: ",
            "Box FedEx 2: ",
            "Box FedEx 3: ",
            "Box FedEx 4: ",
        ]
    else:
        questions = [
            "FedEx Express is currently the largest express delivery company on the planet. What services does FedEx offer in Brazil?",
            "For efficient international delivery, FedEx provides its customers with two services: International Priority and International Priority Freight. What is the average transit time for these services?",
            "Some delivery solutions are extremely important for the transportation market. Which of the following solutions does FedEx offer for imports and exports?",
            "FedEx provides transportation services to goods of various types, values, sizes and weights. Which of the options below does FedEx also transport in its international service? ",
            "FedEx has been working towards a more sustainable future. In percentage, what is FedEx´s goal to reduce carbon emissions in its operations by 2040?"
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
            "RIGHT ANSWER!",
            "RIGHT ANSWER!",
            "RIGHT ANSWER!",
            "RIGHT ANSWER!",
            "RIGHT ANSWER!"
        ]

        incorrect_messages = [
            "WRONG ANSWER!",
            "WRONG ANSWER!",
            "WRONG ANSWER!",
            "WRONG ANSWER!",
            "WRONG ANSWER!"
        ]

        message_after_reply = [
            "FedEx Express is the private company with the largest combination of air and ground transportation infrastructure in the country. \n\n"
            "In addition to connecting more than 220 countries and territories worldwide through its international services, "
            "FedEx also offers domestic and logistics services throughout the country, connecting more than 5,300 locations.",

            "To address customers’ urgent delivery requirements, FedEx provides two distinct services: \n\n"
            "International Priority, "
            "for packages weighing up to 68 kg, and International Priority Freight for packages exceeding 68 kg.",

            "FedEx offers a variety of solutions for each customer profile, both in international and domestic services, "
            "as well as in the entire logistics process. \n\n"
            "To learn more about FedEx´s portfolio, talk to our sales team.",

            "FedEx has a team of dangerous goods specialists to guide customers and to answer all questions about how to "
            "properly prepare dangerous goods shipments and the necessary documentation to ensure that deliveries are made "
            "on time and safely.",

            "FedEx's goal is to achieve carbon-neutral operations by 2040 through several initiatives, including vehicle "
            "electrification, sustainable fuels, efficient facilities, among others."
        ]

        correct_answers = [4, 1, 4, 4, 3]

        in_weight = [
            "Box FedEx 1: ",
            "Box FedEx 2: ",
            "Box FedEx 3: ",
            "Box FedEx 4: ",
        ]
    show_question(questions[current_question], answers[current_question], current_question, in_weight)
    update_timer()

def back_PTEN():
    selected_language = ""
    show_language_selection()

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
    elif event.widget.get().strip() == placeholder_text:
        event.widget.delete(0, "end")
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
    # Lista de teclas que serão exibidas no teclado
    keys = [
        '1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
        'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P',
        'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L',
        'Z', 'X', 'C', 'V', 'B', 'N', 'M', '-', '_', '@',
        'Backspace'
    ]

    # Configuração inicial para a posição e aparência dos botões
    x_offset = 289
    y_offset = screen_height // 2
    button_width = int(18)
    button_height = 6
    button_bg = '#d3d3d3'
    button_fg = 'black'
    button_font = tkFont.Font(family="Sans Light", size=10, weight='bold')
    #button_font = tkFont.Font(family="Sans BOLD", size=45)
    button_spacing = 4  # Espaçamento horizontal entre as teclas

    # Loop através de cada tecla na lista de keys
    for i, key in enumerate(keys):
        # Determina a linha e coluna da tecla atual
        row = i // 10
        col = i % 10



        # Calcula a posição x e y do botão no canvas
        x = x_offset + col * (button_width * 10 - button_spacing)
        y = y_offset + row * (button_height + 1) * 20

        # Define a ação do botão; 'Backspace' tem uma ação especial
        if key == 'Backspace':
            command = backspace_pressed
            key = "\u2190"  # Símbolo de seta para a esquerda
        else:
            command = lambda k=key: key_pressed(k)

        # Cria o botão com as configurações definidas e a ação associada
        button = tk.Button(root, text=key, font=button_font, command=command,
                           width=button_width, height=button_height,
                           bg=button_bg, fg=button_fg, bd=1, relief='raised')

        # Posiciona o botão no canvas
        canvas.create_window(x, y, window=button)



    #---------------------- Tecla de espaço ---------------------------------
    space_button_width = int(screen_width // 10)
    # Cria o botão de espaço separadamente, pois ele é maior e ocupa uma linha inteira
    space_button = tk.Button(root, text="Espaço", font=button_font,
                             command=lambda: key_pressed(' '),
                             width=space_button_width, height=button_height,
                             bg=button_bg, fg=button_fg, bd=1, relief='raised')

    # Posiciona o botão de espaço no canvas
    canvas.create_window(screen_width // 2, y_offset + (screen_height // 6), window=space_button)

def formatar_telefone(event=None):
    telefone = phone_entry.get().replace("(", "").replace(")", "").replace("-", "").replace(" ", "").replace("+", "")
    telefone = telefone[:13]  # Limitar a quantidade de dígitos (2 para código do país + 2 para DDD + 9 para o número)
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

    phone_entry.delete(0, tk.END)
    phone_entry.insert(0, telefone_formatado)

    # Verificar se o campo está vazio ou igual ao placeholder_text
    if not telefone or telefone_formatado.strip() == phone_entry.placeholder_text:
        phone_entry.insert(0, phone_entry.placeholder_text)
        phone_entry.config(fg="grey")

def formatar_e_validar_cnpj(event=None):
    cnpj = cnpj_entry.get().replace(".", "").replace("/", "").replace("-", "").replace(" ", "")

    if cnpj == "99999999999999":
        cnpj_formatado = f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
        cnpj_entry.delete(0, tk.END)
        cnpj_entry.insert(0, cnpj_formatado)
        return

    if not validar_cnpj(cnpj):
        cnpj_entry.delete(0, tk.END)
        cnpj_entry.insert(0, cnpj_entry.placeholder_text)
        cnpj_entry.config(fg="grey")
        return

    cnpj = cnpj[:14]  # Limitar a quantidade de dígitos do CNPJ
    cnpj_formatado = ""

    if len(cnpj) > 2:
        cnpj_formatado += cnpj[:2] + "."
    if len(cnpj) > 5:
        cnpj_formatado += cnpj[2:5] + "."
    if len(cnpj) > 8:
        cnpj_formatado += cnpj[5:8] + "/"
    if len(cnpj) > 12:
        cnpj_formatado += cnpj[8:12] + "-"
    if len(cnpj) > 0:
        cnpj_formatado += cnpj[12:]

    cnpj_entry.delete(0, tk.END)
    cnpj_entry.insert(0, cnpj_formatado)

    # Verificar se o campo está vazio ou igual ao placeholder_text
    if not cnpj or cnpj_formatado.strip() == cnpj_entry.placeholder_text:
        cnpj_entry.insert(0, cnpj_entry.placeholder_text)
        cnpj_entry.config(fg="grey")


def validar_cnpj(cnpj):
    # Remover caracteres não numéricos
    cnpj = re.sub(r'\D', '', cnpj)

    # Verificar se o CNPJ tem 14 dígitos
    if len(cnpj) != 14:
        return False

    # Verificar se todos os dígitos são iguais
    if cnpj == cnpj[0] * 14:
        return False

    # Calcular o primeiro dígito verificador
    def calcular_digito(cnpj, peso):
        soma = sum(int(cnpj[i]) * peso[i] for i in range(len(cnpj)))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    # Pesos para os cálculos dos dígitos verificadores
    peso1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    peso2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    # Calcular dígitos verificadores
    primeiro_digito = calcular_digito(cnpj[:12], peso1)
    segundo_digito = calcular_digito(cnpj[:12] + str(primeiro_digito), peso2)

    # Verificar se os dígitos verificadores estão corretos
    return cnpj[-2:] == f"{primeiro_digito}{segundo_digito}"


def show_registration_form(language):
    global selected_language, name_entry, email_entry, phone_entry, city_entry, uf_entry
    global company_entry, cnpj_entry, segment_entry, logo_img, logo_photo, active_entry

    def change_color_reg_1(event):
        register_button.config(bg="white", fg="black")

        x1, y1 = screen_width - (screen_width // 2.5), y_btn_position - 65  # Início do preto
        x2, y2 = screen_width - (screen_width // 10), y_btn_position + 116  # Final do preto

        create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=65, outline='white', width=2, fill='white', tags="b1")

    def change_color_reg_2(event):
        back_button.config(bg="white", fg="black")
        x1, y1 = screen_width // 10, y_btn_position - 65  # Início do preto
        x2, y2 = screen_width // 2.5, y_btn_position + 116  # Final do preto

        create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=65, outline='white', width=2, fill='white', tags="b2")

    def Remove_change_color_reg_1(event):
        register_button.config(bg="black", fg="white")
        canvas.delete("b1")

    def Remove_change_color_reg_2(event):
        back_button.config(bg="black", fg="white")
        canvas.delete("b2")


    # Para quando a função é chamada, o timer de inatividade é parado.
    stop_time()

    # Define a linguagem selecionada (português ou inglês) conforme o parâmetro passado.
    selected_language = language

    # Limpa todos os elementos no canvas.
    canvas.delete("all")

    # Define a imagem de fundo.
    canvas.create_image(0, 0, image=background_photo, anchor="nw")

    # Carrega o logo da FedEx, redimensiona e converte para o formato necessário.
    logo_img = Image.open("fedexLogo.png").convert("RGBA")
    logo_img = logo_img.resize((480, 133), Image.Resampling.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_img)

    # Posiciona o logo da FedEx no centro da tela, um pouco acima do meio.
    canvas.create_image(screen_width // 2, screen_height // 8, image=logo_photo, anchor="center")

    #----------------------------------- Formulario de registro ------------------------------
    # Define os rótulos e suas versões em inglês.
    labels = ["Nome e Sobrenome", "Email", "Celular", "Cidade", "UF", "Empresa", "Segmento", "CNPJ"]
    labels_en = ["Name and Last Name", "Email", "Phone", "City", "State", "Company", "Segment", "Business ID"]

    # Define a posição Y de cada rótulo.
    y_distance_standar = screen_height // 7
    y_positions = [y_distance_standar + 150 + 50 + 20,
                   y_distance_standar + 250 + 100 + 40,
                   y_distance_standar + 350 + 150 + 60,
                   y_distance_standar + 450 + 200 + 80,
                   y_distance_standar + 450 + 200 + 80,
                   y_distance_standar + 550 + 250 + 100,
                   y_distance_standar + 550 + 250 + 100,
                   y_distance_standar + 650 + 300 + 120]

    # Define a fonte personalizada.
    custom_font = tkFont.Font(family="Sans Light", size=45)

    # Cria uma lista para armazenar os campos de entrada (entries).
    entries = []

    # RAIO Padrao
    stardard_radius = 30

    # X Padrao
    standard_x_start = ((screen_width // 10) + 5) - 5
    print(screen_width)
    print(standard_x_start)
    standard_x_end = screen_width - ((screen_width // 10) - 2)

    #Altura da caixa de cadastro
    stardard_final_height = 120

    #Cor do fundo da área de texto
    color_background_insert = "#FAF9F6"
    Widht_Box_insert_font = 51


    # Loop para criar cada campo de entrada e seu respectivo rótulo.
    for idx, label in enumerate(labels):
        # Define o texto do placeholder conforme a linguagem selecionada.
        placeholder_text = labels[idx] if language == "pt" else labels_en[idx]

        # Se o índice não for 3, 4, 5 ou 6, cria um campo de entrada de tamanho maior.
        if idx != 3 and idx != 4 and idx != 5 and idx != 6:

            # Define a posição e dimensões da caixa ao redor do campo de entrada.
            x1, y1 = standard_x_start - 3, y_positions[idx] - 15  # início do preto
            x2, y2 = standard_x_end + 3, y_positions[idx] + stardard_final_height  # Final do preto
            create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=stardard_radius, outline='black', width=2, fill='black')

            x1, y1 = standard_x_start + 3, y_positions[idx] - 9  # ponto inicial
            x2, y2 = standard_x_end - 3, y_positions[idx] + stardard_final_height - 6  # ponto final
            create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=stardard_radius, outline='black', width=1, fill=color_background_insert)

            # Cria o campo de entrada com um placeholder text, cor e largura definidas.
            entry = tk.Entry(root, font=custom_font, width=Widht_Box_insert_font, fg="black", bg=color_background_insert, bd=0)
            entry.insert(0, placeholder_text)

            # Adiciona eventos para quando o campo ganha ou perde o foco, para manipular o placeholder text.
            entry.bind("<FocusIn>", lambda event, placeholder=placeholder_text: on_entry_click(event, placeholder))
            entry.bind("<FocusOut>", lambda event, placeholder=placeholder_text: on_focusout(event, placeholder))

            # Adiciona eventos específicos para formatação de telefone e validação de CNPJ para os respectivos campos.
            if idx == 2 and language == "pt":  # Index 2 é o campo de telefone (Celular)
                entry.bind("<FocusOut>", formatar_telefone)
            if idx == 7 and language == "pt":  # Index 7 é o campo de CNPJ
                entry.bind("<FocusOut>", formatar_e_validar_cnpj)

            # Posiciona o campo de entrada no canvas.
            canvas.create_window((x1 + x2) // 2 + 15, (y1 + y2) // 2, window=entry)
            # Adiciona o campo de entrada à lista de entradas.
            entries.append(entry)
        else:
            # Caso o índice seja 3, 4, 5 ou 6, cria um campo de entrada de tamanho menor.
            if idx == 3 or idx == 5:
                x1, y1 = standard_x_start - 3, y_positions[idx] - 15  # ponto inicial
                x2, y2 = screen_width // 2 + 180, y_positions[idx] + stardard_final_height  # Final do preto
                create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=stardard_radius, outline='black', width=3, fill='black')
                x1, y1 = standard_x_start + 3, y_positions[idx] - 9  # ponto inicial
                x2, y2 = screen_width // 2 + 177 - 3, y_positions[idx] + stardard_final_height - 6  # final do branco
                create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=stardard_radius, outline='black', width=1, fill=color_background_insert)
                entry = tk.Entry(root, font=custom_font, width= int(Widht_Box_insert_font * 0.60), fg="black", bg=color_background_insert, bd=0)
                entry.insert(0, placeholder_text)
                entry.bind("<FocusIn>", lambda event, placeholder=placeholder_text: on_entry_click(event, placeholder))
                entry.bind("<FocusOut>", lambda event, placeholder=placeholder_text: on_focusout(event, placeholder))
                canvas.create_window((x1 + x2) // 2 + 15, (y1 + y2) // 2, window=entry)
                entries.append(entry)
            else:
                x1, y1 = screen_width // 2 + 200, y_positions[idx] - 15 # inicial do preto
                x2, y2 = standard_x_end + 3, y_positions[idx] + stardard_final_height  # Final do preto
                create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=stardard_radius, outline='black', width=2, fill='black')
                x1, y1 = screen_width // 2 + 203 + 3, y_positions[idx] - 9  # inicial do branco
                x2, y2 = standard_x_end - 3, y_positions[idx] + stardard_final_height - 6  # final do branco
                create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=stardard_radius, outline='black', width=1, fill=color_background_insert)
                entry = tk.Entry(root, font=custom_font, width=int(Widht_Box_insert_font * 0.38) // 2 + 10, fg="black", bg=color_background_insert, bd=0)
                entry.insert(0, placeholder_text)
                entry.bind("<FocusIn>", lambda event, placeholder=placeholder_text: on_entry_click(event, placeholder))
                entry.bind("<FocusOut>", lambda event, placeholder=placeholder_text: on_focusout(event, placeholder))
                canvas.create_window((x1 + x2) // 2 + 15, (y1 + y2) // 2, window=entry)
                entries.append(entry)

    # Atribui os campos de entrada às variáveis globais para serem acessíveis em outras partes do programa.
    name_entry, email_entry, phone_entry, city_entry, uf_entry, company_entry, segment_entry, cnpj_entry = entries

    # Define o placeholder_text para phone_entry e cnpj_entry.
    phone_entry.placeholder_text = "Celular:" if language == "pt" else "Phone:"
    cnpj_entry.placeholder_text = "CNPJ:" if language == "pt" else "Business ID:"

    # ----------------------------------- Fim do Formulario de registro ------------------------------


    # ----------------------------------- Botões de iniciar e voltar ---------------------------------
    y_btn_position = screen_height // 2 + (screen_height // 4)

    # Cria e posiciona o botão de "INICIAR"/"START" no canvas.
    x1, y1 = screen_width - (screen_width // 2.5), y_btn_position - 65  # Início do preto
    x2, y2 = screen_width - (screen_width // 10), y_btn_position + 116  # Final do preto

    create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=65, outline='black', width=2, fill='black')
    custom_font = tkFont.Font(family="Sans Light", size=35)

    register_button = tk.Button(root, text="INICIAR" if language == "pt" else "START",
                                font=custom_font,
                                command=save_registration_data, fg="white", bd=0,
                                bg="black", width=24, height=2,
                                activebackground="white", activeforeground="black",
                                highlightthickness=0)
    canvas.create_window(screen_width // 2 + (screen_width // 4), y_btn_position + 25,
                         window=register_button, anchor="center")

    # Cria e posiciona o botão de "VOLTAR"/"BACK" no canvas.
    x1, y1 = screen_width // 10, y_btn_position - 65  # Início do preto
    x2, y2 = screen_width // 2.5, y_btn_position + 116  # Final do preto

    create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=65, outline='black', width=2, fill='black')
    back_button = tk.Button(root, text="VOLTAR" if language == "pt" else "BACK",
                            font=custom_font,
                            command=back_PTEN, fg="white", bd=0,
                            bg="black", width=24, height=2,
                            activebackground="white", activeforeground="black",
                            highlightthickness=0)
    canvas.create_window(screen_width // 2 - (screen_width // 4), y_btn_position + 25, window=back_button, anchor="center")

    register_button.bind("<Button-1>", change_color_reg_1)
    back_button.bind("<Button-1>", change_color_reg_2)

    register_button.bind("<Enter>", change_color_reg_1)
    back_button.bind("<Enter>", change_color_reg_2)

    register_button.bind("<ButtonRelease-1>", Remove_change_color_reg_1)
    back_button.bind("<ButtonRelease-1>", Remove_change_color_reg_2)

    register_button.bind("<Leave>", Remove_change_color_reg_1)
    back_button.bind("<Leave>", Remove_change_color_reg_2)

    # ----------------------------------- Fim de iniciar e voltar ---------------------------------

    # Cria o teclado virtual para entrada de dados.
    create_keyboard(root, canvas)


def show_rest_screen():
    canvas.delete("all")
    canvas.create_image(0, 0, image=background_photo, anchor="nw")
    canvas.unbind("<Button-1>")
    logo_img = Image.open("fedexLogo.png").convert("RGBA")
    logo_img = logo_img.resize((600, 166), Image.Resampling.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_img)
    canvas.create_image(screen_width // 2, screen_height // 2, image=logo_photo, anchor="center")
    canvas.bind("<Button-1>", lambda event: show_language_selection())
    root.mainloop()


def show_language_selection():
    global inactivity_timer

    def on_interaction(event):
        reset_timer()

    def on_interaction2():
        reset_timer()
    def change_color1(event):
        pt_button.config(bg="white", fg="black")
        x1, y1 = screen_width // 6 - 30, screen_height // 4 + 20  # Inicio do preto
        x2, y2 = screen_width // 2 + (screen_width // 3), screen_height // 4 + 180  # Final do preto
        create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=65, outline='white', width=2, fill='white', tags="b1")

        on_interaction2()

    def change_color2(event):
        en_button.config(bg="white", fg="black")
        x1, y1 = screen_width // 6 - 30, screen_height // 4 + 220  # Inicio do preto
        x2, y2 = screen_width // 2 + (screen_width // 3), screen_height // 4 + 380  # Final do preto
        create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=65, outline='white', width=2, fill='white', tags="b2")
        on_interaction2()

    def Remove_change_color1(event):
        pt_button.config(bg="black", fg="white")
        canvas.delete("b1")
        on_interaction2()
    def Remove_change_color2(event):
        en_button.config(bg="black", fg="white")
        canvas.delete("b2")
        on_interaction2()

    canvas.delete("all")
    canvas.create_image(0, 0, image=background_photo, anchor="nw")

    canvas.unbind("<Button-1>")
    logo_img = Image.open("fedexLogo.png").convert("RGBA")
    logo_img = logo_img.resize((370, 103), Image.Resampling.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_img)
    canvas.create_image(screen_width // 2, screen_width // 6, image=logo_photo, anchor="center")
    x1, y1 = screen_width // 6 - 5, screen_height // 4 + 20  # Inicio do preto
    x2, y2 = screen_width // 2 + (screen_width // 3), screen_height // 4 + 180  # Final do preto
    create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=65, outline='black', width=2, fill='black')
    custom_font = tkFont.Font(family="Sans Light", size=45)

    pt_button = tk.Button(root, text="PORTUGUÊS", font=custom_font, bd=0,
                          command=lambda: show_registration_form("pt"),
                          fg="white", bg="black", width=42, height=1,
                          activebackground="white", activeforeground="black")
    pt_button_window = canvas.create_window(screen_width // 2, screen_height // 4 + 100, anchor="center",
                                            window=pt_button)
    x1, y1 = screen_width // 6 - 5, screen_height // 4 + 220  # Inicio do preto
    x2, y2 = screen_width // 2 + (screen_width // 3), screen_height // 4 + 380  # Final do preto
    create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=65, outline='black', width=2, fill='black')
    en_button = tk.Button(root, text="ENGLISH", font=custom_font, bd=0,
                          command=lambda: show_registration_form("en"),
                          fg="white", bg="black", width=42, height=1,
                          activebackground="white", activeforeground="black")
    en_button_window = canvas.create_window(screen_width // 2, screen_height // 4 + 300, anchor="center",
                                            window=en_button)

    # Adicionar evento de interação para resetar o temporizador
    canvas.bind_all("<Motion>", on_interaction)
    canvas.bind_all("<Key>", on_interaction)

    pt_button.bind("<Button-1>", change_color1)
    en_button.bind("<Button-1>", change_color2)

    pt_button.bind("<Enter>", change_color1)
    en_button.bind("<Enter>", change_color2)

    pt_button.bind("<ButtonRelease-1>", Remove_change_color1)
    en_button.bind("<ButtonRelease-1>", Remove_change_color2)

    pt_button.bind("<Leave>", Remove_change_color1)
    en_button.bind("<Leave>", Remove_change_color2)

    reset_timer()
    Start_time_after_all()  # Iniciar o temporizador de inatividade
    root.mainloop()

# Configuração da interface gráfica
root = tk.Tk()
root.title("Quiz")
root.attributes('-fullscreen', True)
#place_on_second_monitor(root)  # Garantir que a janela ocupe toda a tela do segundo monitor

background_image = Image.open("background.png")
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
background_image = background_image.resize((screen_width, screen_height), Image.LANCZOS)
background_photo = ImageTk.PhotoImage(background_image)

canvas = tk.Canvas(root, width=screen_width, height=screen_height)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=background_photo, anchor="nw")
rfid_text = canvas.create_text(screen_width // 2, screen_height - 50, text="RFID Data: ", font=("Sans Light", 24),
                               fill="black")
timer_text_id = canvas.create_text(screen_width - 150, 152, text=f'Tempo: {time_left}s', font=("Sans Light", 18),
                                   fill="black")
questions = []
answers = []
correct_answers = []
threading.Thread(target=read_rfid, daemon=True).start()
root.after(1000, update_rfid_label)
show_rest_screen()