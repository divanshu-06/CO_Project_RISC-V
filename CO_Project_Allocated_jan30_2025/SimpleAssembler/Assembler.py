import sys

registers = {
    "zero": "00000", "ra": "00001", "sp": "00010", "gp": "00011", "tp": "00100",
    "t0": "00101", "t1": "00110", "t2": "00111", "s0": "01000", "s1": "01001",
    "a0": "01010", "a1": "01011", "a2": "01100", "a3": "01101", "a4": "01110",
    "a5": "01111", "a6": "10000", "a7": "10001", "s2": "10010", "s3": "10011",
    "s4": "10100", "s5": "10101", "s6": "10110", "s7": "10111", "s8": "11000",
    "s9": "11001", "s10": "11010", "s11": "11011", "t3": "11100", "t4": "11101",
    "t5": "11110", "t6": "11111"
}

instructions = {
    "add": {"opcode": "0110011", "funct3": "000", "funct7": "0000000"},
    "sub": {"opcode": "0110011", "funct3": "000", "funct7": "0100000"},
    "slt": {"opcode": "0110011", "funct3": "010", "funct7": "0000000"},
    "srl": {"opcode": "0110011", "funct3": "101", "funct7": "0000000"},
    "or": {"opcode": "0110011", "funct3": "110", "funct7": "0000000"},
    "addi": {"opcode": "0010011", "funct3": "000"},
    "lw": {"opcode": "0000011", "funct3": "010"},
    "jalr": {"opcode": "1100111", "funct3": "000"},
    "sw": {"opcode": "0100011", "funct3": "010"},
    "beq": {"opcode": "1100011", "funct3": "000"},
    "bne": {"opcode": "1100011", "funct3": "001"},
    "jal": {"opcode": "1101111"},
    "rst": {"opcode": "1110011", "funct3": "001"},
    "halt": {"opcode": "1110011", "funct3": "010"}
}

def to_binary(num, bits):
    if num < 0:
        num = (1 << bits) + num
    binary = bin(num)[2:]
    return binary.zfill(bits)

def check_immediate(imm, bits, line_num):
    max_val = (1 << (bits - 1)) - 1
    min_val = -(1 << (bits - 1))
    if imm > max_val or imm < min_val:
        print(f"Error at line {line_num}: Immediate {imm} out of bounds for {bits} bits")
        sys.exit(1)

def parse_r_type(parts, line_num):
    if len(parts) != 4:
        print(f"Error at line {line_num}: Invalid R-type format")
        sys.exit(1)
    opcode = parts[0]
    rd = registers.get(parts[1])
    rs1 = registers.get(parts[2])
    rs2 = registers.get(parts[3])
    if not (rd and rs1 and rs2):
        print(f"Error at line {line_num}: Invalid register name")
        sys.exit(1)
    if opcode not in instructions:
        print(f"Error at line {line_num}: Invalid instruction {opcode}")
        sys.exit(1)
    inst = instructions[opcode]
    return inst["funct7"] + rs2 + rs1 + inst["funct3"] + rd + inst["opcode"]

def parse_i_type(parts, line_num):
    opcode = parts[0]
    if opcode not in instructions:
        print(f"Error at line {line_num}: Invalid instruction {opcode}")
        sys.exit(1)
    inst = instructions[opcode]
    if opcode == "lw":
        if len(parts) != 3 or "(" not in parts[2] or ")" not in parts[2]:
            print(f"Error at line {line_num}: Invalid I-type format for lw")
            sys.exit(1)
        rd = registers.get(parts[1])
        imm_part = parts[2].split("(")
        try:
            imm = int(imm_part[0])
            check_immediate(imm, 12, line_num)
        except ValueError:
            print(f"Error at line {line_num}: Invalid immediate {imm_part[0]}")
            sys.exit(1)
        rs1 = registers.get(imm_part[1].strip(")"))
    else:
        if len(parts) != 4:
            print(f"Error at line {line_num}: Invalid I-type format")
            sys.exit(1)
        rd = registers.get(parts[1])
        rs1 = registers.get(parts[2])
        try:
            imm = int(parts[3])
            check_immediate(imm, 12, line_num)
        except ValueError:
            print(f"Error at line {line_num}: Invalid immediate {parts[3]}")
            sys.exit(1)
    if not (rd and rs1):
        print(f"Error at line {line_num}: Invalid register name")
        sys.exit(1)
    imm_bin = to_binary(imm, 12)
    return imm_bin + rs1 + inst["funct3"] + rd + inst["opcode"]

def parse_s_type(parts, line_num):
    if len(parts) != 3 or "(" not in parts[2] or ")" not in parts[2]:
        print(f"Error at line {line_num}: Invalid S-type format")
        sys.exit(1)
    opcode = parts[0]
    rs2 = registers.get(parts[1])
    imm_part = parts[2].split("(")
    try:
        imm = int(imm_part[0])
        check_immediate(imm, 12, line_num)
    except ValueError:
        print(f"Error at line {line_num}: Invalid immediate {imm_part[0]}")
        sys.exit(1)
    rs1 = registers.get(imm_part[1].strip(")"))
    if not (rs2 and rs1):
        print(f"Error at line {line_num}: Invalid register name")
        sys.exit(1)
    if opcode not in instructions:
        print(f"Error at line {line_num}: Invalid instruction {opcode}")
        sys.exit(1)
    inst = instructions[opcode]
    imm_bin = to_binary(imm, 12)
    return imm_bin[0:7] + rs2 + rs1 + inst["funct3"] + imm_bin[7:12] + inst["opcode"]

def parse_b_type(parts, line_num, labels, pc):
    if len(parts) != 4:
        print(f"Error at line {line_num}: Invalid B-type format")
        sys.exit(1)
    opcode = parts[0]
    rs1 = registers.get(parts[1])
    rs2 = registers.get(parts[2])
    if parts[3] in labels:
        imm = labels[parts[3]] - pc
    else:
        try:
            imm = int(parts[3])
        except ValueError:
            print(f"Error at line {line_num}: Invalid immediate or label {parts[3]}")
            sys.exit(1) 
    if imm % 2 != 0:
        print(f"Error at line {line_num}: Branch offset must be even (align to halfword)")
        sys.exit(1)
    check_immediate(imm, 13, line_num)
    if not (rs1 and rs2):
        print(f"Error at line {line_num}: Invalid register name")
        sys.exit(1)
    if opcode not in instructions:
        print(f"Error at line {line_num}: Invalid instruction {opcode}")
        sys.exit(1)     
    inst = instructions[opcode]
    imm_bin = to_binary(imm, 13)  
    return imm_bin[0] + imm_bin[2:8] + rs2 + rs1 + inst["funct3"] + imm_bin[8:12] + imm_bin[1] + inst["opcode"]

def parse_j_type(parts, line_num, labels, pc):
    if len(parts) != 3:
        print(f"Error at line {line_num}: Invalid J-type format")
        sys.exit(1)
    opcode = parts[0]
    rd = registers.get(parts[1])
    if parts[2] in labels:
        imm = labels[parts[2]] - pc  
    else:
        try:
            imm = int(parts[2])
        except ValueError:
            print(f"Error at line {line_num}: Invalid immediate or label {parts[2]}")
            sys.exit(1)
    if imm % 2 != 0:
        print(f"Error at line {line_num}: Jump offset must be even (align to halfword)")
        sys.exit(1)
    check_immediate(imm, 21, line_num)
    if not rd:
        print(f"Error at line {line_num}: Invalid register name")
        sys.exit(1)
    if opcode not in instructions:
        print(f"Error at line {line_num}: Invalid instruction {opcode}")
        sys.exit(1)  
    inst = instructions[opcode]
    imm_bin = to_binary(imm, 21)
    return imm_bin[0] + imm_bin[10:20] + imm_bin[9] + imm_bin[1:9] + rd + inst["opcode"]


def parse_bonus_type(parts, line_num):
    if len(parts) != 1:
        print(f"Error at line {line_num}: {parts[0]} takes no operands")
        sys.exit(1)
    opcode = parts[0]
    if opcode not in instructions:
        print(f"Error at line {line_num}: Invalid instruction {opcode}")
        sys.exit(1)
    inst = instructions[opcode]
    return "000000000000" + "00000" + inst["funct3"] + "00000" + inst["opcode"]

def assemble(input_file, output_file):
    with open(input_file, "r") as f:
        lines = f.readlines()
    labels = {}
    instruction_lines = []
    pc = 0  
    for i, line in enumerate(lines, 1):
        clean_line = line.strip()
        if not clean_line:
            continue
        if ":" in clean_line:
            parts = clean_line.split(":", 1)
            label = parts[0].strip()
            if not label[0].isalpha():
                print(f"Error at line {i}: Label must start with a character")
                sys.exit(1)
            if label in labels:
                print(f"Error at line {i}: Duplicate label '{label}'")
                sys.exit(1)             
            labels[label] = pc
            clean_line = parts[1].strip()
        if not clean_line:
            continue           
        instruction_lines.append((i, clean_line))
        pc += 4  
    binary_lines = []
    pc = 0
    has_terminator = False   
    for line_num, line in instruction_lines:
        parts = line.replace(",", " ").split()
        opcode = parts[0]
        if opcode in ["add", "sub", "slt", "srl", "or"]:
            binary = parse_r_type(parts, line_num)
        elif opcode in ["addi", "lw", "jalr"]:
            binary = parse_i_type(parts, line_num)
        elif opcode == "sw":
            binary = parse_s_type(parts, line_num)
        elif opcode in ["beq", "bne"]:
            binary = parse_b_type(parts, line_num, labels, pc)
            if opcode == "beq" and parts[1] == "zero" and parts[2] == "zero":
                is_zero_offset = False
                try:
                    is_zero_offset = (int(parts[3]) == 0)
                except ValueError:
                    if parts[3] in labels and labels[parts[3]] == pc:
                        is_zero_offset = True
                        
                if is_zero_offset:
                    has_terminator = True
        elif opcode == "jal":
            binary = parse_j_type(parts, line_num, labels, pc)
        elif opcode in ["rst", "halt"]:
            binary = parse_bonus_type(parts, line_num)
            if opcode == "halt":
                has_terminator = True
        else:
            print(f"Error at line {line_num}: Invalid instruction {opcode}")
            sys.exit(1)
        binary_lines.append(binary)
        pc += 4
    if not has_terminator:
        print("Error: Missing terminating instruction (beq zero,zero,0 or halt)")
        sys.exit(1)
    terminator_instructions = ["00000000000000000000000001100011", "000000000000000000010000001110011"]
    if binary_lines[-1] not in terminator_instructions:
        print("Error: Terminating instruction (beq zero,zero,0 or halt) must be last")
        sys.exit(1)
    with open(output_file, "w") as f:
        for binary in binary_lines:
            f.write(binary + "\n")
    print(f"Successfully assembled. Output written to {output_file}")

if __name__ == "_main_":
    if len(sys.argv) != 3:
        print("Usage: python assembler.py input.asm output.bin")
        sys.exit(1)
    assemble(sys.argv[1], sys.argv[2])
