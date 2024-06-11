    // main.cu

    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include "cuda_md5.cu"

    __global__
    void calculate_md5(const unsigned char* input, unsigned long long input_len, unsigned char* result) {
        cuda_md5(input, input_len, result);
        printf("%s", result);
    }

    void byte_to_hex(const unsigned char* byte_array, char* hex_string, size_t length) {
        const char hex_digits[] = "0123456789abcdef";
        for (size_t i = 0; i < length; ++i) {
            hex_string[i * 2] = hex_digits[(byte_array[i] >> 4) & 0x0F];
            hex_string[i * 2 + 1] = hex_digits[byte_array[i] & 0x0F];
        }
        hex_string[length * 2] = '\0'; // Null-terminate the string
    }

    int main(int argc, char *argv[]) {
        if (argc != 2) {
            fprintf(stderr, "Uso: %s <cadena>\n", argv[0]);
            return 1;
        }

        const char* input = argv[1];
        size_t input_len = strlen(input);

        unsigned char result[16]; // MD5 produce un hash de 16 bytes

        unsigned char* d_input;
        unsigned char* d_result;
        cudaMalloc(&d_input, input_len * sizeof(unsigned char));
        cudaMalloc(&d_result, 16 * sizeof(unsigned char));
        cudaMemcpy(d_input, reinterpret_cast<const unsigned char*>(input), input_len * sizeof(unsigned char), cudaMemcpyHostToDevice);

        calculate_md5<<<1, 1>>>(d_input, input_len, d_result);

        cudaMemcpy(result, d_result, 16 * sizeof(unsigned char), cudaMemcpyDeviceToHost);

        char hex_result[33]; // 32 hex characters + null terminator
        byte_to_hex(result, hex_result, 16);

        printf("Hash MD5 de '%s': %s\n", input, hex_result);

        cudaFree(d_input);
        cudaFree(d_result);

        return 0;
    }
