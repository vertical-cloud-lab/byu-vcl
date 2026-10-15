import time
from machine import I2C, Pin
from as7341_sensor import Sensor

# Initialize the AS7341 sensor
sensor = Sensor(i2c=I2C(0, scl=Pin(5), sda=Pin(4)))

def read_sensor_data():
  """Read dictionary of sensor data"""
  # Get all channel data from the sensor
  channel_data = sensor.all_channels

  CHANNEL_NAMES = [
      "ch410",
      "ch440",
      "ch470",
      "ch510",
      "ch550",
      "ch583",
      "ch620",
      "ch670",
  ]

  # Return a dictionary that maps channel names to sensor data
  return dict(zip(CHANNEL_NAMES, channel_data))


print("Testing sensor...")
sensor_data = read_sensor_data()
print(sensor_data)


def test_sensor():
  """Interactive testing interface for the AS7341 sensor."""
  print("AS7341 Sensor Test")
  print("==================")
  print("Type 'read' to sample data or 'exit' to quit.")

  while True:
      # Wait for a command from the user
      command = input("Command: ").strip().lower()

      if command == "read":
          # Ask whether to turn on the LED
          led_choice = input("Turn on LED for this reading? (yes/no): ").strip().lower()
          if led_choice == "yes":
              sensor.LED = True  # Turn on LED
              print("LED is ON.")

          # Trigger sensor data reading
          sensor_data = read_sensor_data()
          if sensor_data:
              print("Sensor Data:")
              for wavelength, value in sensor_data.items():
                  #print(f"{wavelength}: {value}")
                  print(f"{value}")
          else:
              print("Failed to read sensor data.")

          # Turn off the LED if it was turned on
          if led_choice == "yes":
              sensor.LED = False  # Turn off LED
              print("LED is OFF.")

      elif command == "exit":
          print("Exiting the program.")
          break
      else:
          print("Invalid command. Type 'read' to sample or 'exit' to quit.")

# Directly call the test_sensor function
test_sensor()
