#!/bin/bash

while true; do
  rm -rf .cache
  sm run -s prog/iio2.cpp -t in/iio0.in
  if [ $? -ne 0 ]; then
    break
  fi
done
