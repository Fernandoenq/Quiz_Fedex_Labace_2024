import tkinter as tk
import serial
import threading

# Configuração da porta serial
port = 'COM4'
baud_rate = 9600
rfid_data = ""
current_question = 0
current_answer = 0  # This will store the current answer
answers = []

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
                        next_question()
                    else:
                        print(f"Resposta incorreta: {rfid_data}")
                        rfid_data = ""

    except serial.SerialException as e:
        print(f"Erro na comunicação serial: {e}")


def update_rfid_label():
    global rfid_data
    if rfid_data:
        rfid_label.config(text=f"RFID Data: {rfid_data}")
    root.after(1000, update_rfid_label)


def show_question(question, possible_answers):
    for widget in frame.winfo_children():
        if widget != rfid_label:
            widget.destroy()
    question_label = tk.Label(frame, text=question, font=("Helvetica", 24))
    question_label.pack(pady=20)
    for idx, answer in enumerate(possible_answers):
        answer_button = tk.Button(frame, text=answer, font=("Helvetica", 18))
        answer_button.pack(pady=10)


def next_question():
    global current_question
    if current_question < len(questions) - 1:
        current_question += 1
        show_question(questions[current_question], answers[current_question])
    else:
        show_final_message()


def start_quiz(language):
    global questions, answers, correct_answers
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
        correct_answers = [4, 1, 4, 4, 3]  # Corrected answer indices

    show_question(questions[current_question], answers[current_question])


def show_language_selection():
    for widget in frame.winfo_children():
        widget.destroy()
    language_label = tk.Label(frame, text="Choose Language / Escolha a Língua", font=("Helvetica", 24))
    language_label.pack(pady=20)
    pt_button = tk.Button(frame, text="Português", font=("Helvetica", 18), command=lambda: start_quiz("pt"))
    pt_button.pack(pady=10)
    en_button = tk.Button(frame, text="English", font=("Helvetica", 18), command=lambda: start_quiz("en"))
    en_button.pack(pady=10)


def show_final_message():
    for widget in frame.winfo_children():
        if widget != rfid_label:
            widget.destroy()
    final_label = tk.Label(frame, text="Quiz Finished! / Quiz Finalizado!", font=("Helvetica", 24))
    final_label.pack(pady=20)


# Configuração da interface gráfica
root = tk.Tk()
root.title("RFID Quiz")
root.geometry("1080x1920")

frame = tk.Frame(root)
frame.pack(pady=20)

rfid_label = tk.Label(root, text="RFID Data: ", font=("Helvetica", 24))
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
