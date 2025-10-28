#include <Wire.h>

#define ADXL345_ADDRESS 0x53
#define REG_POWER_CTL 0x2D
#define POWER_CTL_MEASURE_MODE 0x08
#define REG_DATAX0 0x32
#define REG_DATAY0 0x34
#define REG_DATAZ0 0x36

void setup() {
  Serial.begin(115200);
  Wire.begin();

  // Inicializa o sensor ADXL345
  Wire.beginTransmission(ADXL345_ADDRESS);
  Wire.write(REG_POWER_CTL);
  Wire.write(POWER_CTL_MEASURE_MODE);
  Wire.endTransmission();

  Serial.println("📟 Sensor ADXL345 iniciado com sucesso!");
}

void loop() {
  int16_t x, y, z;

  // Lê os eixos
  x = read16(REG_DATAX0);
  y = read16(REG_DATAY0);
  z = read16(REG_DATAZ0);

  // Calcula o valor de "vibração" (magnitude)
  float vibracao = sqrt(x * x + y * y + z * z);

  // Exibe os valores
  Serial.print("X: ");
  Serial.print(x);
  Serial.print(" | Y: ");
  Serial.print(y);
  Serial.print(" | Z: ");
  Serial.print(z);
  Serial.print(" | Vibração: ");
  Serial.println(vibracao, 2);

  delay(500); // taxa de leitura (a cada 0,5 segundo)
}

int16_t read16(byte reg) {
  Wire.beginTransmission(ADXL345_ADDRESS);
  Wire.write(reg);
  Wire.endTransmission(false);
  Wire.requestFrom(ADXL345_ADDRESS, 2);
  byte low = Wire.read();
  byte high = Wire.read();
  return (int16_t)((high << 8) | low);
}
