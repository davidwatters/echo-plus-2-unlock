#include "common.h"
#include "debug.h"

void (*send_usb_response)(int, int, int) = (void*)0x6C7D;
int (*send_dword)() = (void*)0xD1FF;
int (*recv_dword)() = (void*)0xD1CB;
int (*send_data)() = (void*)0xD2C7;
int (*recv_data)() = (void*)0xD241;