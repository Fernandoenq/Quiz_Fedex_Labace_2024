from flask import Flask, jsonify, render_template, request
import serial
import threading

app = Flask(__name__)

# Configure a porta serial
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
                    cleaned_rfid_data = rfid_data.replace(" ", "").upper()
                    print(cleaned_rfid_data)

                    if (cleaned_rfid_data == "UIDTAG:0429D495BE2A81"):
                        print("Resposta 1")

                    elif (cleaned_rfid_data == "UIDTAG:0448CD95BE2A81"):
                        print("Resposta 2")

                    elif (cleaned_rfid_data == "UIDTAG:0417DA95BE2A81"):
                        print("Resposta 3")

                    elif (cleaned_rfid_data == "UIDTAG:04FFDF95BE2A81"):
                        print("Resposta 4")

    except serial.SerialException as e:
        print(f"Erro na comunicação serial: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_rfid')
def get_rfid():
    global rfid_data
    return jsonify({"rfid_data": rfid_data})

if __name__ == "__main__":
    threading.Thread(target=read_rfid, daemon=True).start()
    app.run(debug=True)
