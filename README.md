# Modernized C

A mostly conceptual and modernized view for the C programming language + an
experimental MC to C transpiler.

## Data

Improve data management with three  types  of  data:  readonly,  write-only  and
read-and-write.  Readonly   and   write-only   accept   read-and-write   values.
Read-and-write can be casted to a write-only or to a readonly but not the  other
way around.

```text
i32  // readonly i32
^i32 // write-only i32
&i32 // read-and-write i32
```

The types above correspond to:

```text
const int
int
int
```

Note that a variable cannot be declared with a write-only data type.

## Variables and constants

Variables are declared with the keyword `var` and constants  with  `const`.  The
difference between the two is that while `var`, even if is a readonly type,  can
change at runtime [^1], `const` cannot  and  its  value  is  static.  The  other
difference is that variables can be declared  but  not  assigned  and  constants
cannot.

Both variables and constants  can  infer  their  type  when  assigned  a  value.

[^1]: This  can  happen  when  a  function  has  a  readonly  argument   but   a
read-and-write one is passed.

```text
var my_variable = 5;
```

## Pointers

Pointers  are  indicated  with  `*`.  All  write-only  pointers  are  considered
equivalent even if the  types  after  are  incompatible  regarding  reading  and
writing.

```text
*i32   // readonly pointer to readonly i32
*&i32  // readonly pointer to read-and-write i32
^*i32  // write-only pointer to i32
&*&i32 // read-and-write pointer to read-and-write i32
&*i32  // read-and-write pointer to readonly i32
```

The types above correspond to:

```text
const int const*
int const*
int *
int *
const int *
```

## Arrays

Arrays in C are quite weird since they correspond to  `*&T`  in  the  operations
they allow but are not pointers since they contain the data directly instead  of
containing the address of the first element. They are always fixed size.

```text
[i32:10]  // an array of size 10 of readonly i32
[&i32:30] // an array of size 30 of read-and-write i32
```

The types above correspond to:

```text
const int x[10]
int x[10]
```

## Functions

Functions should be divided into pure functions (unmarked), and  functions  that
access global values (marked). A pure function cannot call  a  global  function.

```text
// pure function
fn pure() i32 {...}

// function that can access global state
global fn impure() i32 {...}
```
