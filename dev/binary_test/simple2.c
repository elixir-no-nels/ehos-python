#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include "testlib.h"

int main(int argc, char **argv)
{
    int sleep_time;
    int input;
    int failure;

    if (argc != 3) {
        printf("Usage: simple <sleep-time> <integer>\n");
        return 1;
    } 

    sleep_time = atoi(argv[1]);
    input      = atoi(argv[2]);
    
    printf("We calculated: %d\n", input * 2);
    printf("Thinking really hard for %d seconds...\n", sleep_time);
    sleep(sleep_time);

    return 0;
}
