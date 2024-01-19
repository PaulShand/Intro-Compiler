## Local Value Numbering (LVN) Overview

Building on the parser and AST components, this section of the project introduces `local_value_numbering.py`, a module that enhances code optimization through local value numbering.

### Functionality of `local_value_numbering.py`

- **Purpose**: Implements Local Value Numbering (LVN) to optimize the intermediate representation (IR) of code.
- **Process**:
  - **Block Creation**: Splits the program into basic blocks based on control flow (branching and labels).
  - **Value Enumeration**: Assigns unique numbers to virtual registers and updates instructions accordingly.
  - **Optimization**: Applies LVN within each block to reduce redundant computations and improve efficiency.

### Key Features

- **Basic Block Management**: Segregates the program into manageable blocks for localized optimization.
- **Regular Expression Matching**: Utilizes regular expressions to identify and process various instruction patterns.
- **Instruction Rewriting**: Rewrites instructions to reflect the latest state of operands, based on their usage and assignment.
- **Operation Tracking**: Maintains a record of operations to identify and eliminate redundant calculations.
- **Code Linearization**: Linearizes the optimized code blocks back into a single program flow.

### Optimization Techniques

- **Operand Numbering**: Assigns a unique number to each instance of a variable or virtual register.
- **Commutative Operation Ordering**: Ensures operands of commutative operations (like addition, multiplication) are ordered consistently for easy identification of redundancy.
- **Known Value Propagation**: Replaces variables with their known values where possible.
- **Redundant Operation Elimination**: Removes or simplifies operations that are redundant due to previous calculations.

The LVN module significantly enhances the efficiency of the generated code, making it a vital part of the optimization pipeline in compiler design.
