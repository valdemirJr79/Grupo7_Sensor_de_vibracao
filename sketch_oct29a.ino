#include <Wire.h>  
// Inclui a biblioteca Wire, que permite comunicação I2C (necessária para o ADXL345)

#define ADXL345_ADDRESS 0x53  
// Endereço I2C padrão do sensor ADXL345

#define REG_POWER_CTL 0x2D  
// Registro de controle de energia do ADXL345

#define POWER_CTL_MEASURE_MODE 0x08  
// Valor para colocar o sensor no modo de medição (ativa leitura de aceleração)

#define REG_DATAX0 0x32  
#define REG_DATAY0 0x34  
#define REG_DATAZ0 0x36  
// Endereços dos registradores de dados brutos dos eixos X, Y e Z (cada eixo ocupa 2 bytes)

void setup() {
  Serial.begin(115200);  
  // Inicializa a comunicação serial com o computador para envio de dados

  Wire.begin();  
  // Inicializa a comunicação I2C

  // Inicializa o sensor ADXL345 colocando-o em modo de medição
  Wire.beginTransmission(ADXL345_ADDRESS);  // Inicia comunicação com o endereço do sensor
  Wire.write(REG_POWER_CTL);                // Seleciona o registro de controle de energia
  Wire.write(POWER_CTL_MEASURE_MODE);      // Escreve valor para ativar modo de medição
  Wire.endTransmission();                   // Envia os dados e termina a transmissão

  Serial.println("Sensor ADXL345 iniciado com sucesso!");  
  // Confirma que o sensor foi inicializado
}

void loop() {
  int16_t xRaw = read16(REG_DATAX0);  
  int16_t yRaw = read16(REG_DATAY0);  
  int16_t zRaw = read16(REG_DATAZ0);  
  // Lê os valores brutos de cada eixo (16 bits) usando a função read16()

  // Converte valores brutos para G (considerando ±16G, cada unidade = 0.0039 G)
  float x = xRaw * 0.0039;  
  float y = yRaw * 0.0039;  
  float z = zRaw * 0.0039;  

  // Calcula a magnitude total da aceleração (sqrt(x² + y² + z²))
  float vibracao = sqrt(x * x + y * y + z * z);

  // Envia os valores para a porta serial no mesmo formato que o Python espera
  Serial.print("X: ");  
  Serial.print(x, 2);  
  Serial.print(" | Y: ");  
  Serial.print(y, 2);  
  Serial.print(" | Z: ");  
  Serial.print(z, 2);  
  Serial.print(" | Vibração: ");  
  Serial.println(vibracao, 2);  
  // Cada valor é enviado com 2 casas decimais

  delay(500);  
  // Pausa de 500ms entre leituras (taxa de 2 leituras por segundo)
}

// Função para ler 16 bits (2 bytes) de um registrador do ADXL345
int16_t read16(byte reg) {
  Wire.beginTransmission(ADXL345_ADDRESS);  
  // Inicia comunicação com o sensor
  Wire.write(reg);  
  // Seleciona o registrador a ser lido
  Wire.endTransmission(false);  
  // Envia a requisição sem liberar o barramento (requerido para leitura I2C)
  Wire.requestFrom(ADXL345_ADDRESS, 2);  
  // Solicita 2 bytes de dados do sensor
  byte low = Wire.read();  
  byte high = Wire.read();  
  // Lê os bytes baixo e alto
  return (int16_t)((high << 8) | low);  
  // Combina os bytes em um valor de 16 bits com sinal
}
