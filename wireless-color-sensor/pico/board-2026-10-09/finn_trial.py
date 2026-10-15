from machine import I2C, Pin
for bus_id, sda, scl in [(0, 0, 1), (0, 4, 5), (0, 8, 9), (1, 2, 3), (1, 6, 7), (1, 10, 11)]:
    try:
        devs = I2C(bus_id, sda=Pin(sda), scl=Pin(scl)).scan()
        print(f"bus {bus_id} sda={sda} scl={scl} -> {[hex(d) for d in devs]}")
    except Exception as e:
        print(f"bus {bus_id} sda={sda} scl={scl} -> {e}")