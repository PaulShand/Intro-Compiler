## Parser Overview

This project features a parser designed for interpreting programming languages through syntactic analysis, with a specific grammar implemented as outlined in `grammar.txt`.

### Integration and Error Handling
- **Scanner Integration**: Uses a `Scanner` object for tokenization.
- **Error Handling**: Employs `SymbolTableException` and `ParserException` for error management.

### Key Functionalities
- **Initialization**: Initializes with a `Scanner` and an option for symbol table usage.
- **Token Matching**: Checks if current tokens match expected syntax, with error handling for mismatches.
- **Parsing Process**: Begins parsing and constructs a syntax tree.

### Syntax Tree Construction
- **Statement Types**: Handles various statement types like declarations and control structures.
- **Expression Handling**: Processes expressions while maintaining operation precedence.
- **Scope Management**: Manages scopes using the symbol table.

### Additional Features
- **Symbol Table Management**: Crucial for identifier declaration and usage checks.
- **Recursive Parsing**: Uses recursive methods to adhere to grammatical rules.

### Implemented Grammar
The grammar implemented in the parser is detailed in `grammar.txt` and includes:

- **OP Tokens**: Basic operators and symbols like `PLUS (+)`, `MULT (*)`, `SEMI (;)` etc.
- **Keywords**: Reserved words like `FOR`, `IF`, `ELSE`, `INT`, `FLOAT`.
- **Grammar Rules**: Defined for `statement_list`, `statement`, `declaration_statement`, etc., with specific first+ sets.

This parser is pivotal in translating source code into a structured form, essential in compiler or interpreter pipelines.

