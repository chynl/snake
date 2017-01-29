#ifndef SNAKE_UTIL_H_
#define SNAKE_UTIL_H_

#include <sstream>
#include <string>
#include <iomanip>
#include <ctime>
#include <thread>
#include <random>

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
Return the distance of a given index relative to the origin index in an integer cycle.

@param ori  The origin index
@param x    The given index
@param size The size of the integer cycle
*/
template<typename SizeType>
SizeType getDistance(const SizeType ori, const SizeType x, const SizeType size) {
    return ori < x ? x - ori : (x + size) - ori;
}

/*
Random number generator.
*/
template<typename RandEngine = std::default_random_engine>
class Random {
public:
    /*
    Destructor.
    */
    ~Random() {}

    /*
    Return the only instance.
    */
    static Random<>* getInstance() {
        static Random<> instance;
        return &instance;
    }

    /*
    Return a random real number in the interval [min, max).
    */
    double nextDouble(const double min = 0, const double max = 1) {
        return std::uniform_real_distribution<double>(min, max)(engine);
    }

    /*
    Return a random integer in the interval [min, max].
    */
    template<typename Integer>
    Integer nextInt(const Integer min, const Integer max) {
        return std::uniform_int_distribution<Integer>(min, max)(engine);
    }

    /*
    Shuffle the elements in an array randomly.
    Reference: https://en.wikipedia.org/wiki/Fisher%E2%80%93Yates_shuffle.

    @param beg The iterator of the first element
    @param end The iterator of the element after the last element
    */
    template<typename RanIt>
    void shuffle(RanIt beg, RanIt end) {
        if (end - beg > 1) {
            std::size_t i = end - beg - 1;
            for (RanIt it = end - 1; it != beg; --it, --i) {
                swap(*it, *(beg + nextInt<decltype(i)>(0, i)));
            }
        }
    }
private:
    RandEngine engine;

    /*
    Initialize.
    */
    Random() : engine((unsigned)std::time(nullptr)) {}
};

}

#endif
