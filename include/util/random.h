#ifndef SNAKE_RANDOM_H_
#define SNAKE_RANDOM_H_

#include "internal/base.h"
#include "util/swap.h"
#include <cstdlib>
#include <ctime>
#include <vector>

UTIL_NS_BEGIN

/*
Return a random number in [0, 1).
*/
inline double rand() {
    static bool seeded = false;
    if (!seeded) {
        std::srand((unsigned)std::time(nullptr));
        seeded = true;
    }
    return (double)std::rand() / RAND_MAX;
}

/*
Return a random integer in the interval [min, max].
*/
template<typename Int>
Int randInt(const Int min, const Int max) {
    return (Int)(rand() * (max - min + 1) + min);
}

/*
Rearrange the elements in a vector randomly.
Reference: https://en.wikipedia.org/wiki/Fisher%E2%80%93Yates_shuffle
*/
template<typename T>
void randChange(std::vector<T> &arr) {
    if (!arr.empty()) {
        for (auto i = arr.size() - 1; i >= 1; --i) {
            swap(arr[i], arr[randInt<decltype(i)>(0, i)]);
        }
    }
}

UTIL_NS_END

#endif
