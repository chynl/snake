#ifndef SNAKE_MAP_H
#define SNAKE_MAP_H

#include "base/point.h"
#include <list>

/*
Game map.
*/
class Map {
public:
    typedef Pos::SizeType SizeType;

public:
    Map(const SizeType rowCnt_, const SizeType colCnt_);
    ~Map();

    Point& getPoint(const Pos &p);
    const Point& getPoint(const Pos &p) const;

    SizeType getRowCount() const;
    SizeType getColCount() const;

    bool isInside(const Pos &p) const;
    bool isEmpty(const Pos &p) const;
    bool isEmptyNotVisit(const Pos &p) const;
    bool isSafe(const Pos &p) const;
    bool isAllBody() const;

    void createRandFood();
    void createFood(const Pos &pos);
    void removeFood();
    bool hasFood() const;
    const Pos& getFood() const;

    void setTestEnabled(const bool e);
    bool isTestEnabled() const;
    void showTestPos(const Pos &p);
    void showTestPath(const Pos &start, const std::list<Direction> &path);

    /*
    Return the number of points in the map excluding the boundaries.
    */
    SizeType getSize() const;

    /*
    Return the manhatten distance between two positions.

    @param from The starting position
    @param to   The ending position
    @return     The manhatten distance
    */
    static SizeType distance(const Pos &from, const Pos &to);

private:
    std::vector<Pos> getEmptyPoints() const;

    void setPointTypeWithDelay(const Pos &p, const Point::Type type);

private:
    bool testEnabled = false;
    Pos food;
    SizeType size;
    std::vector<std::vector<Point>> content;
};

#endif
