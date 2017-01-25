#include "GameCtrl.h"
#include "util/Console.h"
#include "util/random.h"
#include "util/swap.h"
#include "model/Map.h"
#include <algorithm>
#include <queue>

using std::vector;
using std::string;
using std::list;
using std::queue;

Map::Map(const SizeType rowCnt_, const SizeType colCnt_)
    : content(rowCnt_, vector<Point>(colCnt_)), showDetail(false) {
    // Add boundary walls
    SizeType row = getRowCount(), col = getColCount();
    for (SizeType i = 0; i < row; ++i) {
        if (i == 0 || i == row - 1) {  // The first and last row
            for (SizeType j = 0; j < col; ++j) {
                content[i][j].setType(Point::Type::WALL);
            }
        } else {  // Rows in the middle
            content[i][0].setType(Point::Type::WALL);
            content[i][col - 1].setType(Point::Type::WALL);
        }
    }
}

Map::~Map() {}

Point& Map::getPoint(const Pos &p) {
    return content[p.getX()][p.getY()];
}

const Point& Map::getPoint(const Pos &p) const {
    return content[p.getX()][p.getY()];
}

Map::SizeType Map::getRowCount() const {
    return content.size();
}

Map::SizeType Map::getColCount() const {
    return content[0].size();
}

void Map::setShowDetail(const bool show) {
    showDetail = show;
}

bool Map::isInside(const Pos &p) const {
    return p.getX() > 0 && p.getY() > 0
        && p.getX() < getRowCount() - 1
        && p.getY() < getColCount() - 1;
}

bool Map::isHead(const Pos &p) const {
    return isInside(p) && content[p.getX()][p.getY()].getType() == Point::Type::SNAKE_HEAD;
}

bool Map::isTail(const Pos &p) const {
    return isInside(p) && content[p.getX()][p.getY()].getType() == Point::Type::SNAKE_TAIL;
}

bool Map::isEmpty(const Pos &p) const {
    return isInside(p) && content[p.getX()][p.getY()].getType() == Point::Type::EMPTY;
}

bool Map::isSafe(const Pos &p) const {
    return isInside(p) && (getPoint(p).getType() == Point::Type::EMPTY
        || getPoint(p).getType() == Point::Type::FOOD);
}

bool Map::isAllBody() const {
    SizeType row = getRowCount(), col = getColCount();
    for (SizeType i = 1; i < row - 1; ++i) {
        for (SizeType j = 1; j < col - 1; ++j) {
            auto type = content[i][j].getType();
            if (!(type == Point::Type::SNAKE_HEAD
                || type == Point::Type::SNAKE_BODY
                || type == Point::Type::SNAKE_TAIL)) {
                return false;
            }
        }
    }
    return true;
}

void Map::createRandFood() {
    vector<Pos> emptyPoints = getEmptyPoints();
    if (!emptyPoints.empty()) {
        SizeType i = util::randInt((SizeType)0, emptyPoints.size() - 1);
        createFood(emptyPoints[i]);
    }
}

void Map::createFood(const Pos &pos) {
    food = pos;
    content[food.getX()][food.getY()].setType(Point::Type::FOOD);
}

void Map::removeFood() {
    if (hasFood()) {
        content[food.getX()][food.getY()].setType(Point::Type::EMPTY);
    }
}

bool Map::hasFood() const {
    return isInside(food) && getPoint(food).getType() == Point::Type::FOOD;
}

const Pos& Map::getFood() const {
    return food;
}

vector<Pos> Map::getEmptyPoints() const {
    vector<Pos> points;
    SizeType row = getRowCount(), col = getColCount();
    for (SizeType i = 1; i < row - 1; ++i) {
        for (SizeType j = 1; j < col - 1; ++j) {
            if (content[i][j].getType() == Point::Type::EMPTY) {
                points.push_back(Pos(i, j));
            }
        }
    }
    return points;
}

Map::SizeType Map::distance(const Pos &from, const Pos &to) {
    SizeType fromX = from.getX(), toX = to.getX();
    SizeType fromY = from.getY(), toY = to.getY();
    SizeType dx = fromX > toX ? fromX - toX : toX - fromX;
    SizeType dy = fromY > toY ? fromY - toY : toY - fromY;
    return dx + dy;
}

void Map::showPos(const Pos &p, const Point::Type type) {
    getPoint(p).setType(type);
    GameCtrl::getInstance()->sleepFor(10);
}

void Map::showVisitPos(const Pos &p) {
    if (showDetail) {
        showPos(p, Point::Type::TEST_VISIT);
    }
}

void Map::showPath(const Pos &start, const list<Direction> &path) {
    if (showDetail) {
        Pos tmp = start;
        for (const auto &d : path) {
            showPos(tmp, Point::Type::TEST_PATH);
            tmp = tmp.getAdj(d);
        }
        showPos(tmp, Point::Type::TEST_PATH);
    }
}

void Map::constructPath(const Pos &from, const Pos &to, list<Direction> &path) const {
    Pos tmp = to, parent;
    while (tmp != from) {
        parent = getPoint(tmp).getParent();
        path.push_front(parent.getDirectionTo(tmp));
        tmp = parent;
    }
}

void Map::findMinPath(const Pos &from, const Pos &to, const Direction direc, list<Direction> &path) {
    if (!isInside(from) || !isInside(to)) {
        return;
    }
    // Init
    SizeType row = getRowCount(), col = getColCount();
    for (SizeType i = 1; i < row - 1; ++i) {
        for (SizeType j = 1; j < col - 1; ++j) {
            content[i][j].setVisit(false);
            content[i][j].setDist(Point::MAX_DIST);
        }
    }
    path.clear();
    getPoint(from).setDist(0);
    queue<Pos> openList;
    openList.push(from);
    // BFS
    while (!openList.empty()) {
        const Pos curPos = openList.front();
        const Point &curPoint = getPoint(curPos);
        openList.pop();
        showVisitPos(curPos);
        if (curPos == to) {
            constructPath(from, to, path);
            showPath(from, path);
            break;
        }
        // Arrange the order of traversing to make the result path as straight as possible
        vector<Pos> adjPositions = curPos.getAllAdj();
        util::randChange(adjPositions);
        Direction bestDirec = (curPos == from ? direc : curPoint.getParent().getDirectionTo(curPos));
        for (SizeType i = 0; i < adjPositions.size(); ++i) {
            if (bestDirec == curPos.getDirectionTo(adjPositions[i])) {
                util::swap(adjPositions[0], adjPositions[i]);
                break;
            }
        }
        // Traverse the adjacent positions
        for (const Pos &adjPos : adjPositions) {
            Point &adjPoint = getPoint(adjPos);
            if (isEmpty(adjPos) && adjPoint.getDist() == Point::MAX_DIST) {
                adjPoint.setParent(curPos);
                adjPoint.setDist(curPoint.getDist() + 1);
                openList.push(adjPos);
            }
        }
    }
}

void Map::findMaxPath(const Pos &from, const Pos &to, const Direction direc, list<Direction> &path) {
    if (!isInside(from) || !isInside(to)) {
        return;
    }
    // Init
    SizeType row = getRowCount(), col = getColCount();
    for (SizeType i = 1; i < row - 1; ++i) {
        for (SizeType j = 1; j < col - 1; ++j) {
            content[i][j].setVisit(false);
            content[i][j].setDist((Point::DistType)distance(Pos(i, j), to));
        }
    }
    path.clear();
    // DFS
    findMax(from, direc, from, to, path);
    showPath(from, path);
}

void Map::findMax(const Pos &curPos,
                  const Direction &curDirec,
                  const Pos &from,
                  const Pos &to,
                  list<Direction> &path) {
    if (!path.empty()) {  // A solution is found
        return;
    }
    getPoint(curPos).setVisit(true);
    showVisitPos(curPos);
    if (curPos == to) {
        constructPath(from, to, path);
    } else {
        // Arrange the order of traversing to make the result path as straight as possible
        vector<Pos> adjPositions = curPos.getAllAdj();
        util::randChange(adjPositions);
        std::sort(adjPositions.begin(), adjPositions.end(),
                  [&](const Pos &a, const Pos &b) {
            return getPoint(a).getDist() > getPoint(b).getDist();
        });
        Point::DistType maxDist = getPoint(adjPositions[0]).getDist();
        for (SizeType i = 0; i < adjPositions.size(); ++i) {
            if (getPoint(adjPositions[i]).getDist() == maxDist
                && curPos.getDirectionTo(adjPositions[i] == curDirec)) {
                util::swap(adjPositions[0], adjPositions[i]);
                break;
            }
        }
        // Traverse the adjacent positions
        for (const Pos &adjPos : adjPositions) {
            if (isEmpty(adjPos) && !getPoint(adjPos).isVisit()) {
                getPoint(adjPos).setParent(curPos);
                findMax(adjPos, curPos.getDirectionTo(adjPos), from, to, path);
            }
        }
    }
}
