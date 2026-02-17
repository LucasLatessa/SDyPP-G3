#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#include "cuda_md5.cu"

#define THREADS 256

__device__ void int_to_str(int num, char *str, int *len) {
    int i = 0;
    if (num == 0) {
        str[0] = '0';
        *len = 1;
        return;
    }

    char temp[16];
    while (num > 0) {
        temp[i++] = '0' + (num % 10);
        num /= 10;
    }

    *len = i;
    for (int j = 0; j < i; j++)
        str[j] = temp[i - j - 1];
}

__device__ bool starts_with_hex(const uint8_t* hash, const char* prefix, int prefix_len) {
    const char hex_digits[] = "0123456789abcdef";
    for (int i = 0; i < prefix_len; i++) {
        uint8_t byte = hash[i / 2];
        char hex_char = (i % 2 == 0) ?
            hex_digits[(byte >> 4) & 0xF] :
            hex_digits[byte & 0xF];

        if (hex_char != prefix[i])
            return false;
    }
    return true;
}

__global__
void calculate_md5(
    const char* input,
    int input_len,
    const char* prefix,
    int prefix_len,
    int from,
    int to,
    int* found_flag,
    int* found_nonce
) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    int nonce = from + idx;

    if (nonce > to || *found_flag)
        return;

    char nonce_str[16];
    int nonce_len;
    int_to_str(nonce, nonce_str, &nonce_len);

    char buffer[128];
    memcpy(buffer, input, input_len);
    memcpy(buffer + input_len, nonce_str, nonce_len);

    int total_len = input_len + nonce_len;

    uint8_t digest[16];
    cuda_md5((uint8_t*)buffer, total_len, digest);

    if (starts_with_hex(digest, prefix, prefix_len)) {
        if (atomicCAS(found_flag, 0, 1) == 0) {
            *found_nonce = nonce;
        }
    }
}

int main(int argc, char *argv[]) {

    if (argc != 5) {
        printf("Uso: %s <from> <to> <prefix> <input>\n", argv[0]);
        return 1;
    }

    int from = atoi(argv[1]);
    int to   = atoi(argv[2]);
    const char* prefix = argv[3];
    const char* input  = argv[4];

    int input_len = strlen(input);
    int prefix_len = strlen(prefix);

    char *d_input, *d_prefix;
    int *d_found_flag, *d_found_nonce;

    cudaMalloc(&d_input, input_len);
    cudaMalloc(&d_prefix, prefix_len);
    cudaMalloc(&d_found_flag, sizeof(int));
    cudaMalloc(&d_found_nonce, sizeof(int));

    cudaMemcpy(d_input, input, input_len, cudaMemcpyHostToDevice);
    cudaMemcpy(d_prefix, prefix, prefix_len, cudaMemcpyHostToDevice);

    int zero = 0;
    cudaMemcpy(d_found_flag, &zero, sizeof(int), cudaMemcpyHostToDevice);

    int total = to - from + 1;
    int blocks = (total + THREADS - 1) / THREADS;

    cudaEvent_t start, stop;
    float elapsed;

    cudaEventCreate(&start);
    cudaEventCreate(&stop);

    cudaEventRecord(start);

    calculate_md5<<<blocks, THREADS>>>(
        d_input,
        input_len,
        d_prefix,
        prefix_len,
        from,
        to,
        d_found_flag,
        d_found_nonce
    );

    cudaEventRecord(stop);
    cudaEventSynchronize(stop);
    cudaEventElapsedTime(&elapsed, start, stop);

    int found_flag = 0;
    int found_nonce = 0;

    cudaMemcpy(&found_flag, d_found_flag, sizeof(int), cudaMemcpyDeviceToHost);
    cudaMemcpy(&found_nonce, d_found_nonce, sizeof(int), cudaMemcpyDeviceToHost);

    if (found_flag) {
        printf("Nonce encontrado: %d\n", found_nonce);
    } else {
        printf("No encontrado\n");
    }

    printf("Tiempo: %.4f ms\n", elapsed);

    cudaFree(d_input);
    cudaFree(d_prefix);
    cudaFree(d_found_flag);
    cudaFree(d_found_nonce);

    return 0;
}
