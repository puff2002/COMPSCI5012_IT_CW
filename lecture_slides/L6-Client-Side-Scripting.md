Client-Side Scripting

Internet Technology
ITECH

1

Client-Server model

Presentation

Processing

Content

Content

Python

Content

Processing

Processing

Client-side Scripting

Content

Device

Browser

HTML

CSS

JS

HTTP

Stylesheet(s)

Script(s)

3

Scripting in Context

4

HTMLCSSJavaScriptWeb BrowserWWWRequestResponseJAVASCRIPT

5

The Name

It is a completely different language

•
• Good/bad marketing idea
• Originally called “LiveScript”, but this was not confusing enough

6

JavaScriptJavaTypecasting

• Designed to run in Netscape Navigator (1995)
• Became standard in all browsers
• Useful for a wide range of programming tasks (e.g. node.js)

7

JavaScriptWebOnlyProcedural and functional

•

Javascript looks like a procedural language,
but is closer to functional

• Functions are first class
• Supports anonymous functions (heavily used by jQuery)

8

Moving Target

• Opinions formed on earlier versions
• Lacked object-orientation and exception handling
• There is a standard (ECMA) - ECMA-262, 15th edition, June 2024

9

JavaScript v4JavaScript v3JavaScript v2JavaScript v1Brief history of the
standard

• 1st edition: 1997
• 3rd edition: 1999
• 4th edition – abandoned
• 5th edition: 2009
• 6th edition: 2015 ES6 Harmony

– Supported in more than 98% of browsers

• 16th edition: 2025

10

Design Errors

• No language is perfect (that’s why there are so many)
• Small things annoy (semi-colon insertion, overloaded

operators)

• Problems can be avoided by using a linter JSLint

• JSLint: http://www.jslint.com/
• ESLint: https://eslint.org

11

Object-Oriented

•

Is it Object-Oriented?
• Yes, has objects, which encapsulate data/methods

• Where are the classes? Where is inheritance?
• Prototype-based object-oriented language
• A class in Javascript is a special function
• The “class” keyword is part of ES6

• Also inheritance - ”extends” keyword

12

Lousy Implementations

• The JavaScript engines of early browsers were buggy
• The browsers containing JavaScript engines were buggy
•

JavaScript performance war has helped

13

Bunch of Amateurs

• Most people writing JavaScript are not programmers
• Lack of training, discipline, common sense
• Expressive language that is severely underutilized

14

??!Bad books

15

THE MISUNDERSTOOD LANGUAGE

"frustration" by Sean MacEntee is licensed under CC BY 2.0.

16

Popularity 2011

http://www.tiobe.com/index.php/content/paperinfo/tpci/index.html

17

Popularity 2024

http://www.tiobe.com/tiobe-index

18

Core Features

• Syntactically similar to Java/C
  (if/else, while, for)

• Familiar primitive datatypes
(numbers, strings, Booleans)

• Object-oriented
(in its own way)

19

Core Features

• Interpreted Language
   (no compiling)

• Dynamic Typing
   (var x = 10; var y = “abc”;)

• Functions are first class

(can also be anonymous and nested)

20

Inline JavaScript

• Scripts can be included inline with HTML code
• Good for experimentation
• Violates separation of concerns

<html>
  <head>
  </head>
  <body>
    <script type="text/javascript">
      document.writeln("Hello World!");
    </script>
  </body>
</html>

• Scripts can also be
added to event
handlers

• Fragile to maintain

21

External JavaScript

• Scripts can be kept in external files and

linked to from the <head> section
• Easier to manage code (over time)

<html>
  <head>
    <script type="text/javascript” src=“myScript.js”></script>
  </head>
  <body>
  </body>
</html>

22

DOM Integration

• The intent behind JavaScript was to

dynamically script/manipulate documents

• HTML documents are modelled using

DOM

• DOM methods and properties can be
accessed and altered using JavaScript

23

Finding Elements in the
DOM

• Finding DOM elements to manipulate
• getElementsByTagName( )
• getElementById( )

// Find the number of tables in a document
var tables = document.getElementsByTagName("table");
alert("This document contains " + tables.length + " tables");

// Find a specific Table within a document and count its rows
var tableOfContents = document.getElementById("TOC");
var rows = tableOfContents.getElementsByTagName("tr");
var numrows = rows.length;

24

Modifying Elements in the
DOM
• The real impact of JavaScript is changing

the content of the DOM

// This function traverses the DOM tree and
// converts all Text node data to uppercase
function upcase(n) {
  if (n.nodeType == 3 /*Node.TEXT_NODE*/) {
    n.nodeValue = n.nodeValue.toUpperCase();
  } else {
      // If the node is not Text, loop through its children
      // and recursively call this function on each child.
      var kids = n.childNodes;
      for (var i = 0; i < kids.length; i++) {
        upcase(kids[i]);
      }
  }
}

25

Modifying Elements in the
DOM

• nodeType returns the type of the node

̶ 1 for an element node
̶ 2 for an attribute node
̶ 3 for a text node
̶ 8 for a comment node
̶ 9 for a document node

• Include a reference to script containing upcase

in html head

• Call this function by putting the following at the

bottom of the document body:

<script type="text/javascript">
upcase(document.body)

</script>

 TRY THIS

26

The JavaScript Language

• A simple script
• Lexical Structure
• Datatypes and values
• Variables
• Expressions and Operators
• Statements
• Objects and Arrays
• Functions
• Class, Constructors and Prototypes
• Pattern Matching and Regular Expressions

27

FOOD FOR THOUGHT…

28

The Problem

• Despite JavaScript and DOM being

functionally useful, coding on the client-
side is not particularly easy

• Consider Java and its huge standard
   library of useful functionality

• DOM scripting entails a lot of repetitive
   domain-specific boilerplate coding

29

A Solution

• JavaScript needs its own standard library

• Focus on the domain-specific

programming tasks (user interaction,
animation, etc)

• More than one solution: jQuery, AngularJS,

React, node.js, etc

30

Resources

Overview
https://jgthms.com/javascript-in-14-minutes/

W3Schools JavaScript Tutorial
http://www.w3schools.com/js/default.asp

JavaScript: The Definitive Guide
D. Flanagan
http://oreilly.com/catalog/9780596101992

JavaScript: The Good Parts
D. Crockford
http://oreilly.com/catalog/9780596517748/

31

Other Resources

Search for Douglas Crockford & JavaScript for
some video lectures by JavaScript’s
cranky evangelist:

•  The World’s Most Misunderstood Language
•  The Good Parts
•  4 Part Series for Beginners
•  Advanced JavaScript

32

SYNTAX

33

The JavaScript Language

• A simple script
• Lexical Structure
• Datatypes
• Variables
• Expressions and Operators
• Statements
• Objects and Functions
• Class and Constructors
• Pattern Matching and Regular Expressions

Factorials （N!）

<html>
  <head>
    <title>Factorials</title>
  </head>
  <body>
    <h3>Table of Factorials</h3>
    <p id="demo"></p>
    <script type="text/javascript" src="factorial.js"></script>
  </body>
</html>

CodeExa
mples:
Factorial

var fact = 1;
var text = "";
for (var i = 1; i < 10; i++) {

factorial.js

fact *= i;
text += (i + "! = " + fact + "<br />");

}
document.getElementById("demo").innerHTML =
text;

35

Button Event

Code
Examples:
Button

<html>
  <head>
    <title>Button Event</title>
  </head>
  <body>
    <h3>Button Event</h3>
    <button onClick="alert('You clicked the button');">
      Click Here
    </button>
  </body>
</html>

36

The JavaScript Language

• A simple script
• Lexical Structure
• Datatypes
• Variables
• Expressions and Operators
• Statements
• Objects and Functions
• Class and Constructors
• Pattern Matching and Regular Expressions

Lexical Structure

• JavaScript is a case-sensitive language (keywords,

identifiers, variables, functions etc must be
consistent)

• Whitespace is ignored (spaces, tabs and

newlines) but see below

• Semi-colons are optional – but it is good practice
– JavaScript interpreters automatically add them – this

is a very bad thing so it is better to be explicit!

return
true;

return;
true;

What happens is that undefined is returned instead of true

38

Lexical Structure

• Comments can be single // or multiline /* */

C-style

• Literals are data values that appear directly in the

language: 12, 1.2, “hello”, true, false

• Identifiers are names for variables and functions
– First character must be letter, underscore or dollar
– Remaining characters can include above and numbers

• Reserved word set cannot be used as identifier
– Be careful, JavaScript has an unusually large set of

reserved words that may become part of the language
in the future

https://www.w3schools.com/js/js_reserved.asp

39

Literal example

<script>
document.write('Boolean(12) is ' + Boolean(12));
document.write('<br>');
document.write('Boolean("Hello") is ' + Boolean("Hello"));
document.write('<br>');
document.write('Boolean(3 > 0.02) is ' + Boolean(3 > 0.02));
document.write('<br>');
document.write("Boolean('false') is " + Boolean('false'));
document.write('<br>');
document.write('Boolean(0) is ' + Boolean(0));
</script>

<script>
document.getElementById("no1").innerHTML = 100.25;
</script>
<script>
document.getElementById("no2").innerHTML = 56e4;
</script>

Code
Examples:
Boolean/
Float
Literals

40

The JavaScript Language

• A simple script
• Lexical Structure
• Datatypes
• Variables
• Expressions and Operators
• Statements
• Objects and Functions
• Class and Constructors
• Pattern Matching and Regular Expressions

Datatypes

• Three primitive types:

– Number: no distinction between integers (123) and
decimal (3.14) and floating-point (6.02e23) values

– String: sequence of Unicode letters, digits and punctuation
characters delimited by single or double quotes (“Hello!”)

– Boolean: true or false

• Two trivial types:

– null: an assignment value that can represent no value –

null is (a placeholder for) an object, technically a primitive
– undefined: variable that has been declared but no value
has been assigned to it, or an object property that does
not exist

42

Datatypes: Functions

• A function is a piece of executable code that is
defined once, but can be called multiple times
• In other languages, functions or methods are
often just a useful syntax construct to gather
related code

• In JavaScript, functions are 1st class objects in the

language, and can be passed as datatypes
• No return type required in function signature

function square(x) {
  return x * x;
}
y  = square(4);

var square = function(x) {
  return x * x };

y  = square(4);

43

Datatypes: Objects

• An Object is a collection of named values
• Named values are known as the object’s

Properties

Code
Examples:
Object 1
Object 2

• Objects are created by invoking a constructor or

using the object literal short-hand syntax:

function point(xVal, yVal)
{
  this.x = xVal;
  this.y = yVal;
}

var point1=new point(2.5,
5.4)

var point = new Object( );
point.x = 2.5;
point.y = 5.4;

// same as above
var point = {x:2.5, y:5.4};

44

Datatypes: Arrays

• Arrays are also very similar to Objects, acting as a collection

of data values

• For objects, each value has a name (obj.x), whilst arrays

have an index (arr[0]) instead

• The elements in an array do not have to have the same

type (cf. Java arrays), and their size is dynamic

• Methods: join, reverse, sort, concat, slice, splice, push, pop

var collection = new Array( );
collection[0] = 120;
collection[1] = ‘hello!’;

// array literal syntax, same as above
var collection = [120, ‘hello!’];

45

The JavaScript Language

• A simple script
• Lexical Structure
• Datatypes and values
• Variables
• Expressions and Operators
• Statements
• Class, Constructors and Prototypes
• Pattern Matching and Regular Expressions

Variables

• An identifier associated with a value
• Used to store and manipulate values in a program
• All variables are untyped (weak or loose typing)
• Variables are declared using the var keyword

– if this is missing, the variable is global – not recommended
• Scope of variables depends on where they are declared

– global variables can be seen everywhere
– variables declared in a function are only visible locally
– omitting var in functions will use matching global variables
– there is no block scope like C/Java languages (e.g. in for or

if/else blocks

var i = 10;
i = “hello!”;

47

The JavaScript Language

• A simple script
• Lexical Structure
• Datatypes
• Variables
• Expressions and Operators
• Statements
• Objects and Functions
• Class and Constructors
• Pattern Matching and Regular Expressions

Expressions

• An expression is a phrase of code that can be

evaluated to produce a value

1.5               // a numeric literal
“hello!”             // a string literal
True              // a Boolean literal
/java/             // a regular expression
                        literal
{x:1.2, y:2}        // an object literal
[1, 2, 3, 4, 5]      // an array literal
function(x) {return x*x;}// function literal
sum               // the variable sum

49

Operators

• Simple expressions can be combined by using

Operators

• JavaScript supports a common set of operators

compared to other C/Java languages
– arithmetic (+), equality (==), relational (>), logical

(&&), bitwise (<<)

• Care should be taken when using operators

– ‘+’ can mean addition or concatenation
– ‘==‘ tests for equality, ‘===‘ equality and type

if (true == 1)  // evaluates as true
if (true === 1) // evaluates as false

50

The JavaScript Language

• A simple script
• Lexical Structure
• Datatypes
• Variables
• Expressions and Operators
• Statements
• Objects and Functions
• Class and Constructors
• Pattern Matching and Regular Expressions

Statements

// expression statement
var x = 1 + 2;

// if/else if/else
// statement
if (condition) {
  statements
}
else if (condition) {
  statements
}
else {
  statements
}

// while statement
while (condition) {
  statements
}

// for statement
for (init ; test; inc) {
  statements
}

// function statement
function name (args) {
  statements
}

52

Statements

// try catch finally statement
try {
  // normally this code runs from top to bottom
  // sometimes an exception may be thrown
  // either directly with a throw statement,
  // or indirectly by calling another method
}
catch (e) {
  // the statements here are executed if, and only
  // if, the try statement generated an exception
  // these statements handle the exception somehow
}
finally {
  // the statements here are always executed
  // regardless of what happened in the try block
}

53

The JavaScript Language

• A simple script
• Lexical Structure
• Datatypes
• Variables
• Expressions and Operators
• Statements
• Objects and Functions
• Class and Constructors
• Pattern Matching and Regular Expressions

Objects

• Unordered collections of properties
• Besides the ‘dot’ operator to access properties,

the […] operator can be used
– one way to think of this is like Python Dictionaries or

the Java Hashtable class

• As JavaScript is dynamic, objects can have
properties added at any time, this is a very
convenient method

55

Objects - example

<body>

<script type="text/javascript">

Example:
Objects3

var addr = "";
var customer=new Object();
customer.address0="36 King Street";
customer.address1="42 Queen Road";
customer.address2="16 Abbey Hill";
customer.address3="29 Regent Gardens";
for (i = 0; i < 4; i++) {
 addr += customer["address" + i] + "<br>";
}
document.writeln(addr);

</script>

</body>

56

Functions

• Functions can also be nested
• Functions support optional arguments

– if invoked with fewer arguments, undefined is used

• Arguments objects can be used with variable

length argument lists
– e.g. Function object has a property arguments
which can be inspected to find which and how
many arguments were given (e.g. if
(arguments.length != 3) { … }

• Functions that are properties of objects are

usually referred to as methods

57

The JavaScript Language

• A simple script
• Lexical Structure
• Datatypes
• Variables
• Expressions and Operators
• Statements
• Objects and Functions
• Class and Constructors
• Pattern Matching and Regular Expressions

Classes and Constructors

• Creating a class to model Rectangles

class Rectangle {
  // Define the constructor
  // Note how it calls a method referred to by "this”
  constructor (idString, xVal, yVal) {
    this.id = idString;
    this.resize(xVal,yVal);
  }

  // What follows is a method
  resize (xVal, yVal) {
    this.x = xVal;
    this.y = yVal;
  }

59

Classes and Constructors

• Creating a class to model Rectangles (cont)

Code
Examples:
Rectangle

// Here is another method

  getArea () {
      return this.x * this.y;
  }
}

// Test out the constructor and methods
var rect = new Rectangle ("Test", 4, 5);
document.writeln(rect.id);
document.writeln(rect.getArea());
rect.resize(6, 7);
document.writeln(rect.getArea());

60

The JavaScript Language

• A simple script
• Lexical Structure
• Datatypes
• Variables
• Expressions and Operators
• Statements
• Objects and Functions
• Class and Constructors
• Pattern Matching and Regular Expressions

Regular Expressions

• A regular expression is an object that describes a
pattern of characters that can be used to perform
pattern matching and search and replace actions
on text

• Often RegExps can be thought of as programs

within a program

• However, despite their utility, they can be a

documentation nightmare

Some people, when confronted with a problem, think
"I know, I'll use regular expressions.”
Now they have two problems.

J. Zawinski, ‘9762

Regular Expressions

• In JavaScript, regular expressions are represented

by RegExp objects

• Syntax of a regular expression:

– /pattern/modifiers;
– Example 1:

var pattern = /Free/i;
• “Free” is a pattern and “i” is a modifier (case

insensitive)

– Example 2:

var pattern = /s$/;
• match any string that ends with ‘s’

63

Regular Expressions

• RegExp object methods:

– search() – returns starting position of the first match, or -1

• Example:

var str = "Visit W3Schools";
var n = str.search(/w3schools/i);
returns 6

– exec() – returns the first match, or null

• Example:

var str = "Visit W3Schools";
var match = /w3schools/i.exec(str);
returns “W3Schools”

CodeExa
mples:
RegExp

– true() – returns true if there is a match, false otherwise

• Example:

var str = "Visit W3Schools";
var match = /w3schools/i.test(str);
returns “true”

http://www.w3schools.com/js/js_regexp.asp

64

Takeaways

• JS is a programming language that is one of

the core technologies of the World Wide Web,
alongside HTML and CSS.

• JS is a high-level, often just-in-time compiled
language that conforms to the ECMAScript
standard.

• JS has various important features, such as a
simple scripting style, lexical structure and
datatypes etc.


