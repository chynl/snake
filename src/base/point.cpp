#include "base/point.h"

const Point::ValueType Point::MAX_VALUE = UINT32_MAX;
const Point::ValueType Point::EMPTY_DIST = 999999;

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

void Point::setIdx(const ValueType index_) {
    idx = index_;
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

Point::ValueType Point::getIdx() const {
    return idx;
}
