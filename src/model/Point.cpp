#include "model/Point.h"

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

void Point::setValue(const ValueType dist_) {
    val = dist_;
}

Pos Point::getParent() const {
    return parent;
}

bool Point::isVisit() const {
    return visit;
}

Point::ValueType Point::getValue() const {
    return val;
}
