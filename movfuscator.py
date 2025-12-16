lookup_add = ""
for op1 in range(256):
    for op2 in range(256):
        lookup_add += str(op1 + op2) + " "

def add(op1, op2):
    ret = ""
    ret += "movl $lookup_add, %ebx\n"
    ret += f"movl ${op1}, %esi\n"
    ret += f"movl ${op2}, %edi\n"
    
    for i in ["0", "1", "2", "3"]:
        ret += "movl $0, %eax\n"
        ret += f"movb {i}(%esi), %ah\n"
        ret += f"movb {i}(%edi), %al\n"
        ret += "movb (%ebx, %eax), %dl\n"
        ret += f"movb %dl, {i}(%edi)\n"

    return ret

def inc(op):
    ret = ""
    
    ret += add("$1", op)

    return ret

def mul(op1, op2):
    ret += ""
    # Save op2 original somewhere for multiplication
    for i in range(len(256)):
        ret += f"mov $op2, ($1001)\n"
        ret += f"mov $0, ($1000)\n"


        ret += f"mov ${i}, %eax\n"
        ret += f"mov {op1}, %ebx\n"
        ret += f"mov $0, (%eax)\n"
        ret += f"mov $1, (%ebx)\n"
        ret += f"mov (%eax), %ecx\n"
        ret += f"mov %1000($1, %ecx), %ecx\n"

        ret += f"mov %ecx, {op2}\n"
        ret += add(op2, op2)
        ret += f"mov ($1001), {op2}\n"

def shl(op1, op2):
    ret += ""
    for i in range(len(256)):
        ret += f"mov $op2, ($1001)\n"
        ret += f"mov $0, ($1000)\n"


        ret += f"mov ${i}, %eax\n"
        ret += f"mov {op1}, %ebx\n"
        ret += f"mov $0, (%eax)\n"
        ret += f"mov $1, (%ebx)\n"
        ret += f"mov (%eax), %ecx\n"
        ret += f"mov %1000($1, %ecx), %ecx\n"

        ret += f"mov %ecx, {op2}\n"
        ret += add(op2, op2)
        ret += f"mov ($1001), {op2}\n"


out = open("out.asm", "w")

with open("file.asm", "r") as assembly:
    for line in assembly.readlines():
        # Add lookups to .data
        if (line.split(" ")[0][0:5] == ".data"):
            out.write(line)
            out.write(f"    lookup_add: .single 65536 {lookup_add} \n")
            out.write("    temp: .space 4 \n")
        elif (line.split(" ")[0][0:5] == ".main"):
            out.write(line)
        else:
            if "add" in line:
                line = line.replace(",", "")
                args= line.split(" ")
                op1 = args[1]
                op2 = args[2]
                out.write(add(op1, op2))
            elif "mul" in line:
                line = line.replace(",", "")
                args= line.split(" ")
                op1 = args[1]
                op2 = args[2]
                out.write(mul(op1, op2))
            elif "shl" in line:
                line = line.replace(",", "")
                args= line.split(" ")
                op1 = args[1]
                op2 = args[2]
                out.write(mul(op1, op2))
            elif "inc" in line:
                args= line.split(" ")
                op = args[1]
                out.write(inc(op))
            else:
                out.write(line)
        
out.close()