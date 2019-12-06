#include "mbed.h"
#include "rtos.h"

Serial pc(USBTX, USBRX); // tx, rx

Thread thread;
DigitalOut led1(LED1);
volatile bool running = true;

void blink(DigitalOut *led) {
    while (running) {
        *led = !*led;
        wait(1);
    }
}

int main() {
     pc.printf("start\n\r");
    thread.start(callback(blink, &led1));
    wait(5);
    running = false;
    thread.join();
}