#ifndef IDEEZ_BIOMETRICS_H
#define IDEEZ_BIOMETRICS_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

#define IDEEZ_BIOMETRICS_OK 0
#define IDEEZ_BIOMETRICS_INVALID_INPUT 1
#define IDEEZ_BIOMETRICS_INVALID_DIMENSION 2
#define IDEEZ_BIOMETRICS_ZERO_VECTOR 3
#define IDEEZ_BIOMETRICS_NONFINITE_VALUE 4
#define IDEEZ_BIOMETRICS_INVALID_THRESHOLD 5

typedef struct {
    int valid;
    int matched;
    float similarity;
} IdeezMatchResult;

int ideez_embedding_validate(
    const float *embedding,
    size_t dimension
);

float ideez_cosine_similarity(
    const float *a,
    const float *b,
    size_t dimension,
    int *status
);

int ideez_embedding_match(
    const float *probe,
    const float *reference,
    size_t dimension,
    float threshold,
    IdeezMatchResult *result
);

#ifdef __cplusplus
}
#endif

#endif