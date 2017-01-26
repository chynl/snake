#ifndef SNAKE_SNAKE_H_
#define SNAKE_SNAKE_H_

#include "model/Map.h"
#include <memory>

/*
Game snake.
*/
class Snake {
public:
    typedef Map::SizeType SizeType;

    Snake();
    ~Snake();

    void setDirection(const Direction &d);
    void setMap(std::shared_ptr<Map> m);
    Direction getDirection() const;
    bool isDead() const;

    /*
    Testing methods.
    */
    void testMinPath(const Pos &from, const Pos &to, std::list<Direction> &path);
    void testMaxPath(const Pos &from, const Pos &to, std::list<Direction> &path);

    /*
    Add a new snake body.

    @param p The position of the new bodies
    @return  True if adding succeed, false otherwise
    */
    void addBody(const Pos &p);

    /*
    Move the snake at current direction.
    */
    void move();

    /*
    Move the snake along a given path.
    */
    void move(const std::list<Direction> &path);

    /*
    Enable the snake AI based on the hamiltonian cycle.
    */
    void enableHamilton();

    /*
    Decide the next moving direction. After its execution,
    the next moving direction will be stored in field 'direc'.
    */
    void decideNext();

private:
    bool dead;
    Direction direc;

    std::list<Pos> bodies;
    std::shared_ptr<Map> map;

    bool hamiltonEnabled;

    /*
    Remove the snake tail.
    */
    void removeTail();

    /*
    Get the head position.
    */
    const Pos& getHead() const;

    /*
    Get the tail position.
    */
    const Pos& getTail() const;

    /*
    Find path between two points.

    @param path The result path will be stored in this field.
    */
    void findMinPathToFood(std::list<Direction> &path);
    void findMinPathToTail(std::list<Direction> &path);
    void findMaxPathToTail(std::list<Direction> &path);

    /*
    Find path from the snake's head to a given position.

    @param type 0->shortest path, 1->longest path
    @param to   The given position
    @param path The result path will be stored in this field.
    */
    void findPathTo(const int type, const Pos &to, std::list<Direction> &path);

    /*
    Find a shortest path as straight as possible between two positions.
    Notice that only EMPTY points are searched by the algorithm.

    @param from The starting position
    @param to   The ending position
    @param path The result will be stored in this field
    */
    void findMinPath(const Pos &from, const Pos &to, std::list<Direction> &path);

    /*
    Find a longest path as straight as possible between two positions.
    Notice that only EMPTY points are searched by the algorithm.

    @param from The starting position
    @param to   The ending position
    @param path The result will be stored in this field
    */
    void findMaxPath(const Pos &from, const Pos &to, std::list<Direction> &path);

    /*
    A recursive method called in findMaxPath().
    */
    void findMax(const Pos &curPos,
                 const Direction curDirec,
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
};

#endif
