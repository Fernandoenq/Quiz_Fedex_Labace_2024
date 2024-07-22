import tkinter as tk
from tkinter import messagebox
import serial
import threading

# Configuração da porta serial
port = 'COM4'
baud_rate = 9600
rfid_data = ""

def read_rfid():
    global rfid_data
    try:
        with serial.Serial(port, baud_rate, timeout=1) as ser:
            while True:
                if ser.in_waiting > 0:
                    rfid_data = ser.readline().decode('utf-8').strip()
                    print(f"Tag RFID detectada: {rfid_data}")
                    rfid_data = rfid_data.replace(" ", "").upper()
                    print(rfid_data)

                    if (rfid_data == "UIDTAG:0429D495BE2A81"):
                        print("Resposta 1")
                        rfid_data = "Resposta 1"

                    elif (rfid_data == "UIDTAG:0448CD95BE2A81"):
                        print("Resposta 2")
                        rfid_data = "Resposta 2"

                    elif (rfid_data == "UIDTAG:0417DA95BE2A81"):
                        print("Resposta 3")
                        rfid_data = "Resposta 3"

                    elif (rfid_data == "UIDTAG:04FFDF95BE2A81"):
                        print("Resposta 4")
                        rfid_data = "Resposta 4"

    except serial.SerialException as e:
        print(f"Erro na comunicação serial: {e}")

def update_rfid_label():
    global rfid_data
    if rfid_data:
        rfid_label.config(text=f"RFID Data: {rfid_data}")
    root.after(1000, update_rfid_label)

def show_question(question, answers):
    for widget in frame.winfo_children():
        if widget != rfid_label:
            widget.destroy()
    question_label = tk.Label(frame, text=question, font=("Helvetica", 24))
    question_label.pack(pady=20)
    for answer in answers:
        answer_button = tk.Button(frame, text=answer, font=("Helvetica", 18), command=lambda: next_question())
        answer_button.pack(pady=10)

def next_question():
    global current_question
    current_question = (current_question + 1) % len(questions)
    show_question(questions[current_question], answers[current_question])

# Configuração da interface gráfica
root = tk.Tk()
root.title("RFID Quiz")
root.geometry("1080x1920")

frame = tk.Frame(root)
frame.pack(pady=20)

rfid_label = tk.Label(frame, text="RFID Data: ", font=("Helvetica", 24))
rfid_label.pack(pady=10)

# Lista de perguntas e respostas
questions = [
    "Pergunta 1: Qual é a cor do céu?",
    "Pergunta 2: Qual é a capital da França?",
    "Pergunta 3: Qual é 2 + 2?",
    "Pergunta 4: Qual é o maior oceano do mundo?",
    "Pergunta 5: Qual é a velocidade da luz?"
]

answers = [
    ["Azul", "Verde", "Vermelho", "Amarelo", "Preto"],
    ["Londres", "Berlim", "Paris", "Madrid", "Roma"],
    ["1", "2", "3", "4", "5"],
    ["Atlântico", "Índico", "Ártico", "Antártico", "Pacífico"],
    ["300 km/s", "300,000 km/s", "150,000 km/s", "100,000 km/s", "50,000 km/s"]
]

current_question = 0

# Iniciar a leitura do RFID em um thread separado
threading.Thread(target=read_rfid, daemon=True).start()

# Atualizar o rótulo de RFID periodicamente
root.after(1000, update_rfid_label)

# Mostrar a primeira pergunta
show_question(questions[current_question], answers[current_question])

root.mainloop()
