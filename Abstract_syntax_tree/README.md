## Abstract Syntax Tree (AST) Project Overview

This section of the project extends the capabilities of the parser by incorporating an Abstract Syntax Tree (AST) structure and an intermediate representation (IR) compiler. The key components include `ir_compiler.py` and `C_ast.py`.

### IR Compiler (`ir_compiler.py`)

- **Purpose**: Generates a list of 3-address instructions using the parser, which are then wrapped in a C++ function for compilation and execution.
- **Initialization**: Takes a `Parser` object as input.
- **Functionality**:
  - **Program Printing**: Generates C++ function headers and compiles 3-address instructions into a cohesive program.
  - **Compilation**: Transforms parsed code into an intermediate representation, ready for further compilation.

### C AST (`C_ast.py`)

- **Node Structure**: Defines various node types for constructing the AST, including `ASTNode`, `ASTLeafNode`, `ASTBinOpNode`, `ASTUnOpNode`, etc.
- **Type Handling**: Manages data types like INT and FLOAT.
- **Code Generation**:
  - **Three-Address Code**: Each AST node type has a method to generate its corresponding 3-address code.
  - **Linearization**: Converts the AST into a linear list of instructions for the IR compiler.

### AST Operations

- **AST Construction**: The parser generates an AST based on the input code.
- **Linearization**: The AST is linearized into a sequence of instructions.
- **Three-Address Code**: Each node in the AST translates into 3-address instructions, suitable for IR compilation.

This section of the project demonstrates the integration of AST with parsing processes, enhancing the compiler's ability to interpret, optimize, and generate executable code.
