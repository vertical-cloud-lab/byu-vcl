# Powering the Pi 5 on the PiPER's wrist

The Pi 5 rides on the gripper. Its power has to come about 3 to 3.5 m from a power strip at the arm's
base, up the arm, with a service loop at each joint. The lab has one supply for it so far, Raspberry
Pi's [27 W USB-C supply](https://www.raspberrypi.com/products/27w-power-supply/): 5.1 V / 5 A on a
captive 1.2 m, 17 AWG lead, from a bulky wall plug. That lead doesn't reach, and the plug can't ride
on the arm.

A lab Pi 5 has already lost its USB-C socket to a yanked cable
([#234](https://github.com/vertical-cloud-lab/byu-vcl/pull/234#issuecomment-5841723129), the CubXL
Pi). So besides getting power up the arm, the socket must never be what takes the pull.

## Why not a USB-C extension

- **At 5 V, every milliohm counts.** The Pi 5 flags under-voltage below **4.63 V**, measured after
  its input fuse. A 5.1 V supply leaves 0.47 V for everything between the supply and the board.
- **A compliant USB-C cable may drop 0.75 V on its own:** 500 mV on VBUS plus 250 mV on GND at its
  rated current ([Benson Leung](https://medium.com/@leung.benson/what-does-it-mean-when-a-usb-c-cable-is-rated-at-3a-52b4fd66385e),
  from the USB Type-C spec). Longer cables are only compliant because they use thicker wire.
- **Extensions aren't allowed by the USB-C spec.** They add length and a second mated connector
  that no cable's budget allows for. They can also pass the supply's 5 A advertisement on through a
  lead that can't carry it.
- **The Pi 5 draws about 1.5 A** streaming two cameras, and up to 2.5 A with a busy CPU and the
  fan at full speed.

[`voltage_drop.py`](voltage_drop.py) ([`voltage_drop.json`](voltage_drop.json)). Copper at 20 °C, VBUS and GND both carrying the current, 20 mΩ per mated USB-C pair:

| Route (3 to 3.5 m to the wrist) | at 1.5 A | at 2.5 A |
|---|---|---|
| Official 27 W supply alone: its 1.2 m, 17 AWG lead (too short to reach) | 5.01 V | 4.95 V |
| Official supply + 2 m USB-C extension (22 AWG, one more mated pair) | 4.66 V | 4.37 V (low) |
| Official supply + 2 m extension of a thin 3 A cable (26 AWG) | 4.18 V (low) | 3.56 V (low) |
| 5 A PD supply + one 3 m 5 A cable (20 AWG) | 4.77 V | 4.55 V (low) |
| 5 A PD supply + one 3 m 3 A cable (24 AWG) | 4.31 V (low) | 3.79 V (low) |
| 24 V up 3.5 m of 22 AWG, 5.1 V buck converter at the Pi | 5.10 V | 5.10 V (the converter sees 23.78 V; 0.9 % lost) |
| 12 V up 3.5 m of 22 AWG, 5.1 V buck converter at the Pi | 5.10 V | 5.10 V (the converter sees 11.56 V; 3.6 % lost) |

Even the best 5 V route, one continuous 3 m cable with 20 AWG conductors, sags under load. Any
extension is marginal at best.

## What people do instead: send a higher voltage and convert at the Pi

Robot integrators rarely send 5 V up an arm. They send 24 V (the arm's own tool voltage) or 48 V
Power over Ethernet, and put the 5 V converter next to the load. At 24 V the current is a fifth as
much for the same power, so the loss is a twenty-fifth. Thin, flexible wire is enough, and the
converter holds the Pi at 5.1 V whatever the lead does.

1. **24 V (or 12 V) plus a buck converter on the carrier (recommended).** Use a small 24 V supply at
   the base, and a two-core high-flex lead up the arm with the service loops. A buck converter with a
   USB-C output that advertises 5.1 V / 5 A sits on the carrier, with a 10 to 15 cm USB-C lead to
   the Pi. It's light and cheap, the Pi keeps its 5 A USB budget, and a breakaway on a two-wire DC
   lead is easy. Don't take the 24 V from the PiPER's J6 XT30: the gripper shares that 2 A.
2. **Power over Ethernet**, if the camera streams should be on a wire too. One Cat6 cable carries
   802.3at power (25.5 W at ~50 V) and gigabit Ethernet. At the base it needs a PoE+ injector or
   switch. At the Pi it needs a PoE HAT that fits a Pi 5, or an inline splitter with a USB-C output.
   It's heavier than option 1, and the RJ45 latch holds on, so a yank goes straight into the jack
   unless the cable is clamped.
3. **One continuous USB-C cable from a 5 V / 5 A supply**, no extension, 2 m at most, with 20 AWG
   (5 A, e-marked) conductors. That only works if the supply can sit within 2 m of the wrist along
   the arm, and at 3 m it's already below 4.63 V at 2.5 A (table above).

## Stopping a yank from reaching the socket

1. **Clamp the lead to the carrier** 20 to 30 mm from the plug, with slack between the clamp and the
   plug. A pull then loads the printed part, not the solder joints of the Pi's socket.
   `../sim/ccx_stress.py` checks what the carrier takes (see the main README's
   [Stress](../README.md#stress-calculix) section).
2. **Put a weak link on the arm's side of the clamp.** Use a magnetic breakaway, rated for the
   current, in the lead. The pull that separates it should sit well below what damages the socket or
   the mount. On the 24 V route this can be a two-pin magnetic DC connector, which only has to carry
   about 0.6 A.
3. **Use right-angle plugs at the Pi.** They put the plug body along the board, not sticking out
   from it, which shortens the lever a sideways pull acts through.

## Shopping list

The search through the CubXL Pi is still running; its shortlist lands here in the next commit.
