#ifndef SNAKE_POS_H
#define SNAKE_POS_H

#include "base/direction.h"
#include <vector>
#include <string>
#include <cstddef>

/*
Integer coordinate in 2D plane.
*/
class Pos {
public:
    typedef std::size_t SizeType;

public:
    Pos(const SizeType x_ = 0, const SizeType y_ = 0);
    ~Pos();

    SizeType getX() const;
    SizeType getY() const;
    void setX(const SizeType x_);
    void setY(const SizeType y_);

    friend Pos operator+(const Pos &a, const Pos &b);
    friend bool operator==(const Pos &a, const Pos &b);
    friend bool operator!=(const Pos &a, const Pos &b);

    std::string toString() const;

    /*
    Return the direction of a given position reletive to this
    position. If the given position is not adjacent to this
    position, return Direction::NONE.

    @param p The given position
    */
    Direction getDirectionTo(const Pos &p) const;

    /*
    Return the adjacent position at a given direction. If there
    is no valid position at the given direction, return current position.

    @param d The given direction
    */
    Pos getAdj(const Direction d) const;

    /*
    Return all adjacent positions.
    */
    std::vector<Pos> getAllAdj() const;

private:
    SizeType x;
    SizeType y;
};

#endif
