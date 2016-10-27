#include "Pos.h"

const Pos Pos::INVALID = Pos(-1, -1);

Pos::Pos(const attr_type &x_, const attr_type &y_)
    : x(x_), y(y_) {
}

Pos::~Pos() {
}

Pos::attr_type Pos::getX() const {
    return x;
}

Pos::attr_type Pos::getY() const {
    return y;
}

void Pos::setX(const attr_type &x_) {
    x = x_;
}

void Pos::setY(const attr_type &y_) {
    y = y_;
}

Pos operator+(const Pos &a, const Pos &b) {
    return Pos(a.x + b.x, a.y + b.y);
}

bool operator==(const Pos &a, const Pos &b) {
    return a.x == b.x && a.y == b.y;
}

bool operator!=(const Pos &a, const Pos &b) {
    return !(a == b);
}

unsigned Pos::hash(const Pos &p) {
    std::hash<attr_type> h;
    return h(p.x) ^ h(p.y);
}

std::vector<Pos> Pos::getAllAdjPos() const {
    std::vector<Pos> res(4);
    int dx[] = {0, -1, 0, 1};
    int dy[] = {-1, 0, 1, 0};
    for (int i = 0; i < 4; ++i) {
        res[i].setX(x + dx[i]);
        res[i].setY(y + dy[i]);
    }
    return res;
}

Direction Pos::getDirectionTo(const Pos &p) const  {
    int dx = p.x - x;
    int dy = p.y - y;
    if (dx == 0 && dy == -1) {
        return LEFT;
    } else if (dx == 0 && dy == 1) {
        return RIGHT;
    } else if (dx == -1 && dy == 0) {
        return UP;
    } else if (dx == 1 && dy == 0) {
        return DOWN;
    } else {
        return NONE;
    }
}

Pos Pos::getAdjPos(const Direction &d) const {
    int dx = 0, dy = 0;
    switch (d) {
        case LEFT:
            dx = 0; dy = -1; break;
        case UP:
            dx = -1; dy = 0; break;
        case RIGHT:
            dx = 0; dy = 1; break;
        case DOWN:
            dx = 1; dy = 0; break;
        default:
            break;
    }
    return Pos(x + dx, y + dy);
}

std::string Pos::toString() const {
    return "(" + intToStr(x) + "," + intToStr(y) + ")";
}
