ROOT=../..
STD=-std=gnu++11
INCLUDE=$(ROOT)/include
LIB=$(ROOT)/lib
GTEST=$(ROOT)/gtest-1.7.0

all:
	g++ $(STD) -c Renderable2d.cpp -o bin/Renderable2d.o
	g++ $(STD) -c Renderer2d.cpp -I$(INCLUDE) -o bin/Renderable2d.o
	g++ $(STD) -c test/Renderer2d.cpp -I. -I$(INCLUDE) -I$(GTEST)/include \
	    -o test/bin/Renderer2d.o
	g++ $(STD) -isystem $(GTEST)/include -I$(GTEST) \
        -c $(GTEST)/src/gtest-all.cc \
        -o test/bin/gtest-all.o
	ar -rv test/bin/libgtest.a test/bin/gtest-all.o

	g++ $(STD) -isystem $(GTEST)/include \
	    bin/*.o test/bin/*.o test/bin/libgtest.a \
	    -L$(LIB) -lmingw32 -lSDL2main -lSDL2 -mwindows \
	    -o test/bin/Renderer2d
