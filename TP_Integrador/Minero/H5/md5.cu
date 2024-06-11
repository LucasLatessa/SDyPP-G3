// main.cu

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "cuda_md5.cu"

__device__ size_t num_digits(int num) {
    if (num == 0) return 1;
    size_t digits = 0;
    if (num < 0) digits++; // Contar el signo negativo
    while (num != 0) {
        num /= 10;
        digits++;
    }
    return digits;
}

__device__ void int_to_str(int num, char *str) {
    int i = 0;

    // Manejo del caso especial cuando num es 0
    if (num == 0) {
        str[0] = '0';
        str[1] = '\0';
        return;
    }

    // Manejo del caso negativo
    bool is_negative = false;
    if (num < 0) {
        is_negative = true;
        num = -num;
    }

    // Almacenamiento temporal de los dígitos en orden inverso
    char temp[64];
    while (num != 0) {
        temp[i++] = '0' + (num % 10);
        num /= 10;
    }

    // Si el número es negativo, añadir el signo negativo
    int j = 0;
    if (is_negative) {
        str[j++] = '-';
    }

    // Copiar los dígitos en orden correcto a str
    while (i > 0) {
        str[j++] = temp[--i];
    }

    // Añadir el terminador nulo
    str[j] = '\0';
}

__device__ bool starts_with(const uint8_t* hash, const uint8_t* prefix, int prefix_len) {  
    printf("hash: %s prefix: %s len: %d\n", hash, prefix, prefix_len); 
	for (int i = 0; i < prefix_len; ++i) {
		if ((char)hash[i] != (char)prefix[i])
			return false;
	}
    
	return true;

}

__device__ void byte_to_hex_div(const unsigned char* byte_array, char* hex_string, size_t length) {
    const char hex_digits[] = "0123456789abcdef";
    for (size_t i = 0; i < length; ++i) {
        hex_string[i * 2] = hex_digits[(byte_array[i] >> 4) & 0x0F];
        hex_string[i * 2 + 1] = hex_digits[byte_array[i] & 0x0F];
    }
    hex_string[length * 2] = '\0';
}

__global__
void calculate_md5(char* input,char* prefix,int input_len, int prefix_len, uint8_t* result, int* nonce, int from) {
    int _nonce = from + blockIdx.x * blockDim.x + threadIdx.x;
    char _nonce_num_str[64];
    size_t buffer_len = num_digits(_nonce) ;
    int suma = (input_len + buffer_len);
    
    char* concatenated_str = (char*)malloc(suma + 1);
    int_to_str(_nonce, _nonce_num_str);
    memcpy(concatenated_str, input, input_len);    
    memcpy(concatenated_str, _nonce_num_str, buffer_len);   
    //printf("%s\n",_nonce_num_str);
    memcpy(concatenated_str + buffer_len, input, input_len);

    concatenated_str[suma + 1] = '\0';
    printf("%s\n",concatenated_str);


    uint8_t *input_uint8 = reinterpret_cast<uint8_t*>(concatenated_str);
    uint8_t *prefix_uint8 = reinterpret_cast<uint8_t*>(prefix);

    uint8_t resultado[32];
    cuda_md5(input_uint8, suma, resultado);

    char hex_result[33];
    byte_to_hex_div(resultado,hex_result,16);
    uint8_t *resultado_uint8 = reinterpret_cast<uint8_t*>(hex_result);

    if (starts_with(resultado_uint8, prefix_uint8, prefix_len)){
        atomicCAS(nonce, -1, _nonce);
        memcpy(result, resultado_uint8, 32 * sizeof(uint8_t));
    }
}


int main(int argc, char *argv[]) {
    if (argc != 5) {
        fprintf(stderr, "Uso: %s <cadena>\n", argv[0]);
        return 1;
    }

    int from = atoi(argv[1]);
	int to = atoi(argv[2]);

    const char* prefix = argv[3];
    const char* input = argv[4];
    
    size_t input_len = strlen(input);
    size_t prefix_len = strlen(prefix);

    unsigned char result[16]; // MD5 produce un hash de 16 bytes

    char* d_input;
    char* d_prefix;
    unsigned char* d_result;
    int* dev_nonce;
    int nonce = -1;

    cudaMalloc(&d_input, input_len * sizeof(unsigned char));
    cudaMalloc(&d_prefix, prefix_len * sizeof(unsigned char));
    cudaMalloc(&d_result, 32 * sizeof(unsigned char));
    cudaMalloc((void**)&dev_nonce, sizeof(int));
    cudaMemcpy(dev_nonce, &nonce, sizeof(int), cudaMemcpyHostToDevice);
    cudaMemcpy(d_input,input, input_len * sizeof(char), cudaMemcpyHostToDevice);
    cudaMemcpy(d_prefix,prefix, prefix_len * sizeof(char), cudaMemcpyHostToDevice);

    int threads = 16;
    int blocks  = (to - from + threads - 1) / threads;;
    calculate_md5<<<blocks, threads>>>(d_input, d_prefix, input_len, prefix_len, d_result, dev_nonce, from);

    cudaDeviceSynchronize();
    cudaError_t error = cudaGetLastError();

    if (error != cudaSuccess) {
        printf("{ error: true, cuda: %s }", cudaGetErrorString(error));
        return 1;
    }
    cudaMemcpy(&nonce, dev_nonce, sizeof(int), cudaMemcpyDeviceToHost);
    cudaMemcpy(&result, d_result, 32 * sizeof(unsigned char), cudaMemcpyDeviceToHost);
    printf("Prefijo agregado: %d\n", nonce);

    printf("Hash MD5 de '%d%s': %s\n", nonce, input, result);

    cudaFree(d_input);
    cudaFree(d_result);
    

    return nonce;
}
