// Off-target check of the stirrer control loop that cubos/firmware/panda-arduino-stirrer.patch
// adds to the PANDA Arduino firmware. Arduino.h here is a minimal host shim, and the fan is
// a first-order lag: 2600 rpm at full duty, nothing below 12 % duty, tau 0.6 s. The output
// of the run below is in sim_output.txt.
//
//   git clone https://github.com/BU-KABlab/PANDA_Arduino.git /tmp/fw && git -C /tmp/fw checkout 228615b
//   for p in p20-and-driver-status tic796-and-fast-moveto spreadcycle stirrer; do
//       git -C /tmp/fw apply "$PWD/cubos/firmware/panda-arduino-$p.patch"; done
//   D=hardware/vial-stirrer-cubxl/firmware/uno_sim
//   g++ -std=c++17 -I$D -I/tmp/fw/include $D/sim.cpp /tmp/fw/src/Stirrer.cpp -o /tmp/stirsim.bin && /tmp/stirsim.bin
#include "Arduino.h"
#include "Stirrer.h"
unsigned long sim_us = 0;
volatile uint16_t OCR1B = 0, ICR1 = 0, TCNT1 = 0;
volatile uint8_t TCCR1A = 0, TCCR1B = 0;
void (*sim_isr)() = nullptr;
SerialT Serial;
// Fan + bar: steady state 2600 rpm at full duty, nothing below 12 % duty (stiction), tau 0.6 s.
double fan = 0, phase = 0; bool jammed = false;
void run(double seconds, bool quiet = false) {
    unsigned long end = sim_us + (unsigned long)(seconds * 1e6);
    double lastPrint = sim_us / 1e6;
    while (sim_us < end) {
        sim_us += 1000;                                  // 1 ms steps
        double d = OCR1B / 625.0;
        double ss = (jammed || d < 0.12) ? 0 : 2600 * d;
        fan += (ss - fan) * 0.001 / 0.6;
        phase += fan / 60.0 * 0.001;
        if (phase >= 1.0) { phase -= 1.0; if (sim_isr) sim_isr(); }   // one falling edge per turn
        if (sim_us % 10000 == 0) updateStirrer();                       // loop() runs every ~10 ms
        if (!quiet && sim_us / 1e6 - lastPrint >= 2.0) { lastPrint = sim_us / 1e6; printf("t=%5.1f fan=%6.0f  ", lastPrint, fan); sendStirrerStatusResponse(); }
    }
}
int main() {
    setupStirrer();
    printf("-- RPM 600 from rest\n"); setStirrer(600, 0); run(30);
    printf("-- RPM 1200\n"); setStirrer(1200, 0); run(20);
    printf("-- RPM 300 for 10 s (timed)\n"); setStirrer(300, 10); run(16);
    printf("-- RPM 600, then the fan jams at t+10 s\n"); setStirrer(600, 0); run(10, true); jammed = true; run(20);
    printf("-- RPM 0 / NaN / out of range\n");
    printf("set 0 -> %.0f, set nan -> %.0f, set 5000 -> %.0f, set 20 -> %.0f\n", setStirrer(0, 0), setStirrer(NAN, 0), setStirrer(5000, 0), setStirrer(20, 0));
    setStirrer(0, 0); sendStirrerStatusResponse();
    printf("OCR1B after stop = %u, TCCR1A=0x%02x TCCR1B=0x%02x ICR1=%u\n", OCR1B, TCCR1A, TCCR1B, ICR1);
}
