def add(op1, op2):
    fi = ""
    s = "   "
    for i in [0, 1, 2, 3]:
        fi += f"{s} mov $lookup_add, %ebp \n"
        fi += f"{s} movb {i}({op1}), %eax \n" #  Must save the values of registers
        fi += f"{s} movb {i}({op2}), %ebx \n" #  Must save the values of registers
        fi += f"{s} movb $ebp(%eax, %ebx, 255), {i}($temp_reg) \n"

    fi += f"{s} mov $temp_reg, {op2} \n"

    return fi

lookup_add = "1 2 3" # Placeholder for now
#for op2 in range(256):
#    for op1 in range(256):
#        # At memory op1 + 255 * op2
#        lookup_add = lookup_add + f"{op1+op2} "




out = open("out.as", "w")

with open("file.as", "r") as assembly:
    for line in assembly.readlines():
        # Add lookups to .data
        if (line.split(" ")[0][0:5] == ".data"):
            out.write(line)
            out.write(f"    lookup_add: .single 65536 {lookup_add} \n")
            out.write("    temp_reg: .space 4 \n")
        elif (line.split(" ")[0][0:5] == ".main"):
            out.write(line)
        else:
            if "add" in line:
                line = line.replace(",", "")
                op1 = line.split(" ")[1]
                op2 = line.split(" ")[2]
                out.write(add(op1, op2))
            else:
                out.write(line)
        
out.close()