#
# Makefile to build distributable packages for Windows, OSX and Linux.
#
#


#echo colors
cecho := echo -e
export red   :=\e[0;31m
export RED   :=\e[1;31m
export green :=\e[0;32m
export GREEN :=\e[1;32m
export blue  :=\e[0;34m
export BLUE  :=\e[1;34m
export yellow:=\e[0;33m
export YELLOW:=\e[1;33m
export cyan  :=\e[0;36m
export CYAN  :=\e[1;36m
# No Color
export NC  :=\e[0m
ifeq (${shell uname},Darwin)
    ${shell echo "#!/usr/bin/python \nimport sys;print ' '.join(sys.argv[1:]).replace('\\\\\\\\e','\\\\033')" > /tmp/cecho && chmod a+x /tmp/cecho }
    cecho := /tmp/cecho
endif
ifeq (${shell uname},Linux)
    ${shell echo -e "#!/usr/bin/python \nimport sys;print ' '.join(sys.argv[1:]).replace('\\\\\\\\e','\\\\033')" > /tmp/cecho && chmod a+x /tmp/cecho }
    cecho := /tmp/cecho
endif

PYTHON := python
ifeq (${CORES},)
    ifneq (${NUMBER_OF_PROCESSORS},)
        CORES := ${NUMBER_OF_PROCESSORS}
    else
        ifeq (`uname`,Linux)
            CORES := ${shell (expr `cat /proc/cpuinfo | grep processor | tail -1 | cut -d':' -f2` + 1)}
        else
            #CORES := ${shell (${PYTHON} -c 'import multiprocessing;print multiprocessing.cpu_count()')}
        endif
    endif
    ifeq (${CORES},)
        CORES := 1
    endif
endif

WORK_DIR := ${TMP}/chemshapes
#WORK_DIR := ${shell  pwd}

# Set up variables holding the names of source directories
pwd_folder     	:= ${shell  pwd}
working_dir	    := ${WORK_DIR}
build_dir	    := ${WORK_DIR}/build
dist_dir	    := ${WORK_DIR}/dist
top_dir         := ${WORK_DIR}
top_src_dir     := ${shell pwd}/src
src_dir         := ${shell pwd}/src
src_include_dir := ${top_src_dir}/include
src_make_dir    := ${top_src_dir}/make


#include ${src_make_dir}/globals.mk

all: help

#########################################################################
# 'make help' prints important make targets
help:
	@${cecho} "${BLUE}-----------------------------------------------------------------------------------------------------${CYAN}"
	@${cecho} "Targets:${YELLOW}"
	@${cecho}  ""
	@${cecho}  "  make                (default target is 'help')"
	@${cecho}  "  make help           show this help message"
	@${cecho}  "  make dev            run software without building. Use this to test run dev code."
	@${cecho}  ""
	@${cecho}  "  make win            build optimized Windows 32bit binaries in ${shell (echo ${dist_dir})}"
	@${cecho}  "                      temporary build files in ${shell (echo ${build_dir})}."
	@${cecho}  ""
	@${cecho}  "  make osx            build optimized OSX 32bit binaries in ${shell (echo ${dist_dir})},"
	@${cecho}  "                      temporary build files in ${shell (echo ${build_dir})}."
	@${cecho}  ""
	@${cecho}  "  make linux          build linux distribution package ${shell (echo ${dist_dir})},"
	@${cecho}  "                      temporary build files in ${shell (echo ${build_dir})}."
	@${cecho}  ""
	@${cecho}  "  make clean          Remove the temporary files in ${shell (echo ${build_dir})}."
	@${cecho}  ""
	@${cecho}  "  make realclean      Remove both ${shell (echo ${build_dir})} AND ${shell (echo ${dist_dir})}"
	@${cecho}  ""
	@${cecho} "${BLUE}-----------------------------------------------------------------------------------------------------${CYAN}"
	@${cecho}  ""
	@${cecho}  ""




#########################################################################
# dist_files lists (relative to build) all files that end up in an
# external distribution
dist_bins    	:=
dist_libs     	:=
dist_includes	:=


dev:
	@ python ./draft.py

win:
	@ ${MAKE} platform=mingw hw=i686 install
	@ kill -9 $$PPID

osx:
	@ ${MAKE} platform=macosx32 hw=i686
	@ kill -9 $$PPID

linux:
	@ ${MAKE} platform=linux hw=i686
	@ kill -9 $$PPID


win64:
	@ ${MAKE} platform=mingw hw=x86_64
	@ kill -9 $$PPID

osx64:
	@ ${MAKE} platform=macosx hw=x86_64
	@ kill -9 $$PPID

linux64:
	@ ${MAKE} platform=linux hw=x86_64
	@ kill -9 $$PPID


ifneq (${platform},)
    -include ${src_make_dir}/master.mk
endif