#include "Point.h"

Point::Point() {
}

Point::~Point() {
}

Point::Type Point::getType() const {
    return type;
}

void Point::setType(Type type_) {
    type = type_;
}

void Point::setG(const value_type g_) {
    g = g_;
}

void Point::setH(const value_type h_) {
    h = h_;
}

void Point::setParent(const Pos &p_) {
    parent = p_;
}

void Point::setPos(const Pos &p) {
    pos = p;
}

Point::value_type Point::getG() const {
    return g;
}

Point::value_type Point::getH() const {
    return h;
}

Point::value_type Point::getF() const {
    return g + h;
}

Pos Point::getParent() const {
    return parent;
}

Pos Point::getPos() const {
    return pos;
}

bool operator<(const Point &a, const Point &b) {
    return a.getF() < b.getF();
}

bool operator>(const Point &a, const Point &b) {
    return a.getF() > b.getF();
}

bool operator<=(const Point &a, const Point &b) {
    return a.getF() <= b.getF();
}

bool operator>=(const Point &a, const Point &b) {
    return a.getF() >= b.getF();
}
