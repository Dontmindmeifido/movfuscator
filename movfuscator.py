# .data
#    lookup_mul: .space 65536 0, 1, 2...


# 8 bits
lookup_mul = ""
for op2 in range(256):
    for op1 in range(256):
        # At memory op1 + 255 * op2
        lookup_mul = lookup_mul + f"{op1+op2} "

print(lookup_mul)