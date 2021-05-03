# lwis-cpu-simulator
Simulates a CPU executing instructions in LWIS, a custom instruction set

This was a project I wrote for CS601 Algorithms, Architecture and Languages. The goal of the project was to create an instruction set encoding, and a program simulating a CPU using this instruction set. 

## Instruction Set Design

LWIS, or Large Width Instruction Set, was an experiment in the benefits and drawbacks of using an enormous amount of space for each instruction. Every instuction in LWIS is 64 bits long, although not all bits are always used.

The first byte of the instruction, starting from the low bits, is the instruction layout. This specifies the size of each subequent section of the instruction, so that the decoder in the CPU simulator knows how to parse it. For example, Layout 2 is a sequence of four one byte sections followed by empty space, and Layout 4 is three one byte sections followed by a 32 bit section. The one byte soze of this section means that 256 unique layouts are possible.

The second byte of the instruction is the opcode. There are 256 unique opcodes possible for every unique layout. In fact, when taken together, the total possible number of opcodes is 256^2, or 65,536.

The size and function of the bits after this point is defined by the opcode and layout. Typically, the instructions follow a three register pattern where two operand registers and one result register are specified. Register addresses are always one byte, allowing for - you guessed it - 256 unique registers. Sometimes, a 32 bit integer is asked for, either as an immediate value or an address offset. Some layouts even allow some registers to be optional. If the register addresses are set to zero, they remain unused.

## CPU Simulator design

I decided to write my CPU simulator in Python. This was, perhaps, not the right choice as CPUs need to be very performant, but it was much easier to write (and therefore fit into my schedule) than a simulator written in C or C++. I stored all of my instructions in a two dimensional list, either as lambda functions or references to fucntions, such that the first coordinate was the layout, and the second coordinate the opcode. I also stored the instruction layouts as tuples in their own list.

Executing an instruction was made relatively straightforward with this architecture. The passed list of instructions, representing program memory, was parsed one by one, and the instruction at the appropriate location in the list was called, passing the rest of the sections of the parsed instruction as a list.

## Results

The instruction set and simulator was tested by writing the Sieve of Eratosthenes to find every prime below one million. This took about fifty seconds to do, which is not very fast compared to a C++ implementation of the algorithm. A classmate using a simpler, smaller instruction set was able to do it in about half the time.

While the simulator was shown to handle arithmetic, assignment, and conditionals with ease, function calls were never tested. The optional registers were also not tested very rigorously.
