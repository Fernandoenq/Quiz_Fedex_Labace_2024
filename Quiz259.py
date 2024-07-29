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
    # Declara as variáveis globais usadas na função
    global time_remaining, inactivity_timer, inactivity_timeout, stop_time_var

    # Verifica se a variável stop_time_var está definida como False, indicando que o temporizador não está pausado
    if stop_time_var is False:

        # Verifica se ainda há tempo restante para a inatividade
        if time_remaining > 0:

            # Imprime o tempo restante para a inatividade no console
            print(f"Tempo restante para inatividade: {time_remaining} segundos")

            # Decrementa o tempo restante em 1 segundo
            time_remaining -= 1

            # Define um temporizador que chama a função update_inactivity_timer após 1000 milissegundos (1 segundo)
            inactivity_timer = root.after(1000, update_inactivity_timer)

        # Se o tempo restante para inatividade for 0 ou menos, chama a função show_rest_screen
        else:
            show_rest_screen()

    # Se stop_time_var for True, a função simplesmente passa sem fazer nada
    else:
        pass


def reset_timer():
    # Declara as variáveis globais usadas na função
    global inactivity_timer, time_remaining

    # Reinicia o tempo restante para a inatividade, convertendo de milissegundos para segundos
    time_remaining = inactivity_timeout // 1000

    # Verifica se o temporizador de inatividade está definido
    if inactivity_timer is not None:
        # Cancela o temporizador de inatividade existente
        root.after_cancel(inactivity_timer)

    # Define um novo temporizador que chama a função update_inactivity_timer após 1000 milissegundos (1 segundo)
    inactivity_timer = root.after(1000, update_inactivity_timer)


def stop_time():
    # Declara as variáveis globais usadas na função
    global inactivity_timer, time_remaining, stop_time_var

    # Define a variável stop_time_var como True, indicando que o temporizador está pausado
    stop_time_var = True


def Start_time_after_all():
    # Declara as variáveis globais usadas na função
    global inactivity_timer, time_remaining, stop_time_var

    # Inicializa a variável inactivity_timer como None
    inactivity_timer = None

    # Define o tempo de inatividade como 15000 milissegundos (15 segundos)
    inactivity_timeout = 15000

    # Converte o tempo de inatividade para segundos e atribui a time_remaining
    time_remaining = inactivity_timeout // 1000  # Tempo restante em segundos

    # Define a variável stop_time_var como False, indicando que o temporizador não está pausado
    stop_time_var = False


# ---------------------------------------------------------

def place_on_second_monitor(root):
    # Obtém a lista de monitores conectados
    monitors = get_monitors()

    # Verifica se há mais de um monitor conectado
    if len(monitors) > 1:
        # Seleciona o segundo monitor (índice 1, pois o índice 0 é o primeiro monitor)
        second_monitor = monitors[1]

        # Define a geometria da janela 'root' para ocupar todo o segundo monitor
        root.geometry(f'{second_monitor.width}x{second_monitor.height}+{second_monitor.x}+{second_monitor.y}')

        # Atualiza a interface gráfica para refletir a nova geometria
        root.update_idletasks()
    else:
        # Imprime uma mensagem no console caso apenas um monitor seja detectado
        print("Apenas um monitor detectado. Não é possível colocar a janela no segundo monitor.")

def place_on_first_monitor(root):
    # Obtém a lista de monitores conectados
    monitors = get_monitors()

    # Verifica se há pelo menos um monitor conectado
    if len(monitors) > 0:
        # Seleciona o primeiro monitor (índice 0)
        first_monitor = monitors[0]

        # Define a geometria da janela 'root' para ocupar todo o primeiro monitor
        root.geometry(f'{first_monitor.width}x{first_monitor.height}+{first_monitor.x}+{first_monitor.y}')
    else:
        # Imprime uma mensagem no console caso nenhum monitor seja detectado
        print("Nenhum monitor detectado. Não é possível colocar a janela no primeiro monitor.")


def change_answer_bg_color(answer_index, temp_color):
    # Altera a cor de fundo do item de resposta específico no canvas
    canvas.itemconfig(answer_bg_ids[answer_index], fill=temp_color)

    # Adiciona um atraso de 2000 milissegundos (2 segundos) antes de executar a próxima linha
    delay(8000)

    # Exibe uma mensagem sobreposta com a mensagem atual, sub-mensagem e se a resposta está correta ou não
    show_overlay_message(current_message, current_sub_message, current_is_correct)


def update_timer():
    # Declara as variáveis globais usadas na função
    global time_left, is_paused

    # Verifica se o temporizador não está pausado
    if not is_paused:

        # Verifica se ainda há tempo restante
        if time_left > 0:

            # Decrementa o tempo restante em 1 segundo
            time_left -= 1

            # Imprime o tempo restante no console
            print(time_left)

            # Atualiza o texto do temporizador no canvas
            canvas.itemconfig(timer_text_id, text=f'Tempo: {time_left}s')

            # Define um novo temporizador que chama a função update_timer após 1000 milissegundos (1 segundo)
            root.after(1000, update_timer)

        # Se o tempo restante for 0 ou menos, chama a função show_final_message
        else:
            show_final_message(in_time=False)

    # Se o temporizador estiver pausado, imprime "Pausado" no console
    else:
        print("Pausado")


def delay(ms):
    # Define um atraso de ms milissegundos antes de executar o próximo comando
    root.after(ms)

    # Atualiza a interface gráfica para refletir quaisquer mudanças
    root.update()


def resume_timer():
    # Declara a variável global usada na função
    global is_paused

    # Define a variável is_paused como False, indicando que o temporizador não está mais pausado
    is_paused = False

    # Chama a função update_timer para retomar o temporizador
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
    # Declaração de variáveis globais usadas na função
    global rfid_data, current_question, current_answer, current_hits, rfid_allowed

    # Lista para armazenar as leituras de RFID
    rfid_readings = []

    # Número de leituras necessárias para considerar uma leitura válida
    max_readings = 5

    # Intervalo máximo entre leituras em segundos
    reading_interval = 2

    # Armazena o tempo da última leitura
    last_read_time = time.time()

    # Função interna para reiniciar as leituras
    def reset_readings():
        nonlocal rfid_readings
        rfid_readings.clear()  # Limpa as leituras acumuladas
        print("Leituras de RFID reiniciadas devido ao intervalo de tempo sem leitura")

    try:
        # Abre a porta serial com os parâmetros definidos
        with serial.Serial(port, baud_rate, timeout=1) as ser:
            while True:
                # Verifica se há dados na porta serial
                if ser.in_waiting > 0:
                    # Lê e processa a linha de dados recebida da porta serial
                    rfid_data = ser.readline().decode('utf-8').strip().upper()
                    print(f"Tag RFID detectada: {rfid_data}")

                    # Remove espaços e converte a leitura para maiúsculas
                    cleaned_rfid_data = rfid_data.replace(" ", "").upper()

                    # Obtém o tempo atual
                    current_time = time.time()

                    # Verifica se o intervalo de tempo entre leituras foi excedido
                    if current_time - last_read_time > reading_interval:
                        reset_readings()  # Reinicia as leituras se o intervalo for excedido

                    # Atualiza o tempo da última leitura
                    last_read_time = current_time

                    # Verifica se a leitura de RFID é permitida
                    if rfid_allowed:
                        # Adiciona a leitura de RFID à lista de leituras
                        rfid_readings.append(cleaned_rfid_data)

                        # Mantém apenas as últimas 'max_readings' leituras
                        if len(rfid_readings) > max_readings:
                            rfid_readings.pop(0)

                        # Verifica se todas as leituras são iguais
                        if len(rfid_readings) == max_readings and all(r == rfid_readings[0] for r in rfid_readings):
                            # Define a resposta atual com base na leitura de RFID
                            if cleaned_rfid_data == "UIDTAG:0429D495BE2A81":
                                current_answer = 1
                            elif cleaned_rfid_data == "UIDTAG:0448CD95BE2A81":
                                current_answer = 2
                            elif cleaned_rfid_data == "UIDTAG:0417DA95BE2A81":
                                current_answer = 3
                            elif cleaned_rfid_data == "UIDTAG:04FFDF95BE2A81":
                                current_answer = 4

                            # Verifica se a resposta é correta ou incorreta e atualiza a pontuação
                            if current_question < len(correct_answers) and current_answer == correct_answers[
                                current_question]:
                                current_hits += 1
                                show_correct_message(current_question)
                            elif current_question < len(correct_answers) and current_answer != correct_answers[
                                current_question]:
                                show_incorrect_message(current_question)

                            # Limpa a leitura de RFID após o processamento
                            rfid_data = ""
                            # Limpa as leituras acumuladas
                            rfid_readings.clear()
                            # Bloqueia leituras adicionais até a próxima pergunta
                            rfid_allowed = False
    except serial.SerialException as e:
        # Trata erros de comunicação serial
        print(f"Erro na comunicação serial: {e}")

    # Programa o reinício das leituras após o intervalo de tempo definido
    root.after(int(reading_interval * 1000), reset_readings)


def update_rfid_label():
    # Declara a variável global usada na função
    global rfid_data

    # Verifica se há dados de RFID
    if rfid_data:
        # Atualiza o texto do rótulo de RFID no canvas com os dados de RFID
        canvas.itemconfig(rfid_text, text=f"RFID Data: {rfid_data}")

    # Define um temporizador que chama a função update_rfid_label após 1000 milissegundos (1 segundo)
    root.after(1000, update_rfid_label)


def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=25, **kwargs):
    """Cria um retângulo arredondado no canvas."""
    # Define os pontos para criar o retângulo arredondado
    points = [x1 + radius, y1,  # Ponto superior esquerdo (arredondado)
              x1 + radius, y1,
              x2 - radius, y1,  # Ponto superior direito (arredondado)
              x2 - radius, y1,
              x2, y1,  # Ponto superior direito (reta)
              x2, y1 + radius,
              x2, y1 + radius,
              x2, y2 - radius,  # Ponto inferior direito (arredondado)
              x2, y2 - radius,
              x2, y2,  # Ponto inferior direito (reta)
              x2 - radius, y2,
              x2 - radius, y2,
              x1 + radius, y2,  # Ponto inferior esquerdo (arredondado)
              x1 + radius, y2,
              x1, y2,  # Ponto inferior esquerdo (reta)
              x1, y2 - radius,
              x1, y2 - radius,
              x1, y1 + radius,
              x1, y1 + radius,
              x1, y1]  # Ponto superior esquerdo (reta)

    # Cria um polígono com os pontos definidos e retorna o objeto do canvas
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
    # Imprime uma linha em branco (pode ser usada para depuração)
    print()

    # Declara as variáveis globais usadas na função
    global boximg, logo_photo_boximg

    # Tenta executar o bloco de código abaixo e captura exceções caso ocorram
    try:
        # Abre a imagem "Box.png", converte para RGBA (inclui canal alfa)
        boximg = Image.open("Box.png").convert("RGBA")

        # Redimensiona a imagem para 500x600 pixels usando a técnica de redimensionamento LANCZOS
        boximg = boximg.resize((500, 600), Image.Resampling.LANCZOS)

        # Converte a imagem redimensionada para um objeto ImageTk.PhotoImage, que pode ser usado no canvas
        logo_photo_boximg = ImageTk.PhotoImage(boximg)

        # Cria uma imagem no canvas na posição especificada, com a imagem redimensionada e ancorada no centro
        canvas.create_image(screen_width // 2, screen_height // 2 + (screen_height // 4), image=logo_photo_boximg,
                            anchor="center")

    # Captura qualquer exceção que ocorra durante a execução do bloco try
    except Exception as e:
        # Imprime a mensagem de erro no console
        print(f"Erro ao carregar a imagem: {e}")


def set_rfid_allowed(state):
    # Declara a variável global usada na função
    global rfid_allowed

    # Define o estado de permissão de leitura de RFID
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
    # Declaração de variáveis globais usadas na função
    global logo_img, logo_photo, current_hits, current_question, time_left, is_paused

    # Pausa o temporizador
    is_paused = True

    # Para o temporizador de inatividade
    stop_time()

    # Limpa todos os elementos do canvas
    canvas.delete("all")

    # Define as mensagens principais e secundárias com base no desempenho do usuário
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

    # Define a imagem de fundo do canvas
    canvas.create_image(0, 0, image=background_photo, anchor="nw")

    # Carrega o logo da FedEx, redimensiona e converte para o formato necessário
    logo_img = Image.open("fedexLogo.png").convert("RGBA")
    logo_img = logo_img.resize((550, 152), Image.Resampling.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_img)

    # Posiciona o logo da FedEx no centro da tela
    canvas.create_image(screen_width // 2, 100, image=logo_photo, anchor="center")

    # Define diferentes fontes personalizadas
    custom_font1 = tkFont.Font(family="Sans Light", size=40)
    custom_font2 = tkFont.Font(family="Sans Light", size=24)
    custom_font3 = tkFont.Font(family="Sans Light", size=70)

    # Verifica a linguagem selecionada e adiciona as mensagens correspondentes ao canvas
    if selected_language == "pt":
        canvas.create_text(screen_width // 2, screen_height // 2 - 180, text=main_message_pt, font=custom_font1, fill="black")
        canvas.create_text(screen_width // 2, screen_height // 2 - 100, text=sub_message_pt, font=custom_font2, fill="black")

        if current_hits > 3 and in_time is True:
            x1, y1 = screen_width // 2 - (screen_width // 4) + 100, screen_height // 2 + 125  # Início do retângulo
            x2, y2 = screen_width // 2 + (screen_width // 4) - 100, screen_height // 2 + 150  # Fim do retângulo
            create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=65, outline='#4D148C', width=2, fill='#4D148C')
            canvas.create_text(screen_width // 2, screen_height // 2 + 160, text=last_message_pt, font=custom_font3, fill="black")
    else:
        canvas.create_text(screen_width // 2, screen_height // 2 - 180, text=main_message_en, font=custom_font1, fill="black")
        canvas.create_text(screen_width // 2, screen_height // 2 - 100, text=sub_message_en, font=custom_font2, fill="black")

        if current_hits > 3 and in_time is True:
            x1, y1 = screen_width // 2 - (screen_width // 4) + 100, screen_height // 2 + 125  # Início do retângulo
            x2, y2 = screen_width // 2 + (screen_width // 4) - 100, screen_height // 2 + 150  # Fim do retângulo
            create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=65, outline='#4D148C', width=2, fill='#4D148C')
            canvas.create_text(screen_width // 2, screen_height // 2 + 160, text=last_message_en, font=custom_font3, fill="black")

    # Adiciona um evento para reiniciar o quiz ao clicar em qualquer parte da tela
    canvas.bind("<Button-1>", restart_quiz)

def restart_quiz(event=None):
    # Declaração de variáveis globais usadas na função
    global current_question, current_hits, time_left, rfid_data, is_paused, stop_time_var, rfid_allowed

    # Reinicia as variáveis globais para o estado inicial do quiz
    current_question = 0
    current_hits = 0
    time_left = 120  # Reinicia o temporizador para 120 segundos
    rfid_data = ""
    is_paused = False
    stop_time_var = False
    rfid_allowed = False

    # Reiniciar o temporizador de inatividade
    reset_timer()

    # Mostrar a tela de seleção de idioma
    show_language_selection()


def next_question():
    global current_question  # Declaração de variável global para rastrear a pergunta atual
    if current_question < len(questions) - 1:  # Verifica se há mais perguntas disponíveis
        current_question += 1  # Incrementa o índice da pergunta atual
        show_question(questions[current_question], answers[current_question], current_question, in_weight)  # Exibe a próxima pergunta
    else:
        show_final_message(in_time=True)  # Mostra a mensagem final se não houver mais perguntas

def start_quiz(language):
    # Declaração de variáveis globais para armazenar dados do quiz
    global questions, answers, correct_answers, correct_messages, incorrect_messages, message_after_reply, time_left, in_weight, current_question, current_hits
    current_question = 0  # Reinicia o índice da pergunta atual
    current_hits = 0  # Reinicia o contador de acertos
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

    # Exibe a primeira pergunta do quiz e inicia o temporizador
    show_question(questions[current_question], answers[current_question], current_question, in_weight)
    update_timer()

def back_PTEN():
    selected_language = ""  # Reseta a variável de idioma selecionado para uma string vazia
    show_language_selection()  # Chama a função para exibir a tela de seleção de idioma

def save_registration_data():
    # Coleta os dados de entrada do formulário e armazena em um dicionário
    data = {
        "Nome": name_entry.get(),  # Obtém o valor do campo de entrada "Nome"
        "Email": email_entry.get(),  # Obtém o valor do campo de entrada "Email"
        "Celular": phone_entry.get(),  # Obtém o valor do campo de entrada "Celular"
        "Cidade": city_entry.get(),  # Obtém o valor do campo de entrada "Cidade"
        "UF": uf_entry.get(),  # Obtém o valor do campo de entrada "UF"
        "Empresa": company_entry.get(),  # Obtém o valor do campo de entrada "Empresa"
        "CNPJ": cnpj_entry.get(),  # Obtém o valor do campo de entrada "CNPJ"
        "Segmento": segment_entry.get()  # Obtém o valor do campo de entrada "Segmento"
    }
    file_path = "registration_data.xlsx"  # Define o caminho do arquivo onde os dados serão salvos

    if os.path.exists(file_path):  # Verifica se o arquivo já existe
        existing_df = pd.read_excel(file_path)  # Lê os dados existentes do arquivo
        new_df = pd.concat([existing_df, pd.DataFrame([data])], ignore_index=True)  # Adiciona os novos dados aos existentes
    else:
        new_df = pd.DataFrame([data])  # Cria um novo DataFrame com os dados coletados

    new_df.to_excel(file_path, index=False)  # Salva os dados no arquivo Excel, sem incluir o índice

    start_quiz(selected_language)  # Inicia o quiz com base no idioma selecionado

def on_entry_click(event, placeholder_text, idx):
    print("Entrou no on_entry_click")
    print(event)
    print(placeholder_text)
    print(idx)
    global active_entry  # Declara a variável global active_entry
    if idx == 2:
        print("Entrou no on_entry_click dentro de telefone")
        print(event.widget.get())
        phone = event.widget.get()
        phone_clean = re.sub(r'[\s\(\)\-]', '', phone)
        regex = re.compile(r'^(\+?55)?(\d{2})(9\d{8})$')
        match = regex.match(phone_clean)

        if phone == placeholder_text or match is None:
            event.widget.delete(0, "end")  # Apaga o texto do campo se for placeholder ou número inválido
        else:
            event.widget.config(fg="black")  # Muda a cor do texto para preto
    if idx == 7:
        print("Entrou no on_entry_click dentro de CNPJ")
        cnpj = event.widget.get().replace(".", "").replace("/", "").replace("-", "").replace(" ", "")
        if cnpj == placeholder_text or not validar_cnpj(cnpj):
            event.widget.delete(0, "end")
        else:
            event.widget.config(fg="black")

    active_entry = event.widget  # Define active_entry como o widget que disparou o evento
    if event.widget.get() == placeholder_text:  # Verifica se o conteúdo do campo é o placeholder_text
        event.widget.delete(0, "end")  # Se for, apaga o texto do campo
        event.widget.config(fg="black")  # Muda a cor do texto para preto

# Duplicata da função on_entry_click, a segunda definição sobrescreve a primeira


def on_focusout(event, placeholder_text):
    print("Entrou no on_focusout")
    print(event)
    print(placeholder_text)

    # Quando o campo de entrada perde o foco, esta função é chamada.
    if event.widget.get() == "":
        # Se o campo de entrada estiver vazio, insere o placeholder_text e muda a cor do texto para cinza.
        event.widget.insert(0, placeholder_text)
        event.widget.config(fg="black")
    elif event.widget.get().strip() == placeholder_text:
        # Se o campo de entrada contiver apenas o placeholder_text, mantém o placeholder_text e a cor cinza.
        event.widget.delete(0, "end")
        event.widget.insert(0, placeholder_text)
        event.widget.config(fg="black")

def key_pressed(char):
    # Insere o caractere pressionado no campo de entrada ativo.
    if char is not None:
        active_entry.insert(tk.END, char)

def backspace_pressed():
    # Remove o último caractere do campo de entrada ativo, se houver.
    if active_entry and len(active_entry.get()) > 0:
        active_entry.delete(len(active_entry.get()) - 1, tk.END)

def create_keyboard(root, canvas):
    # Lista de teclas que serão exibidas no teclado virtual.
    keys = [
        '1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
        'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P',
        'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L',
        'Z', 'X', 'C', 'V', 'B', 'N', 'M', '-', '_', '@',
        'Backspace'
    ]

    # Configuração inicial para a posição e aparência dos botões.
    x_offset = 289  # Deslocamento inicial no eixo X
    y_offset = screen_height // 2  # Deslocamento inicial no eixo Y
    button_width = int(18)  # Largura do botão
    button_height = 6  # Altura do botão
    button_bg = '#d3d3d3'  # Cor de fundo do botão
    button_fg = 'black'  # Cor do texto do botão
    button_font = tkFont.Font(family="Sans Light", size=10, weight='bold')  # Fonte do botão
    button_spacing = 4  # Espaçamento horizontal entre as teclas

    # Loop para criar e posicionar cada tecla no canvas.
    for i, key in enumerate(keys):
        row = i // 10  # Calcula a linha da tecla atual
        col = i % 10  # Calcula a coluna da tecla atual

        # Calcula a posição X e Y do botão no canvas.
        x = x_offset + col * (button_width * 10 - button_spacing)
        y = y_offset + row * (button_height + 1) * 20

        # Define a ação do botão; 'Backspace' tem uma ação especial.
        if key == 'Backspace':
            command = backspace_pressed
            key = "\u2190"  # Símbolo de seta para a esquerda
        else:
            command = lambda k=key: key_pressed(k)

        # Cria o botão com as configurações definidas e a ação associada.
        button = tk.Button(root, text=key, font=button_font, command=command,
                           width=button_width, height=button_height,
                           bg=button_bg, fg=button_fg, bd=1, relief='raised')

        # Posiciona o botão no canvas.
        canvas.create_window(x, y, window=button)

    #---------------------- Tecla de espaço ---------------------------------
    space_button_width = int(screen_width // 10)  # Largura do botão de espaço
    # Cria o botão de espaço separadamente, pois ele é maior e ocupa uma linha inteira.
    space_button = tk.Button(root, text="Espaço", font=button_font,
                             command=lambda: key_pressed(' '),
                             width=space_button_width, height=button_height,
                             bg=button_bg, fg=button_fg, bd=1, relief='raised')

    # Posiciona o botão de espaço no canvas.
    canvas.create_window(screen_width // 2, y_offset + (screen_height // 6), window=space_button)


def formatar_telefone(event=None):
    print("Valor telefone")
    phone = phone_entry.get()
    print(phone)

    # Remover espaços, parênteses e traços
    phone = re.sub(r'[\s\(\)\-]', '', phone)
    print("Telefone limpo:", phone)

    # Regex para verificar números de telefone brasileiros com 11 dígitos obrigatórios
    regex = re.compile(r'^(\+?55)?(\d{2})(\d{9})$')

    # Verificar se o telefone corresponde ao padrão
    match = regex.match(phone)
    print("Match:", match)

    if phone in ["Celular:", "Phone:"] or match is None:
        print("Entrou para resetar")

        if phone not in ["Celular:", "Phone:", ""]:
            phone_entry.delete(0, tk.END)
            phone_entry.insert(0, "Número inválido")
            return

        phone_entry.delete(0, tk.END)
        phone_entry.insert(0, phone_entry.placeholder_text)
        phone_entry.config(fg="black")

        return


    telefone = phone.replace("+", "")
    if not telefone.startswith("55"):
        telefone = "55" + telefone

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
        print("Entrou no if para resetar")

        phone_entry.insert(0, phone_entry.placeholder_text)
        phone_entry.config(fg="black")

def formatar_e_validar_cnpj(event=None):
    # Obtém o texto do campo de entrada de CNPJ e remove caracteres indesejados
    cnpj = cnpj_entry.get().replace(".", "").replace("/", "").replace("-", "").replace(" ", "")

    # Se o CNPJ for "99999999999999", formata-o diretamente e retorna
    if cnpj == "99999999999999":
        cnpj_formatado = f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
        cnpj_entry.delete(0, tk.END)
        cnpj_entry.insert(0, cnpj_formatado)
        return

    # Se o CNPJ não for válido
    if not validar_cnpj(cnpj):
        if cnpj_entry.get() == "" or cnpj_entry.get() == cnpj_entry.placeholder_text:
            print("if 1")
            cnpj_entry.delete(0, tk.END)
            cnpj_entry.insert(0, cnpj_entry.placeholder_text)
        else:
            print("if 1")
            cnpj_entry.delete(0, tk.END)
            cnpj_entry.insert(0, "CNPJ Inválido")
        cnpj_entry.config(fg="black")
        return

    cnpj = cnpj[:14]  # Limita a quantidade de dígitos do CNPJ
    cnpj_formatado = ""

    # Formata o CNPJ adicionando os caracteres apropriados
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

    # Atualiza o campo de entrada com o CNPJ formatado
    cnpj_entry.delete(0, tk.END)
    cnpj_entry.insert(0, cnpj_formatado)

    # Verifica se o campo está vazio ou igual ao placeholder_text
    if not cnpj or cnpj_formatado.strip() == cnpj_entry.placeholder_text:
        cnpj_entry.insert(0, cnpj_entry.placeholder_text)
        cnpj_entry.config(fg="black")

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
    # Declaração de variáveis globais usadas na função
    global selected_language, name_entry, email_entry, phone_entry, city_entry, uf_entry
    global company_entry, cnpj_entry, segment_entry, logo_img, logo_photo, active_entry

    def change_color_reg_1(event):
        # Altera a cor do botão "INICIAR" quando o mouse está sobre ele
        register_button.config(bg="white", fg="black")

        # Desenha um retângulo ao redor do botão
        x1, y1 = screen_width - (screen_width // 2.5), y_btn_position - 65  # Início do retângulo
        x2, y2 = screen_width - (screen_width // 10), y_btn_position + 116  # Fim do retângulo

        create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=65, outline='white', width=2, fill='white', tags="b1")

    def change_color_reg_2(event):
        # Altera a cor do botão "VOLTAR" quando o mouse está sobre ele
        back_button.config(bg="white", fg="black")

        # Desenha um retângulo ao redor do botão
        x1, y1 = screen_width // 10, y_btn_position - 65  # Início do retângulo
        x2, y2 = screen_width // 2.5, y_btn_position + 116  # Fim do retângulo

        create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=65, outline='white', width=2, fill='white', tags="b2")

    def Remove_change_color_reg_1(event):
        # Remove a alteração de cor e o retângulo ao redor do botão "INICIAR" quando o mouse sai
        register_button.config(bg="black", fg="white")
        canvas.delete("b1")

    def Remove_change_color_reg_2(event):
        # Remove a alteração de cor e o retângulo ao redor do botão "VOLTAR" quando o mouse sai
        back_button.config(bg="black", fg="white")
        canvas.delete("b2")

    # Para o temporizador de inatividade quando a função é chamada
    stop_time()

    # Define a linguagem selecionada (português ou inglês) conforme o parâmetro passado
    selected_language = language

    # Limpa todos os elementos no canvas
    canvas.delete("all")

    # Define a imagem de fundo
    canvas.create_image(0, 0, image=background_photo, anchor="nw")

    # Carrega o logo da FedEx, redimensiona e converte para o formato necessário
    logo_img = Image.open("fedexLogo.png").convert("RGBA")
    logo_img = logo_img.resize((480, 133), Image.Resampling.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_img)

    # Posiciona o logo da FedEx no centro da tela, um pouco acima do meio
    canvas.create_image(screen_width // 2, screen_height // 8, image=logo_photo, anchor="center")

    # Define os rótulos e suas versões em inglês
    labels = ["Nome e Sobrenome", "Email", "Celular", "Cidade", "UF", "Empresa", "Segmento", "CNPJ"]
    labels_en = ["Name and Last Name", "Email", "Phone", "City", "State", "Company", "Segment", "Business ID"]

    # Define a posição Y de cada rótulo
    y_distance_standar = screen_height // 7
    y_positions = [y_distance_standar + 150 + 50 + 20,
                   y_distance_standar + 250 + 100 + 40,
                   y_distance_standar + 350 + 150 + 60,
                   y_distance_standar + 450 + 200 + 80,
                   y_distance_standar + 450 + 200 + 80,
                   y_distance_standar + 550 + 250 + 100,
                   y_distance_standar + 550 + 250 + 100,
                   y_distance_standar + 650 + 300 + 120]

    # Define a fonte personalizada
    custom_font = tkFont.Font(family="Sans Light", size=45)

    # Cria uma lista para armazenar os campos de entrada (entries)
    entries = []

    # Configurações padrões
    stardard_radius = 30  # Raio padrão
    standard_x_start = ((screen_width // 10) + 5) - 5  # X inicial padrão
    standard_x_end = screen_width - ((screen_width // 10) - 2)  # X final padrão
    stardard_final_height = 120  # Altura padrão da caixa de cadastro
    color_background_insert = "#FAF9F6"  # Cor de fundo da área de texto
    Widht_Box_insert_font = 51  # Largura da fonte da caixa de entrada

    # Loop para criar cada campo de entrada e seu respectivo rótulo
    for idx, label in enumerate(labels):
        # Define o texto do placeholder conforme a linguagem selecionada
        placeholder_text = labels[idx] if language == "pt" else labels_en[idx]

        # Se o índice não for 3, 4, 5 ou 6, cria um campo de entrada de tamanho maior
        if idx != 3 and idx != 4 and idx != 5 and idx != 6:
            # Define a posição e dimensões da caixa ao redor do campo de entrada
            x1, y1 = standard_x_start - 3, y_positions[idx] - 15  # Início do retângulo preto
            x2, y2 = standard_x_end + 3, y_positions[idx] + stardard_final_height  # Fim do retângulo preto
            create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=stardard_radius, outline='black', width=2, fill='black')

            x1, y1 = standard_x_start + 3, y_positions[idx] - 9  # Início do retângulo branco
            x2, y2 = standard_x_end - 3, y_positions[idx] + stardard_final_height - 6  # Fim do retângulo branco
            create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=stardard_radius, outline='black', width=1, fill=color_background_insert)

            # Cria o campo de entrada com um placeholder text, cor e largura definidas
            entry = tk.Entry(root, font=custom_font, width=Widht_Box_insert_font, fg="black", bg=color_background_insert, bd=0)
            entry.insert(0, placeholder_text)

            # Adiciona eventos para quando o campo ganha ou perde o foco, para manipular o placeholder text
            entry.bind("<FocusIn>", lambda event, placeholder=placeholder_text: on_entry_click(event, placeholder, idx))


            # Adiciona eventos específicos para formatação de telefone e validação de CNPJ para os respectivos campos
            if idx == 2 and language == "pt":  # Index 2 é o campo de telefone (Celular)
                entry.bind("<FocusOut>", formatar_telefone)
            elif idx == 7 and language == "pt":  # Index 7 é o campo de CNPJ
                entry.bind("<FocusOut>", formatar_e_validar_cnpj)
            else:
                entry.bind("<FocusOut>", lambda event, placeholder=placeholder_text: on_focusout(event, placeholder))




            # Posiciona o campo de entrada no canvas
            canvas.create_window((x1 + x2) // 2 + 15, (y1 + y2) // 2, window=entry)
            # Adiciona o campo de entrada à lista de entradas
            entries.append(entry)
        else:
            # Caso o índice seja 3, 4, 5 ou 6, cria um campo de entrada de tamanho menor
            if idx == 3 or idx == 5:
                x1, y1 = standard_x_start - 3, y_positions[idx] - 15  # Início do retângulo preto
                x2, y2 = screen_width // 2 + 180, y_positions[idx] + stardard_final_height  # Fim do retângulo preto
                create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=stardard_radius, outline='black', width=3, fill='black')
                x1, y1 = standard_x_start + 3, y_positions[idx] - 9  # Início do retângulo branco
                x2, y2 = screen_width // 2 + 177 - 3, y_positions[idx] + stardard_final_height - 6  # Fim do retângulo branco
                create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=stardard_radius, outline='black', width=1, fill=color_background_insert)
                entry = tk.Entry(root, font=custom_font, width=int(Widht_Box_insert_font * 0.60), fg="black", bg=color_background_insert, bd=0)
                entry.insert(0, placeholder_text)
                entry.bind("<FocusIn>", lambda event, placeholder=placeholder_text: on_entry_click(event, placeholder, idx))
                entry.bind("<FocusOut>", lambda event, placeholder=placeholder_text: on_focusout(event, placeholder))
                canvas.create_window((x1 + x2) // 2 + 15, (y1 + y2) // 2, window=entry)
                entries.append(entry)
            else:
                x1, y1 = screen_width // 2 + 200, y_positions[idx] - 15  # Início do retângulo preto
                x2, y2 = standard_x_end + 3, y_positions[idx] + stardard_final_height  # Fim do retângulo preto
                create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=stardard_radius, outline='black', width=2, fill='black')
                x1, y1 = screen_width // 2 + 203 + 3, y_positions[idx] - 9  # Início do retângulo branco
                x2, y2 = standard_x_end - 3, y_positions[idx] + stardard_final_height - 6  # Fim do retângulo branco
                create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=stardard_radius, outline='black', width=1, fill=color_background_insert)
                entry = tk.Entry(root, font=custom_font, width=int(Widht_Box_insert_font * 0.38) // 2 + 10, fg="black", bg=color_background_insert, bd=0)
                entry.insert(0, placeholder_text)
                entry.bind("<FocusIn>", lambda event, placeholder=placeholder_text: on_entry_click(event, placeholder, idx))
                entry.bind("<FocusOut>", lambda event, placeholder=placeholder_text: on_focusout(event, placeholder))
                canvas.create_window((x1 + x2) // 2 + 15, (y1 + y2) // 2, window=entry)
                entries.append(entry)

    # Atribui os campos de entrada às variáveis globais para serem acessíveis em outras partes do programa
    name_entry, email_entry, phone_entry, city_entry, uf_entry, company_entry, segment_entry, cnpj_entry = entries

    # Define o placeholder_text para phone_entry e cnpj_entry
    phone_entry.placeholder_text = "Celular:" if language == "pt" else "Phone:"
    cnpj_entry.placeholder_text = "CNPJ:" if language == "pt" else "Business ID:"

    # ----------------------------------- Fim do Formulario de registro ------------------------------

    # ----------------------------------- Botões de iniciar e voltar ---------------------------------
    y_btn_position = screen_height // 2 + (screen_height // 4)

    # Cria e posiciona o botão de "INICIAR"/"START" no canvas
    x1, y1 = screen_width - (screen_width // 2.5), y_btn_position - 65  # Início do retângulo preto
    x2, y2 = screen_width - (screen_width // 10), y_btn_position + 116  # Fim do retângulo preto

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

    # Cria e posiciona o botão de "VOLTAR"/"BACK" no canvas
    x1, y1 = screen_width // 10, y_btn_position - 65  # Início do retângulo preto
    x2, y2 = screen_width // 2.5, y_btn_position + 116  # Fim do retângulo preto

    create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=65, outline='black', width=2, fill='black')
    back_button = tk.Button(root, text="VOLTAR" if language == "pt" else "BACK",
                            font=custom_font,
                            command=back_PTEN, fg="white", bd=0,
                            bg="black", width=24, height=2,
                            activebackground="white", activeforeground="black",
                            highlightthickness=0)
    canvas.create_window(screen_width // 2 - (screen_width // 4), y_btn_position + 25, window=back_button, anchor="center")

    # Bind events para mudar a cor dos botões ao interagir com eles
    register_button.bind("<Button-1>", change_color_reg_1)
    back_button.bind("<Button-1>", change_color_reg_2)

    register_button.bind("<Enter>", change_color_reg_1)
    back_button.bind("<Enter>", change_color_reg_2)

    register_button.bind("<ButtonRelease-1>", Remove_change_color_reg_1)
    back_button.bind("<ButtonRelease-1>", Remove_change_color_reg_2)

    register_button.bind("<Leave>", Remove_change_color_reg_1)
    back_button.bind("<Leave>", Remove_change_color_reg_2)

    # ----------------------------------- Fim de iniciar e voltar ---------------------------------

    # Cria o teclado virtual para entrada de dados
    create_keyboard(root, canvas)

def show_rest_screen():
    # Limpa todos os elementos do canvas
    canvas.delete("all")
    # Define a imagem de fundo
    canvas.create_image(0, 0, image=background_photo, anchor="nw")
    # Remove qualquer binding anterior de clique no canvas
    canvas.unbind("<Button-1>")
    # Carrega o logo da FedEx, redimensiona e converte para o formato necessário
    logo_img = Image.open("fedexLogo.png").convert("RGBA")
    logo_img = logo_img.resize((600, 166), Image.Resampling.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_img)
    # Posiciona o logo da FedEx no centro da tela
    canvas.create_image(screen_width // 2, screen_height // 2, image=logo_photo, anchor="center")
    # Vincula o clique do mouse para chamar a função show_language_selection
    canvas.bind("<Button-1>", lambda event: show_language_selection())
    # Inicia o main loop do Tkinter para a interface gráfica
    root.mainloop()

def show_language_selection():
    global inactivity_timer

    def on_interaction(event):
        # Reseta o temporizador de inatividade ao detectar uma interação
        reset_timer()

    def on_interaction2():
        # Reseta o temporizador de inatividade
        reset_timer()

    def change_color1(event):
        # Altera a cor do botão "PORTUGUÊS" quando o mouse está sobre ele
        pt_button.config(bg="white", fg="black")
        # Desenha um retângulo ao redor do botão
        x1, y1 = screen_width // 6 - 30, screen_height // 4 + 20
        x2, y2 = screen_width // 2 + (screen_width // 3), screen_height // 4 + 180
        create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=65, outline='white', width=2, fill='white', tags="b1")
        # Reseta o temporizador de inatividade
        on_interaction2()

    def change_color2(event):
        # Altera a cor do botão "ENGLISH" quando o mouse está sobre ele
        en_button.config(bg="white", fg="black")
        # Desenha um retângulo ao redor do botão
        x1, y1 = screen_width // 6 - 30, screen_height // 4 + 220
        x2, y2 = screen_width // 2 + (screen_width // 3), screen_height // 4 + 380
        create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=65, outline='white', width=2, fill='white', tags="b2")
        # Reseta o temporizador de inatividade
        on_interaction2()

    def Remove_change_color1(event):
        # Remove a alteração de cor e o retângulo ao redor do botão "PORTUGUÊS" quando o mouse sai
        pt_button.config(bg="black", fg="white")
        canvas.delete("b1")
        # Reseta o temporizador de inatividade
        on_interaction2()

    def Remove_change_color2(event):
        # Remove a alteração de cor e o retângulo ao redor do botão "ENGLISH" quando o mouse sai
        en_button.config(bg="black", fg="white")
        canvas.delete("b2")
        # Reseta o temporizador de inatividade
        on_interaction2()

    # Limpa todos os elementos do canvas
    canvas.delete("all")
    # Define a imagem de fundo
    canvas.create_image(0, 0, image=background_photo, anchor="nw")
    # Remove qualquer binding anterior de clique no canvas
    canvas.unbind("<Button-1>")
    # Carrega o logo da FedEx, redimensiona e converte para o formato necessário
    logo_img = Image.open("fedexLogo.png").convert("RGBA")
    logo_img = logo_img.resize((370, 103), Image.Resampling.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_img)
    # Posiciona o logo da FedEx no centro da tela, um pouco acima do meio
    canvas.create_image(screen_width // 2, screen_width // 6, image=logo_photo, anchor="center")

    # Define a posição e dimensões do retângulo ao redor do botão "PORTUGUÊS"
    x1, y1 = screen_width // 6 - 5, screen_height // 4 + 20
    x2, y2 = screen_width // 2 + (screen_width // 3), screen_height // 4 + 180
    create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=65, outline='black', width=2, fill='black')

    # Define a fonte personalizada para os botões
    custom_font = tkFont.Font(family="Sans Light", size=45)

    # Cria e posiciona o botão "PORTUGUÊS"
    pt_button = tk.Button(root, text="PORTUGUÊS", font=custom_font, bd=0,
                          command=lambda: show_registration_form("pt"),
                          fg="white", bg="black", width=42, height=1,
                          activebackground="white", activeforeground="black")
    pt_button_window = canvas.create_window(screen_width // 2, screen_height // 4 + 100, anchor="center",
                                            window=pt_button)

    # Define a posição e dimensões do retângulo ao redor do botão "ENGLISH"
    x1, y1 = screen_width // 6 - 5, screen_height // 4 + 220
    x2, y2 = screen_width // 2 + (screen_width // 3), screen_height // 4 + 380
    create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=65, outline='black', width=2, fill='black')

    # Cria e posiciona o botão "ENGLISH"
    en_button = tk.Button(root, text="ENGLISH", font=custom_font, bd=0,
                          command=lambda: show_registration_form("en"),
                          fg="white", bg="black", width=42, height=1,
                          activebackground="white", activeforeground="black")
    en_button_window = canvas.create_window(screen_width // 2, screen_height // 4 + 300, anchor="center",
                                            window=en_button)

    # Adiciona eventos de interação para resetar o temporizador
    canvas.bind_all("<Motion>", on_interaction)
    canvas.bind_all("<Key>", on_interaction)

    # Bind events para mudar a cor dos botões ao interagir com eles
    pt_button.bind("<Button-1>", change_color1)
    en_button.bind("<Button-1>", change_color2)

    pt_button.bind("<Enter>", change_color1)
    en_button.bind("<Enter>", change_color2)

    pt_button.bind("<ButtonRelease-1>", Remove_change_color1)
    en_button.bind("<ButtonRelease-1>", Remove_change_color2)

    pt_button.bind("<Leave>", Remove_change_color1)
    en_button.bind("<Leave>", Remove_change_color2)

    # Reseta o temporizador de inatividade
    reset_timer()
    # Inicia o temporizador de inatividade
    Start_time_after_all()
    # Inicia o main loop do Tkinter para a interface gráfica
    root.mainloop()

# Configuração da interface gráfica
root = tk.Tk()  # Cria a janela principal do Tkinter
root.title("Quiz")  # Define o título da janela
root.attributes('-fullscreen', True)  # Configura a janela para ocupar a tela inteira

# Carrega a imagem de fundo
background_image = Image.open("background.png")
screen_width = root.winfo_screenwidth()  # Obtém a largura da tela
screen_height = root.winfo_screenheight()  # Obtém a altura da tela
background_image = background_image.resize((screen_width, screen_height), Image.LANCZOS)  # Redimensiona a imagem de fundo para caber na tela
background_photo = ImageTk.PhotoImage(background_image)  # Converte a imagem redimensionada para o formato PhotoImage do Tkinter

# Cria um canvas para desenhar elementos gráficos
canvas = tk.Canvas(root, width=screen_width, height=screen_height)
canvas.pack(fill="both", expand=True)  # Expande o canvas para ocupar toda a janela
canvas.create_image(0, 0, image=background_photo, anchor="nw")  # Define a imagem de fundo no canvas

# Adiciona texto no canvas para exibir dados de RFID
rfid_text = canvas.create_text(screen_width // 2, screen_height - 50, text="RFID Data: ", font=("Sans Light", 24),
                               fill="black")

# Adiciona texto no canvas para exibir o temporizador
timer_text_id = canvas.create_text(screen_width - 150, 152, text=f'Tempo: {time_left}s', font=("Sans Light", 18),
                                   fill="black")

# Inicializa as listas para perguntas, respostas e respostas corretas
questions = []
answers = []
correct_answers = []

# Inicia a leitura de RFID em uma thread separada para não bloquear a interface gráfica
threading.Thread(target=read_rfid, daemon=True).start()

# Agenda a atualização do texto RFID após 1 segundo
root.after(1000, update_rfid_label)

# Exibe a tela de descanso inicial
show_rest_screen()
