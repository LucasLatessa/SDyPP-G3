#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include "cuda_md5.cu"

__device__ bool starts_with(const uint8_t* hash, const uint8_t* prefix, int prefix_len) {
	for (int i = 0; i < prefix_len; ++i) {
		if (hash[i] != prefix[i])
			return false;
	}
	return true;
}

__global__ void cuda_minero(const uint8_t* buffer, size_t buffer_len, int from, const uint8_t* prefix, int prefix_len, int* nonce) {
	int _nonce = from + blockIdx.x * blockDim.x + threadIdx.x;
	
	uint8_t local_buffer[40];
	uint8_t result[32];

	// Prepare the buffer with the nonce and data
	uint32_to_hex(local_buffer, _nonce, 0);
	for (int i = 8; i < 40; i++) {
		local_buffer[i] = buffer[i - 8];
	}
		
	// Compute the MD5 hash
	cuda_md5(local_buffer, 40, result);
	
	// Check if the hash starts with the given prefix
	if (starts_with(result, prefix, prefix_len)) {
		// Attempt to set the nonce if it hasn't been set yet
		atomicCAS(nonce, 0, _nonce);
	}
}

int main(int argc, char *argv[]) {
	if (argc != 5) {
		printf("Use: miner FROM TO PREFIX HASH\n");
		printf("Where: \nFROM: integer\nTO: integer\nPREFIX: string\nHASH: string[32]\n");
		return 0;
	}
		
	int from = atoi(argv[1]);
	int to = atoi(argv[2]);
	
	const char* prefix = argv[3];
	const char* buffer = argv[4];
	
	size_t buffer_len = strlen(buffer);
	size_t prefix_len = strlen(prefix);

	uint8_t* dev_buffer;
	uint8_t* dev_prefix;
	int* dev_nonce;

	cudaMalloc((void**)&dev_buffer, (buffer_len + sizeof(int)) * sizeof(uint8_t));
	cudaMalloc((void**)&dev_prefix, prefix_len * sizeof(uint8_t));
	cudaMalloc((void**)&dev_nonce, sizeof(int));

	cudaMemcpy(dev_buffer, buffer, buffer_len * sizeof(uint8_t), cudaMemcpyHostToDevice);
	cudaMemcpy(dev_prefix, prefix, prefix_len * sizeof(uint8_t), cudaMemcpyHostToDevice);

	// Initialize nonce to 0 on the device
	int nonce = 0;
	cudaMemcpy(dev_nonce, &nonce, sizeof(int), cudaMemcpyHostToDevice);
	
	int threads = 512;
	int blocks  = (to - from + threads - 1) / threads; // Ensure all threads are covered

	// Launch the CUDA kernel
	cuda_minero<<<blocks, threads>>>(dev_buffer, buffer_len, from, dev_prefix, prefix_len, dev_nonce);
	cudaDeviceSynchronize();
	
	cudaError_t error = cudaGetLastError();
	
	if (error != cudaSuccess) {
		printf("{ \"error\": true, \"cuda\": \"%s\" }", cudaGetErrorString(error));
		return 1;
	}
	
	// Copy the nonce result back to the host
	cudaMemcpy(&nonce, dev_nonce, sizeof(int), cudaMemcpyDeviceToHost);
	
	// Free device memory
	cudaFree(dev_buffer);
	cudaFree(dev_prefix);
	cudaFree(dev_nonce);
	
	if (nonce > 0) {
		printf("{ \"error\": false, \"nonce\": %d, \"hex\": \"%08x\" }", nonce, nonce);
	} else {
		printf("{ \"error\": true, \"from\": %d, \"to\": %d, \"prefix\": \"%s\", \"hash\": \"%s\" }", from, to, prefix, buffer);
	}

	return 0;
}
