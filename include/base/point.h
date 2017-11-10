#ifndef SNAKE_POINT_H_
#define SNAKE_POINT_H_

#include "base/pos.h"
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
    void setDist(const ValueType dist_);
    void setIndex(const ValueType index_);
    Type getType() const;
    Pos getParent() const;
    bool isVisit() const;
    ValueType getDist() const;
    ValueType getIndex() const;

private:
    Type type = EMPTY;
    Pos parent;
    bool visit;
    ValueType dist;
    ValueType index;
};

#endif
