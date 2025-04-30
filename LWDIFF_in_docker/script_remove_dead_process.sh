#!/bin/bash

while true; do
    processes=$(ps -eo pid,etimes,cmd | awk '/to_test.*\.wasm/ && $2 > 3 {print $1}')

    if [ -n "$processes" ]; then
        for pid in $processes; do
            kill -9 $pid
        done
    fi

    processes=$(ps -eo pid,etimes,cmd | awk '/iwasm.*-f to_test/ && $2 > 3 {print $1}')

    if [ -n "$processes" ]; then
        for pid in $processes; do
            kill -9 $pid
        done
    fi
    processes=$(ps -eo pid,etimes,cmd | awk '/wasmedge.*\.wasm.*to_test/ && $2 > 3 {print $1}')

    if [ -n "$processes" ]; then
        for pid in $processes; do
            kill -9 $pid
        done
    fi


    processes=$(ps -eo pid,etimes,cmd | awk '/wasmtime.*to_test/ && $2 > 3 {print $1}')

    if [ -n "$processes" ]; then
        for pid in $processes; do
            kill -9 $pid
        done
    fi
    

    processes=$(ps -eo pid,etimes,cmd | awk '/wasmer.*to_test/ && $2 > 3 {print $1}')

    if [ -n "$processes" ]; then
        for pid in $processes; do
            kill -9 $pid
        done
    fi
    
    sleep 1
done
