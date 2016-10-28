#pragma once

#include "Point.h"
#include <list>

/*
Game map.
*/
class Map {
public:
    typedef std::vector<std::vector<Point>> content_type;
    typedef content_type::size_type size_type;
    typedef Point::Type point_type;

    Map(const size_type &rowCnt_, const size_type &colCnt_);
    ~Map();

    /*
    Get the point object of a given position on the map.
    */
    Point& getPoint(const Pos &p);
    const Point& getPoint(const Pos &p) const;

    /*
    Check whether the position is inside the map,
    namely not on the boundary.
    */
    bool isInside(const Pos &p) const;

    /*
    Check the type at one position.
    */
    bool isHead(const Pos &p) const;
    bool isTail(const Pos &p) const;
    bool isEmpty(const Pos &p) const;

    /*
    Check whether the position is safe.
    */
    bool isSafe(const Pos &p) const;

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
    Estimate the distance between two positions. (Manhatten distance)

    @param from the start position
    @param to the end position
    @return the estimated distance
    */
    static Point::value_type estimateDist(const Pos &from, const Pos &to);

    /*
    Find the shortest path between two positions.
    Notice that only EMPTY points are searched by the algorithm.

    @param from the start position
    @param to the end position
    @param path the result will be stored in this field.
    */
    void findMinPath(const Pos &from, const Pos &to, std::list<Direc> &path);

    /*
    Find the longest path between two positions.
    Notice that only EMPTY points are searched by the algorithm.

    @param from the start position
    @param to the end position
    @param path the result will be stored in this field.
    */
    void findMaxPath(const Pos &from, const Pos &to, std::list<Direc> &path);

private:
    content_type content;

    Pos food = Pos::INVALID;

    bool showSearchDetails = false;

    /*
    Initialize map content before searching.
    */
    void init();

    /*
    Use DFS to find the longest path.

    @param n current position
    @param from the start position
    @param to the end position
    @param path the result will be stored in this field
    */
    void findMax(const Pos &n, const Pos &from, const Pos &to, std::list<Direc> &path);

    /*
    Construct the path between two positions.

    @param from the start position
    @param to the end position
    @param path the result will be stored in this field.
    */
    void constructPath(const Pos &from, const Pos &to, std::list<Direc> &path) const;

    /*
    Show the details of a searched position.

    @param p the position
    @param t the type to be set to the point on the position
    */
    void showPosSearchDetail(const Pos &p, const point_type &t);

    /*
    Show a visited position on the map if the field 'showSearchDetails' is true.

    @param n the position of the node
    */
    void showVisitPosIfNeed(const Pos &n);

    /*
    Show a solution path on the map if the field 'showSearchDetails' is true.

    @param start the start point
    @param path the path to show
    */
    void showPathIfNeed(const Pos &start, const std::list<Direc> &path);
};
