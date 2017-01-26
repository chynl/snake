#include "model/Snake.h"
#include "util/util.h"
#include <queue>
#include <algorithm>

using std::vector;
using std::list;
using std::shared_ptr;
using std::queue;

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

void Snake::testMinPath(const Pos &from, const Pos &to, std::list<Direction> &path) {
    map->enableTest();
    findMinPath(from, to, path);
}

void Snake::testMaxPath(const Pos &from, const Pos &to, std::list<Direction> &path) {
    map->enableTest();
    findMaxPath(from, to, path);
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

void Snake::findMinPathToFood(list<Direction> &path) {
    findPathTo(0, map->getFood(), path);
}

void Snake::findMinPathToTail(list<Direction> &path) {
    findPathTo(0, getTail(), path);
}

void Snake::findMaxPathToTail(list<Direction> &path) {
    findPathTo(1, getTail(), path);
}

void Snake::findPathTo(const int pathType, const Pos &goal, list<Direction> &path) {
    Point::Type oriType = map->getPoint(goal).getType();
    map->getPoint(goal).setType(Point::Type::EMPTY);
    if (pathType == 0) {
        findMinPath(getHead(), goal, path);
    } else if (pathType == 1) {
        findMaxPath(getHead(), goal, path);
    }
    map->getPoint(goal).setType(oriType);  // Retore point type
}

void Snake::findMinPath(const Pos &from, const Pos &to, list<Direction> &path) {
    // Init
    SizeType row = map->getRowCount(), col = map->getColCount();
    for (SizeType i = 1; i < row - 1; ++i) {
        for (SizeType j = 1; j < col - 1; ++j) {
            map->getPoint(Pos(i, j)).setValue(Point::MAX_VALUE);
        }
    }
    path.clear();
    map->getPoint(from).setValue(0);
    queue<Pos> openList;
    openList.push(from);
    // BFS
    while (!openList.empty()) {
        const Pos curPos = openList.front();
        const Point &curPoint = map->getPoint(curPos);
        openList.pop();
        map->showPos(curPos);
        if (curPos == to) {
            constructPath(from, to, path);
            map->showPath(from, path);
            break;
        }
        // Arrange the order of traversing to make the result path as straight as possible
        vector<Pos> adjPositions = curPos.getAllAdj();
        Direction bestDirec = (curPos == from ? direc : curPoint.getParent().getDirectionTo(curPos));
        for (SizeType i = 0; i < adjPositions.size(); ++i) {
            if (bestDirec == curPos.getDirectionTo(adjPositions[i])) {
                util::swap(adjPositions[0], adjPositions[i]);
                break;
            }
        }
        // Traverse the adjacent positions
        for (const Pos &adjPos : adjPositions) {
            Point &adjPoint = map->getPoint(adjPos);
            if (map->isEmpty(adjPos) && adjPoint.getValue() == Point::MAX_VALUE) {
                adjPoint.setParent(curPos);
                adjPoint.setValue(curPoint.getValue() + 1);
                openList.push(adjPos);
            }
        }
    }
}

void Snake::findMaxPath(const Pos &from, const Pos &to, list<Direction> &path) {
    // Init
    SizeType row = map->getRowCount(), col = map->getColCount();
    for (SizeType i = 1; i < row - 1; ++i) {
        for (SizeType j = 1; j < col - 1; ++j) {
            map->getPoint(Pos(i, j)).setVisit(false);
            map->getPoint(Pos(i, j)).setValue((Point::ValueType)map->distance(Pos(i, j), to));
        }
    }
    path.clear();
    // DFS
    findMax(from, direc, from, to, path);
    map->showPath(from, path);
}

void Snake::findMax(const Pos &curPos,
                    const Direction curDirec,
                    const Pos &from,
                    const Pos &to,
                    list<Direction> &path) {
    if (!path.empty()) {  // A solution is found
        return;
    }
    map->getPoint(curPos).setVisit(true);
    map->showPos(curPos);
    if (curPos == to) {
        constructPath(from, to, path);
    } else {
        // Arrange the order of traversing to make the result path as straight as possible
        vector<Pos> adjPositions = curPos.getAllAdj();
        std::sort(adjPositions.begin(), adjPositions.end(),
                  [&](const Pos &a, const Pos &b) {
            return map->getPoint(a).getValue() > map->getPoint(b).getValue();
        });
        Point::ValueType maxDist = map->getPoint(adjPositions[0]).getValue();
        for (SizeType i = 0; i < adjPositions.size(); ++i) {
            if (map->getPoint(adjPositions[i]).getValue() == maxDist
                && curPos.getDirectionTo(adjPositions[i] == curDirec)) {
                util::swap(adjPositions[0], adjPositions[i]);
                break;
            }
        }
        // Traverse the adjacent positions
        for (const Pos &adjPos : adjPositions) {
            if (map->isEmpty(adjPos) && !map->getPoint(adjPos).isVisit()) {
                map->getPoint(adjPos).setParent(curPos);
                findMax(adjPos, curPos.getDirectionTo(adjPos), from, to, path);
            }
        }
    }
}

void Snake::constructPath(const Pos &from, const Pos &to, list<Direction> &path) const {
    Pos tmp = to, parent;
    while (tmp != from) {
        parent = map->getPoint(tmp).getParent();
        path.push_front(parent.getDirectionTo(tmp));
        tmp = parent;
    }
}
