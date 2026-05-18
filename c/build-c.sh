#!/bin/bash
gcc -O3 -march=native -flto main.c -o c_server \
-I/usr/include/postgresql \
-lpq -lm