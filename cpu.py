from time import time

MEMORY_SIZE = 10000

stack = []
memory = list(0 for _ in range(MEMORY_SIZE))
register = list(0 for _ in range(256))


def nop():
    pass


def ret():
    register[1] = stack[len(stack) - 1]
    stack.pop(len(stack) - 1)


def immediate_to_register(reg, imm):
    register[reg] = imm


def register_to_memory(reg, mem):
    memory[mem] = register[reg]


def memory_to_register(mem, reg):
    register[reg] = memory[mem]


def div(args):
    register[args[0]] = register[args[2]] // register[args[3]]
    register[args[1]] = register[args[2]] % register[args[3]]
    for i in range(4,6):
        if args[i] == 0:
            break
        register[args[0]] = register[args[0]] // register[args[i]]
        register[args[1]] = register[args[0]] % register[args[i]]


def mul(args):
    register[args[0]] = register[args[1]] * register[args[2]]
    for i in range(3,6):
        if args[i] == 0:
            break
        register[args[0]] = register[args[0]] * register[args[i]]


def add(args):
    register[args[0]] = register[args[1]] + register[args[2]]
    for i in range(3,6):
        if args[i] == 0:
            break
        register[args[0]] = register[args[0]] + register[args[i]]


operations = (
    [
        lambda args: nop(),
        lambda args: ret()
    ],
    [
        lambda args: print(register[args[0]]),
        # lambda args: register[args[0]] = input()
    ],
    [
        lambda args: immediate_to_register(args[0], int(register[args[1]] < register[args[2]])),
        lambda args: immediate_to_register(args[0], int(register[args[1]] > register[args[2]])),
        lambda args: immediate_to_register(args[0], int(register[args[1]] == register[args[2]])),
        lambda args: immediate_to_register(args[0], int(register[args[1]] >= register[args[2]])),
        lambda args: immediate_to_register(args[0], int(register[args[1]] <= register[args[2]])),
    ],
    [
        lambda args: immediate_to_register(args[0], args[1]),
        lambda args: immediate_to_register(1, register[args[0]] + args[1]), # Arbitrary jump
    ],
    [
        lambda args: register_to_memory(args[0], register[args[1]] + args[2]),              # Store
        lambda args: memory_to_register(register[args[1]] + args[2], args[0]),              # Load
        lambda args: immediate_to_register(args[0], register[args[1]] + args[2]),           # Addition
        lambda args: immediate_to_register(args[0], register[args[1]] - args[2]),           # Subtraction
        lambda args: immediate_to_register(args[0], register[args[1]] * args[2]),           # Multiplication
        lambda args: immediate_to_register(args[0], register[args[1]] // args[2]),          # Division
        lambda args: immediate_to_register(args[0], register[args[1]] >> args[2]),          # Shift right
        lambda args: immediate_to_register(args[0], register[args[1]] << args[2]),          # Shift left
        lambda args: immediate_to_register(args[0], register[args[1]] & args[2]),           # AND
        lambda args: immediate_to_register(args[0], register[args[1]] | args[2]),           # OR
        lambda args: immediate_to_register(args[0], register[args[1]] ^ args[2]),           # XOR
        lambda args: immediate_to_register(args[0], int(register[args[1]] < args[2])),      # Less than
        lambda args: immediate_to_register(args[0], int(register[args[1]] > args[2])),      # Greater than
        lambda args: immediate_to_register(args[0], int(register[args[1]] == args[2])),     # Equal to
        lambda args: immediate_to_register(1, register[args[1]] + args[2]) if register[args[0]] > 0 else nop()  # Conditional jump
    ],
    [
        lambda args: div(args),
        lambda args: mul(args),
        lambda args: add(args),
    ]
)


layouts = (
    tuple(),
    (1,), # Extra comma makes it a tuple
    (1, 1, 1),
    (1, 4),
    (1, 1, 4),
    (1, 1, 1, 1, 1, 1)
)


def feed(instruction, width):

    section = 0
    for i in range(0, width):
        section = section | (instruction & (0xFF << (i * 8)))

    return section


def process(instructions):
    start = time()

    instruction = 0
    layout = 0
    opcode = 0
    sections = []
    try:
        register[1] = 0
        while register[1] != len(instructions):
            instruction = instructions[register[1]]
            layout = feed(instruction, 1)
            instruction = instruction >> 8

            opcode = feed(instruction, 1)
            instruction = instruction >> 8

            sections.clear()
            for section_width in layouts[layout]:
                sections.append(feed(instruction, section_width))
                instruction = instruction >> (section_width * 8)

            # print("Line: {} Layout: {} Opcode: {} Arguments: {}".format(register[1], layout, opcode, sections))
            operations[layout][opcode](sections)

            register[1] += 1
    except Exception as e:
        print("Error!")
        print("Line: {} Layout: {} Opcode: {} Arguments: {}".format(register[1], layout, opcode, sections))
        traceback.print_exc()

    print("Time: {}".format(time() - start))

instructions = (
    # n = 10000
    0x2710020003,
    # n < 2
    0x02030003,
    0x0302060002,
    # Put a 1 in memory location 0 and 1
    0x01040003,
    0x040004,
    0x0100040004, # Line 5
        #Start loop
        # Square the counter
        0x0707080105,
        # i**2 >= n
        0x0208060302,
        # Jump to end of loop if true
        0x0A00060E04,
        # Increment loop counter
        0x0107070204,
    # Jump to start of loop
    0x05000103, # Line 10
    # End loop
    # i = 2
    0x02050003, # Line 11
        # Start loop
        # i >= ceil(sqrt(n))
        0x0705060302,
        # Jump to end of loop if true
        0x1800060E04,
        # j = 0
        0x00090003,
        # Square the counter
        0x0505080105, # Line 15
            # Start loop
            # i * j
            0x09050A0105,
            # i * j + i**2
            0x080A0A0205,
            # i * j + i**2 >= n
            0x020A060302,
            # Jump to end of loop if true
            0x1600060E04,
            # Insert 1 at mem[i * j + i**2]
            0x000A040004,
            # Increment j
            0x0109090204,
        # Jump to start of loop
        0x0F000103, # Line 22
        # End loop
        # Increment i
        0x0105050204,
    # Jump to start of loop
    0x0B000103, # Line 24
    # End loop
    # i = 0
    0x00050003, # Line 25
        # Increment i (this is a little cheaty)
        0x0105050204,
        # Start loop
        # i >= n
        0x0205060302,
        # Jump to end of loop if true
        0x2000060E04,
        # Load mem[i]
        0x0005070104,
        # Jump to start if one
        0x1900070E04,
        # Print i
        0x050001,
    # Jump to start of loop
    0x19000103,
    # End of loop
)

process(instructions)