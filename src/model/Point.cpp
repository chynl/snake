#include "model/Point.h"

Point::Point() : type(EMPTY) {}

Point::~Point() {}

Point::Type Point::getType() const {
    return type;
}

void Point::setType(Type type_) {
    type = type_;
}

void Point::setDist(const DistType dist_) {
    dist = dist_;
}

void Point::setParent(const Pos &p_) {
    parent = p_;
}

void Point::setVisit(const bool v) {
    visit = v;
}

Point::DistType Point::getDist() const {
    return dist;
}

Pos Point::getParent() const {
    return parent;
}

bool Point::isVisit() const {
    return visit;
}
