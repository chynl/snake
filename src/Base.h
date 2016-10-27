#pragma once
#ifndef BASE_H
#define BASE_H

#include <string>
#include <vector>

/*
Convert an integer to a string.
*/
std::string intToStr(const int n);

/*
Return a random number in [min, max]
*/
int random(const int min, const int max);

/*
Randomly rearrange the elements.
*/
template<typename T>
void randomChange(std::vector<T> &n) {
    for (unsigned i = 1; i < n.size(); ++i) {
        auto r = random(0, i);
        T tmp = n[i];
        n[i] = n[r];
        n[r] = tmp;
    }
}

#endif