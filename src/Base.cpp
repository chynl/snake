#include "Base.h"
#include <sstream>
#include <ctime>

std::string intToStr(const int n) {
    std::ostringstream oss;
    oss << n;
    return oss.str();
}

int random(const int min, const int max) {
    static bool setSeed = true;
    if (setSeed) srand(static_cast<unsigned>(time(NULL)));
    setSeed = false;
    return rand() % (max - min + 1) + min;
}
