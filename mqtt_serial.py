import serial                      # Importa a biblioteca pySerial para comunicação via porta serial (ESP32, Arduino etc.)
import paho.mqtt.client as mqtt     # Importa a biblioteca MQTT para publicar e receber dados via broker MQTT
import time                        # Importa funções de tempo, como sleep()
import json                        # Importa o módulo para manipulação de JSON
import re                          # Importa o módulo de expressões regulares para buscar padrões em strings

# =================== CONFIG ===================
serial_port = 'COM10'               # Porta serial do seu computador conectada ao ESP32 (ajuste conforme necessário)
baud_rate = 115200                  # Velocidade de comunicação serial (deve ser igual à do ESP32)
broker_address = "broker.hivemq.com" # Endereço do broker MQTT público
broker_port = 1883                  # Porta padrão do broker MQTT
topic = "iot/sala1/vibracao"       # Tópico MQTT onde os dados serão publicados
client_id = "Python-Serial-Publisher" # Identificador único do cliente MQTT

# =================== CALLBACKS ===================
def on_connect(client, userdata, flags, rc):
    # Função chamada automaticamente quando o cliente MQTT se conecta ao broker
    if rc == 0:
        print("✅ Conectado ao broker MQTT!")  # rc = 0 significa conexão bem-sucedida
    else:
        print(f"❌ Falha na conexão, código: {rc}")  # Código diferente de 0 indica erro de conexão

def on_disconnect(client, userdata, rc):
    # Função chamada automaticamente quando o cliente MQTT se desconecta do broker
    print("🔌 Desconectado do broker MQTT!")

# =================== CLIENTE MQTT ===================
client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv311)  # Cria uma instância do cliente MQTT
client.on_connect = on_connect       # Associa a função de callback para conexão
client.on_disconnect = on_disconnect # Associa a função de callback para desconexão

print("Conectando ao broker...")
client.connect(broker_address, broker_port, 60) # Conecta ao broker MQTT com keepalive de 60s
client.loop_start()              # Inicia o loop em background do MQTT para manter a conexão ativa

# =================== LOOP PRINCIPAL ===================
try:
    ser = serial.Serial(serial_port, baud_rate, timeout=1)  # Abre a porta serial com timeout de 1 segundo
    print(f"📡 Porta serial {serial_port} aberta. Lendo dados...")

    while True:   # Loop infinito para leitura contínua de dados
        if ser.in_waiting > 0:  # Verifica se há dados disponíveis na porta serial
            line = ser.readline().decode('utf-8', errors='ignore').strip()  
            # Lê uma linha da serial, decodifica para string UTF-8 e remove espaços extras

            # Ignora mensagens de boot do ESP32 que não contêm dados de vibração
            if not line or "ets " in line or "rst:" in line or "load:" in line or "clock" in line or "SPIWP" in line:
                continue  # Pula para a próxima iteração do loop

            print(f"📖 Dados recebidos: {line}")  # Mostra os dados recebidos da serial

            # Usa expressão regular para extrair X, Y, Z e Vibração da linha recebida
            match = re.search(r"X:\s*(-?\d+\.?\d*)\s*\|\s*Y:\s*(-?\d+\.?\d*)\s*\|\s*Z:\s*(-?\d+\.?\d*)\s*\|\s*Vibração:\s*([\d\.]+)", line)
            if match:  # Se o padrão for encontrado na linha
                try:
                    x = float(match.group(1))  # Converte o valor do eixo X para float
                    y = float(match.group(2))  # Converte o valor do eixo Y para float
                    z = float(match.group(3))  # Converte o valor do eixo Z para float
                    vibracao = float(match.group(4))  # Converte o valor da vibração para float

                    payload = {          # Cria um dicionário com os dados
                        "X": x,
                        "Y": y,
                        "Z": z,
                        "Vibracao": vibracao
                    }

                    mensagem = json.dumps(payload)  # Converte o dicionário para JSON

                    # Verifica se o cliente MQTT está conectado antes de publicar
                    if not client.is_connected():
                        print("🔁 Tentando reconectar ao broker MQTT...")
                        while not client.is_connected():
                            try:
                                client.reconnect()  # Tenta reconectar
                                time.sleep(2)
                            except:
                                print("⚠️ Aguardando reconexão...")
                                time.sleep(3)
                        print("✅ Reconectado ao broker MQTT!")

                    result = client.publish(topic, mensagem, qos=0)  # Publica os dados no tópico MQTT
                    result.wait_for_publish()  # Aguarda a confirmação de publicação
                    print(f"✅ Dados publicados com sucesso! {mensagem}")

                except Exception as e:  # Captura erros de conversão ou publicação
                    print(f"⚠️ Erro ao processar linha: {e}")

            else:
                print("⚠️ Formato não reconhecido, ignorado.")  # Linha não corresponde ao formato esperado

        time.sleep(0.1)  # Pequena pausa para não sobrecarregar o loop

except serial.SerialException as e:  # Captura erro na porta serial
    print(f"❌ Erro na porta serial: {e}")

except KeyboardInterrupt:  # Captura interrupção manual pelo usuário (Ctrl+C)
    print("\n🛑 Programa encerrado pelo usuário.")

finally:  # Sempre executado, independente de erro ou interrupção
    client.loop_stop()       # Para o loop do MQTT
    client.disconnect()      # Desconecta do broker MQTT
    if 'ser' in locals() and ser.is_open:  # Se a porta serial estiver aberta
        ser.close()          # Fecha a porta serial
    print("🔒 Conexão MQTT e porta serial fechadas.")  # Confirma encerramento seguro
