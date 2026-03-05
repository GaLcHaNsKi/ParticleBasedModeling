#ifndef POS_H
#define POS_H

struct pos {
    double x;
    double y;
};

struct q_at_square
{
    pos position;
    unsigned int count;
};

#endif