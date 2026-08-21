#include "crypto.h"
#include <openssl/rand.h>

int ideez_random_bytes(
    uint8_t *output,
    size_t output_len
) {
    if (output == NULL) {
        return 0;
    }

    if (output_len == 0 || output_len > IDEEZ_RANDOM_BYTES_MAX) {
        return 0;
    }

    if (output_len > 2147483647) {
        return 0;
    }

    return RAND_bytes(
        output,
        (int)output_len
    ) == 1;
}