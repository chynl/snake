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
    Set whether to show the details of the searching algorithms.
    */
    void setShowDetail(const bool show);

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
    Find a shortest path as straight as possible between two positions.
    Notice that only EMPTY points are searched by the algorithm.

    @param from  The starting position
    @param to    The ending position
    @param direc The expected searching direction
    @param path  The result will be stored in this field
    */
    void findMinPath(const Pos &from, const Pos &to, const Direction direc, std::list<Direction> &path);

    /*
    Find a longest path as straight as possible between two positions.
    Notice that only EMPTY points are searched by the algorithm.

    @param from  The starting position
    @param to    The ending position
    @param direc The expected searching direction
    @param path  The result will be stored in this field
    */
    void findMaxPath(const Pos &from, const Pos &to, const Direction direc, std::list<Direction> &path);

private:
    std::vector<std::vector<Point>> content;

    Pos food;

    bool showDetail;

    /*
    Return all empty positions.
    */
    std::vector<Pos> getEmptyPoints() const;

    /*
    A recursive method called in findMaxPath().
    */
    void findMax(const Pos &curPos,
                 const Direction &curDirec,
                 const Pos &from,
                 const Pos &to,
                 std::list<Direction> &path);

    /*
    Construct the path between two positions.

    @param from The start position
    @param to   The end position
    @param path The result will be stored in this field.
    */
    void constructPath(const Pos &from, const Pos &to, std::list<Direction> &path) const;

    /*
    Show the details of a searched position.

    @param p    The position
    @param type The new point type of the position
    */
    void showPos(const Pos &p, const Point::Type type);

    /*
    Show a visited position on the map if the field 'showDetail' is true.
    */
    void showVisitPos(const Pos &p);

    /*
    Show a solution path on the map if the field 'showDetail' is true.

    @param start The starting point of the path
    @param path  The path
    */
    void showPath(const Pos &start, const std::list<Direction> &path);
};

#endif