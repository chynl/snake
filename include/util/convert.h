#ifndef SNAKE_CONVERT_H_
#define SNAKE_CONVERT_H_

#include "internal/base.h"
#include <sstream>
#include <string>
#include <iomanip>

UTIL_NS_BEGIN

/*
Convert an object to a std::string object.
*/
template<typename T>
std::string toString(const T &obj) {
    std::ostringstream oss;
    oss << std::setiosflags(std::ios::fixed) << obj;
    return oss.str();
}

UTIL_NS_END

#endif
