#include "biometrics.h"
#include <math.h>
#include <stddef.h>

int ideez_embedding_match(
    const float *probe,
    const float *reference,
    size_t dimension,
    float threshold,
    IdeezMatchResult *result
) {
    if (result == NULL) {
        return IDEEZ_BIOMETRICS_INVALID_INPUT;
    }

    result->valid = 0;
    result->matched = 0;
    result->similarity = 0.0f;

    if (!isfinite(threshold) || threshold < -1.0f || threshold > 1.0f) {
        return IDEEZ_BIOMETRICS_INVALID_THRESHOLD;
    }

    int status = IDEEZ_BIOMETRICS_OK;

    float similarity = ideez_cosine_similarity(
        probe,
        reference,
        dimension,
        &status
    );

    if (status != IDEEZ_BIOMETRICS_OK) {
        return status;
    }

    result->valid = 1;
    result->similarity = similarity;
    result->matched = similarity >= threshold;

    return IDEEZ_BIOMETRICS_OK;
}