#define trigPin 13
#define echoPin 12


void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  long duration, distance;

  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  duration = pulseIn(echoPin, HIGH);
  // convert distance to mm
  distance = duration/2/2.91;

  Serial.print("distance_mm:");
  Serial.print(distance);
  Serial.print(",duration_micros:");
  Serial.print(duration);
  Serial.print(",");
  Serial.println();

  delay(50);
}
