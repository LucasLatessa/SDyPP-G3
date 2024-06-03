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

	uint32_to_hex(local_buffer, _nonce, 0);
	for ( int i = 8; i < 40; i++ ) {
		local_buffer[i] = buffer[i - 8];
	}
		
	cuda_md5(local_buffer, 40, result);
	
	//if ( (*nonce == 0) && starts_with(result, prefix, prefix_len) ) {
	//	printf("Voy a setear %d / %d\n", _nonce, *nonce);		
	//}
	//
	//if ( (*nonce != 0) && starts_with(result, prefix, prefix_len) ) {
	//	printf("Alguien me gano %d / %d\n", _nonce, *nonce);		
	//}
	//
	//*nonce = ( (*nonce == 0) && starts_with(result, prefix, prefix_len) ? _nonce : 0 );
	
	int i = 0;
	while ( *nonce == 0 && i <= _nonce ) {
		if ( (i == _nonce) && starts_with(result, prefix, prefix_len) ) {
			printf("Setea resultado %d / %d\n", _nonce, *nonce);
			*nonce = _nonce;
		}
		
		i++;
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
	//cudaMemcpy(dev_nonce, nonce, sizeof(int), cudaMemcpyHostToDevice);
	
	int threads = 512;
	int blocks  = round((to - from) / threads);
	/*
		There are multiple limits. 
		All must be satisfied.
	
		The maximum number of threads in the block is limited to 1024. 
		This is the product of whatever your threadblock dimensions are (xyz). 
		For example (32,32,1) creates a block of 1024 threads. (33,32,1) is not legal, since 33*32*1 > 1024.
	
		The maximum x-dimension is 1024. (1024,1,1) is legal. (1025,1,1) is not legal.
		The maximum y-dimension is 1024. (1,1024,1) is legal. (1,1025,1) is not legal.
		The maximum z-dimension is 64. (1,1,64) is legal. (2,2,64) is also legal. (1,1,65) is not legal.
	
		Also, threadblock dimensions of 0 in any position are not legal.
		Your choice of threadblock dimensions (x,y,z) must satisfy each of the rules 1-4 above.
	*/

	cuda_minero<<<blocks, threads>>>(dev_buffer, buffer_len, from, dev_prefix, prefix_len, dev_nonce);
	cudaDeviceSynchronize();
	
	cudaError_t error = cudaGetLastError();
	
	if (error != cudaSuccess) {
		printf("{ \"error\": true, \"cuda\": \"%s\" }", cudaGetErrorString(error));
		return 1;
	}
	
	int nonce = 0;
	cudaMemcpy(&nonce, dev_nonce, sizeof(int), cudaMemcpyDeviceToHost);
	
	cudaFree(dev_buffer);
	cudaFree(dev_prefix);
	cudaFree(dev_nonce);
	
	if ( nonce > 0 ) {
		printf("{ \"error\": false, \"nonce\": %d, \"hex\": \"%08x\" }", nonce, nonce);
	} else {
		printf("{ \"error\": true, \"from\": %d, \"to\": %d, \"prefix\": \"%s\", \"hash\": \"%s\" }", from, to, prefix, buffer);
	}

	return 0;
}