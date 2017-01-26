#ifndef SNAKE_POINT_H_
#define SNAKE_POINT_H_

#include "model/Pos.h"
#include <cstdint>

/*
Point on the game map.
*/
class Point {
public:
    typedef uint32_t ValueType;

    static const ValueType MAX_VALUE = UINT32_MAX;

    enum Type {
        EMPTY,
        WALL,
        FOOD,
        SNAKE_BODY,
        SNAKE_HEAD,
        SNAKE_TAIL,
        TEST_VISIT,
        TEST_PATH
    };

    Point();
    ~Point();

    void setType(Type type_);
    void setParent(const Pos &p_);
    void setVisit(const bool v);
    void setValue(const ValueType dist_);
    Type getType() const;
    Pos getParent() const;
    bool isVisit() const;
    ValueType getValue() const;

private:
    Type type = EMPTY;
    Pos parent;
    bool visit;

    /*
    This field has different usages:
    1. When searching the shortest path, it stores the minimum distance
       to the starting point.
    2. When searching the longest path, it stores the estimated distance
       to the destination.
    3. When building a hamiltonian cycle, it stores the cycle's path index.
    */
    ValueType val;
};

#endif
