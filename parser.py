###############################################################################
# Name:     parser.py .                                                       #
# Indent:   = 4 spaces (no tab).                                              #
# Width:    79 (comment lines < 73).                                          #
# Author:   github.com/gitcordier                                             #
# license:  Nope; consider the below code as public domain.                   #
###############################################################################

# Parser: BEGINNING. ---------------------------------------------------------#
#
# The parser. See Readme.md.

def parse_molecule(formula, debug=None):

    """
        The parser is a six-state automaton that reads the formula 
        from RIGHT to LEFT. 
        
        Inputs:
            1.  formula: A string that represents a formula e.g. "H2O".
            2.  debug: For debugging features. Optional argument.
        Output: The parsed formula e.g. {'H': 2, 'O': 1}.

        Policy/Exceptions:
            if debug:
                if formula is None, then a TypeError is raised.
            if not:
                form
    """
    
    # The parser states:
    INITIAL     = "initial"
    DIGIT       = "digit"
    LOWERCASE   = "lowercase"
    UPPERCASE   = "uppercase"
    OPEN        = {"]", "}", ")"} # Yes: We read from right to left.
    CLOSE       = {"[", "{", "("} # Same remark.
    

    def set_array(formula):

        """
            We enumerate the elements.
            
            Input: The formula.
            Output: the relevant information, in a list.
            
            Policy/Exceptions: 
                1.  If formula is None, then a TypeError is 
                        being raised.
                2.  If formula contains a character that is (either):
                        i.   not in {'A', 'a', ..., 'Z', 'z'};
                        ii.  not in {'0', ..., '9'};
                        iii. not a bracket,
                    then  a ZeroDivisionError is raised.
        """

        # is_upper: True if and only if c = 'A', 'B', ..., 'Z'.
        # is_upper: True if and only if c = 'a', 'b', ..., 'z'.
        is_upper = lambda c: c in map(chr, range(65, 91 )) and c.isupper()
        is_lower = lambda c: c in map(chr, range(97, 123)) and c.islower()

        try:
            element             = "" # Stores two-letter element, e.g. 'He'.
            index               = "" # Stores digit/consecutive digits.
            data                = formula[::-1]
            state               = INITIAL
            array               = []
            is_legal            = True
            formula_beginning   = data[-1]

            for c in data:
                try:
                    if c.isdigit():
                        if state is DIGIT:
                            # Since we are reading a sequence of digits,
                            index = c + index
                        else:
                            # i.e. c is a new digit
                            index = c 
                            state = DIGIT
                        
                    elif is_upper(c):
                        if state is DIGIT:
                            # Thus c denotes the element. 
                            # The index has then been entirely read.
                            array.append([c, int(index)])
                            #
                        elif state is LOWERCASE:
                            # element := c + element
                            array.append([c + element, int(index)])
                            #
                        else: 
                            array.append([c, 1])

                        if state is not UPPERCASE:
                            state = UPPERCASE
                    
                    elif is_lower(c): # Second letter of a new element:
                        element = c

                        if state in [INITIAL, UPPERCASE, OPEN, CLOSE]:
                            index = 1 
                        
                        elif state is LOWERCASE:
                            array.append([c,0, 
                                    "ERROR: Consecutive lowercase letters."])
                        state = LOWERCASE

                    elif c in OPEN:
                        if state is DIGIT: # Index has then been read:
                            array.append([c, int(index)])

                        elif state in [INITIAL, UPPERCASE, OPEN]:
                            array.append([c, 1])

                        elif state is CLOSE: 
                            array.append([c, 1, 
                                    "WARNING: Useless closing bracket."])
                        elif state is LOWERCASE:
                            array.append([c, 0, 
                                    "ERROR: Lowercase before bracket."])
                        
                        state = OPEN

                    elif c in CLOSE:
                        if state in [UPPERCASE, CLOSE]:
                            array.append([c, 0])
                        
                        elif state is INITIAL:
                            array.append([c, 0, 
                                    "ERROR: Opening bracket at the end."])
                        elif state is LOWERCASE:
                            array.append([c, 0, 
                                    "ERROR: Unexpected lowercase."])
                        elif state is OPEN:
                            array.append([c, 0, 
                                    "WARNING: Empty group was set."])
                        else: #STATE is DIGIT
                            array.append([c, 0, "ERROR: Misplaced digit."])
                            
                        #
                        state = CLOSE
                    else:
                        is_legal = False
                    
                    1/is_legal

                except Exception as ex:
                    raise ZeroDivisionError("Formula contains irrelevant characters.") from ex
                #
            #
            if  formula_beginning.islower() or \
                formula_beginning.isdigit() or \
                formula_beginning in OPEN: 
                array.append(["", 0, "ERROR: formula begins with irrelevant character."])
        except TypeError as ex:
            raise ex
        return array


    # set_array: END----------------------------------------------------------#

    array           = set_array(formula)
    dictionary      = {}
    dictionary_log  = {}
    weight_         = [1]
    depth           = 0

    # DEBUGGING:
    # DEBUG_i will be displayed whether array[DEBUG_i] brings some trouble.
    # If 'ERROR:...' message, then dictionary becomes a 'debugging' one.
    
    DEBUG_i     = -1
    ERROR_key   = None

    for e in array:

        # DEBUGGING-----------------------------------------------------------#
        DEBUG_i += 1

        if "ERROR" in str(e[-1]):
            ERROR_key = "ERROR - Illegal string"
            dictionary_log = {
                ERROR_key: "Check array[" + str(DEBUG_i) + "]."
            }
            break
        # --------------------------------------------------------------------#
        # 
        read            = e[0]
        new_weight      = e[1]

        if read in OPEN:
            weight_.append(weight_[depth] * new_weight)
            depth += 1

        elif read.isalpha():
            new_weight *= weight_[depth]

            if read in dictionary.keys():
                dictionary[read] +=  new_weight
            else:
                dictionary[read] =  new_weight
            
        elif read in CLOSE:
            del weight_[depth]
            depth -= 1

            if depth < 0:
                # DEBUGGING---------------------------------------------------#
                ERROR_key = "ERROR - Parsing"
                dictionary_log = {
                    ERROR_key: "{c: c in OPEN} < #{c: c in CLOSE}." \
                    "See 'array[" + str(DEBUG_i) + "]."
                }
                # ------------------------------------------------------------#
                break
            #
        #
    # DEBUGGING---------------------------------------------------------------#
    if len(array) == 0:
        dictionary_log["WARNING - empty"] = "You don't want an empty string." 
    # DEBUGGING---------------------------------------------------------------#
    
    # Because we want to look under the hood.
    if debug:
        # DEBUGGING-----------------------------------------------------------#
        if depth > 0:
                dictionary_log["WARNING - Parsing"] = \
                "#{c: c in CLOSE} < #{c: c in OPEN}."
        # --------------------------------------------------------------------#
        return {**dictionary, **dictionary_log}, array

    # DEBUGGING---------------------------------------------------------------#
    elif ERROR_key:
        dictionary_log["DEBUG"] = \
            "Call 'display_result(True)', so that 'array' gets displayed."
    # ------------------------------------------------------------------------#
    return {**dictionary, **dictionary_log}

# parse_molecule: END---------------------------------------------------------#

# Parser: END. ---------------------------------------------------------------#

# Inputs and display: BEGINNING. ---------------------------------------------#

def display_result(debug=None):
    
    __      = "--  "
    formula = ""

    def get_result(result):
        array       = ""
        dictionary  = result
        
        if debug:
            dictionary = result[0]
            array +=__+__+     "array = "   + "\n" + "".join(
                    __+__+__+   str(e)      + "\n"      for e in result[1])
        
        return dictionary, array
    #

    for k in formula_:
        formula             = formula_[k]
        dictionary, array   = get_result(parse_molecule(formula, debug))
        print(  __                                      + "\n" + 
                __+     k                               + "\n" +
                __+__+  formula                         + "\n" +
                __+__+ "parsed: " + str(dictionary)     + "\n" + array)
    #

# The to-be-parsed formulae are embedded in a dictionary:
formula_ = {
    "expected_success_1":   "HeK17[C13ON[SO11]7ON[CHe5]3]2",
    "expected_success_2":   "[HeK17[C13ON[SO11]7ON[CHe5]3]2}",
    "expected_succes_3":    "[HeK17[C13ON[SO11]7ON[CHe5]3]2}10",
    "expected_warning_1":    "[[]]",
    "expected_warning_2":    "[[]]]",
    "expected_failure_1":   "]",
    "expected_failure_2":   "Hee4",
    "expected_failure_3":   "2CO",
    "expected_failure_4":   "{",
    # Real world examples:
    "water":                "H2O",
    "magnesium_hydoxide":   "Mg(OH)2",
    "fremy_salt":           "K4[ON(SO3)2]2",
    "Iron (II) nitrate":    "Fe(NO3)2"
}

# Here we are:
display_result(True)
# display_result()
# END. -----------------------------------------------------------------------#



