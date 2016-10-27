#pragma once

#include "Point.h"
#include <list>
#include <queue>
#include <unordered_set>
#include <functional>

/*
Game map.
*/
class Map {
public:
    typedef std::vector<std::vector<Point>> content_type;
    typedef content_type::size_type size_type;
    typedef std::unordered_set<Pos, decltype(Pos::hash)*> hash_table;
    typedef std::priority_queue<Point, std::vector<Point>, std::greater<Point>> min_heap;

    Map(const size_type &rowCnt_, const size_type &colCnt_);
    ~Map();

    /*
    Get the point object of a given position on the map.
    */
    Point& getPoint(const Pos &p);
    const Point& getPoint(const Pos &p) const;

    /*
    Check if the position is unsafe.
    */
    bool isUnsafe(const Pos &p) const;

    /*
    Check if the position is inside the map.
    */
    bool isInside(const Pos &p) const;

    /*
    Check if the point at the position is a snake's head.
    */
    bool isHead(const Pos &p) const;

    /*
    Check if the point at the position is a snake's tail.
    */
    bool isTail(const Pos &p) const;

    /*
    Check whether the map is filled with snake body.
    */
    bool isAllBody() const;

    /*
    Get all empty positions.

    @param res the result will be stored in this field.
    */
    void getEmptyPoints(std::vector<Pos> &res) const;

    /*
    Create food at an empty position randomly.
    */
    void createRandFood();

    /*
    Create food at a given position.
    */
    void createFood(const Pos &pos);

    /*
    Remove food from the map.
    */
    void removeFood();

    /*
    Check if there is food on the map.
    */
    bool hasFood() const;

    /*
    Get food position.
    */
    const Pos& getFood() const;

    /*
    Get the amount of rows.
    */
    size_type getRowCount() const;

    /*
    Get the amount of columns.
    */
    size_type getColCount() const;

    /*
    Set whether to show the details of the search algorithms.
    */
    void setShowSearchDetails(const bool &b);

    /*
    Compute the heuristic value between two positions.

    @param from the start position
    @param to the end position
    @return the heuristic value
    */
    static Point::value_type heuristic(const Pos &from, const Pos &to);

    /*
    Find the shortest path between two positions. (BFS + A* search)

    @param from the start position
    @param to the end position
    @param path the result will be stored in this field.
    */
    void findMinPath(const Pos &from, const Pos &to, std::list<Direction> &path);

    /*
    Find the longest path between two positions. (DFS + A* search)

    @param from the start position
    @param to the end position
    @param path the result will be stored in this field.
    */
    void findMaxPath(const Pos &from, const Pos &to, std::list<Direction> &path);

private:
    content_type content;

    Pos food = Pos::INVALID;

    bool showSearchDetails = false;

    /*
    Initialize.
    */
    void init();

    /*
    Check if the position does not need to
    be visited in the searching algorithm.
    */
    bool isUnsearch(const Pos &p) const;

    /*
    Calculate the manhatten distance between two positions.

    @param from the start position
    @param to the end position
    @return the manhatten distance
    */
    static unsigned getManhattenDist(const Pos &from, const Pos &to);

    /*
    Use DFS to find the longest(approximately) path.

    @param n current position
    @param from the start position
    @param to the end position
    @param closeList stores the positions that have been visited
    @param path the result will be stored in this field
    */
    void dfsFindLongest(const Pos &n,
                        const Pos &from,
                        const Pos &to,
                        Map::hash_table &closeList,
                        std::list<Direction> &path);

    /*
    Construct the path between two positions.

    @param from the start position
    @param to the end position
    @param path the result will be stored in this field.
    */
    void constructPath(const Pos &from, const Pos &to, std::list<Direction> &path);

    /*
    Show a visited node on the map. This method is designed for
    showing search details. It first checks if showSearchDetails
    field is true.

    @param n the point of the node
    @param type the new type of the grid at the point n
    */
    void showVisitedNodeIfNeeded(const Pos &n, const Point::Type &type);

    /*
    Show the path on the map. This method is designed for
    showing search details. It first checks if showSearchDetails
    field is true.

    @param start the start point
    @param path the path to show
    */
    void showPathIfNeeded(const Pos &start, const std::list<Direction> &path);
};
