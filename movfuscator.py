# .data
#    lookup_add: .space 65536 0, 1, 2...


# 8 bits
lookup_add = ""
for op2 in range(256):
    for op1 in range(256):
        # At memory op1 + 255 * op2
        lookup_add = lookup_add + f"{op1+op2} "
