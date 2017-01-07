#include "Map.h"
#include "GameCtrl.h"
#include "Console.h"
#include <algorithm>
#include <queue>

using std::vector;
using std::string;
using std::list;
using std::queue;

Map::Map(const size_type &rowCnt_, const size_type &colCnt_)
    : content(rowCnt_, vector<Point>(colCnt_)) {
    // Add boundary walls
    auto rows = getRowCount(), cols = getColCount();
    for (size_type i = 0; i < rows; ++i) {
        if (i == 0 || i == rows - 1) {  // The first and last row
            for (size_type j = 0; j < cols; ++j) {
                content[i][j].setType(point_type::WALL);
            }
        } else {  // Rows in the middle
            content[i][0].setType(point_type::WALL);
            content[i][cols - 1].setType(point_type::WALL);
        }
    }
}

Map::~Map() {
}

Point& Map::getPoint(const Pos &p) {
    return content[p.getX()][p.getY()];
}

const Point& Map::getPoint(const Pos &p) const {
    return content[p.getX()][p.getY()];
}

bool Map::isInside(const Pos &p) const {
    return p.getX() > 0 && p.getY() > 0
        && p.getX() < (Pos::attr_type)getRowCount() - 1
        && p.getY() < (Pos::attr_type)getColCount() - 1;
}

bool Map::isSafe(const Pos &p) const {
    return isInside(p) 
        && (getPoint(p).getType() == point_type::EMPTY
        || getPoint(p).getType() == point_type::FOOD);
}

bool Map::isHead(const Pos &p) const {
    return isInside(p) && content[p.getX()][p.getY()].getType() == point_type::SNAKE_HEAD;
}

bool Map::isTail(const Pos &p) const {
    return isInside(p) && content[p.getX()][p.getY()].getType() == point_type::SNAKE_TAIL;
}

bool Map::isEmpty(const Pos &p) const {
    return isInside(p) && content[p.getX()][p.getY()].getType() == point_type::EMPTY;
}

bool Map::isAllBody() const {
    auto rows = getRowCount(), cols = getColCount();
    for (size_type i = 1; i < rows - 1; ++i) {
        for (size_type j = 1; j < cols - 1; ++j) {
            auto type = content[i][j].getType();
            if (!(type == point_type::SNAKE_HEAD
                || type == point_type::SNAKE_BODY
                || type == point_type::SNAKE_TAIL)) {
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
                == point_type::EMPTY) {
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
    // Test code to create food at a given order.
    //static vector<Pos> tmp = {Pos(2, 3), Pos(3, 3), Pos(3, 2), Pos(2, 2), Pos(2, 1), Pos(3, 1)};
    //static int cnt = 0;
    //if (cnt >= 0 && cnt <= 5) {
    //    createFood(tmp[cnt++]);
    //}
}

void Map::createFood(const Pos &pos) {
    food = pos;
    content[food.getX()][food.getY()].setType(point_type::FOOD);
}

void Map::removeFood() {
    if (food != Pos::INVALID) {
        content[food.getX()][food.getY()].setType(point_type::EMPTY);
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

Point::value_type Map::estimateDist(const Pos &from, const Pos &to) {
    Pos::attr_type fromX = from.getX(), toX = to.getX();
    Pos::attr_type fromY = from.getY(), toY = to.getY();
    auto dx = fromX > toX ? fromX - toX : toX - fromX;
    auto dy = fromY > toY ? fromY - toY : toY - fromY;
    return dx + dy;
}

void Map::showPosSearchDetail(const Pos &p, const point_type &t) {
    getPoint(p).setType(t);
    GameCtrl::getInstance()->sleepFor(detailInterval);
}

void Map::showVisitPosIfNeed(const Pos &n) {
    if (showSearchDetails) {
        showPosSearchDetail(n, point_type::TEST_VISIT);
    }
}

void Map::showPathIfNeed(const Pos &start, const list<Direc> &path) {
    if (showSearchDetails) {
        auto tmp = start;
        for (const auto &d : path) {
            showPosSearchDetail(tmp, point_type::TEST_PATH);
            tmp = tmp.getAdjPos(d);
        }
        showPosSearchDetail(tmp, point_type::TEST_PATH);
    }
}

void Map::constructPath(const Pos &from, const Pos &to, list<Direc> &path) const {
    Pos tmp = to, parent;
    while (tmp != Pos::INVALID && tmp != from) {
        parent = getPoint(tmp).getParent();
        path.push_front(parent.getDirectionTo(tmp));
        tmp = parent;
    }
}

void Map::init() {
    auto rows = getRowCount(), cols = getColCount();
    for (size_type i = 1; i < rows - 1; ++i) {
        for (size_type j = 1; j < cols - 1; ++j) {
            content[i][j].setDist(INF);
            content[i][j].setVisit(false);
        }
    }
}

void Map::findMinPath(const Pos &from, const Pos &to, const Direc &initDirec, list<Direc> &path) {
    if (!isInside(from) || !isInside(to)) {
        return;
    }

    // Prepare work for searching
    init();
    path.clear();
    getPoint(from).setDist(0);
    queue<Pos> openList;
    openList.push(from);

    // Start BFS
    while (!openList.empty()) {

        // Get current search point
        Pos curPos = openList.front();
        Point curPoint = getPoint(curPos);
        openList.pop();
        showVisitPosIfNeed(curPos);

        // Check if the goal is found
        if (curPos == to) {
            constructPath(from, to, path);
            showPathIfNeed(from, path);
            break;
        }

        // Arrange the order of traversing to make the result path as straight as possible
        Direc bestDirec = (curPos == from ? initDirec : curPoint.getParent().getDirectionTo(curPos));
        auto adjPositions = curPos.getAllAdjPos();
        for (unsigned i = 0; i < adjPositions.size(); ++i) {
            if (bestDirec == curPos.getDirectionTo(adjPositions[i])) {
                std::swap(adjPositions[0], adjPositions[i]);
                break;
            }
        }

        // Traverse adjacent positions
        for (const auto &adjPos : adjPositions) {
            Point &adjPoint = getPoint(adjPos);
            if (isEmpty(adjPos) && adjPoint.getDist() == INF) {
                adjPoint.setParent(curPos);
                adjPoint.setDist(curPoint.getDist() + 1);
                openList.push(adjPos);
            }
        }
    }
}

void Map::findMaxPath(const Pos &from, const Pos &to, const Direc &initDirec, list<Direc> &path) {
    if (!isInside(from) || !isInside(to)) {
        return;
    }
    init();
    path.clear();
    findMax(from, initDirec, from, to, path);
    showPathIfNeed(from, path);
}

void Map::findMax(const Pos &curPos, const Direc &curDirec, const Pos &from, const Pos &to, list<Direc> &path) {
    if (!path.empty()) {  // A solution is found
        return;
    }
    getPoint(curPos).setVisit(true);
    showVisitPosIfNeed(curPos);
    if (curPos == to) {  // Check if the goal is found
        constructPath(from, to, path);
    } else {

        // Compute estimated distance of adjacent points
        auto adjPositions = curPos.getAllAdjPos();
        if (adjPositions.empty()) {
            return;
        }
        for (const auto &pos : adjPositions) {
            Point &adjPoint = getPoint(pos);
            if (adjPoint.getDist() == INF) {
                adjPoint.setDist(estimateDist(pos, to));
            }
        }

        // Arrange the order of traversing to make the result path as straight as possible
        std::sort(adjPositions.begin(), adjPositions.end(), [&](const Pos &a, const Pos &b) {
            return getPoint(a).getDist() > getPoint(b).getDist();
        });
        auto maxDist = getPoint(adjPositions[0]).getDist();
        for (unsigned i = 0; i < adjPositions.size(); ++i) {
            if (getPoint(adjPositions[i]).getDist() == maxDist
                && curDirec == curPos.getDirectionTo(adjPositions[i])) {
                std::swap(adjPositions[0], adjPositions[i]);
                break;
            }
        }

        // Traverse adjacent positions
        for (const auto &adjPos : adjPositions) {
            if (isEmpty(adjPos) && !getPoint(adjPos).isVisit()) {
                getPoint(adjPos).setParent(curPos);
                findMax(adjPos, curPos.getDirectionTo(adjPos), from, to, path);
            }
        }
    }
}
