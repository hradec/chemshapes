#!/bin/bash 

cd `dirname "$BASH_SOURCE"`
env \
    PATH=.:`pwd`/__debug_env_osx/2.7/bin:`pwd`/__debug_env_osx/2.7/lib:$PATH \
    PYTHONPATH=.:`pwd`/__debug_env_osx/2.7/lib/python2.7/site-packages/:`pwd`/gletools \
    DYLD_LIBRARY_PATH=.:`pwd`/__debug_env_osx/2.7:`pwd`/__debug_env_osx/2.7/lib \
__debug_env_osx/2.7/bin/python2.7 ./draft.py &

