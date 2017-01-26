#ifndef SNAKE_UTIL_H_
#define SNAKE_UTIL_H_

#include <sstream>
#include <string>
#include <iomanip>
#include <cstdlib>
#include <ctime>
#include <vector>
#include <thread>

namespace util {

/*
Sleep current thread for a few milliseconds.
*/
inline void sleep(const long ms) {
    std::this_thread::sleep_for(std::chrono::milliseconds(ms));
}

/*
Convert an object to a std::string object.
*/
template<typename T>
std::string toString(const T &obj) {
    std::ostringstream oss;
    oss << std::setiosflags(std::ios::fixed) << obj;
    return oss.str();
}

/*
Swap the values of two elements.
*/
template<typename T>
void swap(T &a, T &b) {
    T tmp = a;
    a = b;
    b = tmp;
}

/*
Return a random integer in the interval [min, max].
*/
template<typename Int>
Int randInt(const Int min, const Int max) {
    return (Int)std::rand() % (max - min + 1) + min;
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

}

#endif
