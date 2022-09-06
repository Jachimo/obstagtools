---
created: "2022-09-01 16:44 EDT"
tags:
  - testfile
alias: "Obsidian Keyword Test"
---
# Obsidian Keyword Test Document

## 26-bit Addressing

In computer architecture, 26-bit integers, memory addresses, or other data units are those that are 26 bits wide, and
thus can represent values up to 64 mega (base 2). Two examples of CPUs that featured 26-bit memory
addressing are certain second generation IBM System/370 mainframe models introduced in 1981 (and several
subsequent models), which had 26-bit physical addresses, but only the same 24-bit virtual addresses as earlier
models, and the first generations of ARM processors.

## Wikipedia on ARM Architecture

There have been several generations of the ARM design. The original ARM1 used a 32-bit internal structure but had a
26-bit address space that limited it to 64 MB of main memory. This limitation was removed in the ARMv3 series, which has
a 32-bit address space, and several additional generations up to ARMv7 remained 32-bit. Released in 2011, the ARMv8-A
architecture added support for a 64-bit address space and 64-bit arithmetic with its new 32-bit fixed-length instruction
set. Arm Ltd. has also released a series of additional instruction sets for different rules; the "Thumb" extension adds
both 32- and 16-bit instructions for improved code density, while Jazelle added instructions for directly handling Java
bytecode. More recent changes include the addition of simultaneous multithreading (SMT) for improved performance or
fault tolerance.

##  RISC PC

The Risc PC is Acorn Computers's 'RISC OS/Acorn RISC Machine', launched on 15 April 1994, which superseded the
Acorn Archimedes. The Acorn PC card and software allows PC compatible software to be run.

Like the Archimedes, the Risc PC continues the practice of having the RISC OS operating system in a ROM module. Risc PC
augments the ROM-based core OS with a disk-based directory structure containing configuration information, and some
applications which had previously been kept in ROM. At the 1996 BETT Educational Computing & Technology Awards, the
machine was awarded Gold in the hardware category.

**Processors:**  
- ARM610 at 30 MHz or 33 MHz
- ARM710 at 40 MHz
- StrongARM at 203 MHz, 236 MHz or 300 MHz.
- Additionally prototypes of 33 MHz ARM700 and 55 MHz ARM810 processors were developed by Acorn, but not released.

## Flat Memory Model

Flat memory model or linear memory model refers to a memory addressing paradigm in which "memory appears to the program
as a single contiguous address space." The CPU can directly (and linearly) address all of the available memory locations
without having to resort to any sort of memory segmentation or paging schemes.

Memory management and address translation can still be implemented on top of a flat memory model in order to facilitate
the operating system's functionality, resource protection, multitasking or to increase the memory capacity beyond the
limits imposed by the processor's physical address space, but the key feature of a flat memory model is that the entire
memory space is linear, sequential and contiguous.

In a simple controller, or in a single tasking embedded application, where memory management is not needed nor
desirable, the flat memory model is the most appropriate, because it provides the simplest interface from the
programmer's point of view, with direct access to all memory locations and minimum design complexity.

In a general purpose computer system, which requires multitasking, resource allocation, and protection, the flat memory
system must be augmented by some memory management scheme, which is typically implemented through a combination of
dedicated hardware (inside or outside the CPU) and software built into the operating system. The flat memory model (at
the physical addressing level) still provides the greatest flexibility for implementing this type of memory management.
