<h1>Conventions</h1>

<h2>Attribute and Function Ordering</h2>
Public Inner Class (Meta first then alphabetical order if possible)  
Abstract Validation Functions (alphabetical order)  
Concrete Validation Functions (alphabetical order)  
Class Attributes (no required order)  
Dunder Functions (`__init__` first then alphabetical order)  
Public Abstract Functions (alphabetical order if possible)  
Public Concrete Functions (alphabetical order if possible)  
Public Properties (alphabetical order on attribute then getter, setter)
Private Functions (alphabetical order)  
Abstract Class Functions (alphabetical order)  
Concrete Class Functions (alphabetical order)  
Static Functions (alphabetical order)

<h2>Data Types</h2>
<h3>List</h3>
A particular list usage can vary in length but all elements must
be of the same type
<h3>Tuple</h3>
A particular tuple usage must not vary in length and elements
must be in the same order but can be of different types.

<h2>Docstrings and Type Hints</h2>
Use Google Python Style guide. Put type hints in docstring where code
linking works. Put type hints in the code where code linking does not 
work.
<h3>List</h3>
list[str, int] implies that attribute is a list in which all elements
are str or all elements are int (not a mix of strs and ints)
<h3>Tuple</h3>
tuple[str, int] implies that attribute is a 2-tuple in which the 
first elements is a str and the second element is an int
<h3>Dict</h3>
dict[str, int] implies that keys are strs and values are ints

<h2>Imports</h2>
Follow PEP 8.

Standard library imports.  
Blank Line.  
Related third party imports.  
Blank Line.  
Local application/library specific imports.

Within each group, put from statements before import statements. 
Relative imports before absolute imports. dot has higher precedence 
than alphabet characters (dot before alphabet characters when reading
from top to bottom)
