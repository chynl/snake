#ifndef SNAKE_SWAP_H_
#define SNAKE_SWAP_H_

#include "internal/base.h"

UTIL_NS_BEGIN

/*
Swap the values of two elements.
*/
template<typename T>
void swap(T &a, T &b) {
    T tmp = a;
    a = b;
    b = tmp;
}

UTIL_NS_END

#endif
