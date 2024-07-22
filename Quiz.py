import serial

# Configure a porta serial. Certifique-se de que a porta está correta
# No Windows, pode ser algo como 'COM3', 'COM4', etc.
port = 'COM4'
baud_rate = 9600

def read_rfid():
    try:
        with serial.Serial(port, baud_rate, timeout=1) as ser:
            while True:
                if ser.in_waiting > 0:
                    rfid_data = ser.readline().decode('utf-8').strip()
                    cleaned_rfid_data = rfid_data.replace(" ", "").upper()
                    print(cleaned_rfid_data)

                    if(cleaned_rfid_data == "UIDTAG:0429D495BE2A81"):
                      print("Resposta 1")

                    elif(cleaned_rfid_data == "UIDTAG:0448CD95BE2A81"):
                      print("Resposta 2")

                    elif (cleaned_rfid_data == "UIDTAG:0417DA95BE2A81"):
                      print("Resposta 3")

                    elif (cleaned_rfid_data == "UIDTAG:04FFDF95BE2A81"):
                      print("Resposta 4")

    except serial.SerialException as e:
        print(f"Erro na comunicação serial: {e}")

if __name__ == "__main__":
    read_rfid()
