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
    Decide the next moving direction. After its execution,
    the next moving direction will be stored in field 'direc'.
    */
    void decideNext();

private:
    bool dead;
    Direction direc;

    std::list<Pos> bodies;
    std::shared_ptr<Map> map;

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
};

#endif
