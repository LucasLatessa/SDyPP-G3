#include <stdint.h>
#include <stdio.h>

__device__ uint32_t shifts[] = {  7, 12, 17, 22,  5,  9, 14, 20,  4, 11, 16, 23,  6, 10, 15, 21 };
__device__ uint32_t sines[]  = { 0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee, 0xf57c0faf, 0x4787c62a, 0xa8304613, 0xfd469501,
                                 0x698098d8, 0x8b44f7af, 0xffff5bb1, 0x895cd7be, 0x6b901122, 0xfd987193, 0xa679438e, 0x49b40821,
                                 0xf61e2562, 0xc040b340, 0x265e5a51, 0xe9b6c7aa, 0xd62f105d, 0x02441453, 0xd8a1e681, 0xe7d3fbc8,
                                 0x21e1cde6, 0xc33707d6, 0xf4d50d87, 0x455a14ed, 0xa9e3e905, 0xfcefa3f8, 0x676f02d9, 0x8d2a4c8a,
                                 0xfffa3942, 0x8771f681, 0x6d9d6122, 0xfde5380c, 0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70,
                                 0x289b7ec6, 0xeaa127fa, 0xd4ef3085, 0x04881d05, 0xd9d4d039, 0xe6db99e5, 0x1fa27cf8, 0xc4ac5665,
                                 0xf4292244, 0x432aff97, 0xab9423a7, 0xfc93a039, 0x655b59c3, 0x8f0ccc92, 0xffeff47d, 0x85845dd1,
                                 0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1, 0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391 };

__device__ uint32_t left_rotate(uint32_t x, uint32_t c) {
    return ((x << c) | (x >> (32 - c)));
}

__device__ void cuda_md5(const uint8_t* initial_msg, size_t initial_len, uint8_t* digest) {
    uint32_t h0, h1, h2, h3;

    // These vars will contain the hash
    h0 = 0x67452301;
    h1 = 0xefcdab89;
    h2 = 0x98badcfe;
    h3 = 0x10325476;

    int new_len = ((((initial_len + 8) / 64) + 1) * 64) - 8;

    uint8_t* msg = (uint8_t*)malloc(new_len + 64);
    memcpy(msg, initial_msg, initial_len);
    msg[initial_len] = 128; // append the "1" bit; most significant bit is "1"
    for (int i = initial_len + 1; i < new_len; i++) {
        msg[i] = 0; // append "0" bits
    }

    uint64_t bits_len = 8 * initial_len;
    memcpy(msg + new_len, &bits_len, 8); // in little-endian

    for (int offset = 0; offset < new_len; offset += 64) {
        uint32_t* w = (uint32_t*)(msg + offset);
        uint32_t a = h0, b = h1, c = h2, d = h3;

        for (int i = 0; i < 64; i++) {
            uint32_t f, g;

            if (i < 16) {
                f = (b & c) | ((~b) & d);
                g = i;
            } else if (i < 32) {
                f = (d & b) | ((~d) & c);
                g = (5 * i + 1) % 16;
            } else if (i < 48) {
                f = b ^ c ^ d;
                g = (3 * i + 5) % 16;
            } else {
                f = c ^ (b | (~d));
                g = (7 * i) % 16;
            }

            uint32_t temp = d;
            d = c;
            c = b;
            b = b + left_rotate((a + f + sines[i] + w[g]), shifts[(i / 16) * 4 + (i % 4)]);
            a = temp;
        }

        h0 += a;
        h1 += b;
        h2 += c;
        h3 += d;
    }

    free(msg);

    ((uint32_t*)digest)[0] = h0;
    ((uint32_t*)digest)[1] = h1;
    ((uint32_t*)digest)[2] = h2;
    ((uint32_t*)digest)[3] = h3;
}