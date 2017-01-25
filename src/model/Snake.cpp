#include "model/Snake.h"
#include "GameCtrl.h"

using std::vector;
using std::list;
using std::shared_ptr;

Snake::Snake() : dead(false), direc(NONE) {}

Snake::~Snake() {}

void Snake::setDirection(const Direction &d) {
    direc = d;
}

void Snake::setMap(std::shared_ptr<Map> m) {
    map = m;
}

Direction Snake::getDirection() const {
    return direc;
}

bool Snake::isDead() const {
    return dead;
}

void Snake::addBody(const Pos &p) {
    if (map && map->isInside(p)) {
        if (bodies.size() == 0) {  // Insert a head
            map->getPoint(p).setType(Point::Type::SNAKE_HEAD);
        } else {  // Insert a body
            if (bodies.size() > 1) {
                const Pos &oldTail = getTail();
                map->getPoint(oldTail).setType(Point::Type::SNAKE_BODY);
            }
            map->getPoint(p).setType(Point::Type::SNAKE_TAIL);
        }
        bodies.push_back(p);
    }
}

const Pos& Snake::getHead() const {
    return *bodies.begin();
}

const Pos& Snake::getTail() const {
    return *bodies.rbegin();
}

void Snake::removeTail() {
    if (map) {
        map->getPoint(getTail()).setType(Point::Type::EMPTY);
    }
    bodies.pop_back();
    if (bodies.size() > 1) {
        map->getPoint(getTail()).setType(Point::Type::SNAKE_TAIL);
    }
}

void Snake::move() {
    if (isDead() || direc == NONE || !map) {
        return;
    }
    map->getPoint(getHead()).setType(Point::Type::SNAKE_BODY);
    Pos newHead = getHead().getAdj(direc);
    bodies.push_front(newHead);
    if (!map->isSafe(newHead)) {
        dead = true;
    } else {
        if (map->getPoint(newHead).getType() != Point::Type::FOOD) {
            removeTail();
        } else {
            map->removeFood();
        }
    }
    map->getPoint(newHead).setType(Point::Type::SNAKE_HEAD);
}

void Snake::move(const std::list<Direction> &path) {
    for (const Direction &d : path) {
        setDirection(d);
        move();
    }
}

void Snake::findPathTo(const int type, const Pos &to, std::list<Direction> &path) {
    Point::Type oriType = map->getPoint(to).getType();
    map->getPoint(to).setType(Point::Type::EMPTY);
    if (type == 0) {
        map->findMinPath(getHead(), to, direc, path);
    } else if (type == 1) {
        map->findMaxPath(getHead(), to, direc, path);
    }
    map->getPoint(to).setType(oriType);  // Retore point type
}

void Snake::findMinPathToFood(std::list<Direction> &path) {
    findPathTo(0, map->getFood(), path);
}

void Snake::findMinPathToTail(std::list<Direction> &path) {
    findPathTo(0, getTail(), path);
}

void Snake::findMaxPathToTail(std::list<Direction> &path) {
    findPathTo(1, getTail(), path);
}

void Snake::decideNext() {
    if (isDead() || !map) {
        return;
    } else if (!map->hasFood()) {
        direc = NONE;
        return;
    }
    list<Direction> pathToFood, pathToTail;
    // Create a virtual snake
    Snake tmpSnake(*this);
    shared_ptr<Map> tmpMap = std::make_shared<Map>(*map);
    tmpSnake.setMap(tmpMap);
    // Step 1
    tmpSnake.findMinPathToFood(pathToFood);
    if (!pathToFood.empty()) {
        // Step 2
        tmpSnake.move(pathToFood);
        if (tmpMap->isAllBody()) {
            this->setDirection(*(pathToFood.begin()));
            return;
        } else {
            // Step 3
            tmpSnake.findMaxPathToTail(pathToTail);
            if (pathToTail.size() > 1) {
                this->setDirection(*(pathToFood.begin()));
                return;
            }
        }
    }
    // Step 4
    this->findMaxPathToTail(pathToTail);
    if (pathToTail.size() > 1) {
        this->setDirection(*(pathToTail.begin()));
        return;
    }
    // Step 5
    Pos head = getHead();
    SizeType max = 0;
    vector<Pos> adjPositions = head.getAllAdj();
    for (const Pos &adjPos : adjPositions) {
        if (map->isSafe(adjPos)) {
            SizeType dist = Map::distance(adjPos, map->getFood());
            if (dist >= max) {
                max = dist;
                direc = head.getDirectionTo(adjPos);
            }
        }
    }
}
