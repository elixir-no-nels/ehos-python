PROG   = simple_static simple_dynamic simple2

all:	$(PROG)


simple_static: 
	gcc  simple.c testlib.c -o simple_static

simple_dynamic: libtest.so
	gcc -L ./ -I ./ simple.c -l:libtest.so -o simple_dynamic

simple2: 
	gcc  simple2.c -o simple2

libtest.so: testlib.c testlib.h
	gcc -Wall -fPIC -c testlib.c
	gcc -shared -Wl,-soname,libtest.so -o libtest.so testlib.o 


clean:
	rm *.o libtest.so simple_dynamic simple_static
