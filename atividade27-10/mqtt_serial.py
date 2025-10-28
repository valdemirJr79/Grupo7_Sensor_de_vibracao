import serial
import paho.mqtt.client as mqtt
import time
import json
import re

# =================== CONFIG ===================
serial_port = 'COM10'   # ajuste conforme sua porta
baud_rate = 115200      # mesma velocidade do seu ESP32
broker_address = "broker.hivemq.com"
broker_port = 1883
topic = "iot/sala1/vibracao"
client_id = "Python-Serial-Publisher"

# =================== CALLBACKS ===================
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Conectado ao broker MQTT!")
    else:
        print(f"❌ Falha na conexão, código: {rc}")

def on_disconnect(client, userdata, rc):
    print("🔌 Desconectado do broker MQTT!")

# =================== CLIENTE MQTT ===================
client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv311)
client.on_connect = on_connect
client.on_disconnect = on_disconnect

print("Conectando ao broker...")
client.connect(broker_address, broker_port, 60)
client.loop_start()

# =================== LOOP PRINCIPAL ===================
try:
    ser = serial.Serial(serial_port, baud_rate, timeout=1)
    print(f"📡 Porta serial {serial_port} aberta. Lendo dados...")

    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()

            # Ignora mensagens de boot do ESP32
            if not line or "ets " in line or "rst:" in line or "load:" in line or "clock" in line or "SPIWP" in line:
                continue

            print(f"📖 Dados recebidos: {line}")

            # Tenta extrair valores numéricos do texto recebido
            match = re.search(r"X:\s*(-?\d+)\s*\|\s*Y:\s*(-?\d+)\s*\|\s*Z:\s*(-?\d+)\s*\|\s*Vibração:\s*([\d.]+)", line)
            if match:
                try:
                    x = int(match.group(1))
                    y = int(match.group(2))
                    z = int(match.group(3))
                    vibracao = float(match.group(4))

                    # Monta mensagem JSON
                    payload = {
                        "X": x,
                        "Y": y,
                        "Z": z,
                        "Vibracao": vibracao
                    }

                    mensagem = json.dumps(payload)

                    # Reforça reconexão MQTT se cair
                    if not client.is_connected():
                        print("🔁 Tentando reconectar ao broker MQTT...")
                        while not client.is_connected():
                            try:
                                client.reconnect()
                                time.sleep(2)
                            except:
                                print("⚠️ Aguardando reconexão...")
                                time.sleep(3)
                        print("✅ Reconectado ao broker MQTT!")

                    # Publica no tópico
                    result = client.publish(topic, mensagem, qos=0)
                    result.wait_for_publish()
                    print(f"✅ Dados publicados com sucesso! {mensagem}")

                except Exception as e:
                    print(f"⚠️ Erro ao processar linha: {e}")

            else:
                print("⚠️ Formato não reconhecido, ignorado.")

        time.sleep(0.1)

except serial.SerialException as e:
    print(f"❌ Erro na porta serial: {e}")

except KeyboardInterrupt:
    print("\n🛑 Programa encerrado pelo usuário.")

finally:
    client.loop_stop()
    client.disconnect()
    if 'ser' in locals() and ser.is_open:
        ser.close()
    print("🔒 Conexão MQTT e porta serial fechadas.")
