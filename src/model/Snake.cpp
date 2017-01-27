#include "model/Snake.h"
#include "util/util.h"
#include <queue>
#include <algorithm>
#include <stdexcept>

using std::vector;
using std::list;
using std::queue;

Snake::Snake() {}

Snake::~Snake() {}

void Snake::setDirection(const Direction &d) {
    direc = d;
}

void Snake::setMap(Map *const m) {
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

void Snake::testHamilton() {
    map->enableTest();
    enableHamilton();
    SizeType row = map->getRowCount(), col = map->getColCount();
    for (SizeType i = 1; i < row - 1; ++i) {
        for (SizeType j = 1; j < col - 1; ++j) {
            map->showPos(Pos(i, j));
        }
    }
}

void Snake::addBody(const Pos &p) {
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

void Snake::move() {
    if (isDead() || direc == NONE) {
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

void Snake::enableHamilton() {
    // Check map size
    SizeType row = map->getRowCount(), col = map->getColCount();
    if (row % 2 == 1 && col % 2 == 1) {
        throw std::range_error("Snake.enableHamilton(): require even amount of rows or columns.");
    }
    // Preparation for building a hamiltonian cycle
    hamiltonEnabled = true;
    for (SizeType i = 0; i < row; ++i) {
        for (SizeType j = 0; j < col; ++j) {
            Point &point = map->getPoint(Pos(i, j));
            point.setVisit(false);
            point.setValue(Point::MAX_VALUE);
        }
    }
    Point::ValueType val = 0;
    for (auto it = bodies.crbegin(); it != bodies.crend(); ++it) {
        Point &point = map->getPoint(*it);
        point.setVisit(true);
        point.setValue(val++);
    }
    // Build a hamiltonian cycle
    SizeType visitCnt = bodies.size();
    buildHamilton(getHead(), getTail(), visitCnt);
}

void Snake::decideNext() {
    if (isDead()) {
        return;
    } else if (!map->hasFood()) {
        direc = NONE;
        return;
    }

    if (hamiltonEnabled) {  // AI based on the hamiltonian cycle

        Direction hamiltonDirec = Direction::NONE;
        const SizeType size = map->getSize();
        const Pos head = getHead(), tail = getTail();
        const Point::ValueType curPathIndex = map->getPoint(head).getValue();
        const vector<Pos> adjPositions = head.getAllAdj();
        for (const Pos &adjPos : adjPositions) {
            Point adjPoint = map->getPoint(adjPos);
            Point::ValueType adjVal = adjPoint.getValue();
            Point::ValueType headVal = map->getPoint(head).getValue();
            Point::ValueType tailVal = map->getPoint(tail).getValue();
            if (adjPoint.getType() == Point::Type::FOOD && tailVal != (adjVal + 1) % size) {
                // Check whether to take shortcuts to eat the food
                if (tailVal < headVal && (adjVal > headVal || adjVal < tailVal)) {
                    direc = head.getDirectionTo(adjPos);
                    return;
                } else if (tailVal > headVal && (adjVal > headVal && adjVal < tailVal)) {
                    direc = head.getDirectionTo(adjPos);
                    return;
                }
            }
            if (adjVal == (curPathIndex + 1) % size) {
                hamiltonDirec = head.getDirectionTo(adjPos);
            }
        }
        // No shorcuts found, just move along the hamiltonian cycle
        direc = hamiltonDirec;

    } else {  // AI based on searching

        list<Direction> pathToFood, pathToTail;
        // Create a virtual snake
        Map tmpMap = *map;
        Snake tmpSnake(*this);
        tmpSnake.setMap(&tmpMap);
        // Step 1
        tmpSnake.findMinPathToFood(pathToFood);
        if (!pathToFood.empty()) {
            // Step 2
            tmpSnake.move(pathToFood);
            if (tmpMap.isAllBody()) {
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
}

const Pos& Snake::getHead() const {
    return *bodies.begin();
}

const Pos& Snake::getTail() const {
    return *bodies.rbegin();
}

void Snake::removeTail() {
    map->getPoint(getTail()).setType(Point::Type::EMPTY);
    bodies.pop_back();
    if (bodies.size() > 1) {
        map->getPoint(getTail()).setType(Point::Type::SNAKE_TAIL);
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
    auto random = util::Random<>::getInstance();
    SizeType row = map->getRowCount(), col = map->getColCount();
    for (SizeType i = 1; i < row - 1; ++i) {
        for (SizeType j = 1; j < col - 1; ++j) {
            Point &point = map->getPoint(Pos(i, j));
            point.setValue(Point::MAX_VALUE);
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
            buildPath(from, to, path);
            map->showPath(from, path);
            break;
        }
        // Arrange the order of traversing to make the result path as straight as possible
        vector<Pos> adjPositions = curPos.getAllAdj();
        random->shuffle(adjPositions.begin(), adjPositions.end());
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
            Point &point = map->getPoint(Pos(i, j));
            point.setVisit(false);
            point.setValue((Point::ValueType)map->distance(Pos(i, j), to));
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
        buildPath(from, to, path);
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

void Snake::buildPath(const Pos &from, const Pos &to, list<Direction> &path) const {
    Pos tmp = to, parent;
    while (tmp != from) {
        parent = map->getPoint(tmp).getParent();
        path.push_front(parent.getDirectionTo(tmp));
        tmp = parent;
    }
}

bool Snake::buildHamilton(const Pos &curPos, const Pos &goal, const SizeType visitCnt) {
    auto random = util::Random<>::getInstance();
    Point &curPoint = map->getPoint(curPos);
    vector<Pos> adjPositions = curPos.getAllAdj();
    random->shuffle(adjPositions.begin(), adjPositions.end());
    for (const Pos &adjPos : adjPositions) {
        if (adjPos == goal && visitCnt == map->getSize()) {
            return true;
        }
        if (map->isInside(adjPos)) {
            Point &adjPoint = map->getPoint(adjPos);
            if (!adjPoint.isVisit()) {
                adjPoint.setVisit(true);
                adjPoint.setValue(curPoint.getValue() + 1);
                if (buildHamilton(adjPos, goal, visitCnt + 1)) {
                    return true;
                }
                adjPoint.setVisit(false);
            }
        }
    }
    return false;
}
