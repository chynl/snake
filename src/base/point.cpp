#include "base/point.h"

Point::Point() {}

Point::~Point() {}

Point::Type Point::getType() const {
    return type;
}

void Point::setType(Type type_) {
    type = type_;
}

void Point::setParent(const Pos &p_) {
    parent = p_;
}

void Point::setVisit(const bool v) {
    visit = v;
}

void Point::setDist(const ValueType dist_) {
    dist = dist_;
}

void Point::setIndex(const ValueType index_) {
    index = index_;
}

Pos Point::getParent() const {
    return parent;
}

bool Point::isVisit() const {
    return visit;
}

Point::ValueType Point::getDist() const {
    return dist;
}

Point::ValueType Point::getIndex() const {
    return index;
}
