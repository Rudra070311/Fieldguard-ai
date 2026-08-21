#include "crypto.h"
#include <openssl/evp.h>

int ideez_sha256(
    const uint8_t *data,
    size_t data_len,
    uint8_t digest[IDEEZ_SHA256_DIGEST_SIZE]
) {
    if (data == NULL || digest == NULL) {
        return 0;
    }

    EVP_MD_CTX *ctx = EVP_MD_CTX_new();

    if (ctx == NULL) {
        return 0;
    }

    unsigned int digest_len = 0;

    int success =
        EVP_DigestInit_ex(ctx, EVP_sha256(), NULL) == 1 &&
        EVP_DigestUpdate(ctx, data, data_len) == 1 &&
        EVP_DigestFinal_ex(ctx, digest, &digest_len) == 1 &&
        digest_len == IDEEZ_SHA256_DIGEST_SIZE;

    EVP_MD_CTX_free(ctx);

    return success;
}