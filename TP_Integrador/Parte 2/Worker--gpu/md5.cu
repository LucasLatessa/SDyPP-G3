#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#include "cuda_md5.cu"

#define THREADS 256
#define MAX_MESSAGE_LEN 512

__device__ void uint64_to_str(unsigned long long num, char *str, int *len) {
    int i = 0;

    if (num == 0) {
        str[0] = '0';
        *len = 1;
        return;
    }

    char temp[32];

    while (num > 0) {
        temp[i++] = '0' + (num % 10);
        num /= 10;
    }

    *len = i;

    for (int j = 0; j < i; j++) {
        str[j] = temp[i - j - 1];
    }
}

__device__ bool starts_with_hex(const uint8_t *hash, const char *prefix, int prefix_len) {
    const char hex_digits[] = "0123456789abcdef";

    for (int i = 0; i < prefix_len; i++) {
        uint8_t byte = hash[i / 2];
        char hex_char = (i % 2 == 0)
            ? hex_digits[(byte >> 4) & 0xF]
            : hex_digits[byte & 0xF];

        if (hex_char != prefix[i]) {
            return false;
        }
    }

    return true;
}

__global__ void calculate_md5(
    const char *input,
    int input_len,
    const char *prefix,
    int prefix_len,
    unsigned long long from,
    unsigned long long to,
    int *found_flag,
    unsigned long long *found_nonce,
    uint8_t *found_digest
) {
    unsigned long long idx =
        ((unsigned long long)blockIdx.x * blockDim.x) + threadIdx.x;

    unsigned long long nonce = from + idx;

    if (nonce > to || *found_flag) {
        return;
    }

    char nonce_str[32];
    int nonce_len = 0;
    uint64_to_str(nonce, nonce_str, &nonce_len);

    int total_len = nonce_len + input_len;

    if (total_len >= MAX_MESSAGE_LEN) {
        return;
    }

    char buffer[MAX_MESSAGE_LEN];

    memcpy(buffer, nonce_str, nonce_len);
    memcpy(buffer + nonce_len, input, input_len);

    uint8_t digest[16];
    cuda_md5((uint8_t *)buffer, total_len, digest);

    if (starts_with_hex(digest, prefix, prefix_len)) {
        if (atomicCAS(found_flag, 0, 1) == 0) {
            *found_nonce = nonce;

            for (int i = 0; i < 16; i++) {
                found_digest[i] = digest[i];
            }
        }
    }
}

void write_json_empty() {
    FILE *file = fopen("json_output.txt", "w");

    if (!file) {
        fprintf(stderr, "No se pudo abrir json_output.txt\n");
        return;
    }

    fprintf(file, "{\"numero\": 0, \"hash_md5_result\": \"\"}");
    fclose(file);
}

void write_json_result(unsigned long long nonce, uint8_t *digest) {
    const char hex_digits[] = "0123456789abcdef";
    char hash_hex[33];

    for (int i = 0; i < 16; i++) {
        hash_hex[i * 2] = hex_digits[(digest[i] >> 4) & 0xF];
        hash_hex[i * 2 + 1] = hex_digits[digest[i] & 0xF];
    }

    hash_hex[32] = '\0';

    FILE *file = fopen("json_output.txt", "w");

    if (!file) {
        fprintf(stderr, "No se pudo abrir json_output.txt\n");
        return;
    }

    fprintf(
        file,
        "{\"numero\": %llu, \"hash_md5_result\": \"%s\"}",
        nonce,
        hash_hex
    );

    fclose(file);
}

int main(int argc, char *argv[]) {
    if (argc != 5) {
        printf("Uso: %s <from> <to> <prefix> <input>\n", argv[0]);
        return 1;
    }

    unsigned long long from = strtoull(argv[1], NULL, 10);
    unsigned long long to = strtoull(argv[2], NULL, 10);
    const char *prefix = argv[3];
    const char *input = argv[4];

    int input_len = strlen(input);
    int prefix_len = strlen(prefix);

    if (to < from) {
        write_json_empty();
        return 0;
    }

    if (input_len + 32 >= MAX_MESSAGE_LEN) {
        fprintf(stderr, "Input demasiado largo para MAX_MESSAGE_LEN\n");
        write_json_empty();
        return 1;
    }

    char *d_input = NULL;
    char *d_prefix = NULL;
    int *d_found_flag = NULL;
    unsigned long long *d_found_nonce = NULL;
    uint8_t *d_found_digest = NULL;

    cudaMalloc(&d_input, input_len);
    cudaMalloc(&d_prefix, prefix_len);
    cudaMalloc(&d_found_flag, sizeof(int));
    cudaMalloc(&d_found_nonce, sizeof(unsigned long long));
    cudaMalloc(&d_found_digest, 16);

    cudaMemcpy(d_input, input, input_len, cudaMemcpyHostToDevice);
    cudaMemcpy(d_prefix, prefix, prefix_len, cudaMemcpyHostToDevice);

    int zero = 0;
    unsigned long long zero_nonce = 0;
    uint8_t zero_digest[16] = {0};

    cudaMemcpy(d_found_flag, &zero, sizeof(int), cudaMemcpyHostToDevice);
    cudaMemcpy(d_found_nonce, &zero_nonce, sizeof(unsigned long long), cudaMemcpyHostToDevice);
    cudaMemcpy(d_found_digest, zero_digest, 16, cudaMemcpyHostToDevice);

    unsigned long long total = to - from + 1;
    unsigned long long blocks_64 = (total + THREADS - 1) / THREADS;

    if (blocks_64 > 2147483647ULL) {
        fprintf(stderr, "Rango demasiado grande para un solo kernel\n");
        write_json_empty();
        return 1;
    }

    int blocks = (int)blocks_64;

    cudaEvent_t start_event, stop_event;
    float elapsed = 0.0f;

    cudaEventCreate(&start_event);
    cudaEventCreate(&stop_event);

    cudaEventRecord(start_event);

    calculate_md5<<<blocks, THREADS>>>(
        d_input,
        input_len,
        d_prefix,
        prefix_len,
        from,
        to,
        d_found_flag,
        d_found_nonce,
        d_found_digest
    );

    cudaEventRecord(stop_event);
    cudaEventSynchronize(stop_event);
    cudaEventElapsedTime(&elapsed, start_event, stop_event);

    cudaError_t kernel_error = cudaGetLastError();

    if (kernel_error != cudaSuccess) {
        fprintf(stderr, "CUDA error: %s\n", cudaGetErrorString(kernel_error));
        write_json_empty();
        return 1;
    }

    int found_flag = 0;
    unsigned long long found_nonce = 0;
    uint8_t found_digest[16] = {0};

    cudaMemcpy(&found_flag, d_found_flag, sizeof(int), cudaMemcpyDeviceToHost);
    cudaMemcpy(&found_nonce, d_found_nonce, sizeof(unsigned long long), cudaMemcpyDeviceToHost);
    cudaMemcpy(found_digest, d_found_digest, 16, cudaMemcpyDeviceToHost);

    if (found_flag) {
        printf("Nonce encontrado: %llu\n", found_nonce);
        write_json_result(found_nonce, found_digest);
    } else {
        printf("No encontrado\n");
        write_json_empty();
    }

    printf("Tiempo CUDA: %.4f ms\n", elapsed);

    cudaFree(d_input);
    cudaFree(d_prefix);
    cudaFree(d_found_flag);
    cudaFree(d_found_nonce);
    cudaFree(d_found_digest);

    cudaEventDestroy(start_event);
    cudaEventDestroy(stop_event);

    return 0;
}
