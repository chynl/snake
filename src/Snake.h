#pragma once

#include "Map.h"
#include <memory>

/*
Game snake.
*/
class Snake {
public:
    typedef Map::size_type size_type;

    Snake();
    ~Snake();

    /*
    Move the snake at current direction.
    */
    void move();

    /*
    Move the snake according to a given path.
    */
    void move(const std::list<Direction> &path);

    /*
    Check whether the snake is dead.
    */
    bool isDead() const;

    /*
    Add a new snake body.

    @param p the position of the new body
    @return true if adding succeed, false otherwise
    */
    bool addBody(const Pos &p);

    /*
    Get the length of the snake.
    */
    size_type length() const;

    /*
    Decide next move direction. (result will be stored in direc field)
    */
    void decideNext();

    // Getters and setters
    void setDirection(const Direction &d);
    void setHeadType(const Point::Type &type);
    void setBodyType(const Point::Type &type);
    void setTailType(const Point::Type &type);
    void setMap(std::shared_ptr<Map> m);
    Direction getDirection() const;

private:
    bool dead = false;
    Direction direc = NONE;

    std::list<Pos> body;
    std::shared_ptr<Map> map;

    Point::Type headType;
    Point::Type bodyType;
    Point::Type tailType;

    /*
    Find path between two points.

    @param path the result will be stored in this field.
    */
    void findMinPathToFood(std::list<Direction> &path);
    void findMinPathToTail(std::list<Direction> &path);
    void findMaxPathToTail(std::list<Direction> &path);

    /*
    Find a path from the snake's head to the goal point.

    @param type 0->find shortest path
                1->find longest path
    @param to the goal point
    @param path the result will be stored in this field.
    */
    void findPathTo(const int type, const Pos &to, std::list<Direction> &path);

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
};
