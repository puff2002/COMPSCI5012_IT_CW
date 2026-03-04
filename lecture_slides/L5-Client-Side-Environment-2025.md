Client Side Environment

Internet Technology
ITECH

The Creator
(of the web)

The Whole Stack

• HTTP
• HTTP Server
• HTML
• Web Browser / Editor / Usenet / FTP
• only ran on NeXT

Mostly developed and in place by

1990

The first web page

Web pages in 2026

• What has drastically changed? The web browser!

Web
Browser

Browsers Now

• Worldwide browser market share: now

Safari
18.37%

Edge
5.05%

Firefox
3.18%

Other
6.68%

UC Browser
0.76%

Android
0.54%
IE
0.25%

Opera
2.39%

Samsung
2.74%

Chrome
66.72%

StatCounter. (2024). Global market share held by leading internet browsers from January 2012 to February
2024. Statista. Statista Inc.. Accessed: February 12, 2024. https://www.statista.com/statistics/268254/market-share-
of-internet-browsers-worldwide-since-2009/

Browsers Evolution

• Worldwide browser market share over time

Chrome

Safari

Edge

Firefox

Internet Explorer

%

E
G
A
S
U

70.00

60.00

50.00

40.00

30.00

20.00

10.00

0.00

2
1

'

n
a
J

2
1

'

r
p
A

2
1

'

l

u
J

2
1

'

t
c
O

3
1

'

n
a
J

3
1

'

r
p
A

3
1

'

l

u
J

3
1

'

t
c
O

4
1

'

n
a
J

4
1

'

r
p
A

4
1

'

l

u
J

4
1

'

t
c
O

5
1

'

n
a
J

5
1

'

r
p
A

5
1

'

l

u
J

5
1

'

t
c
O

6
1

'

n
a
J

6
1

'

r
p
A

6
1

'

l

u
J

6
1

'

t
c
O

7
1

'

n
a
J

7
1

'

r
p
A

7
1

'

l

u
J

7
1

'

t
c
O

8
1

'

n
a
J

8
1

'

r
p
A

8
1

'

l

u
J

8
1

'

t
c
O

9
1

'

n
a
J

9
1

'

r
p
A

9
1

'

l

u
J

9
1

'

t
c
O

0
2

'

n
a
J

0
2

'

r
p
A

0
2

'

l

u
J

0
2

'

t
c
O

1
2

'

n
a
J

1
2

'

r
p
A

1
2

'

l

u
J

1
2

'

t
c
O

2
2

'

n
a
J

2
2

'

r
p
A

2
2

'

l

u
J

2
2

'

t
c
O

3
2

'

n
a
J

3
2

'

r
p
A

3
2

'

l

u
J

3
2

'

t
c
O

4
2

'

n
a
J

StatCounter. (2024). Global market share held by leading internet browsers from January 2012 to February
2024. Statista. Statista Inc.. Accessed: February 12, 2024. https://www.statista.com/statistics/268254/market-share-
of-internet-browsers-worldwide-since-2009/

BROWSER COMPONENTS

What is in a page?

HTML =
content

CSS =
appearance

JavaScript =
behavior

Client-side

Presentation

Processing

Content

Content

Cascading Style Sheets

Object-Relational Mapping

Python

Content

Processing

Processing

The Client-side environment
is the Browser

• The browser is the web application runtime
• Browser components:

– Rendering Engine: This engine parses HTML and CSS and

computes what you see

– JavaScript Engine: This engine executes your JavaScript

code

– Web APIs (Browser APIs): This is how Javascript interacts

with your page

▪ DOM API: read/change the page
▪ Events: clicks, input, submit, keydown…
▪ Fetch: network requests
▪ Storage: localStorage/sessionStorage
▪ Timers: setTimeout/setInterval

JavaScript

Guide &

Reference

or visit

w3schools

What JavaScript adds to the
web

• HTML + CSS are static

o HTML describes structure
o CSS describes appearance
o By themselves, the page doesn’t respond or change

• JavaScript adds behavior

o Respond to user actions (click, input, submit, keydown…)
o Run logic (validation, calculations, UI rules)
o Change the page without a full reload (update text,

classes, elements)

o Communicate with servers (fetch data) and update the UI

How JavaScript adds behaviour

• JavaScript does not edit the HTML file!
• JavaScript runs in the browser…

o but it needs a way to read and change what’s on

screen

• Javascript uses DOM  = Document Object Model

o A live tree of objects representing the HTML

(elements, attributes, text)

o JavaScript uses the DOM to select elements, listen for

events, update the page

DOCUMENT OBJECT MODEL

HTML Source Code

Document Object Model

“The Document Object Model is a platform- and
language-neutral interface that will allow
programs and scripts to dynamically access and
update the content, structure and style of
documents.

The document can be further processed and the
results of that processing can be incorporated back
into the presented page.”

DOM Standard (whatwg.org)

Document
node

Document Object Model
has a hierarchical structure
i.e., is a tree

Element
node

Text node

Attribute node

DocumentRoot Element:<html>Element:<head>Element:<title>Text:"A title"Element:<body>Element:<a>Attribute:"href"Text:"A Link"Element:<p>Text:'A paragraph'Parts of the tree can be
referred to as parents,
children and siblings.

Root Element:<html>Element:<head>Element:<body>First ChildLast ChildParent NodenextSiblingpreviousSiblingElement:<div>Element:<h1>Element:<a>First ChildLast ChildParent NodenextSiblingpreviousSiblingElement:<p>nextSiblingpreviousSiblingWhy do we need DOM
in the client side?

• A web page is a document
that can be either displayed in
the browser window or as the
HTML source.
• In both cases, it is the same
document but the Document
Object Model (DOM)
representation allows it to be
manipulated.

Element Properties &
Methods

Properties:
someElement.innerHTML - the text value
someElement.nodeName - the name
someElement.nodeValue - the value
someElement.parentNode - the parent node
someElement.childNodes - the child nodes
someElement.attributes - the attributes nodes

Methods:
someElement.getElementById(id) - get the element with a specified id
someElement.getElementsByTagName(name) - get all elements with a specified tag name
someElement.appendChild(node) - insert a child node
someElement.removeChild(node) - remove a child node

Element:<a>Attribute:"href"Text:"A Link"Finding HTML Elements

When you want to access HTML elements with JavaScript, you
have to find the elements first.

There are a couple of ways to do this:

•

•

•

Finding HTML elements by id:

document.getElementById(id);

Finding HTML elements by tag name:

document.getElementsByTagName(tag_name);

Finding HTML elements by class name

document.getElementsByClassName(class_name);
•
      document.querySelectorAll(CSS_selector).

Finding HTML elements by CSS selectors

Finding HTML elements by ID

<html>

<body>

 <p id="intro">Hello World!</p>

 <script type="text/javascript">
   txt=document.getElementById("intro")
                .innerHTML;
   document.write("<p>The

                   text from the intro
                   paragraph: " + txt + "</p>");

 </script>

</body>
</html>

https://www.w3schools.com/js/tryit.asp?filename=tryjs_dom_getelementbyid

Finding HTML Elements

by tag name

<html>
<body>

 <h2>JavaScript HTML DOM</h2>
 <p>Finding HTML Elements by Tag Name.</p>
 <p>This example demonstrates the <b>getElementsByTagName</b>

method.</p>

 <p id="demo"></p>

 <script>
   const element = document.getElementsByTagName("p");

   document.getElementById("demo").innerHTML
       = 'The text in first paragraph (index 0)
          is: ' + element[0].innerHTML;
  </script>

</body>
</html>

https://www.w3schools.com/js/tryit.asp?filename=tryjs_dom_getelementsbytagname2

Finding HTML Elements
by class name

<html>
<body>

 <h2>JavaScript HTML DOM</h2>
 <p class="intro">Finding HTML Elements by Class Name.</p>
 <p class="intro">This example demonstrates

                   the<b>getElementsByTagName</b> method.</p>

 <p id="demo"></p>

 <script>
   const x = document.getElementsByClassName("intro");
   document.getElementById("demo").innerHTML =
      'The first paragraph (index 0) with class="intro" is: '

       + x[0].innerHTML;
  </script>

</body>
</html>

https://www.w3schools.com/js/tryit.asp?filename=tryjs_dom_getelementsbyclassname

Finding HTML Elements
by CSS selector

<html>
<body>

 <h2>JavaScript HTML DOM</h2>
 <p class="intro">Finding HTML Elements by Query Selector.</p>
 <p class="intro">This example demonstrates

                   the<b>getElementsByTagName</b> method.</p>

 <p id="demo"></p>

 <script>
   const x = document.querySelectorAll("p.intro");
   document.getElementById("demo").innerHTML =
      'The first paragraph (index 0) with class="intro" is: '

        + x[0].innerHTML;
  </script>

</body>
</html>

https://www.w3schools.com/js/tryit.asp?filename=tryjs_dom_queryselectorall

DOM Advantages

• Tree structure makes the DOM easy to traverse
• Elements can be accessed one or more times

• Structure of the Tree is modifiable

• Values/Elements/Structure can be added, changed

and modified

•

It is a standard of the W3C
•

i.e. the unofficial/official law of the jungle

DOM Disadvantages

• Resource Intensive consuming lots of memory
it needs to be fully loaded in main memory

•

• Can be slow

• Depends on the size and complexity of the Tree

• May not be the best choice for all devices

•

i.e. graphics intensive applications or games

• A better alternative might be to use the Canvas,

directly
•

i.e. OpenGL

Working with the DOM

Javascript
Jquery
XHTML
CSS

XML
SAX/DOM Parsing
AJAX

MORE INFO…

W3Schools DOM Tutorial:
(https://www.w3schools.com/whatis/whatis_htmldom.asp)

Video: An Inconvenient API: The Theory of the DOM
(https://www.youtube.com/watch?v=Y2Y0U-2qJMs)

Tracking
User Activity

Handle this…

* onMouseDown ** Scroll ** onMouseOver ** onFocus ** onSelect ** onBlur ** onKeypress ** onMouseUp ** onClick ** ondblClick *Event Object

• Each event has an associated object
• Part of the DOM
• The Event Object provides information about:

– target element in which the event occurred
– state of the keyboard keys
– location of the mouse cursor
– state of the mouse buttons

Event Handling

• Like any interactive application, events can be

caught and used to execute functions

• You can add EventListeners to any DOM object

• For example, user input from forms can be
validated on the client-side using JavaScript
<form name="login_form" action="login" onsubmit="return
validateForm()" method="post">
           First name: <input type="text" name="fname">
           <input type="submit" value="Submit">
</form>

Event Flow

• Each event object has an ‘Event Target’, e.g., any
node in the DOM tree from where an event
originated

• There are two main types of event flow, handling

events targeted at nested elements
– event capture (global handling)
– event bubbling (local handling)

• Eventflow follows a “RoundTrip” pattern/model

Event Capture

• The event propagates
downwards though an
element’s ancestors

• Any event listeners of
the ancestor elements
will be executed first

addEventListener(type, listener, useCapture)
method of the EventTarget interface sets up a
function that will be called whenever the specified
event is delivered to the target.

alert()  instructs the browser to display a dialog
with an optional message, and to wait until the
user dismisses the dialog.

<Input>Event<Div><Body>*le click*Event Bubbling

• The event propagates
upwards though an
element’s ancestors

• Any event listeners of
the element will be
executed first

• Ancestors can then

potentially handle
the event

<Input>Event e<Div><Body>*le click*Remember…

• Event handling order under event capture:

handler1() - > handler2() -> handler3()

• Event handling order under event bubbling:

handler3() - > handler2() -> handler1()

JAVASCRIPT FRAMEWORKS
(TBC)

JavaScript Frameworks

• Ember

– initially released in December 2011
– Used less than more modern frameworks but still
– Benefits: stability, community support, clever coding principles

• Angular

– open-source web application framework led by the Angular

Team at  (originally AngularJS)

– released in 2016
– a component-based framework which uses declarative HTML

templates which are translated to optimised JavaScript
instructions.

– Angular uses TypeScript, a superset of JavaScript

JavaScript Frameworks

• Vue (Pronounce as view)

– released in 2014
– Vue, like AngularJS, extends HTML with some of its own
code, but mainly relies modern, standard JavaScript

• React

– Released by Facebook in 2013
– Technically a library for rendering UI components
– used in combination with other libraries to make

applications i.e. React and React Native enable developers
to make mobile applications, React and ReactDOM enable
them to make web applications, etc.

– React extends JavaScript with HTML-like syntax, known

as JSX

Summary

• Clients change on a regular basis – Chrome

has taken over from IE

• Client-side environment relies on HTML, CSS

and JavaScript as basic building blocks
• There are JS Frameworks that can help to

build web applications

• Important to understand DOM and event

handling


