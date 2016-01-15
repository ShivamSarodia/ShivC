# ShivC

A small, functional C compiler witten in Python in a couple weeks over my winter break. Generates x64 Intel-format assembly, which is then assembled and linked by `nasm` and `ld`.

Tested on OS X El Capitan 10.11.1 64-bit, Python 3.4.3, and NASM 2.11.08. The assembly uses OS X system calls, so it certainly won't run on Linux or Windows, and it may not run on other versions of OS X.

Note: ShivC is not meant to generate binaries that run quickly. The output code is at times extremely inoptimal.

### Features

See the `tests` folder for examples that compile.

- Math
  - Operations: `+`, `-`, `*`, `/`, `%`, `++`, `--`, `&&`, `||`, `!`
  - Assignment: `=`, `+=`, `-=`, `*=`, `/=`, `%=`
  - Comparison: `==`, `!=`, `<`, `<=`, `>`, `>=`
- `int` type variables
- Control structures:
  - `if`
  - `while`
  - `for`
  - `break`
  - `continue`
- Pointers (referencing and dereferencing)
- Arrays
- Function definition and calling
- `print` statement: `print n` outputs the integer `n` to stdout.
  - This isn't in the C spec, but I included it to facilitate outputting values from the program; ShivC is nowhere near being able to compile the stdio C libraries.
  
