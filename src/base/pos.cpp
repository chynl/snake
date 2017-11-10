#include "base/pos.h"
#include "util/util.h"

Pos::Pos(const SizeType x_, const SizeType y_) : x(x_), y(y_) {}

Pos::~Pos() {}

Pos::SizeType Pos::getX() const {
    return x;
}

Pos::SizeType Pos::getY() const {
    return y;
}

void Pos::setX(const SizeType x_) {
    x = x_;
}

void Pos::setY(const SizeType y_) {
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

std::string Pos::toString() const {
    return "(" + util::toString(x) + "," + util::toString(y) + ")";
}

Direction Pos::getDirectionTo(const Pos &p) const {
    if (x == p.x) {
        if (p.y - y == 1) {
            return RIGHT;
        } else if (y - p.y == 1) {
            return LEFT;
        }
    } else if (y == p.y) {
        if (p.x - x == 1) {
            return DOWN;
        } else if (x - p.x == 1) {
            return UP;
        }
    }
    return NONE;
}

Pos Pos::getAdj(const Direction d) const {
    switch (d) {
        case LEFT:
            if (y) {
                return Pos(x, y - 1);
            }
            break;
        case UP:
            if (x) {
                return Pos(x - 1, y);
            }
            break;
        case RIGHT:
            return Pos(x, y + 1);
        case DOWN:
            return Pos(x + 1, y);
        default:
            break;
    }
    return *this;
}

std::vector<Pos> Pos::getAllAdj() const {
    std::vector<Pos> adj;
    for (int i = 1; i <= 4; ++i) {
        Pos p = getAdj((Direction)i);
        if (p != *this) {
            adj.push_back(p);
        }
    }
    return adj;
}
