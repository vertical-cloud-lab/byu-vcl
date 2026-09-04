# Wireless color sensor — verification run, 2026-09-04

Written after a challenge that earlier reports contradicted themselves. Every
number below came from the physical board on this date, and each test was run at
least three times.

Board: uid `e6647c15673a2438`, MicroPython **1.29.0 / RPI_PICO_W**, AS7341 at
`0x39` on `I2C(0, scl=GP5, sda=GP4)`.

## Two channels, not one

The confusion worth clearing up is that "SSH to the Pi" and "the board connected
to the broker" describe different links that exist at the same time:

```
CI runner --Tailscale/SSH--> Pi --USB serial--> Pico W        (control: loads and runs code)
                                                Pico W --WiFi--> HiveMQ Cloud  (data: the wireless path)
```

`board_wifi_negative_control.py` proves they are independent. With the radio off
the USB link keeps printing while the broker becomes unreachable
(`OSError(113)`, EHOSTUNREACH); with the radio back on it connects again.

## Results

Repeatability, `gain=4` (three trials per run, three separate runs):

```
chan           415    445    480    515    555    590    630    680
dark             5     17     20     44     64     75     80     52   tot=357
led_on         474   3131   3927   4026   4754   4653   5102   3843   tot=29916
dark_again       5     17     20     44     64     75     80     52   tot=357
```

Spread across all nine trials was under 0.2%, and the baseline returns to the
same value after the LED goes off.

Gain sweep — the normalised spectral shape is identical to three decimals across
gains 1, 2 and 4, which is what makes this a spectral measurement rather than
noise. It stops agreeing at gain 8 only because three channels clip:

| gain | total | note |
| --- | --- | --- |
| 1 | 3,844 | |
| 2 | 7,683 | |
| 4 | 29,916 | **use this** |
| 8 | 438,337 | saturated (driver default) |
| 16 | 438,214 | saturated |

MQTT round trip: **9/9 across three runs.** The board resolved the broker to
external addresses (`46.137.47.218`, later `52.31.149.80` — AWS eu-west-1 DNS
load balancing) and each published message came back from the broker.

## What is wrong with the deployed firmware

Three faults, all in `main.py`, none of them hardware:

1. **`sensor.LED = True` is commented out** in `read_sensor_data()`. The reading
   is therefore whatever ambient light happens to be. Sampled over 18 s it was
   stable to 0.1%, but that is a property of the room, not of the instrument.
2. **`set_color` is never defined**, and `NeoPixel` is imported but never
   instantiated. `board_neopixel_scan.py` drove all 24 usable GPIO pins and the
   sensor responded to none of them, so **no illumination source is physically
   wired** — the R/Y/B values in a command are ignored.
3. **The driver default `gain=8` saturates** once the LED is on: 555, 590 and 630
   all pin at 65535, so different samples return identical numbers. `main.py`
   passes no gain, so it gets this default.

## Scope

These tests establish that the AS7341 measures eight spectral bands correctly,
reproducibly and linearly, and that the wireless path works end to end. They do
**not** establish that the device can distinguish two different coloured samples
— that needs someone to physically put two samples in front of it, and it cannot
be done remotely. It also cannot illuminate a sample in a chosen colour until a
NeoPixel is actually wired.
