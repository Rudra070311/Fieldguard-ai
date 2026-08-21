#include "biometrics.h"
#include <math.h>
#include <stddef.h>

int ideez_embedding_validate(
    const float *embedding,
    size_t dimension
) {
    if (embedding == NULL) {
        return IDEEZ_BIOMETRICS_INVALID_INPUT;
    }

    if (dimension == 0) {
        return IDEEZ_BIOMETRICS_INVALID_DIMENSION;
    }

    for (size_t i = 0; i < dimension; ++i) {
        if (!isfinite(embedding[i])) {
            return IDEEZ_BIOMETRICS_NONFINITE_VALUE;
        }
    }

    return IDEEZ_BIOMETRICS_OK;
}

float ideez_cosine_similarity(
    const float *a,
    const float *b,
    size_t dimension,
    int *status
) {
    if (status == NULL) {
        return 0.0f;
    }

    *status = ideez_embedding_validate(a, dimension);

    if (*status != IDEEZ_BIOMETRICS_OK) {
        return 0.0f;
    }

    *status = ideez_embedding_validate(b, dimension);

    if (*status != IDEEZ_BIOMETRICS_OK) {
        return 0.0f;
    }

    double dot = 0.0;
    double norm_a = 0.0;
    double norm_b = 0.0;

    for (size_t i = 0; i < dimension; ++i) {
        const double va = (double)a[i];
        const double vb = (double)b[i];

        dot += va * vb;
        norm_a += va * va;
        norm_b += vb * vb;
    }

    if (norm_a <= 0.0 || norm_b <= 0.0) {
        *status = IDEEZ_BIOMETRICS_ZERO_VECTOR;
        return 0.0f;
    }

    double similarity =
        dot / (sqrt(norm_a) * sqrt(norm_b));

    if (similarity > 1.0) {
        similarity = 1.0;
    } else if (similarity < -1.0) {
        similarity = -1.0;
    }

    return (float)similarity;
}