# cpu.py
# Mark Underwood
# March 2021

"""
    Simulates a CPU using LWIS (Large Width Instruction Set) instructions. In
    addition to the CPU, register table, and the opcode lookup table, the
    simulator also simulates system memory and a call stack.

    The first two registers are read-only. Register zero is the null register,
    which can be used to read a zero, or represent an unused optional register.
    Register one is the program counter, which can only be overwritten by a
    valid jump, call, or ret instruction.

    Reading input, calling functions, and optional features of certain
    instructions have not been tested.

    Using a conditional jump with a negative offset has also not been tested.

    Performance is not excellent, given the execution time of Python and the
    decoding process necessary to execute LWIS instructions. The LWIS implementation
    of the Sieve of Eratosthenes near the bottom of this file found all the primes
    up to one million in about fifty seconds or so.
"""

from time import time
import traceback

MEMORY_SIZE = 1000000

stack = []                                      # Call/return stack
memory = list(0 for _ in range(MEMORY_SIZE))    # Memory capacity of the system
register = list(0 for _ in range(256))          # Registers on the CPU


# Check if the register is one of the two reserved registers
def check_register(reg):
    if reg < 2:
        raise IndexError("Illegal attempt to modify register {}".format(reg))


# Change the program counter to the given address
def modify_program_counter(val):
    register[1] = val


# Jump back to the address stored on the stack
def ret():
    modify_program_counter(stack.pop(len(stack) - 1))


# Call a function by saving the return address and jumping
def call(mem):
    stack.append(register[1])
    modify_program_counter(mem)


# Read a value from stdin
def read_stdin(reg):
    check_register(reg)
    register[reg] = int(input()) & 0xFFFFFFFF


# Load an immediate value into a register
def immediate_to_register(reg, imm):
    check_register(reg)
    register[reg] = imm


# Store a value from a register to memory
def register_to_memory(reg, mem):
    memory[mem] = register[reg]


# Load a value out of memory and into a register
def memory_to_register(mem, reg):
    check_register(reg)
    register[reg] = memory[mem]


# Divide the thrid register by the fourth, and store the result in the first.
# The remainder goes in the second.
# Every register after that is optional, and will divide the result register by
# the optional register, storing the result in the result register.
def div(args):
    check_register(args[0])
    check_register(args[1])
    register[args[0]] = register[args[2]] // register[args[3]]
    register[args[1]] = register[args[2]] % register[args[3]]
    for i in range(4,6):
        if args[i] == 0:
            break
        register[args[0]] = register[args[0]] // register[args[i]]
        register[args[1]] = register[args[0]] % register[args[i]]


# mul, add, sub, and_f, or_f, and xor_f all do basically the same thing:
# Compute the expression using the second and third registers, then store the
# result in the first register. Every register after that is optional, and will
# apply the operation to the result register and the optional register, storing the result in
# the result register.


def mul(args):
    check_register(args[0])
    register[args[0]] = register[args[1]] * register[args[2]]
    for i in range(3,6):
        if args[i] == 0:
            break
        register[args[0]] = register[args[0]] * register[args[i]]


def add(args):
    check_register(args[0])
    register[args[0]] = register[args[1]] + register[args[2]]
    for i in range(3,6):
        if args[i] == 0:
            break
        register[args[0]] = register[args[0]] + register[args[i]]


def sub(args):
    check_register(args[0])
    register[args[0]] = register[args[1]] - register[args[2]]
    for i in range(3,6):
        if args[i] == 0:
            break
        register[args[0]] = register[args[0]] - register[args[i]]


def and_f(args):
    check_register(args[0])
    register[args[0]] = register[args[1]] & register[args[2]]
    for i in range(3,6):
        if args[i] == 0:
            break
        register[args[0]] = register[args[0]] & register[args[i]]


def or_f(args):
    check_register(args[0])
    register[args[0]] = register[args[1]] | register[args[2]]
    for i in range(3,6):
        if args[i] == 0:
            break
        register[args[0]] = register[args[0]] | register[args[i]]


def xor_f(args):
    check_register(args[0])
    register[args[0]] = register[args[1]] ^ register[args[2]]
    for i in range(3,6):
        if args[i] == 0:
            break
        register[args[0]] = register[args[0]] ^ register[args[i]]


# A very special move operation that assigns the first three registers to the last three registers
def shuffle_move(args):
    for i in range(0, 3):
        if args[i] != 0:
            check_register(args[i])
            register[args[i + 3]] = register[args[i]]


# Stores what to do for every layout and opcode
operations = (
    # Layout 0
    [
        lambda args: None,
        lambda args: ret()
    ],

    # Layout 1
    [
        lambda args: print(hex(int(register[args[0]]) & 0xFFFFFFFF)),
        lambda args: read_stdin(args[0])
    ],

    # Layout 2
    [
        lambda args: immediate_to_register(args[0], int(register[args[1]] < register[args[2]])),
        lambda args: immediate_to_register(args[0], int(register[args[1]] > register[args[2]])),
        lambda args: immediate_to_register(args[0], int(register[args[1]] == register[args[2]])),
        lambda args: immediate_to_register(args[0], int(register[args[1]] >= register[args[2]])),
        lambda args: immediate_to_register(args[0], int(register[args[1]] <= register[args[2]])),
    ],

    # Layout 3
    # These get extra comments because I can never remember what they do
    [
        lambda args: immediate_to_register(args[0], args[1]),               # Load immediate
        lambda args: modify_program_counter(register[args[0]] + args[1]),   # Arbitrary jump
        lambda args: call(register[args[0]] + args[1])                      # Call function (not tested)
    ],

    # Layout 4
    # These get comments too, because there are a lot of them
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
        lambda args: modify_program_counter(register[args[1]] + args[2]) if register[args[0]] > 0 else None  # Conditional jump
    ],

    # Layout 5
    [
        div,
        mul,
        add,
        sub,
        and_f,
        or_f,
        xor_f,
        shuffle_move,
    ]
)

# The types of layouts we have, showing the width each part of the layout in bits
layouts = (
    tuple(),
    (8,), # Extra comma makes it a tuple
    (8, 8, 8),
    (8, 32),
    (8, 8, 32),
    (8, 8, 8, 8, 8, 8)
)

# The size of various parts of the instruction, organized by number of bits
masks = {
    8: 0xFF,
    32: 0xFFFFFFFF,
}

# The beating heart of the operation
# Decodes and execuates the instructions in the given "program memory"
def process(program_memory):

    # Set up all the necessary variables
    start = time()
    instruction = 0
    layout = 0
    opcode = 0
    max_length = max(map(len, layouts))
    sections = list(0 for _ in range(max_length))
    length_of_program_memory = len(program_memory)
    instructions_executed = 0
    try:
        # Start with the first instruction
        modify_program_counter(0)

        # While we have not reached the end of "program memory"
        while register[1] != length_of_program_memory:
            # Get the instruction
            instruction = program_memory[register[1]]

            # Get the instruction layout
            layout = instruction & masks[8]
            instruction = instruction >> 8

            # Get the opcode within that layout
            opcode = instruction & masks[8]
            instruction = instruction >> 8

            # Get all the parameters to the opcode
            i = 0
            for section_width in layouts[layout]:
                sections[i] = instruction & masks[section_width]
                instruction = instruction >> section_width
                i += 1

            # print("Line: {} Layout: {} Opcode: {} Arguments: {}".format(register[1], layout, opcode, sections))

            # Execute!
            # Calls a function from a 2D list
            operations[layout][opcode](sections)

            # Increment by one
            instructions_executed += 1
            modify_program_counter(register[1] + 1)
    except Exception as e:
        # You broke it, and here's where and what
        print("Error!")
        print("Line: {} Layout: {} Opcode: {} Arguments: {}".format(register[1], layout, opcode, sections))
        traceback.print_exc()

    # Display statistics about the execution
    total_time = time() - start
    print("Total Time: {} seconds".format(round(total_time, 6)))
    print("Instructions Executed: {}".format(instructions_executed))
    print("Average Time per Instruction: {} microseconds".format(
        round(total_time / instructions_executed * 1e6, 2)
    ))

instructions = (
    # n = 1000000 (0xF4240)
    0xF4240020003,
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

# You better have a file called pascal.lwis with LWIS instructions in it
f = open("pascal.lwis", "r")
process(list(map(int, f.readlines())))