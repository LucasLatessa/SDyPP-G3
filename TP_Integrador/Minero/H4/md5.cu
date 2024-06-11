#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "cuda_md5.cu"

__global__
void calculate_md5(const unsigned char* input, unsigned long long input_len, unsigned char* result) {
    cuda_md5(input, input_len, result); //calcula el hash con md5
}

int main(int argc, char *argv[]) {
    if (argc != 2) { //si no se pasa la cadena a hasher, muesta lo siguiente
        fprintf(stderr, "Uso: %s <cadena>\n", argv[0]);
        return 1;
    }

    const char* input = argv[1]; //agarra la palabra a hashear
    size_t input_len = strlen(input); // calcula la longutud

    unsigned char result[16]; // array de 16 bytes

    unsigned char* d_input; // asigna de la cadena puntero
    unsigned char* d_result; // asigna de respuesta puntero
    cudaMalloc(&d_input, input_len * sizeof(unsigned char)); // asigna puntero de la cadena en gpu
    cudaMalloc(&d_result, 16 * sizeof(unsigned char)); // asigna puntero de respuesta en gpu
    cudaMemcpy(d_input, reinterpret_cast<const unsigned char*>(input), input_len * sizeof(unsigned char), cudaMemcpyHostToDevice); // copia cadena desde cpu a gpu

    calculate_md5<<<1, 1>>>(d_input, input_len, d_result); // llama a la funcion del kernel

    cudaMemcpy(result, d_result, 16 * sizeof(unsigned char), cudaMemcpyDeviceToHost); //copia el resultado desde gpu a cpu

    printf("Hash MD5 de '%s': ", input); // muestra el resultado
    for (int i = 0; i < 16; ++i) {
        printf("%02x", result[i]);
    }
    printf("\n");

    cudaFree(d_input); // libera memoria
    cudaFree(d_result);

    return 0;
}
