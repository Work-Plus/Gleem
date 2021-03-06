from Objects.varObject import VariableObject
from Objects.builtinObject import BuiltInFunctionObject
import Objects.loopObject
import Objects.conditionObject


class BodyObject(object):

    def __init__(self, ast, astName, nesting_count):
        # The Name of the ast name using these methods
        self.astName = astName
        self.ast = ast

    def translate_body(self, body_ast, nesting_count):
        """ Transpile Body

        This method will use the body AST in order to create a python version of the gleem
        code for the body statement while managing indentations

        return:
            body_exec_string (str) : The python transpiled code
        """

        # Holds the body executable string of the first statement
        body_exec_string = ""

        # Loop through each ast item in the body dictionary
        for ast in body_ast:

            # This will parse variable declerations within the body
            if self.check_ast('VariableDecleration', ast):
                var_obj = VariableObject(ast)
                transpile = var_obj.translate()
                if self.should_dedent_trailing(ast=ast, full_ast=self.ast):
                    body_exec_string += ("   " * (nesting_count - 1)) + transpile + "\n"
                else:
                    body_exec_string += ("   " * nesting_count) + transpile + "\n"

            # This will parse built-in within the body
            if self.check_ast('PrebuiltFunction', ast):
                gen_builtin = BuiltInFunctionObject(ast)
                transpile = gen_builtin.translate()
                if self.should_dedent_trailing(ast, self.ast):
                    body_exec_string += ("   " * (nesting_count - 1)) + transpile + "\n"
                else:
                    body_exec_string += ("   " * nesting_count) + transpile + "\n"

            # This will parse nested conditional statement within the body
            if self.check_ast('ConditionalStatement', ast):
                # Increase nesting count because this is a condition statement inside a conditional statement
                # Only increase nest count if needed
                if self.should_increment_nest_count(ast, self.ast):
                    nesting_count += 1
                # Create conditional statement exec string
                condition_obj = Objects.conditionObject.ConditionObject(ast, nesting_count)
                # The second nested statement only needs 1 indent not 2
                if nesting_count is 2:
                    # Add the content of conditional statement with correct indentation
                    body_exec_string += "   " + condition_obj.translate()
                else:
                    # Add the content of conditional statement with correct indentation
                    body_exec_string += ("   " * (nesting_count - 1)) + condition_obj.translate()

            # This will parse nested conditional statement within the body
            if self.check_ast('ForLoop', ast):
                # Increase nesting count because this is a condition statement inside a conditional statement
                # Only increase nest count if needed
                if self.should_increment_nest_count(ast, self.ast):
                    nesting_count += 1
                # Create conditional statement exec string
                loop_obj = Objects.loopObject.LoopObject(ast, nesting_count)
                # The second nested statement only needs 1 indent not 2
                if nesting_count is 2:
                    # Add the content of conditional statement with correct indentation
                    body_exec_string += "   " + loop_obj.translate()
                else:
                    # Add the content of conditional statement with correct indentation
                    body_exec_string += ("   " * (nesting_count - 1)) + loop_obj.translate()

        return body_exec_string

    def check_ast(self, astName, ast):
        """ Call and Set Exec

        This method will check if the AST dictionary item being looped through has the
        same key name as the `astName` argument

        args:
            astName (str)  : This will hold the ast name we are matching
            ast     (dict) : The dict which the astName match will be done against
        returns:
            True    (bool) : If the astName matches the one in `ast` arg
            False   (bool) : If the astName doesn't matches the one in `ast` arg
        """
        try:
            # In some cases when method is called from should_dedent_trailing method ast
            # comes back with corret key but empty list value because it is removed. If
            # this is removed this method returns None instead and causes condition trailing
            # code to be indented one more than it should
            if ast[astName] is []: return True
            if ast[astName]: return True
        except:
            return False

    def should_dedent_trailing(self, ast, full_ast):
        """ Should dedent trailing

        This method will check if the ast item being checked is outside a conditional statement e.g.

        if a == 11 {
            if name == "gleem" {
                print "Not it";
            }
            print "Hi"; <--- This is the code that should be dedented by 1 so when found will return true if dedent flag is true
        }

        args:
            ast       (list) : The ConditionalStatement ast we are looking for
            full_ast  (list) : The full ast being parsed
        return:
            True  : If the code should not be indented because it is in current scope below current nested condition
            False : The item should not be dedented
        """
        print('///// - ', ast)
        # This creates an array of only body elements
        new_ast = full_ast[len(full_ast) - 1]['body']
        # This will know whether it should dedent
        dedent_flag = False

        # Loop through body ast's and when a conditonal statement is founds set
        # the dedent flag to 'true'
        for x in new_ast:
            print('-/-/- ', ast, ' ===== ', x)
            if self.check_ast(self.astName, x):
                dedent_flag = True

            if ast is x and dedent_flag is True:
                return True

        return False

    def should_increment_nest_count(self, ast, full_ast):
        """ Should dedent trailing

        This method will check if the ast item being checked is outside a conditional statement e.g.

        if a == 11 {
            if name == "gleem" {
                print "Not it";
            }
            if 1 != 2 { <--- This is the statement that should not be nested more
                print "Yo"
            }
        }

        args:
            ast       (list) : The ConditionalStatement ast we are looking for
            full_ast  (list) : The full ast being parsed
        return:
            True  : If the nesting should increase by 1
            False : If the nesting ahould not be increased
        """

        # Counts of the number of statements in that one scope
        statement_counts = 0

        # Loops through the body to count the number of conditional statements
        for x in full_ast[len(full_ast) - 1]['body']:

            # If a statement is found then increment statement count variable value by 1
            if self.check_ast(self.astName, x): statement_counts += 1
            # If the statement being checked is the one found then break
            if ast is x:
                break

        # Return false if there were less then 1 statements
        if statement_counts > 1:
            return False
        # Return true if there were more than 1 statements
        else:
            return True
