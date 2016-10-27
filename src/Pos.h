#pragma once

#include "Base.h"
#include <vector>
#include <string>

enum Direction {
    NONE,
    LEFT,
    UP,
    RIGHT,
    DOWN
};

/*
Coordinate(position) in 2D plane.
*/
class Pos {
public:
    typedef long attr_type;

    static const Pos INVALID;

    Pos(const attr_type &x_ = 0, const attr_type &y_ = 0);
    ~Pos();

    attr_type getX() const;
    attr_type getY() const;
    void setX(const attr_type &x_);
    void setY(const attr_type &y_);

    friend Pos operator+(const Pos &a, const Pos &b);
    friend bool operator==(const Pos &a, const Pos &b);
    friend bool operator!=(const Pos &a, const Pos &b);

    /*
    Hash function for a position.
    */
    static unsigned hash(const Pos &p);

    /*
    Get the direction from this position to another.

    @param p the other point
    @return the direction from this point to point p.
            If the two points are not adjacent or are
            the same, return NONE.
    */
    Direction getDirectionTo(const Pos &p) const;

    /*
    Get the adjacent position in a given direction.

    @param d the given direction
    @return the adjacent position in the given direction
    */
    Pos getAdjPos(const Direction &d) const;

    /*
    Get all adjacent positions.
    */
    std::vector<Pos> getAllAdjPos() const;

    /*
    Get the string description of the position.
    */
    std::string toString() const;

private:
    attr_type x;
    attr_type y;
};
