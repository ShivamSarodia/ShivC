# ShivC

A small C compiler witten in Python in a couple weeks over my winter break. Generates x64 Intel-format assembly, which is then assembled and linked by `nasm` and `ld`.

Tested on OS X El Capitan 10.11.1 64-bit, Python 3.4.3, and NASM 2.11.08. The assembly uses OS X system calls, so it certainly won't run on Linux or Windows, and it may not run on other versions of OS X.

Note: ShivC is not meant to generate binaries that run quickly. The output code is at times extremely inoptimal.

### Features

See the `tests` folder for examples that compile. The `function_test.c` test is representative of the range of ShivC.

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
- `\* ... */`-form comments
- `print` statement: `print n` outputs the integer `n` to stdout.
  - This isn't in the C spec, but I included it to facilitate outputting values from the program; ShivC is nowhere near being able to compile the stdio C libraries.
  
### ShivyC

 I've recently started working on (ShivyC)[https://github.com/ShivamSarodia/ShivC], a complete rewrite of ShivC, for a few reasons:
 - My coding style has improved significantly in 2016. ShivC's code is quite badly documented, tested, and tough to maintain by my current standards.
 - ShivC was written in just a couple weeks, with no regard for optimization. The generated binaries are times exceedingly inefficient, and implementing some desired improvements would require very heavy rewrite of the code.
 - ShivC produces assembly that is incompatble with x86 conventions in many ways, making it impossible to link ShivC binaries with files compiled by another compiler.
 - My Python is getting sloppy, and I could use a refresher.
I will no longer be contributing to ShivC, as my efforts are now focused on the improved ShivyC.
