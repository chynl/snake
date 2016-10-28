#include "Snake.h"
#include "GameCtrl.h"

using std::vector;
using std::list;
using std::shared_ptr;

Snake::Snake() {
}

Snake::~Snake() {
}

bool Snake::isDead() const {
    return dead;
}

bool Snake::addBody(const Pos &p) {
    if (map && map->isInside(p)) {
        if (body.size() == 0) {  // Insert a head
            map->getPoint(p).setType(headType);
        } else {  // Insert a body
            if (body.size() > 1) {
                auto oldTail = getTail();
                map->getPoint(oldTail).setType(bodyType);
            }
            map->getPoint(p).setType(tailType);
        }
        body.push_back(p);
        return true;
    } else {
        return false;
    }
}

void Snake::setDirection(const Direc &d) {
    direc = d;
}

void Snake::setHeadType(const Point::Type &type) {
    headType = type;
}

void Snake::setBodyType(const Point::Type &type) {
    bodyType = type;
}

void Snake::setTailType(const Point::Type &type) {
    tailType = type;
}

Direc Snake::getDirection() const {
    return direc;
}

void Snake::setMap(std::shared_ptr<Map> m) {
    map = m;
}

const Pos& Snake::getHead() const {
    return *body.begin();
}

const Pos& Snake::getTail() const {
    return *body.rbegin();
}

Snake::size_type Snake::length() const {
    return body.size();
}

void Snake::removeTail() {
    if (map) {
        map->getPoint(getTail()).setType(Point::Type::EMPTY);
    }
    body.pop_back();
    if (body.size() > 1) {
        map->getPoint(getTail()).setType(tailType);
    }
}

void Snake::move() {
    if (isDead() || direc == NONE || !map) {
        return;
    }

    map->getPoint(getHead()).setType(bodyType);
    Pos newHead = getHead().getAdjPos(direc);
    body.push_front(newHead);

    if (!map->isSafe(newHead)) {
        dead = true;
    } else {
        if (map->getPoint(newHead).getType() != Point::Type::FOOD) {
            removeTail();
        } else {
            map->removeFood();
        }
    }

    map->getPoint(newHead).setType(headType);
}

void Snake::move(const std::list<Direc> &path) {
    for (const auto &d : path) {
        setDirection(d);
        move();
    }
}

void Snake::findPathTo(const int type, const Pos &to, std::list<Direc> &path) {
    // To search the path to goal, first set the goal grid type to EMPTY
    // and then start searching because the original type of the goal
    // grid may be a FOOD or another type which is ignored by the search algorithm.
    // After searching, restore the goal grid type.
    auto originType = map->getPoint(to).getType();
    map->getPoint(to).setType(Point::Type::EMPTY);
    if (type == 0) {
        map->findMinPath(getHead(), to, path);
    } else if (type == 1) {
        map->findMaxPath(getHead(), to, path);
    }
    map->getPoint(to).setType(originType);
}

void Snake::findMinPathToFood(std::list<Direc> &path) {
    findPathTo(0, map->getFood(), path);
}

void Snake::findMinPathToTail(std::list<Direc> &path) {
    findPathTo(0, getTail(), path);
}

void Snake::findMaxPathToTail(std::list<Direc> &path) {
    findPathTo(1, getTail(), path);
}

void Snake::decideNext() {
    if (isDead() || !map) {
        return;
    } else if (!map->hasFood()) {
        direc = NONE;
        return;
    }

    // Create a virtual snake
    Snake tmpSnake(*this);
    shared_ptr<Map> tmpMap = std::make_shared<Map>(*map);
    tmpSnake.setMap(tmpMap);

    list<Direc> pathToFood, pathToTail;

    // Step1:
    // If a path to food is found, move the temp snake to eat the food and to 
    // check if there is path to the tail of the temp snake. If there is no path
    // to tail after eating the food, it means that this path is dangerous and
    // will not be chosen.
    // Notice that only if the length of the path to tail is more than
    // 1 can the snake move to its tail because that the length equals
    // 1 means that the head is adjacent to the tail, which will make 
    // the snake die after moving towards the tail.
    tmpSnake.findMinPathToFood(pathToFood);
    if (!pathToFood.empty()) {
        tmpSnake.move(pathToFood);
        if (tmpMap->isAllBody()) {  // Check if the map is full
            this->setDirection(*(pathToFood.begin()));
            return;
        } else {
            tmpSnake.findMaxPathToTail(pathToTail);
            if (pathToTail.size() > 1) {
                this->setDirection(*(pathToFood.begin()));
                return;
            }
        }
    }

    // Step2:
    // If no suitable path is found in step1, make the snake move
    // to its tail along the longest path.
    this->findMaxPathToTail(pathToTail);
    if (pathToTail.size() > 1) {
        this->setDirection(*(pathToTail.begin()));
        return;
    }

    // Step3:
    // If no available path is found in step 1 and 2, then find a
    // direction that is the farthest from the food.
    auto head = getHead();
    int maxDist = -1;
    auto adjPoints = head.getAllAdjPos();
    for (const auto &p : adjPoints) {
        if (map->isSafe(p)) {
            int d = Map::estimateDist(p, map->getFood());
            if (d > maxDist) {
                maxDist = d;
                direc = head.getDirectionTo(p);
            }
        }
    }
}
