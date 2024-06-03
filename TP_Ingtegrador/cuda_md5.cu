/**
 **********************************************************************
 ** Copyright (C) 1990, RSA Data Security, Inc. All rights reserved. **
 **                                                                  **
 ** License to copy and use this software is granted provided that   **
 ** it is identified as the "RSA Data Security, Inc. MD5 Message     **
 ** Digest Algorithm" in all material mentioning or referencing this **
 ** software or this function.                                       **
 **                                                                  **
 ** License is also granted to make and use derivative works         **
 ** provided that such works are identified as "derived from the RSA **
 ** Data Security, Inc. MD5 Message Digest Algorithm" in all         **
 ** material mentioning or referencing the derived work.             **
 **                                                                  **
 ** RSA Data Security, Inc. makes no representations concerning      **
 ** either the merchantability of this software or the suitability   **
 ** of this software for any particular purpose.  It is provided "as **
 ** is" without express or implied warranty of any kind.             **
 **                                                                  **
 ** These notices must be retained in any copies of any part of this **
 ** documentation and/or software.                                   **
 **********************************************************************
 */

__device__ uint32_t shifts[] = {  7, 12, 17, 22,
                                  5,  9, 14, 20,
																	4, 11, 16, 23,
																	6, 10, 15, 21 };

__device__ uint32_t sines[]  = { 0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee,
																 0xf57c0faf, 0x4787c62a, 0xa8304613, 0xfd469501,
																 0x698098d8, 0x8b44f7af, 0xffff5bb1, 0x895cd7be,
																 0x6b901122, 0xfd987193, 0xa679438e, 0x49b40821,
																 0xf61e2562, 0xc040b340, 0x265e5a51, 0xe9b6c7aa,
																 0xd62f105d, 0x02441453, 0xd8a1e681, 0xe7d3fbc8,
																 0x21e1cde6, 0xc33707d6, 0xf4d50d87, 0x455a14ed,
																 0xa9e3e905, 0xfcefa3f8, 0x676f02d9, 0x8d2a4c8a,
																 0xfffa3942, 0x8771f681, 0x6d9d6122, 0xfde5380c,
																 0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70,
																 0x289b7ec6, 0xeaa127fa, 0xd4ef3085, 0x04881d05,
																 0xd9d4d039, 0xe6db99e5, 0x1fa27cf8, 0xc4ac5665,
																 0xf4292244, 0x432aff97, 0xab9423a7, 0xfc93a039,
																 0x655b59c3, 0x8f0ccc92, 0xffeff47d, 0x85845dd1,
																 0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1,
																 0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391 };

__device__ uint32_t left_rotate(uint32_t x, uint32_t c) {
	return ((x << c) | (x >> (32 - c)));
}

__device__ void uint32_to_hex(uint8_t *str, uint32_t num, int skip) {
	const char *hex_digits = "0123456789abcdef";

	for ( int i = 0; i < 8; i++ ) {
		str[skip + i] = hex_digits[(num >> (28 - 4 * i)) & 0xF];
	}
}

__device__ void cuda_md5(const uint8_t* buffer, size_t buffer_len, uint8_t* result) {
	int blocks = (buffer_len + 8) / 64 + 1;

	uint32_t aa = 0x67452301;
	uint32_t bb = 0xefcdab89;
	uint32_t cc = 0x98badcfe;
	uint32_t dd = 0x10325476;

	for (int i = 0; i < blocks; i++) {
		const uint8_t* block = buffer;
		int offset = i * 64;

		if (offset + 64 > buffer_len) {
			uint8_t* padded_block = (uint8_t*)malloc(64);

			for (int j = offset; j < buffer_len; j++) {
					padded_block[j - offset] = buffer[j];
			}
			
			if (offset <= buffer_len) {
					padded_block[buffer_len - offset] = 0x80;
			}
			
			if (i == blocks - 1) {
					padded_block[56] = (uint8_t)(buffer_len << 3);
					padded_block[57] = (uint8_t)(buffer_len >> 5);
					padded_block[58] = (uint8_t)(buffer_len >> 13);
					padded_block[59] = (uint8_t)(buffer_len >> 21);
			}

			block = padded_block;
			offset = 0;
		}

		uint32_t a = aa;
		uint32_t b = bb;
		uint32_t c = cc;
		uint32_t d = dd;

		uint32_t f;
		int g;

		for (int j = 0; j < 64; j++) {
			if (j < 16) {
					f = (b & c) | (~b & d);
					g = j;
			}
			else if (j < 32) {
					f = (b & d) | (c & ~d);
					g = 5 * j + 1;
			}
			else if (j < 48) {
					f = b ^ c ^ d;
					g = 3 * j + 5;
			}
			else {
					f = c ^ (b | ~d);
					g = 7 * j;
			}

			g = (g & 0x0f) * 4 + offset;

			uint32_t hold = d;
			d = c;
			c = b;

			b = a + f + sines[j] + (uint32_t)(block[g] + (block[g + 1] << 8) + (block[g + 2] << 16) + (block[g + 3] << 24));
			b = b << shifts[j & 3 | j >> 2 & ~3] | b >> 32 - shifts[j & 3 | j >> 2 & ~3];
			b += c;

			a = hold;
		}

		aa += a;
		bb += b;
		cc += c;
		dd += d;

		if (offset != 0)
			free((void*)block);
	}
	
	uint32_to_hex(result, aa,  0);
	uint32_to_hex(result, bb,  8);
	uint32_to_hex(result, cc, 16);
	uint32_to_hex(result, dd, 24);
}