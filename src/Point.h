#pragma once

#include "Pos.h"

/*
Point on the game map.
*/
class Point {
public:
    typedef int value_type;

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
    void setDist(const value_type dist_);
    void setParent(const Pos &p_);
    void setVisit(const bool v);
    Type getType() const;
    value_type getDist() const;
    Pos getParent() const;
    bool isVisit() const;

private:
    Type type = EMPTY;

    // Fields for grpah seaching algorithm
    bool visit = false;
    value_type dist = INF;
    Pos parent = Pos::INVALID;
};
