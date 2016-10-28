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

void Point::setDist(const value_type dist_) {
    dist = dist_;
}

void Point::setParent(const Pos &p_) {
    parent = p_;
}

void Point::setVisit(const bool v) {
    visit = v;
}

Point::value_type Point::getDist() const {
    return dist;
}

Pos Point::getParent() const {
    return parent;
}

bool Point::isVisit() const {
    return visit;
}
