# Modernized C

A mostly conceptual and modernized view for the C Programming  Language  and  an
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
var var1 = 5;
var var2 i32 = 5;
var var3 i32;
const constant = 10;
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

You will not be able to read the array itself but only access  its  values.  All
arrays have constant size and VLAs are not supported.

```text
[i32:10]  // an array of size 10 of readonly i32
[&i32:30] // an array of size 30 of read-and-write i32
[[f64:5]:4] // an array of size 4 of arrays of size 5 of readonly f64
*[i32:6] // a pointer to an array of size 6 of readonly i32
```

The types above correspond to:

```text
const int x[10]
int x[10]
double x[5][4]
const int *x;
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

## Function arguments

Functions will accept arguments of all types and this is where write-only  types
become useful. A function that takes an argument of a write-only type can use it
as an additional return value. Note  that  both  read-and-write  and  write-only
arguments are passed as pointers.

```text
fn change(num &i32, result ^i32) {
    num += 10;
    result = num;
}
```

The function above becomes:

```text
static void change(int *num, int *result) {
    *num += 10;
    *result = *num; 
}
```
