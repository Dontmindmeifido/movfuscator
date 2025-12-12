.data
    lookup_add: .single 65536 1 2 3 
    temp_reg: .space 4 
	var: .long 12

.main
	mov $3, %eax
    mov $lookup_add, %ebp 
    movb 0(var), %eax 
    movb 0(%eax), %ebx 
    movb $ebp(%eax, %ebx, 255), 0($temp_reg) 
    mov $lookup_add, %ebp 
    movb 1(var), %eax 
    movb 1(%eax), %ebx 
    movb $ebp(%eax, %ebx, 255), 1($temp_reg) 
    mov $lookup_add, %ebp 
    movb 2(var), %eax 
    movb 2(%eax), %ebx 
    movb $ebp(%eax, %ebx, 255), 2($temp_reg) 
    mov $lookup_add, %ebp 
    movb 3(var), %eax 
    movb 3(%eax), %ebx 
    movb $ebp(%eax, %ebx, 255), 3($temp_reg) 
    mov $temp_reg, %eax 
