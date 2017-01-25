#ifndef SNAKE_POINT_H_
#define SNAKE_POINT_H_

#include "model/Pos.h"

/*
Point on the game map.
*/
class Point {
public:
    typedef uint32_t DistType;

    static const DistType MAX_DIST = UINT32_MAX;

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
    void setDist(const DistType dist_);
    void setParent(const Pos &p_);
    void setVisit(const bool v);
    Type getType() const;
    DistType getDist() const;
    Pos getParent() const;
    bool isVisit() const;

private:
    Type type;
    bool visit;
    Pos parent;
    DistType dist;
};

#endif
