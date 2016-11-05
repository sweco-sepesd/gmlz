def crc32_combine(crc1, crc2, len2):
    """Explanation algorithm: http://stackoverflow.com/a/23126768/654160
    crc32(crc32(0, seq1, len1), seq2, len2) == crc32_combine(
        crc32(0, seq1, len1), crc32(0, seq2, len2), len2)"""
    # degenerate case (also disallow negative lengths)
    if len2 <= 0:
        return crc1

    # put operator for one zero bit in odd
    # CRC-32 polynomial, 1, 2, 4, 8, ..., 1073741824
    odd = [0xedb88320] + [1 << i for i in range(0, 31)]
    even = [0] * 32

    def matrix_times(matrix, vector):
        number_sum = 0
        matrix_index = 0
        while vector != 0:
            if vector & 1:
                number_sum ^= matrix[matrix_index]
            vector = vector >> 1 & 0x7FFFFFFF
            matrix_index += 1
        return number_sum

    # put operator for two zero bits in even - gf2_matrix_square(even, odd)
    even[:] = [matrix_times(odd, odd[n]) for n in range(0, 32)]

    # put operator for four zero bits in odd
    odd[:] = [matrix_times(even, even[n]) for n in range(0, 32)]

    # apply len2 zeros to crc1 (first square will put the operator for one
    # zero byte, eight zero bits, in even)
    while len2 != 0:
        # apply zeros operator for this bit of len2
        even[:] = [matrix_times(odd, odd[n]) for n in range(0, 32)]
        if len2 & 1:
            crc1 = matrix_times(even, crc1)
        len2 >>= 1

        # if no more bits set, then done
        if len2 == 0:
            break

        # another iteration of the loop with odd and even swapped
        odd[:] = [matrix_times(even, even[n]) for n in range(0, 32)]
        if len2 & 1:
            crc1 = matrix_times(odd, crc1)
        len2 >>= 1

        # if no more bits set, then done
    # return combined crc
    crc1 ^= crc2
    return crc1
