# Intro-Compiler Project Overview

## Introduction

The Intro-Compiler project delves into the intricate processes of a compiler, exploring four fundamental stages: tokenization, parsing, Abstract Syntax Tree (AST) construction, and Local Value Numbering (LVN) for optimization. This compiler, written in Python, is designed to compile a simplified version of the C language into a list of assembly language instructions.

## Project Stages

### 1. Tokenization
- **Functionality**: Transforms source code into a sequence of tokens.
- **Components**: Utilizes scanners like Naive Scanner, Exact Matching Scanner, and others for token generation.

### 2. Parser
- **Role**: Analyzes token sequences and checks for grammatical correctness.
- **Implementation**: Incorporates error handling and symbol table management to construct a parse tree based on language grammar.

### 3. Abstract Syntax Tree (AST)
- **Purpose**: Converts the parse tree into an AST, representing the program's hierarchical syntactic structure.
- **Key Features**: Includes various node types for different syntax elements, supporting complex language constructs.

### 4. Local Value Numbering (LVN)
- **Objective**: Optimizes the AST's intermediate representation through LVN.
- **Techniques**: Applies value numbering, operation tracking, and redundant operation elimination for code optimization.

## Compiler Target

- **Language**: Simplified C language.
- **Output**: Generates an optimized list of assembly language instructions.

## Summary

This project provides an insightful exploration into compiler design, showcasing the transformation of high-level language code into optimized low-level assembly instructions. Each stage of the compiler builds upon the previous, creating a comprehensive tool for language compilation and optimization.
