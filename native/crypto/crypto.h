#ifndef IDEEZ_CRYPTO_H
#define IDEEZ_CRYPTO_H

#include <stddef.h>
#include <stdint.h>

#define IDEEZ_SHA256_DIGEST_SIZE 32
#define IDEEZ_RANDOM_BYTES_MAX 4096

int ideez_sha256(
    const uint8_t *data,
    size_t data_len,
    uint8_t digest[IDEEZ_SHA256_DIGEST_SIZE]
);

int ideez_random_bytes(
    uint8_t *output,
    size_t output_len
);

int ideez_secure_compare(
    const uint8_t *a,
    const uint8_t *b,
    size_t len
);

void ideez_secure_zero(
    void *buffer,
    size_t len
);

#endif