#--------------- HELP ---------------#
# top1 - temporary operand 1
# top2 - temporary operand 2
# tax - temporary register eax
# tbx - temporary register ebx
# .
# .
# .
# tdi - temporary register edi
# lookup_add - lookup table for add
# lookup_andd - lookup table for and (and is unavailable)
# lookup_orr - lookup table for or (or is unavailable)
# lookup_nott - lookup table for not (not is unavailable)
# lookup_xor - lookup table for xor
#--------------- HELP ---------------#



lookup_add = ""
for op1 in range(256):
    for op2 in range(256):
        lookup_add += str((op1 + op2) & 0xFF) + ", "
lookup_add = lookup_add[0: -2]

lookup_andd = ""
for op1 in range(256):
    for op2 in range(256):
        lookup_andd += str((op1 & op2) & 0xFF) + ", "
lookup_andd = lookup_andd[0: -2]

lookup_orr = ""
for op1 in range(256):
    for op2 in range(256):
        lookup_orr += str((op1 | op2) & 0xFF) + ", "
lookup_orr = lookup_orr[0: -2]

lookup_nott = ""
for op in range(256):
    lookup_nott += str((~op) & 0xFF) + ", "
lookup_nott = lookup_nott[0: -2]

lookup_xor = ""
for op1 in range(256):
    for op2 in range(256):
        lookup_xor += str((op1 ^ op2) & 0xFF) + ", "
lookup_xor = lookup_xor[0: -2]

def save_registers():
    ret = ""
    ret += "movl %eax, tax\n"
    ret += "movl %ebx, tbx\n"
    ret += "movl %ecx, tcx\n"
    ret += "movl %edx, tdx\n"
    ret += "movl %esi, tsi\n"
    ret += "movl %edi, tdi\n"
    return ret

def restore_registers():
    ret = ""
    ret += "movl tax, %eax\n"
    ret += "movl tbx, %ebx\n"
    ret += "movl tcx, %ecx\n"
    ret += "movl tdx, %edx\n"
    ret += "movl tsi, %esi\n"
    ret += "movl tdi, %edi\n"
    return ret

def add(op1, op2):
    ret = ""

    ret += save_registers()

    ret += "movl $lookup_add, %ebx\n"

    ret += f"movl {op1}, %esi\n"
    ret += f"movl {op2}, %edi\n"

    ret += f"movl %esi, top1\n"
    ret += f"movl %edi, top2\n"

    ret += f"movl $top1, %esi\n"
    ret += f"movl $top2, %edi\n"
    
    for i in ["0", "1", "2", "3"]:
        ret += "movl $0, %eax\n"

        ret += f"movb {i}(%esi), %ah\n"
        ret += f"movb {i}(%edi), %al\n"

        ret += "movb (%ebx, %eax), %dl\n"
        ret += f"movb %dl, {i}(%edi)\n"

    ret += restore_registers()

    if op2.startswith("%"):
        ret += f"movl top2, {op2}\n"
    elif op2.startswith("$"):
        ret += f"movl top2, %eax\n"
        ret += f"movl %eax, {op2[1:]}\n"  
    else:
        ret += f"movl top2, %eax\n"
        ret += f"movl %eax, {op2}\n" 

    return ret

def inc(op):
    ret = ""
    
    ret += add("$1", op)

    return ret

def andd(op1, op2):
    ret = ""

    ret += save_registers()

    ret += "movl $lookup_andd, %ebx\n"

    ret += f"movl {op1}, %esi\n"
    ret += f"movl {op2}, %edi\n"

    ret += f"movl %esi, top1\n"
    ret += f"movl %edi, top2\n"

    ret += f"movl $top1, %esi\n"
    ret += f"movl $top2, %edi\n"
    
    for i in ["0", "1", "2", "3"]:
        ret += "movl $0, %eax\n"

        ret += f"movb {i}(%esi), %ah\n"
        ret += f"movb {i}(%edi), %al\n"

        ret += "movb (%ebx, %eax), %dl\n"
        ret += f"movb %dl, {i}(%edi)\n"

    ret += restore_registers()

    if op2.startswith("%"):
        ret += f"movl top2, {op2}\n"
    elif op2.startswith("$"):
        ret += f"movl top2, %eax\n"
        ret += f"movl %eax, {op2[1:]}\n"  
    else:
        ret += f"movl top2, %eax\n"
        ret += f"movl %eax, {op2}\n" 

    return ret

def orr(op1, op2):
    ret = ""

    ret += save_registers()

    ret += "movl $lookup_orr, %ebx\n"

    ret += f"movl {op1}, %esi\n"
    ret += f"movl {op2}, %edi\n"

    ret += f"movl %esi, top1\n"
    ret += f"movl %edi, top2\n"

    ret += f"movl $top1, %esi\n"
    ret += f"movl $top2, %edi\n"
    
    for i in ["0", "1", "2", "3"]:
        ret += "movl $0, %eax\n"

        ret += f"movb {i}(%esi), %ah\n"
        ret += f"movb {i}(%edi), %al\n"

        ret += "movb (%ebx, %eax), %dl\n"
        ret += f"movb %dl, {i}(%edi)\n"

    ret += restore_registers()

    if op2.startswith("%"):
        ret += f"movl top2, {op2}\n"
    elif op2.startswith("$"):
        ret += f"movl top2, %eax\n"
        ret += f"movl %eax, {op2[1:]}\n"  
    else:
        ret += f"movl top2, %eax\n"
        ret += f"movl %eax, {op2}\n" 

    return ret

def nott(op):
    ret = ""

    ret += save_registers()

    ret += "movl $lookup_nott, %ebx\n"

    ret += f"movl {op}, %esi\n"

    ret += f"movl %esi, top1\n"

    ret += f"movl $top1, %esi\n"
    
    for i in ["0", "1", "2", "3"]:
        ret += "movl $0, %eax\n"

        ret += f"movb {i}(%esi), %al\n"

        ret += "movb (%ebx, %eax), %dl\n"
        ret += f"movb %dl, {i}(%esi)\n"

    ret += restore_registers()

    if op.startswith("%"):
        ret += f"movl top1, {op}\n"
    elif op.startswith("$"):
        ret += f"movl top1, %eax\n"
        ret += f"movl %eax, {op[1:]}\n"  
    else:
        ret += f"movl top1, %eax\n"
        ret += f"movl %eax, {op}\n" 

    return ret

def xor(op1, op2):
    ret = ""

    ret += save_registers()

    ret += "movl $lookup_xor, %ebx\n"

    ret += f"movl {op1}, %esi\n"
    ret += f"movl {op2}, %edi\n"

    ret += f"movl %esi, top1\n"
    ret += f"movl %edi, top2\n"

    ret += f"movl $top1, %esi\n"
    ret += f"movl $top2, %edi\n"
    
    for i in ["0", "1", "2", "3"]:
        ret += "movl $0, %eax\n"

        ret += f"movb {i}(%esi), %ah\n"
        ret += f"movb {i}(%edi), %al\n"

        ret += "movb (%ebx, %eax), %dl\n"
        ret += f"movb %dl, {i}(%edi)\n"

    ret += restore_registers()

    if op2.startswith("%"):
        ret += f"movl top2, {op2}\n"
    elif op2.startswith("$"):
        ret += f"movl top2, %eax\n"
        ret += f"movl %eax, {op2[1:]}\n"  
    else:
        ret += f"movl top2, %eax\n"
        ret += f"movl %eax, {op2}\n" 

    return ret

out = open("out.s", "w")

with open("in.s", "r") as assembly:
    for line in assembly.readlines():
        line = line.strip()

        if not line:
            continue

        # Add lookups to .data
        if (line.split()[0] == ".data"):
            out.write(line + "\n")
            out.write(f"    lookup_add: .byte {lookup_add} \n")
            out.write(f"    lookup_andd: .byte {lookup_andd} \n")
            out.write(f"    lookup_orr: .byte {lookup_orr} \n")
            out.write(f"    lookup_nott: .byte {lookup_nott} \n")
            out.write(f"    lookup_xor: .byte {lookup_xor} \n")

            out.write("    tax: .space 4\n")
            out.write("    tbx: .space 4\n")
            out.write("    tcx: .space 4\n")
            out.write("    tdx: .space 4\n")
            out.write("    tsi: .space 4\n")
            out.write("    tdi: .space 4\n")
            
            out.write("    top1: .space 4 \n")
            out.write("    top2: .space 4 \n")
        elif (line.split()[0] == ".main"):
            out.write(line + "\n")
            # For future use to generate lookup tables ok
        else:
            if line.split()[0] == "inc":
                args= line.split()
                op = args[1]
                out.write(inc(op))
            elif line.split()[0] == "add":
                line = line.replace(",", " ")
                args= line.split()
                op1 = args[1]
                op2 = args[2]
                out.write(add(op1, op2))
            elif line.split()[0] == "and":
                line = line.replace(",", " ")
                args= line.split()
                op1 = args[1]
                op2 = args[2]
                out.write(andd(op1, op2))
            elif line.split()[0] == "or":
                line = line.replace(",", " ")
                args= line.split()
                op1 = args[1]
                op2 = args[2]
                out.write(orr(op1, op2))
            elif line.split()[0] == "not":
                args= line.split()
                op = args[1]
                out.write(nott(op))
            elif line.split()[0] == "xor":
                line = line.replace(",", " ")
                args= line.split()
                op1 = args[1]
                op2 = args[2]
                out.write(xor(op1, op2))
            else:
                out.write(line + "\n")
        
out.close()