# A chemical formula parser
For a given chemical formula represented by a string, parser counts the number 
of atoms of each element contained in the molecule and return a dict.

For example:

```py
water = 'H2O'
parse_molecule(water)              # Returns {'H': 2, 'O': 1}.

magnesium_hydroxide = 'Mg(OH)2'
parse_molecule(magnesium_hydroxide)# Returns {'Mg': 1, 'O': 2, 'H': 2}.

fremy_salt = 'K4[ON(SO3)2]2'
parse_molecule(fremy_salt)         # Returns {'K': 4, 'O': 14, 'N': 2, 'S': 4}.
```
As you can see, some formulas have brackets in them. 
The index outside the brackets tells you that you have to multiply count of 
each atom inside the bracket on this index. 

For example, in Fe(NO3)2 you have one iron atom, two nitrogen atoms and six 
oxygen atoms.

Note that brackets may be round, square or curly and can also be nested. 
Index after the braces is optional.

# How to use the parser.
Simply run "python parser.py" (must be a python 3).
Alternatively, you can run "jupyter notebook", so that Parser.ipynb gets run.

