#include "crypto.h"
#include <stddef.h>

int ideez_secure_compare(
    const uint8_t *a,
    const uint8_t *b,
    size_t len
) {
    if (a == NULL || b == NULL) {
        return 0;
    }

    volatile uint8_t difference = 0;

    for (size_t i = 0; i < len; ++i) {
        difference |= (uint8_t)(a[i] ^ b[i]);
    }

    return difference == 0;
}

void ideez_secure_zero(
    void *buffer,
    size_t len
) {
    if (buffer == NULL) {
        return;
    }

    volatile uint8_t *ptr = (volatile uint8_t *)buffer;

    while (len-- > 0) {
        *ptr++ = 0;
    }
}