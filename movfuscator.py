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

lookup_div2 = ""
for i in range(256):
    lookup_div2 +=str(i // 2)+", "
lookup_div2 = lookup_div2[0: -2]


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

# KNOWN ISSUES: OVERFLOW
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

    # Potentially add another add function that simply writes to eax --TODO--
    if op2.startswith("%"):
        ret += f"movl top2, {op2}\n"
    elif op2.startswith("$"):
        ret += f"movl top2, %eax\n"
        ret += f"movl %eax, {op2[1:]}\n"  
    else:
        ret += f"movl top2, %eax\n"
        ret += f"movl %eax, {op2}\n" 

    return ret

def trlupdprogexec(op1, op2):
    '''
    Trailing update program execution
    
    :param op1: variable
    :param op2: constant
    '''
    ret = ""

    ret += save_registers()

    # Initialize
    ret += "movl $eqtrash, %eax\n"
    ret += f"movl {op1}, %ebx\n"
    ret += f"movl {op2}, %ecx\n"
    ret += "movl progexec, %edx\n"

    # Check equality
    ret += "movl $0, %esi\n"
    ret += "movl %esi, (%eax, %ebx, 4)\n"

    ret += "movl $1, %esi\n"
    ret += "movl %esi, (%eax, %ecx, 4)\n"

    # Get result and do (result or progexec value)
    ret += "movl (%eax, %ebx, 4), %eax\n"
    ret += orr("%eax", "%edx\n")

    # Update progexec with the latest state
    ret += "movl %edx, progexec\n"

    ret += restore_registers()

    return ret

# KNOWN ISSUES: OFERLOWS, IT IS ONLY ON 32 bits. LIMITATION: op1 on 1 byte.
def mul(op1, op2):
    '''
    ATTENTION: MUL SAVES RESULT IN EAX (as opposed to add which saves to destination operand)
    
    :param op1: operand 1
    :param op2: operand 2
    '''
    ret = ""

    ret += save_registers()

    # Initialize branch
    ret += "movl $branch, %edi\n"

    ret += "movl $0, %eax\n"
    ret += "movl $topm1, %ebx\n" # we will save the real branch at the adress of topm1 (Be careful, progexec initially starts at 0 so we want that)
    ret += "movl %ebx, (%edi, %eax, 4)\n"

    ret += "movl $1, %eax\n"
    ret += "movl $topm2, %ebx\n" # we will save the fake branch at the adress of topm2 (Be careful, progexec initially starts at 0 so we want that)
    ret += "movl %ebx, (%edi, %eax, 4)\n"

    # Initialize variables
    ret += f"movl {op2}, %ebx\n"
    ret += "movl $0, %ecx\n"
    ret += f"movb {op1}, %cl\n"

    ret += "movl $0, %edx\n"
    ret += "movl %edx, topm1\n"


    for i in range(256):
        # Do the addition %edx with op2
        ret += add(f"{op2}", "%edx")

        # Update progexec (%ecx is op1)
        ret += trlupdprogexec("%ecx", f"{i}")

        # Save the result to branch (if we wrote to it good, if not then also good)
        ret += "movl progexec, %eax\n"
        ret += "movl (%edi, %eax, 4), %esi\n"
        ret += "movl %edx, (%esi)\n" 

        ret += "movl topm1, %edx\n"
    
    ret += restore_registers()

    # Final result will be in eax
    ret += "movl topm1, %eax"

    return ret

def shl(op1, op2):
    '''
    Shift left (AlSO SAVES IN EAX)

    :param op1: shift left amount
    :param op2: operand to shift
    '''
    ret = ""

    ret += save_registers()

    # Initialize branch
    ret += "movl $branch, %edi\n"

    ret += "movl $0, %eax\n"
    ret += "movl $topm1, %ebx\n" # we will save the real branch at the adress of topm1 (Be careful, progexec initially starts at 0 so we want that)
    ret += "movl %ebx, (%edi, %eax, 4)\n"

    ret += "movl $1, %eax\n"
    ret += "movl $topm2, %ebx\n" # we will save the fake branch at the adress of topm2 (Be careful, progexec initially starts at 0 so we want that)
    ret += "movl %ebx, (%edi, %eax, 4)\n"

    # Initialize variables
    ret += "movl $0, %ecx\n"
    ret += f"movb {op1}, %cl\n"

    ret += f"movl {op2}, %edx\n"
    ret += "movl %edx, topm1\n"


    for i in range(256):
        # Multiply by 2, save in edx
        ret += add("%edx", "%edx")

        # Update progexec (%ecx is op1)
        ret += trlupdprogexec("%ecx", f"{i}")

        # Save the result to branch (if we wrote to it good, if not then also good)
        ret += "movl progexec, %eax\n"
        ret += "movl (%edi, %eax, 4), %esi\n"
        ret += "movl %edx, (%esi)\n" 

        ret += "movl topm1, %edx\n" # This ensures edx is always updated with the necessary value after branching,
                                  # Even though it got corrupted during the add (writing to itself a value not needed to execute by progexec)
    
    ret += restore_registers()

    # Final result will be in eax
    ret += "movl topm1, %eax\n"

    return ret


def shr(op1, op2):
    ret = ""

    ret += save_registers()

    # Initialize branch
    ret += "movl $branch, %edi\n"

    ret += "movl $0, %eax\n"
    ret += "movl $topm1, %ebx\n" # we will save the real branch at the adress of topm1 (Be careful, progexec initially starts at 0 so we want that)
    ret += "movl %ebx, (%edi, %eax, 4)\n"

    ret += "movl $1, %eax\n"
    ret += "movl $topm2, %ebx\n" # we will save the fake branch at the adress of topm2 (Be careful, progexec initially starts at 0 so we want that)
    ret += "movl %ebx, (%edi, %eax, 4)\n"

    # Initialize variables
    ret += "movl $0, %ecx\n"
    ret += f"movb {op1}, %cl\n"

    ret += f"movl {op2}, %edx\n"
    ret += "movl %edx, topm1\n"


    for i in range(256):
        # Multiply by 2, save in edx
        ret += "movl $lookup_div2, %ebp\n"
        for j in ["0", "1", "2", "3"]:
            ret += "movl $0, %eax\n"
            ret += f"movb {j}(%edx), %al\n"
            ret += "movb (%ebp, %eax), %al\n"
            ret += f"movb %al, {j}(%edx)\n"
        ret += trlupdprogexec("%ecx", f"{i}")


        ret +="movl progexec, %eax\n"
        ret += "movl (%edi, %eax, 4), %esi\n"
        ret += "movl %edx, (%esi)\n" 
        ret+= "movl topm1, %edx\n"
    
    ret += restore_registers()

    # Final result will be in eax
    ret += "movl topm1, %eax\n"

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

def sub(op1, op2):
    ret = ""

    ret += "movl %eax, topm2\n"

    ret += f"movl {op1}, %eax\n"
    ret += "movl %eax, topm1\n"

    ret += "movl topm2, %eax\n"

    ret += nott("topm1")
    ret += inc("topm1")

    ret += add("topm1", f"{op2}")

    return ret

def dec(op):
    ret = ""

    ret += sub("$1", op)

    return ret


def divv(op1, op2): 
    ret = ""
    ret+=save_registers()
    ret+="movl $branch, %edi\n"
    ret+="movl $0, %eax\n"
    ret+="movl $rez, %ebx\n"
    ret+="movl %ebx, (%edi, %eax, 4)\n"
    ret+="movl $1, %eax\n"
    ret += 'movl $trash, %ebx\n'
    ret += 'movl %ebx, (%edi, %eax, 4)\n'

    ret+=f"movl {op2}, %edx\n"
    ret+='movl $0, %eax\n'
    ret+='movl %eax, rez\n'
    ret+='movl %eax, progexec\n'


    for i in range(256):
        ret+=sub(op1, "%edx")
        ret+=add("$1", "rez")
        ret+="movl rez, %eax\n"
        ret+="movl %eax, next_val\n"
        ret+=trlupdprogexec("%edx", "$0")



        ret+= "movl progexec, %eax\n"
        ret +="movl (%edi, %eax, 4), %esi\n"
        ret +="movl next_val, %eax\n"
        ret+= "movl %eax, (%esi)\n"

    ret += restore_registers()
    ret+="movl rez, %eax\n"

    return ret


out = open("out.s", "w")
with open("in.s", "r") as assembly:
    for line in assembly.readlines():
        line = line.strip()

        if not line:
            continue

        if (line.split()[0] == ".data"):
            out.write(line + "\n")
            out.write(f"    lookup_add: .byte {lookup_add} \n") # lookup table for add
            out.write(f"    lookup_andd: .byte {lookup_andd} \n") # lookup table for and
            out.write(f"    lookup_orr: .byte {lookup_orr} \n") # lookup table for or
            out.write(f"    lookup_nott: .byte {lookup_nott} \n") # lookup table for not
            out.write(f"    lookup_xor: .byte {lookup_xor} \n") # lookup table for xor
            out.write(f"    lookup_div2: .byte {lookup_div2} \n")

            out.write("    tax: .space 4\n") # temporary space for register eax
            out.write("    tbx: .space 4\n") # temporary space for register ebx
            out.write("    tcx: .space 4\n") # temporary space for register ecx
            out.write("    tdx: .space 4\n") # temporary space for register edx
            out.write("    tsi: .space 4\n") # temporary space for register esi
            out.write("    tdi: .space 4\n") # temporary space for register edi
            
            out.write("    top1: .space 4 \n") # temporary space for add func operand 1
            out.write("    top2: .space 4 \n") # temporary space for add func operand 2
            out.write("    topm1: .space 4 \n") # temporary space for mul func operand 1
            out.write("    topm2: .space 4 \n") # temporary space for mul func operand 2

            out.write("    next_val: .space 4 \n") #next cat
            out.write("    rez: .space 4\n") #div?
            out.write("    trash: .space 4\n") #temporary space for trashing ;)


            out.write("    progexec: .space 4 \n") # dictates program flow
            out.write("    branch: .space 8 \n") # 4 bytes of memory at ($branch, $0, 4) and 4 at ($branch, $1, 4) [obv, arg1 and arg2 in registers]
            out.write("    eqtrash: .space 1024 \n") # trash memory to be used for equality checks between LONG and BYTE at most
        elif (line.split()[0] == ".main"):
            out.write(line + "\n")
            # For future use to generate lookup tables ok (maybe)
        else:
            if line.split()[0] == "inc":
                args= line.split()

                out.write(inc(args[1]))
            elif line.split()[0] == "dec":
                args= line.split()

                out.write(dec(args[1]))
            elif line.split()[0] == "add":
                line = line.replace(",", " ")
                args= line.split()

                out.write(add(args[1], args[2]))
            elif line.split()[0] == "sub":
                line = line.replace(",", " ")
                args= line.split()

                out.write(sub(args[1], args[2]))
            elif line.split()[0] == "mul":
                line = line.replace(",", " ")
                args= line.split()
                op1 = args[1]
                op2 = args[2]
                out.write(mul(args[1], args[2]))
            elif line.split()[0] == "shl":
                line = line.replace(",", " ")
                args= line.split()

                out.write(shl(args[1], args[2]))
            elif line.split()[0] == "and":
                line = line.replace(",", " ")
                args= line.split()

                out.write(andd(args[1], args[2]))
            elif line.split()[0] == "or":
                line = line.replace(",", " ")
                args= line.split()

                out.write(orr(args[1], args[2]))
            elif line.split()[0] == "not":
                args= line.split()

                out.write(nott(args[1]))
            elif line.split()[0] == "div":
                line = line.replace(",", " ")
                args = line.split()
                out.write(divv(args[1], args[2]))
            elif line.split()[0] == "shr":
                line = line.replace(",", " ")
                args = line.split()
                out.write(shr(args[1], args[2]))
            elif line.split()[0] == "xor":
                line = line.replace(",", " ")
                args= line.split()

                out.write(xor(args[1], args[2]))
            else:
                out.write(line + "\n")
        
out.close()