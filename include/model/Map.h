#ifndef SNAKE_MAP_H_
#define SNAKE_MAP_H_

#include "model/Point.h"
#include <list>

/*
Game map.
*/
class Map {
public:
    typedef Pos::SizeType SizeType;

    Map(const SizeType rowCnt_, const SizeType colCnt_);
    ~Map();

    Point& getPoint(const Pos &p);
    const Point& getPoint(const Pos &p) const;

    SizeType getRowCount() const;
    SizeType getColCount() const;

    /*
    Check the state of the map.
    */
    bool isInside(const Pos &p) const;
    bool isHead(const Pos &p) const;
    bool isTail(const Pos &p) const;
    bool isEmpty(const Pos &p) const;
    bool isSafe(const Pos &p) const;
    bool isAllBody() const;

    /*
    Food API.
    */
    void createRandFood();
    void createFood(const Pos &pos);
    void removeFood();
    bool hasFood() const;
    const Pos& getFood() const;

    /*
    Return the manhatten distance between two positions.

    @param from The starting position
    @param to   The ending position
    @return     The manhatten distance
    */
    static SizeType distance(const Pos &from, const Pos &to);

private:
    Pos food;

    std::vector<std::vector<Point>> content;

    /*
    Return all empty positions.
    */
    std::vector<Pos> getEmptyPoints() const;
};

#endif