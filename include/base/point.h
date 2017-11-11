#ifndef SNAKE_POINT_H
#define SNAKE_POINT_H

#include "base/pos.h"
#include <cstdint>

/*
Point on the game map.
*/
class Point {
public:
    typedef uint32_t ValueType;

    static const ValueType MAX_VALUE;
    static const ValueType EMPTY_DIST;

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

public:
    Point();
    ~Point();

    void setType(Type type_);
    void setParent(const Pos &p_);
    void setVisit(const bool v);
    void setDist(const ValueType dist_);
    void setIdx(const ValueType index_);
    Type getType() const;
    Pos getParent() const;
    bool isVisit() const;
    ValueType getDist() const;
    ValueType getIdx() const;

private:
    Type type = EMPTY;
    Pos parent;
    bool visit;
    ValueType dist;
    ValueType idx;
};

#endif
