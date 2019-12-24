#!/bin/bash

for i in {1..1000}; do
    nc localhost 3333 &
done
