###############################################################################
# Name:     parser.py .                                                       #
# Indent:   4 spaces (no tab).                                                #
# Width:    79 (comment lines < 73).                                          #
# Author:   github.com/gitcordier <contact@gcordier.net>                      #
# Version:  2.0.2                                                             #
# license:  Nope; consider the below code as public domain.                   #
###############################################################################


# The parser. See ReadMe.md.
# The parser is a routine (R) that relies on a six-state Turing machine (TM).
# TM reads a formula from RIGHT to LEFT.
# The six states are:
INITIAL   = "initial"
DIGIT     = "digit"
LOWERCASE = "lowercase"
UPPERCASE = "uppercase"
OPEN      = {"]", "}", ")"}  # Yes: We read from right to left.
CLOSE     = {"[", "{", "("}  # Same remark.


# The below function implements R.
# Six 'static' parameters, as a beginning:
DEBUG_ARRAY             = "array"   # Dictionary key.
LOG_EMPTY               = "No proper formula: Empty string. "
LOG_COEFF               = "Coefficient equals 0."
ERR                     = "ERROR: "
WRN                     = "WARNING: "
LOG_CHARACTER_ILLEGAL   = "Formula contains illegal character: "
LOG_CHARACTER_IRRELEVANT= "Formula begins with irrelevant character: '"
# We need:
#   - ascii_lowercase = "abcdefghijklmnopqrstuvwxyz";
#   - ascii_uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
#   - ascii_digits = "0123456789".
# Which yields the following:
import string


def parse_molecule(formula:str, debug=None)->dict:
    """
        Inputs:
            1.  formula: A string that represents a formula e.g. "H2O".
            2.  debug:   For debugging features. Optional argument.
        Output: The parsed formula e.g. {'H': 2, 'O': 1}.

        Policy: 'formula' must not be None.
    """

    # TM implementation.
    def set_array(formula):
        """
            We parse the formula.

            Input:  The formula.
            Output: The relevant information, in a list.

            Policy/Exceptions: 
                1.  Implements parse_molecule's policy: 
                    If formula is None, then a TypeError is raised.

                2.  Implements the chemical nomenclature:
                    If formula contains a character that is (either)
                        i.   not in {'A', 'a', ..., 'Z', 'z'};
                        ii.  not in {'0', ..., '9'};
                        iiii.not a bracket,
                    then a ValueError is catched. 
                    If debug, then the  ValueError is raised.
        """

        def nonzero(index:int)-> int:
            """
                Input:  a natural number 'index'.
                Output: index, as a positive number.

                Exceptions: ValueError for if index is nonpositive.
                If debug, then the ValueError is raised.
            """

            try:
                1/(index > 0)
            except ZeroDivisionError:
                try:
                    raise ValueError(LOG_COEFF)
                except ValueError:
                    index = ERR + LOG_COEFF
                    
                    if debug:
                        raise
                    
            return index

        array = []   # To be returned.

        try:
            if len(formula) == 0:
                return LOG_EMPTY

            element = ""  # Stores two letters, e.g "He".
            index   = 0  # Stores index digit(s).
            data    = formula[::-1]
            last    = formula[0]
            state   = INITIAL

            for c in data:
                try:
                    if c in string.digits:
                        if state is DIGIT:
                            # Since we are reading from the right,
                            index += int(c) * 10
                        else:
                            # i.e. c is an index digit.
                            index = int(c)
                            state = DIGIT

                    elif c in string.ascii_uppercase:
                        if state is DIGIT:
                            # Thus c denotes the element.
                            # The index has then been entirely read.
                            array.append([c, nonzero(index)])

                        elif state is LOWERCASE:
                            # element := c + element
                            array.append([c + element, nonzero(index)])
                        else:
                            array.append([c, 1])

                        if state is not UPPERCASE:
                            state = UPPERCASE
                        
                    elif c in string.ascii_lowercase:
                        element = c
                        if state in [INITIAL, UPPERCASE, OPEN, CLOSE]:
                            index = 1

                        elif state is LOWERCASE:
                            array.append([c, ERR + "Consecutive lowercase."])

                        state = LOWERCASE

                    elif c in OPEN:
                        if state is DIGIT:  # Index has then been read:
                            array.append([c, nonzero(index)])

                        elif state in [INITIAL, UPPERCASE, OPEN]:
                            array.append([c, 1])

                        elif state is CLOSE:
                            array.append([c, 1,WRN+"Useless closing bracket."])

                        elif state is LOWERCASE:
                            array.append([c, ERR+ "Lowercase before bracket."])

                        state = OPEN

                    elif c in CLOSE:
                        if state in [UPPERCASE, CLOSE]:
                            array.append([c, 0])

                        elif state is INITIAL:
                            array.append([c, ERR +"( or [ or { at the right."])

                        elif state is LOWERCASE:
                            array.append([c, ERR +    "Unexpected lowercase."])

                        elif state is OPEN:
                            array.append([c, 0, WRN +  "Empty group was set."])

                        else:  # STATE is DIGIT
                            array.append([c, ERR + "Misplaced digit."])

                        state = CLOSE

                    else:
                        1/(c == "-")    # For example, CO-OH is OK.

                except ZeroDivisionError:
                    array.append(["!!", ERR + LOG_CHARACTER_ILLEGAL + c ])
                    
                    try:
                        raise ValueError(
                            LOG_CHARACTER_ILLEGAL
                        )
                    except ValueError:
                        if debug:
                            raise
                #
            #
            if not(last.isupper() or last in CLOSE):
                array.append([last, ERR + LOG_CHARACTER_IRRELEVANT + last])
            
        except TypeError as err:
            raise TypeError("formula was 'None'.") from err
        
        return array
    # set_array: END----------------------------------------------------------#

  # DEBUGGING:
  # DEBUG_i is be displayed whether array[DEBUG_i] brings some trouble.
  # If 'ERROR:...' message, then the returned dictionary is a 'debugging' one.
    DEBUG_i   = -1
    ERROR_key = None

    array           = set_array(formula)
    WARNING_PARSING = "WARNING - Parsing"
    dictionary_log  = {}
    dictionary      = {}
    weight_         = [1]
    depth           = 0
  # Of course, this should never occur ;) ------------------------------------#
    if array is LOG_EMPTY:
        dictionary_log[WARNING_PARSING] = LOG_EMPTY

        if debug:
            dictionary_log[DEBUG_ARRAY] = []

        return dictionary_log
    #-------------------------------------------------------------------------#
    # So,
    for e in array:
      # DEBUGGING-------------------------------------------------------------#
        DEBUG_i += 1
        DEBUG_message = str(e[-1])

        if  ERR in DEBUG_message:
            ERROR_key = "ERROR - Illegal string"
            dictionary_log[ERROR_key] = "".join([
                "Check array[",
                str(DEBUG_i),
                "]. ",
                DEBUG_message[len(ERR)::]
            ])
            # # # # # # # # # # # # # # # # # #
            # Now we MUST exit from the loop. #
            # # # # # ## # ## # ## # ## # # # #
            break
        #---------------------------------------------------------------------#

      # The routine R:
        read  = e[0]
        index = e[1]

        if read.isalpha():
            index *= weight_[depth]

            if read in dictionary.keys():
                dictionary[read] += index
            else:
                dictionary[read] = index

        elif read in OPEN:
            weight_.append(weight_[depth] * index); depth += 1
        elif read in CLOSE:
            del weight_[depth];                     depth -= 1

          # DEBUGGING:--------------------------------------------------------#
            if depth < 0:
                ERROR_key = "ERROR  - Parsing"
                dictionary_log = {
                    ERROR_key: "{c: c in OPEN} < #{c: c in CLOSE}."
                    "See 'array[" + str(DEBUG_i) + "]."
                }
                break
            #-----------------------------------------------------------------#
        #
    #
    if dictionary == {}:
        dictionary_log[WARNING_PARSING] = "No element found. "

    if debug:
        dictionary_log[DEBUG_ARRAY] = array
        if depth > 0:
            if dictionary_log[WARNING_PARSING]:
                dictionary_log[WARNING_PARSING] += \
                    "#{c: c in CLOSE} < #{c: c in OPEN}."
            else:
                dictionary_log[WARNING_PARSING] = \
                    "#{c: c in CLOSE} < #{c: c in OPEN}."

    elif ERROR_key:
        dictionary_log["DEBUG"] = \
            "Call 'display_result(True)', so that 'array' gets displayed."

    return {**dictionary, **dictionary_log}

# parse_molecule: END---------------------------------------------------------#

# Inputs and display: BEGINNING. ---------------------------------------------#

def display_result(debug=None):

    __ = "--  "    # For lovely indent. Constant.
    formula = ""   # Likely to change...

    def get_result(array):
        """
            Returns:
                1. the very dictionary of the parsing.
                2. The parsing record, whether 'debug' is set.
        """

        dictionary = dict((k, array[k]) for k in array if k is not DEBUG_ARRAY)
        
        if debug:
            return dictionary, \
                __+__ + "array = " + "\n" + "".join(
                __+__+__ + str(e)  + "\n" for e in array[DEBUG_ARRAY])

        return dictionary, ""
    #

    for k in formula_:
        formula = formula_[k]
        dictionary, array = get_result(parse_molecule(formula, debug))
        print(__                                    + "\n" +
              __+     k                             + "\n" +
              __+__ + formula                       + "\n" +
              __+__ + "parsed: " + str(dictionary)  + "\n" + array)
    #

# The to-be-parsed formulae are embedded in a dictionary {(k, v)}:
#    k: A human-readable name of a given element/chemical compound (C).
#    v: C's formula.
#
#    Policy: v is not None.
formula_ = {
    # That MUST return the correct result:
    "expected_success_1": "HeK17[C13ON[SO11]7ON[CHe5]3]2",
    "expected_success_2": "[HeK17[C13ON[SO11]7ON[CHe5]3]2}",
    "expected_success_3": "[HeK17[C13ON[SO11]7ON[CHe5]3]2}10",
    "expected_success_4": "[HeK17[C13ON[SO11]7ON[CHe5]3]2}010",
    "expected_success_5": "CO-OH",
    "expected_warning_1": "[[]]]]",
    "expected_warning_2": "{}[[CH4]]",
    "expected_warning_3": "[[]]",
    "expected_warning_4": "",
    # That MUST fail:
    "expected_failure_1": "]",
    "expected_failure_2": "Hee2",
    "expected_failure_3": "3CO",
    "expected_failure_4": "4{",
    "expected_failure_6": "{",
    #"expected_failure_7": "A0B1",           # Crashes in debug mode.
    #"expected_failure_8": "(CH(CH3)0)2",    # Crashes in debug mode.
    #"expected_failure_9": "CH3@",           # Crashes in debug mode.
    "expected_failure_10": "u",
    # Uncomment if you want an Exception to raise:
    # "expected_Exception": None,
    # Real world examples:
    "water":               "H2O",
    "magnesium_hydoxide":  "Mg(OH)2",
    "Iron (II) nitrate":   "Fe(NO3)2",
    "fremy_salt":          "K4[ON(SO3)2]2",
}

# Here we are:
display_result(True)
display_result()
# END. -----------------------------------------------------------------------#
