# simplecomp
Simple compiler in python with antlr4 and llvmlite
## Requirements
In python:
```sh
pip install llvmlite antlr4-python3-runtime
```

In system:
```
clang antlr-4.9.1
```

# Getting started
```
make all
make test
```

# Example
```cpp
// integer variable
int a = 10;
// double variable
double b = 2.0;

// you can only print by variable name
print a;
print b;

// when declaring new variable you can add or substract value
int a2 = a + a;

// if types don't match there will be implicit casting/conversion if possible
double c = a + b;

print a2;
print c;
```