import sys

memory_keys = [
    "0x00010000", "0x00010004", "0x00010008", "0x0001000C",
    "0x00010010", "0x00010014", "0x00010018", "0x0001001C",
    "0x00010020", "0x00010024", "0x00010028", "0x0001002C",
    "0x00010030", "0x00010034", "0x00010038", "0x0001003C",
    "0x00010040", "0x00010044", "0x00010048", "0x0001004C",
    "0x00010050", "0x00010054", "0x00010058", "0x0001005C",
    "0x00010060", "0x00010064", "0x00010068", "0x0001006C",
    "0x00010070", "0x00010074", "0x00010078", "0x0001007C"
]

def parse_instruction(binary_str):
    if len(binary_str) != 32:
        return "Error: Instruction must be 32 bits long"
    
    opcode = binary_str[25:32]
    instruction = {}
    
    if opcode == "0110011":
        instruction["type"] = "R"
        instruction["opcode"] = opcode
        instruction["funct7"] = binary_str[0:7]
        instruction["rs2"] = binary_str[7:12]
        instruction["rs1"] = binary_str[12:17]
        instruction["funct3"] = binary_str[17:20]
        instruction["rd"] = binary_str[20:25]
        funct7_funct3 = instruction["funct7"] + instruction["funct3"]
        r_ops = {
            "0000000000": "add", "0100000000": "sub", "0000000111": "and",
            "0000000110": "or", "0000000010": "slt","0000000101": "srl"
        }
        instruction["operation"] = r_ops.get(funct7_funct3, "unknown")

    elif opcode == "0000001":  # Halt instruction
        instruction["type"] = "SP"
        instruction["operation"] = "hlt"
        instruction["opcode"] = opcode

    elif opcode == "0000111":  # Reset instruction
        instruction["type"] = "SP"
        instruction["operation"] = "rst"
        instruction["opcode"] = opcode
    
    elif opcode in ["0010011", "0000011", "1100111"]:
        instruction["type"] = "I"
        instruction["opcode"] = opcode
        instruction["imm"] = binary_str[0:12]
        instruction["rs1"] = binary_str[12:17]
        instruction["funct3"] = binary_str[17:20]
        instruction["rd"] = binary_str[20:25]
        i_ops = {"0010011000": "addi", "0000011010": "lw", "1100111000": "jalr"}
        key = opcode + instruction["funct3"]
        instruction["operation"] = i_ops.get(key, "unknown")

    elif opcode == "0100011":
        instruction["type"] = "S"
        instruction["imm11_5"] = binary_str[0:7]
        instruction["rs2"] = binary_str[7:12]
        instruction["rs1"] = binary_str[12:17]
        instruction["funct3"] = binary_str[17:20]
        instruction["imm4_0"] = binary_str[20:25]
        instruction["imm"] = instruction["imm11_5"] + instruction["imm4_0"]
        s_ops = {"010": "sw"}
        instruction["operation"] = s_ops.get(instruction["funct3"], "unknown")

    elif opcode == "1100011":
        instruction["type"] = "B"
        instruction["imm12"] = binary_str[0:1]
        instruction["imm10_5"] = binary_str[1:7]
        instruction["rs2"] = binary_str[7:12]
        instruction["rs1"] = binary_str[12:17]
        instruction["funct3"] = binary_str[17:20]
        instruction["imm4_1"] = binary_str[20:24]
        instruction["imm11"] = binary_str[24:25]
        instruction["imm"] = instruction["imm12"] + instruction["imm11"] + instruction["imm10_5"] + instruction["imm4_1"] + "0"
        b_ops = {"000": "beq", "001": "bne"}
        instruction["operation"] = b_ops.get(instruction["funct3"], "unknown")
    
    elif opcode == "1101111":
        instruction["type"] = "J"
        instruction["imm20"] = binary_str[0:1]
        instruction["imm10_1"] = binary_str[1:11]
        instruction["imm11"] = binary_str[11:12]
        instruction["imm19_12"] = binary_str[12:20]
        instruction["rd"] = binary_str[20:25]
        instruction["imm"] = (instruction["imm20"] + instruction["imm19_12"] + 
                            instruction["imm11"] + instruction["imm10_1"]) + "0"
        instruction["operation"] = "jal"

    else:
        return "Error: Unknown instruction type"
    return instruction

def read_from_file(path):
    instr = []
    with open(path, "r") as file:
        lines = file.readlines()
    for line in lines:
        instr.append(line.strip())
    return instr

def sign_extend(val, bits):
    sign_bit = 1 << (bits - 1)
    return (val & (sign_bit - 1)) - (val & sign_bit)

def _32bit_twos_complement(val):
    if val < 0:
        val = (1 << 32) + val
    return format(val & 0xFFFFFFFF, '032b')

def execute_r_type(instruction, registers, pc):
    rs1 = f"x{int(instruction['rs1'], 2)}"
    rs2 = f"x{int(instruction['rs2'], 2)}"
    rd = f"x{int(instruction['rd'], 2)}"
    operation = instruction["operation"]
    val1 = registers[rs1] if rs1 != "x0" else 0
    val2 = registers[rs2] if rs2 != "x0" else 0
    
    if operation == "add": result = val1 + val2
    elif operation == "sub": result = val1 - val2
    elif operation == "and": result = val1 & val2
    elif operation == "or": result = val1 | val2
    elif operation == "slt": result = 1 if val1 < val2 else 0
    elif operation == "srl": result = val1 >> (val2 & 0x1F)
    else: return pc + 4
    
    if rd != "x0": 
        registers[rd] = result & 0xFFFFFFFF
    return pc + 4

def execute_i_type(instruction, registers, pc):
    rs1 = f"x{int(instruction['rs1'], 2)}"
    rd = f"x{int(instruction['rd'], 2)}"
    imm = sign_extend(int(instruction["imm"], 2), 12)
    operation = instruction["operation"]
    val1 = registers.get(rs1, 0) if rs1 != "x0" else 0

    if operation == "addi":
        result = val1 + imm
        if rd != "x0": registers[rd] = result & 0xFFFFFFFF
        return pc + 4
    elif operation == "lw":
        address = (val1 + imm) & 0xFFFFFFFF
        result = memory.get(address, 0)
        if rd != "x0": registers[rd] = result & 0xFFFFFFFF
        return pc + 4
    elif operation == "jalr":
        if rd != "x0": 
            registers[rd] = pc + 4
        return (val1 + imm) & (~1)

def execute_s_type(instruction, registers, pc):
    rs1 = f"x{int(instruction['rs1'], 2)}"
    rs2 = f"x{int(instruction['rs2'], 2)}"
    imm = sign_extend(int(instruction["imm"], 2), 12)
    operation = instruction["operation"]
    base = registers[rs1] if rs1 != "x0" else 0
    val = registers[rs2] if rs2 != "x0" else 0
    
    if operation == "sw":
        address = base + imm
        memory[address] = val & 0xFFFFFFFF
        return pc + 4
    return pc + 4
