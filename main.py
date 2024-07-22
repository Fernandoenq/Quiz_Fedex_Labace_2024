from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

questions = {
    'en': [
        {"question": "What is the capital of France?", "options": ["Paris", "London", "Berlin", "Madrid"], "answer": "Paris"},
        {"question": "What is 2 + 2?", "options": ["3", "4", "5", "6"], "answer": "4"},
        {"question": "What is the color of the sky?", "options": ["Blue", "Green", "Red", "Yellow"], "answer": "Blue"},
        {"question": "What is the boiling point of water?", "options": ["90°C", "100°C", "110°C", "120°C"], "answer": "100°C"},
        {"question": "Who wrote '1984'?", "options": ["George Orwell", "Mark Twain", "J.K. Rowling", "Ernest Hemingway"], "answer": "George Orwell"},
    ],
    'pt': [
        {"question": "Qual é a capital da França?", "options": ["Paris", "Londres", "Berlim", "Madri"], "answer": "Paris"},
        {"question": "Quanto é 2 + 2?", "options": ["3", "4", "5", "6"], "answer": "4"},
        {"question": "Qual é a cor do céu?", "options": ["Azul", "Verde", "Vermelho", "Amarelo"], "answer": "Azul"},
        {"question": "Qual é o ponto de ebulição da água?", "options": ["90°C", "100°C", "110°C", "120°C"], "answer": "100°C"},
        {"question": "Quem escreveu '1984'?", "options": ["George Orwell", "Mark Twain", "J.K. Rowling", "Ernest Hemingway"], "answer": "George Orwell"},
    ]
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/quiz', methods=['POST'])
def quiz():
    language = request.form['language']
    return render_template('quiz.html', questions=questions[language], language=language)

@app.route('/result', methods=['POST'])
def result():
    language = request.form['language']
    selected_answers = request.form.getlist('answers')
    correct_answers = [q['answer'] for q in questions[language]]
    score = sum([1 for i in range(len(correct_answers)) if selected_answers[i] == correct_answers[i]])
    return render_template('result.html', score=score, total=len(correct_answers))

if __name__ == '__main__':
    app.run(debug=True)
