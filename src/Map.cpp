#include "Map.h"
#include "GameCtrl.h"
#include "Console.h"
#include <algorithm>

using std::vector;
using std::string;
using std::list;

Map::Map(const size_type &rowCnt_, const size_type &colCnt_)
    : content(rowCnt_, vector<Point>(colCnt_)) {
    init();
}

Map::~Map() {
}

void Map::init() {
    auto rows = getRowCount(), cols = getColCount();
    for (size_type i = 0; i < rows; ++i) {
        for (size_type j = 0; j < cols; ++j) {
            content[i][j].setPos(Pos(i, j));
        }
    }
    // Add boundaries
    for (size_type i = 0; i < rows; ++i) {
        if (i == 0 || i == rows - 1) {  // The first and last row
            for (size_type j = 0; j < cols; ++j) {
                content[i][j].setType(Point::Type::WALL);
            }
        } else {  // Rows in the middle
            content[i][0].setType(Point::Type::WALL);
            content[i][cols - 1].setType(Point::Type::WALL);
        }
    }
}

Point& Map::getPoint(const Pos &p) {
    return content[p.getX()][p.getY()];
}

const Point& Map::getPoint(const Pos &p) const {
    return content[p.getX()][p.getY()];
}

bool Map::isUnsafe(const Pos &p) const {
    return getPoint(p).getType() == Point::Type::WALL
        || getPoint(p).getType() == Point::Type::SNAKEHEAD
        || getPoint(p).getType() == Point::Type::SNAKEBODY
        || getPoint(p).getType() == Point::Type::SNAKETAIL;
}

bool Map::isUnsearch(const Pos &p) const {
    return getPoint(p).getType() == Point::Type::WALL
        || getPoint(p).getType() == Point::Type::SNAKEHEAD
        || getPoint(p).getType() == Point::Type::SNAKEBODY
        || getPoint(p).getType() == Point::Type::SNAKETAIL
        || getPoint(p).getType() == Point::Type::FOOD;
}

bool Map::isInside(const Pos &p) const {
    return p.getX() > 0 && p.getY() > 0
        && p.getX() < (Pos::attr_type)getRowCount() - 1
        && p.getY() < (Pos::attr_type)getColCount() - 1;
}

bool Map::isHead(const Pos &p) const {
    return isInside(p) && content[p.getX()][p.getY()].getType() == Point::Type::SNAKEHEAD;
}

bool Map::isTail(const Pos &p) const {
    return isInside(p) && content[p.getX()][p.getY()].getType() == Point::Type::SNAKETAIL;
}

bool Map::isAllBody() const {
    auto rows = getRowCount(), cols = getColCount();
    for (size_type i = 1; i < rows - 1; ++i) {
        for (size_type j = 1; j < cols - 1; ++j) {
            auto type = content[i][j].getType();
            if (!(type == Point::Type::SNAKEHEAD
                || type == Point::Type::SNAKEBODY
                || type == Point::Type::SNAKETAIL)) {
                return false;
            }
        }
    }
    return true;
}

void Map::getEmptyPoints(vector<Pos> &res) const {
    res.clear();
    auto rows = getRowCount(), cols = getColCount();
    for (size_type i = 1; i < rows - 1; ++i) {
        for (size_type j = 1; j < cols - 1; ++j) {
            if (content[i][j].getType()
                == Point::Type::EMPTY) {
                res.push_back(Pos(i, j));
            }
        }
    }
}

void Map::createRandFood() {
    vector<Pos> emptyPoints;
    getEmptyPoints(emptyPoints);
    if (!emptyPoints.empty()) {
        createFood(emptyPoints[random(0, emptyPoints.size() - 1)]);
    }
}

void Map::createFood(const Pos &pos) {
    food = pos;
    content[food.getX()][food.getY()].setType(Point::Type::FOOD);
}

void Map::removeFood() {
    if (food != Pos::INVALID) {
        content[food.getX()][food.getY()].setType(Point::Type::EMPTY);
        food = Pos::INVALID;
    }
}

bool Map::hasFood() const {
    return food != Pos::INVALID;
}

Map::size_type Map::getRowCount() const {
    return content.size();
}

Map::size_type Map::getColCount() const {
    return content[0].size();
}

const Pos& Map::getFood() const {
    return food;
}

void Map::setShowSearchDetails(const bool &b) {
    showSearchDetails = b;
}

Point::value_type Map::heuristic(const Pos &from, const Pos &to) {
    return getManhattenDist(from, to);
}

unsigned Map::getManhattenDist(const Pos &from, const Pos &to) {
    auto dx = abs(from.getX() - to.getX());
    auto dy = abs(from.getY() - to.getY());
    return dx + dy;
}

void Map::showVisitedNodeIfNeeded(const Pos &n, const Point::Type &type) {
    if (showSearchDetails) {
        getPoint(n).setType(type);
        GameCtrl::getInstance()->sleepFor(10);
    }
}

void Map::showPathIfNeeded(const Pos &start, const list<Direction> &path) {
    if (showSearchDetails) {
        auto tmp = start;
        for (const auto &d : path) {
            showVisitedNodeIfNeeded(tmp, Point::Type::SNAKEHEAD);
            tmp = tmp.getAdjPos(d);
        }
        showVisitedNodeIfNeeded(tmp, Point::Type::SNAKEHEAD);
    }
}

void Map::constructPath(const Pos &from, const Pos &to, list<Direction> &path) {
    path.clear();
    Pos tmp = to, parent;
    while (tmp != Pos::INVALID && tmp != from) {
        parent = getPoint(tmp).getParent();
        path.push_front(parent.getDirectionTo(tmp));
        tmp = parent;
    }
}

void Map::findMinPath(const Pos &from, const Pos &to, list<Direction> &path) {
    if (!isInside(from) || !isInside(to)) {
        return;
    }

    // Initialize g value
    auto rows = getRowCount(), cols = getColCount();
    for (size_type i = 0; i < rows; ++i) {
        for (size_type j = 0; j < cols; ++j) {
            content[i][j].setG(GameCtrl::INF);
        }
    }

    min_heap openList;
    hash_table closeList(2 * rows * cols, Pos::hash);

    // Create local variables in the loop to save allocation time
    Point curPoint;
    Pos curPos;

    // Add first search node
    Point &start = getPoint(from);
    start.setG(0);
    start.setH(heuristic(start.getPos(), to));
    openList.push(start);

    while (!openList.empty()) {

        // Loop until the open list is empty or finding
        // a node that is not in the close list.
        do {
            curPoint = openList.top();
            curPos = curPoint.getPos();
            openList.pop();
        } while (!openList.empty() && closeList.find(curPos) != closeList.end());

        // If all the nodes on the map is in the close list,
        // then there is no available path between the two
        // nodes.
        if (openList.empty() && closeList.find(curPos) != closeList.end()) {
            break;
        }

        showVisitedNodeIfNeeded(curPos, Point::Type::SNAKEBODY);

        if (curPos == to) {
            constructPath(from, to, path);
            showPathIfNeeded(from, path);
            break;
        }

        closeList.insert(curPos);
        auto adjPoints = curPos.getAllAdjPos();
        randomChange(adjPoints);  // Ensure randomly traversing
        for (const auto &adjPoint : adjPoints) {
            if (!isUnsearch(adjPoint) && closeList.find(adjPoint) == closeList.end()) {
                Point &adjGrid = getPoint(adjPoint);
                if (curPoint.getG() + 1 < adjGrid.getG()) {
                    adjGrid.setParent(curPos);
                    adjGrid.setG(curPoint.getG() + 1);
                    adjGrid.setH(heuristic(adjGrid.getPos(), to));
                    openList.push(adjGrid);
                }
            }
        }
    }
}

void Map::findMaxPath(const Pos &from, const Pos &to, list<Direction> &path) {
    if (!isInside(from) || !isInside(to)) {
        return;
    }
    hash_table closeList(2 * getRowCount() * getColCount(), Pos::hash);
    dfsFindLongest(from, from, to, closeList, path);
    showPathIfNeeded(from, path);
}

void Map::dfsFindLongest(const Pos &n,
                         const Pos &from,
                         const Pos &to,
                         Map::hash_table &closeList,
                         list<Direction> &path) {
    closeList.insert(n);
    showVisitedNodeIfNeeded(n, Point::Type::SNAKEBODY);
    if (n == to) {
        constructPath(from, to, path);
    } else {
        // Start traversing with the farthest point.
        auto adjPoints = n.getAllAdjPos();
        std::sort(adjPoints.begin(), adjPoints.end(),
                  [&](const Pos &a, const Pos &b) { return heuristic(a, to) > heuristic(b, to); });
        for (const auto &adj : adjPoints) {
            if (!isUnsearch(adj) && closeList.find(adj) == closeList.end()) {
                getPoint(adj).setParent(n);
                dfsFindLongest(adj, from, to, closeList, path);
            }
        }
    }
}
