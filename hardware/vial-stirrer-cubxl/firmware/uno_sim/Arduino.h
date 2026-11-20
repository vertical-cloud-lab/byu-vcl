// Minimal host shim for compiling Stirrer.cpp off-target.
#pragma once
#include <cstdint>
#include <cstdio>
#include <cmath>
#define F(s) s
#define _BV(b) (1u << (b))
#define COM1B1 5
#define WGM11 1
#define WGM13 4
#define CS11 1
#define CS10 0
#define OUTPUT 1
#define INPUT_PULLUP 2
#define LOW 0
#define FALLING 2
#define constrain(a, lo, hi) ((a) < (lo) ? (lo) : ((a) > (hi) ? (hi) : (a)))
#define min(a, b) ((a) < (b) ? (a) : (b))
#define max(a, b) ((a) > (b) ? (a) : (b))
extern unsigned long sim_us;
extern volatile uint16_t OCR1B, ICR1, TCNT1;
extern volatile uint8_t TCCR1A, TCCR1B;
extern void (*sim_isr)();
inline unsigned long millis() { return sim_us / 1000; }
inline unsigned long micros() { return sim_us; }
inline void noInterrupts() {}
inline void interrupts() {}
inline void pinMode(int, int) {}
inline void digitalWrite(int, int) {}
inline int digitalPinToInterrupt(int p) { return p == 2 ? 0 : -1; }
inline void attachInterrupt(int, void (*f)(), int) { sim_isr = f; }
struct SerialT {
    char buf[256]; int n = 0;
    void print(const char* s) { n += snprintf(buf + n, sizeof buf - n, "%s", s); }
    void print(double v, int d) { n += snprintf(buf + n, sizeof buf - n, "%.*f", d, v); }
    void print(int v) { n += snprintf(buf + n, sizeof buf - n, "%d", v); }
    void print(long v) { n += snprintf(buf + n, sizeof buf - n, "%ld", v); }
    void println(const char* s) { print(s); printf("%s\n", buf); n = 0; }
};
extern SerialT Serial;
