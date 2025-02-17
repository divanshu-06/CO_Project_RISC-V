instruction={
#RType
"add":{"type":"R","opcode":"0110011","funct3":"000","funct7":"0000000"},
"sub":{"type":"R","opcode":"0110011","funct3":"000","funct7":"0100000"},
"slt":{"type":"R","opcode":"0110011","funct3":"010","funct7":"0000000"},
"srl":{"type":"R","opcode":"0110011","funct3":"101","funct7":"0000000"},
"or":{"type":"R","opcode":"0110011","funct3":"110","funct7":"0000000"},
"and":{"type":"R","opcode":"0110011","funct3":"111","funct7":"0000000"},

#I-Type
"lw":{"type":"I","opcode":"0000011","funct3":"010"},
"addi":{"type":"I","opcode":"0010011","funct3":"000"},
"jalr":{"type":"I","opcode":"1100111","funct3":"000"},

#S-Type
"sw":{"type":"S","opcode":"0100011","funct3":"010"},

#B-Type
"beq":{"type":"B","opcode":"1100011","funct3":"000"},
"bne":{"type":"B","opcode":"1100011","funct3":"001"},
"blt":{"type":"B","opcode":"1100011","funct3":"100"},

#J-Type
"jal":{"type":"J","opcode":"1101111"},

#U-Type
"auipc":{"type":"U","opcode":"0010111"},
}
