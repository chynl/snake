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
    Return the number of points excluding the boundaries.
    */
    SizeType getSize() const;

    /*
    Enable testing methods.
    */
    void enableTest();

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

    /*
    Show a position on the map if the field 'testEnabled' is true.
    */
    void showPos(const Pos &p);

    /*
    Show a solution path on the map if the field 'testEnabled' is true.

    @param start The starting point of the path
    @param path  The path list
    */
    void showPath(const Pos &start, const std::list<Direction> &path);

private:
    Pos food;
    SizeType size;

    std::vector<std::vector<Point>> content;

    bool testEnabled;

    /*
    Return all empty positions.
    */
    std::vector<Pos> getEmptyPoints() const;

    /*
    Show the details of a position.

    @param p    The position
    @param type The new point type of the position
    */
    void testPos(const Pos &p, const Point::Type type);
};

#endif