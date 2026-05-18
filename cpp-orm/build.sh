#!/bin/bash
g++ -O3 -march=native -flto -DNDEBUG main.cpp -o server \
-I/usr/local/include \
-I/usr/include/jsoncpp \
-L/usr/local/lib \
-ldrogon -ltrantor -lpq -ljsoncpp -luuid -lz -lssl -lcrypto -lpthread
