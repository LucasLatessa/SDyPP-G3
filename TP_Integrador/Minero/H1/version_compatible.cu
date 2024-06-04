#include <stdio.h>

#define gpuErrchk(ans) { gpuAssert(ans); }
inline void gpuAssert(cudaError_t code) {
	if (code != cudaSuccess) {
    	fprintf(stderr, "GPUassert:%s\n",
                     cudaGetErrorString(code));
    	exit(code);
	}
}

int main() {
    gpuErrchk( cudaDeviceSynchronize() );
	return 0;
}
