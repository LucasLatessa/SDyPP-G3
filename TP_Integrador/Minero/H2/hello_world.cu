#include <stdio.h>

__global__ void helloWorld()
{
    printf("Hola Mundo desde la GPU!\n");
}

int main()
{
    helloWorld<<<1, 1>>>();

    cudaDeviceSynchronize();

    return 0;
}
