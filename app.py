from flask import Flask, render_template, request, redirect, url_for, session
import serial
import threading
import time

app = Flask(__name__)
app.secret_key = 'supersecretkey'

arduino_port = 'COM4'  # Altere para a porta correta do seu Arduino
baud_rate = 9600
ser = serial.Serial(arduino_port, baud_rate, timeout=1)

questions = {
    'en': [
        {"question": "What is the capital of France?", "options": ["Paris", "London", "Berlin", "Madrid"],
         "answer": "Paris"},
        {"question": "What is 2 + 2?", "options": ["3", "4", "5", "6"], "answer": "4"},
        {"question": "What is the color of the sky?", "options": ["Blue", "Green", "Red", "Yellow"], "answer": "Blue"},
        {"question": "What is the boiling point of water?", "options": ["90°C", "100°C", "110°C", "120°C"],
         "answer": "100°C"},
        {"question": "Who wrote '1984'?",
         "options": ["George Orwell", "Mark Twain", "J.K. Rowling", "Ernest Hemingway"], "answer": "George Orwell"},
    ],
    'pt': [
        {"question": "Qual é a capital da França?", "options": ["Paris", "Londres", "Berlim", "Madri"],
         "answer": "Paris"},
        {"question": "Quanto é 2 + 2?", "options": ["3", "4", "5", "6"], "answer": "4"},
        {"question": "Qual é a cor do céu?", "options": ["Azul", "Verde", "Vermelho", "Amarelo"], "answer": "Azul"},
        {"question": "Qual é o ponto de ebulição da água?", "options": ["90°C", "100°C", "110°C", "120°C"],
         "answer": "100°C"},
        {"question": "Quem escreveu '1984'?",
         "options": ["George Orwell", "Mark Twain", "J.K. Rowling", "Ernest Hemingway"], "answer": "George Orwell"},
    ]
}


def read_from_port():
    if ser.is_open:
        try:
            reading = ser.readline().decode('utf-8').strip()
            if reading:
                print(f"RFID Detected: {reading}")
        except serial.SerialException as e:
            print(f"Error reading from serial port: {e}")
    threading.Timer(1, read_from_port).start()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/start', methods=['POST'])
def start():
    session['language'] = request.form['language']
    session['current_question'] = 0
    session['answers'] = []
    return redirect(url_for('question'))


@app.route('/question', methods=['GET', 'POST'])
def question():
    language = session.get('language')
    if request.method == 'POST':
        answer = request.form['answer']
        session['answers'].append(answer)
        session['current_question'] += 1

    current_question = session.get('current_question', 0)
    if current_question >= len(questions[language]):
        return redirect(url_for('result'))

    question = questions[language][current_question]
    return render_template('question.html', question=question, question_number=current_question + 1,
                           total_questions=len(questions[language]))


@app.route('/result')
def result():
    language = session.get('language')
    selected_answers = session.get('answers')
    correct_answers = [q['answer'] for q in questions[language]]
    score = sum([1 for i in range(len(correct_answers)) if selected_answers[i] == correct_answers[i]])
    return render_template('result.html', score=score, total=len(correct_answers))


if __name__ == '__main__':
    read_from_port()  # Start reading from the serial port
    app.run(debug=True)
