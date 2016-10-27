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
        SNAKEBODY,
        SNAKEHEAD,
        SNAKETAIL,
    };

    Point();
    ~Point();

    void setType(Type type_);
    void setG(const value_type g_);
    void setH(const value_type h_);
    void setParent(const Pos &p_);
    void setPos(const Pos &p);
    Type getType() const;
    value_type getG() const;
    value_type getH() const;
    Pos getParent() const;
    Pos getPos() const;
    value_type getF() const;  // f = g + h

    // Operators comparing by f value
    friend bool operator<(const Point &a, const Point &b);
    friend bool operator>(const Point &a, const Point &b);
    friend bool operator<=(const Point &a, const Point &b);
    friend bool operator>=(const Point &a, const Point &b);

private:
    Type type = EMPTY;
    value_type g = 0;
    value_type h = 0;
    Pos parent = Pos::INVALID;
    Pos pos = Pos::INVALID;
};
