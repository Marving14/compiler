#######################################
# IMPORTS
#######################################
from string_with_arrows import *
import string
import os
import math
import turtle
import random

#######################################
# TURTLE 
#######################################

global screen
screen = None 
global aTurtle
aTurtle = turtle.Turtle() 

def start_Turtle():
  screen = turtle.getscreen() 
  



#######################################
# TURTLE FUNCTIONS
#######################################
def turtle_square(side):
  aTurtle.fd(side)
  aTurtle.rt(90)
  aTurtle.fd(side)
  aTurtle.rt(90)
  aTurtle.fd(side)
  aTurtle.rt(90)
  aTurtle.fd(side)

def turtle_circle(radius):
  aTurtle.circle(radius)

def turtle_dot(diameter):
  aTurtle.dot(diameter)


#######################################
# CONSTANTS
#######################################
DIGITS = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS

#######################################
# ERRORS
#######################################
class Error:
  def __init__(self, pos_start, pos_end, error_name, details):
    self.pos_start = pos_start
    self.pos_end = pos_end
    self.error_name = error_name
    self.details = details
  
  def as_string(self):
    result  = f'{self.error_name}: {self.details}\n'
    result += f'File {self.pos_start.fn}, line {self.pos_start.ln + 1}'
    result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
    return result

class IllegalCharError(Error):
  def __init__(self, pos_start, pos_end, details):
    super().__init__(pos_start, pos_end, 'Illegal Character', details)

class ExpectedCharError(Error):
  def __init__(self, pos_start, pos_end, details):
    super().__init__(pos_start, pos_end, 'Expected Character', details)

class InvalidSyntaxError(Error):
  def __init__(self, pos_start, pos_end, details=''):
    super().__init__(pos_start, pos_end, 'Invalid Syntax', details)

class RTError(Error):
  def __init__(self, pos_start, pos_end, details, context):
    super().__init__(pos_start, pos_end, 'Runtime Error', details)
    self.context = context

  def as_string(self):
    result  = self.generate_traceback()
    result += f'{self.error_name}: {self.details}'
    result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
    return result

  def generate_traceback(self):
    result = ''
    pos = self.pos_start
    ctx = self.context

    while ctx:
      result = f'  File {pos.fn}, line {str(pos.ln + 1)}, in {ctx.display_name}\n' + result
      pos = ctx.parent_entry_pos
      ctx = ctx.parent

    return 'Traceback (most recent call last):\n' + result

#######################################
# POSITION
#######################################
class Position:
  def __init__(self, idx, ln, col, fn, ftxt):
    self.idx = idx
    self.ln = ln
    self.col = col
    self.fn = fn
    self.ftxt = ftxt

  def advance(self, current_char=None):
    self.idx += 1
    self.col += 1

    if current_char == '\n':
      self.ln += 1
      self.col = 0

    return self

  def copy(self):
    return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

#######################################
# TOKENS
#######################################
TT_INT				= 'Int'
TT_FLOAT    	= 'Float'
TT_STRING			= 'String'
TT_IDENTIFIER	= 'IDENTIFIER'
TT_KEYWORD		= 'KEYWORD'
TT_PLUS     	= 'PLUS'
TT_MINUS    	= 'MINUS'
TT_MUL      	= 'MUL'
TT_DIV      	= 'DIV'
TT_POW				= 'POW'
TT_EQ					= 'EQ'
TT_LPAREN   	= 'LPAREN'
TT_RPAREN   	= 'RPAREN'
TT_LSQUARE    = 'LSQUARE'
TT_RSQUARE    = 'RSQUARE'
TT_LBRACE     = 'LBRACE'
TT_RBRACE     = 'RBRACE'
TT_SEMMICOLOM = 'SEMMICOLOM'
TT_EE					= 'EE'
TT_NE					= 'NE'
TT_LT					= 'LT'
TT_GT					= 'GT'
TT_LTE				= 'LTE'
TT_GTE				= 'GTE'
TT_COMMA			= 'COMMA'
TT_ARROW			= 'ARROW'
TT_NEWLINE		= 'NEWLINE'
TT_EOF				= 'EOF'
TT_FUNCLINE   = 'FUNCLINE'



KEYWORDS = [
  'program',
  'main',
  'var',
  'and',
  'or',
  'not',
  'if',
  'elif',
  'else',
  'for',
  'to',
  'step',
  'while',
  'module',
  'then',
  'end',
  'return',
  'continue',
  'break',
  'do',
  'endFor',
  'Number',
  'Float',
  'Int', 
  'void',
  'String',

		 
]

TYPES = [
  'Int',
  'Float',
  'String',
		   
  'void'
]



class Token:
  def __init__(self, type_, value=None, pos_start=None, pos_end=None):
    self.type = type_
    self.value = value

    if pos_start:
      self.pos_start = pos_start.copy()
      self.pos_end = pos_start.copy()
      self.pos_end.advance()

    if pos_end:
      self.pos_end = pos_end.copy()

  def matches(self, type_, value):
    return self.type == type_ and self.value == value
  
  def __repr__(self):
    if self.value: return f'{self.type}:{self.value}'
    return f'{self.type}'

#######################################
# LEXER
#######################################

class Lexer:
  def __init__(self, fn, text):
    self.fn = fn
    self.text = text
    self.pos = Position(-1, 0, -1, fn, text)
    self.current_char = None
    self.advance()
  
  def advance(self):
    self.pos.advance(self.current_char)
    self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

  def make_tokens(self):
    tokens = []

    while self.current_char != None:
      if self.current_char in ' \t':
        self.advance()
      elif self.current_char == '%':
        self.skip_comment()
      elif self.current_char in ';\n':
        tokens.append(Token(TT_NEWLINE, pos_start=self.pos))
        self.advance()
      elif self.current_char in ':\n':
        tokens.append(Token(TT_FUNCLINE, pos_start=self.pos))
        self.advance()
      elif self.current_char in DIGITS:
        tokens.append(self.make_number())
      elif self.current_char in LETTERS:
        tokens.append(self.make_identifier())
      elif self.current_char == '"':
        tokens.append(self.make_string())
      elif self.current_char == '+':
        tokens.append(Token(TT_PLUS, pos_start=self.pos))
        self.advance()
      elif self.current_char == '-':
        tokens.append(self.make_minus_or_arrow())
      elif self.current_char == '*':
        tokens.append(Token(TT_MUL, pos_start=self.pos))
        self.advance()
      elif self.current_char == '/':
        tokens.append(Token(TT_DIV, pos_start=self.pos))
        self.advance()
      elif self.current_char == '^':
        tokens.append(Token(TT_POW, pos_start=self.pos))
        self.advance()
      elif self.current_char == '(':
        tokens.append(Token(TT_LPAREN, pos_start=self.pos))
        self.advance()
      elif self.current_char == ')':
        tokens.append(Token(TT_RPAREN, pos_start=self.pos))
        self.advance()
      elif self.current_char == '[':
        tokens.append(Token(TT_LSQUARE, pos_start=self.pos))
        self.advance()
      elif self.current_char == ']':
        tokens.append(Token(TT_RSQUARE, pos_start=self.pos))
        self.advance()
      elif self.current_char == '{':
        tokens.append(Token(TT_LBRACE, pos_start=self.pos))
        self.advance()
      elif self.current_char == '}':
        tokens.append(Token(TT_RBRACE, pos_start=self.pos))
        self.advance()
      elif self.current_char == '!':
        token, error = self.make_not_equals()
        if error: return [], error
        tokens.append(token)
      elif self.current_char == '=':
        tokens.append(self.make_equals())
      elif self.current_char == '<':
        tokens.append(self.make_less_than())
      elif self.current_char == '>':
        tokens.append(self.make_greater_than())
      elif self.current_char == ',':
        tokens.append(Token(TT_COMMA, pos_start=self.pos))
        self.advance()
      else:
        pos_start = self.pos.copy()
        char = self.current_char
        self.advance()
        return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

    tokens.append(Token(TT_EOF, pos_start=self.pos))
    return tokens, None

  def make_number(self):
    num_str = ''
    dot_count = 0
    pos_start = self.pos.copy()

    while self.current_char != None and self.current_char in DIGITS + '.':
      if self.current_char == '.':
        if dot_count == 1: break
        dot_count += 1
      num_str += self.current_char
      self.advance()

    if dot_count == 0:
      return Token(TT_INT, int(num_str), pos_start, self.pos)
    else:
      return Token(TT_FLOAT, float(num_str), pos_start, self.pos)

  def make_string(self):
    string = ''
    pos_start = self.pos.copy()
    escape_character = False
    self.advance()

    escape_characters = {
      'n': '\n',
      't': '\t'
    }

    while self.current_char != None and (self.current_char != '"' or escape_character):
      if escape_character:
        string += escape_characters.get(self.current_char, self.current_char)
      else:
        if self.current_char == '\\':
          escape_character = True
        else:
          string += self.current_char
      self.advance()
      escape_character = False
    
    
    self.advance()
    return Token(TT_STRING, string, pos_start, self.pos)

  def make_identifier(self):
    id_str = ''
    pos_start = self.pos.copy()

    while self.current_char != None and self.current_char in LETTERS_DIGITS + '_':
      id_str += self.current_char
      self.advance()

    tok_type = TT_KEYWORD if id_str in KEYWORDS else TT_IDENTIFIER
    return Token(tok_type, id_str, pos_start, self.pos)

  def make_minus_or_arrow(self):
    tok_type = TT_MINUS
    pos_start = self.pos.copy()
    self.advance()

    if self.current_char == '>':
      self.advance()
      tok_type = TT_ARROW

    return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

  def make_not_equals(self):
    pos_start = self.pos.copy()
    self.advance()

    if self.current_char == '=':
      self.advance()
      return Token(TT_NE, pos_start=pos_start, pos_end=self.pos), None

    self.advance()
    return None, ExpectedCharError(pos_start, self.pos, "'=' (after '!')")
  
  def make_equals(self):
    tok_type = TT_EQ
    pos_start = self.pos.copy()
    self.advance()

    if self.current_char == '=':
      self.advance()
      tok_type = TT_EE

    return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

  def make_less_than(self):
    tok_type = TT_LT
    pos_start = self.pos.copy()
    self.advance()

    if self.current_char == '=':
      self.advance()
      tok_type = TT_LTE

    return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

  def make_greater_than(self):
    tok_type = TT_GT
    pos_start = self.pos.copy()
    self.advance()

    if self.current_char == '=':
      self.advance()
      tok_type = TT_GTE

    return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

  def skip_comment(self):
    self.advance()

    if self.current_char =='%':
      while self.current_char != '\n':
        self.advance()
    else:
      return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

    self.advance()

#######################################
# NODES
#######################################

class NumberNode:
  def __init__(self, tok):
    self.tok = tok
    self.type = 'Int'

    self.pos_start = self.tok.pos_start
    self.pos_end = self.tok.pos_end

  def __repr__(self):
    return f'{self.tok}'

class FloatNode:
  def __init__(self, tok):
    self.tok = tok
    self.type = 'Float'

    self.pos_start = self.tok.pos_start
    self.pos_end = self.tok.pos_end

  def __repr__(self):
    return f'{self.tok}'

class IntNode:
  def __init__(self, tok):
    self.tok = tok
    self.type = 'Int'
    
    self.pos_start = self.tok.pos_start
    self.pos_end = self.tok.pos_end

  def __repr__(self):
    return f'{self.tok}'
    

class StringNode:
  def __init__(self, tok):
    self.tok = tok
    self.type = 'String'

    self.pos_start = self.tok.pos_start
    self.pos_end = self.tok.pos_end

  def __repr__(self):
    return f'{self.tok}'

class ListNode:
  def __init__(self, element_nodes, pos_start, pos_end):
    self.element_nodes = element_nodes
    self.type = 'ListNode' 

    self.pos_start = pos_start
    self.pos_end = pos_end

class MatNode:
    def __init__(self, list_nodes, pos_start, pos_end):
      self.list_nodes = list_nodes
      self.type = 'MatNode'

							  
						  

      self.pos_start = pos_start
      self.pos_end = pos_end

class VarAccessNode:
  def __init__(self, var_name_tok):
    self.var_name_tok = var_name_tok
    self.type = 'VarAccessNode'

    self.pos_start = self.var_name_tok.pos_start
    self.pos_end = self.var_name_tok.pos_end

class VarReAssignNode:
  def __init__(self, var_name_tok, value_node):
    self.var_name_tok = var_name_tok
    self.value_node = value_node
    self.type = 'VarReAssignNode'

    self.pos_start = self.var_name_tok.pos_start
    self.pos_end = self.value_node.pos_end


class VarAssignNode:
  def __init__(self, var_name_tok, value_node):
    self.var_name_tok = var_name_tok
    self.value_node = value_node
    self.type = 'VarAssignNode'

    self.pos_start = self.var_name_tok.pos_start
    self.pos_end = self.value_node.pos_end

class BinOpNode:
  def __init__(self, left_node, op_tok, right_node):
    self.left_node = left_node
    self.op_tok = op_tok
    self.right_node = right_node
    self.type = 'BinOpNode'

    self.pos_start = self.left_node.pos_start
    self.pos_end = self.right_node.pos_end

  def __repr__(self):
    return f'({self.left_node}, {self.op_tok}, {self.right_node})'

class UnaryOpNode:
  def __init__(self, op_tok, node):
    self.op_tok = op_tok
    self.node = node
    self.type = 'UnaryOpNode'

    self.pos_start = self.op_tok.pos_start
    self.pos_end = node.pos_end

  def __repr__(self):
    return f'({self.op_tok}, {self.node})'

class IfNode:
  def __init__(self, cases, else_case):
    self.cases = cases
    self.else_case = else_case
    self.type = 'IfNode'

    self.pos_start = self.cases[0][0].pos_start
    self.pos_end = (self.else_case or self.cases[len(self.cases) - 1])[0].pos_end

class MainNode:
  def __init__(self, body_node, should_return_null):
    self.body_node = body_node
    self.should_return_null = should_return_null
    self.type = 'MainNode'

   
    self.pos_start = self.body_node.pos_start
    self.pos_end = self.body_node.pos_end


class ProgramNode:
  def __init__(self, program_name, body_node, should_return_null):
    self.program_name =  program_name
    self.body_node = body_node
    self.should_return_null = should_return_null
    self.type = 'ProgramNode'

    self.pos_start = self.body_node.pos_start
    self.pos_end = self.body_node.pos_end

class ForNode:
  def __init__(self, var_name_tok, start_value_node, end_value_node, step_value_node, body_node, should_return_null):
    self.var_name_tok = var_name_tok
    self.start_value_node = start_value_node
    self.end_value_node = end_value_node
    self.step_value_node = step_value_node
    self.body_node = body_node
    self.should_return_null = should_return_null
    self.type = 'ForNode'

    self.pos_start = self.var_name_tok.pos_start
    self.pos_end = self.body_node.pos_end

class WhileNode:
  def __init__(self, condition_node, body_node, should_return_null):
    self.condition_node = condition_node
    self.body_node = body_node
    self.should_return_null = should_return_null
    self.type = 'WhileNode'

    self.pos_start = self.condition_node.pos_start
    self.pos_end = self.body_node.pos_end

class FuncDefNode:
  def __init__(self, var_name_tok, arg_name_toks, body_node, type_ ,should_auto_return):
    self.var_name_tok = var_name_tok
    self.arg_name_toks = arg_name_toks
    self.body_node = body_node
    self.type_ = type_
    self.should_auto_return = should_auto_return
    self.type = 'FuncDefNode'

    if self.var_name_tok:
      self.pos_start = self.var_name_tok.pos_start
    elif len(self.arg_name_toks) > 0:
      self.pos_start = self.arg_name_toks[0].pos_start
    else:
      self.pos_start = self.body_node.pos_start

    self.pos_end = self.body_node.pos_end

class CallNode:
  def __init__(self, node_to_call, arg_nodes):
    self.node_to_call = node_to_call
    self.arg_nodes = arg_nodes
    self.type = 'CallNode'

    self.pos_start = self.node_to_call.pos_start

    if len(self.arg_nodes) > 0:
      self.pos_end = self.arg_nodes[len(self.arg_nodes) - 1].pos_end
    else:
      self.pos_end = self.node_to_call.pos_end

class returnNode:
  def __init__(self, node_to_return, pos_start, pos_end):
    self.node_to_return = node_to_return
    self.type = 'returnNode'

    self.pos_start = pos_start
    self.pos_end = pos_end

class ContinueNode:
  def __init__(self, pos_start, pos_end):
    self.pos_start = pos_start
    self.pos_end = pos_end
    self.type = 'ContinueNode'

class BreakNode:
  def __init__(self, pos_start, pos_end):
    self.pos_start = pos_start
    self.pos_end = pos_end
    self.type = 'BreakNode'

#######################################
# PARSE RESULT
#######################################

class ParseResult:
  def __init__(self):
    self.error = None
    self.node = None
    self.last_registered_advance_count = 0
    self.advance_count = 0
    self.to_reverse_count = 0

  def register_advancement(self):
    self.last_registered_advance_count = 1
    self.advance_count += 1

  def register(self, res):
    self.last_registered_advance_count = res.advance_count
    self.advance_count += res.advance_count
    if res.error: self.error = res.error
    return res.node

  def try_register(self, res):
    if res.error:
      self.to_reverse_count = res.advance_count
      return None
    return self.register(res)

  def success(self, node):
    self.node = node
    return self

  def failure(self, error):
    if not self.error or self.last_registered_advance_count == 0:
      self.error = error
    return self

#######################################
# PARSER
#######################################

class Parser:
  def __init__(self, tokens):
    self.tokens = tokens
    self.tok_idx = -1
    self.advance()
  
  def update_current_tok(self):
    if self.tok_idx >= 0 and self.tok_idx < len(self.tokens):
      self.current_tok = self.tokens[self.tok_idx]
      

  def advance(self):
    self.tok_idx += 1
    self.update_current_tok()
    return self.current_tok

  def reverse(self, amount=1):
    self.tok_idx -= amount
    self.update_current_tok()
    return self.current_tok

  def parse(self):
    res = self.statements()
    if not res.error and self.current_tok.type != TT_EOF:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        "Token cannot appear after previous tokens"
      ))
    return res

  ###################################

  def statements(self):
    res = ParseResult()
    statements = []
    pos_start = self.current_tok.pos_start.copy()

    while self.current_tok.type == TT_NEWLINE:
      res.register_advancement()
      self.advance()

    statement = res.register(self.statement())
    if res.error: return res
    statements.append(statement)

    more_statements = True

    while True:
      newline_count = 0
      while self.current_tok.type == TT_NEWLINE:
        res.register_advancement()
        self.advance()
        newline_count += 1
      if newline_count == 0:
        more_statements = False
      
      if not more_statements: break
      statement = res.try_register(self.statement())
      if not statement:
        self.reverse(res.to_reverse_count)
        more_statements = False
        continue
      statements.append(statement)

    return res.success(ListNode(
      statements,
      pos_start,
      self.current_tok.pos_end.copy()
    ))


  def statement(self):
    res = ParseResult()
    pos_start = self.current_tok.pos_start.copy()

    if self.current_tok.matches(TT_KEYWORD, 'return'):
      res.register_advancement()
      self.advance()

      expr = res.try_register(self.expr())
      if not expr:
        self.reverse(res.to_reverse_count)
      return res.success(returnNode(expr, pos_start, self.current_tok.pos_start.copy()))
    
    # remove
    if self.current_tok.matches(TT_KEYWORD, 'continue'):
      res.register_advancement()
      self.advance()
      return res.success(ContinueNode(pos_start, self.current_tok.pos_start.copy()))
      
    if self.current_tok.matches(TT_KEYWORD, 'break'):
      res.register_advancement()
      self.advance()
      return res.success(BreakNode(pos_start, self.current_tok.pos_start.copy()))

    expr = res.register(self.expr())
    if res.error:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        "Expected 'return', 'continue', 'break', 'var', 'if', 'for', 'while', 'module', 'Int', 'Float', 'identifier', '+', '-', '(', '[' or 'not'"
      ))
    return res.success(expr)



  def expr(self):
    res = ParseResult()

    if self.current_tok.matches(TT_KEYWORD, 'var'):

      le = len(self.tokens)
      type_ = self.tokens[1].value

      # is list
      isVar = self.tokens[4].type
      isList = self.tokens[4].type
      isMat = self.tokens[5].type

      #check if MAT
      if isMat == 'LSQUARE' and isList == 'LSQUARE' and isVar == 'LSQUARE':
        # Is MAT
        cont  = 6
        while cont < le-3:
          if self.tokens[cont].type == 'COMMA':
            cont = cont +2

          if type_ != self.tokens[cont].type:
            return res.failure(InvalidSyntaxError(
              self.current_tok.pos_start, self.current_tok.pos_end,
              "Type mismatch xd "
            ))
          cont = cont + 2
      elif isMat != 'LSQUARE' and isList == 'LSQUARE' and isVar == 'LSQUARE':
        # IS LIST
        cont = 5
        while cont < le-2:
          if type_ != self.tokens[cont].type:
            return res.failure(InvalidSyntaxError(
              self.current_tok.pos_start, self.current_tok.pos_end,
              "Type mismatch xd "
            ))
          cont = cont + 2

      elif (isMat == 'EOF' or isMat == 'NEWLINE') and isList != 'LSQUARE' and isVar != 'LSQUARE':
        # IS VAR
        if type_ != isVar:
          return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            "Type mismatch xd "
          ))


      res.register_advancement()
      self.advance()

      booll = False
      type_ = ''

      if self.current_tok.matches(TT_KEYWORD, 'Int'):
        type_ = 'Int'
        booll = True
      elif self.current_tok.matches(TT_KEYWORD, 'Number'):
        type_ = 'Number'
        booll = True
      elif self.current_tok.matches(TT_KEYWORD, 'String'):
        type_ = 'String'
        booll = True
      elif self.current_tok.matches(TT_KEYWORD, 'Float'):
        type_ = 'Float'
        booll = True

      if not booll:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected var 'type' "
        ))

      res.register_advancement()
      self.advance()

      if self.current_tok.type != TT_IDENTIFIER:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          "Expected identifier"
        ))

      var_name = self.current_tok

      res.register_advancement()
      self.advance()


      if self.current_tok.type != TT_EQ:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          "Expected '='"
        ))

      res.register_advancement()
      self.advance()
      expr = res.register(self.expr())

      if res.error:
        return res
      return res.success(VarAssignNode(var_name, expr))

    node = res.register(self.bin_op(self.comp_expr, ((TT_KEYWORD, 'and'), (TT_KEYWORD, 'or'))))

    if res.error:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        "Expected 'var', 'if', 'for', 'while', 'module', Int, Float, identifier, '+', '-', '(', '[' or 'not'"
      ))

    return res.success(node)

  def comp_expr(self):
    res = ParseResult()

    if self.current_tok.matches(TT_KEYWORD, 'not'):
      op_tok = self.current_tok
      res.register_advancement()
      self.advance()

      node = res.register(self.comp_expr())
      if res.error: return res
      return res.success(UnaryOpNode(op_tok, node))
    
    node = res.register(self.bin_op(self.arith_expr, (TT_EE, TT_NE, TT_LT, TT_GT, TT_LTE, TT_GTE)))
    
    if res.error:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        "Expected Int, Float, identifier, '+', '-', '(', '[', 'if', 'for', 'while', 'module' or 'not'"
      ))

    return res.success(node)

  def arith_expr(self):
    return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

  def term(self):
    return self.bin_op(self.factor, (TT_MUL, TT_DIV))

  def factor(self):
    res = ParseResult()
    tok = self.current_tok

    if tok.type in (TT_PLUS, TT_MINUS):
      res.register_advancement()
      self.advance()
      factor = res.register(self.factor())
      if res.error: return res
      return res.success(UnaryOpNode(tok, factor))

    return self.power()

  def power(self):
    return self.bin_op(self.call, (TT_POW, ), self.factor)

  def call(self):
    res = ParseResult()
    atom = res.register(self.atom())
    if res.error: return res

    if self.current_tok.type == TT_LPAREN:
      res.register_advancement()
      self.advance()
      arg_nodes = []

      if self.current_tok.type == TT_RPAREN:
        res.register_advancement()
        self.advance()
      else:
        arg_nodes.append(res.register(self.expr()))
        if res.error:
          return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            "Expected ')', 'var', 'if', 'for', 'while', 'module', Int, Float, identifier, '+', '-', '(', '[' or 'not'"
          ))

        while self.current_tok.type == TT_COMMA:
          res.register_advancement()
          self.advance()

          arg_nodes.append(res.register(self.expr()))
          if res.error: return res

        if self.current_tok.type != TT_RPAREN:
          return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            f"Expected ',' or ')'"
          ))

        res.register_advancement()
        self.advance()
      return res.success(CallNode(atom, arg_nodes))
    return res.success(atom)

  def atom(self):
    res = ParseResult()
    tok = self.current_tok
    element_nodes = []
    pos_start = self.current_tok.pos_start.copy()

    if tok.type == TT_INT:
      res.register_advancement()
      self.advance()
      return res.success(IntNode(tok))
    
    if tok.type == TT_FLOAT:
      res.register_advancement()
      self.advance()
      return res.success(FloatNode(tok))

    elif tok.type == TT_STRING:
      res.register_advancement()
      self.advance()
      return res.success(StringNode(tok))

    elif tok.type == TT_IDENTIFIER:
      var_name = self.current_tok

      res.register_advancement()
      self.advance()

      ########################### ident Time

      #if self.current_tok.type == TT_IDENTIFIER:
      if self.current_tok.type == TT_EQ: 
        #var_name = self.current_tok
        res.register_advancement()
        self.advance()

        expr = res.register(self.expr())
        if res.error: return res
        return res.success(VarAssignNode(var_name, expr))
        node = res.register(self.bin_op(self.comp_expr, ((TT_KEYWORD, 'and'), (TT_KEYWORD, 'or'))))

        if res.error:
          return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            "Expected 'var', 'if', 'for', 'while', 'module', Int, Float, identifier, '+', '-', '(', '[' or 'not'"
          ))

        return res.success(node)
        
      ###################################









      ###################################
      #res.register_advancement()
      #self.advance()
      return res.success(VarAccessNode(tok))

    elif tok.type == TT_LPAREN:
      res.register_advancement()
      self.advance()
      expr = res.register(self.expr())
      if res.error: return res
      if self.current_tok.type == TT_RPAREN:
        res.register_advancement()
        self.advance()
        return res.success(expr)
      else:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          "Expected ')'"
        ))

    elif tok.type == TT_LSQUARE:
      list_expr = res.register(self.list_expr())
      if res.error: return res
      return res.success(list_expr)
    
    elif tok.matches(TT_KEYWORD, 'if'):
      if_expr = res.register(self.if_expr())
      if res.error: return res
      return res.success(if_expr)

    elif tok.matches(TT_KEYWORD, 'for'):
      for_expr = res.register(self.for_expr())
      if res.error: return res
      return res.success(for_expr)

    elif tok.matches(TT_KEYWORD, 'while'):
      while_expr = res.register(self.while_expr())
      if res.error: return res
      return res.success(while_expr)
    elif tok.matches(TT_KEYWORD, 'void'):
      func_def = res.register(self.function_def())
      if res.error: return res
      return res.success(func_def)
    elif tok.matches(TT_KEYWORD, 'Number'):
      func_def = res.register(self.function_def())
      if res.error: return res
      return res.success(func_def)
    elif tok.matches(TT_KEYWORD, 'Int'):
      func_def = res.register(self.function_def())
      if res.error: return res
      return res.success(func_def)
    elif tok.matches(TT_KEYWORD, 'String'):
      func_def = res.register(self.function_def())
      if res.error: return res
      return res.success(func_def)
    elif tok.matches(TT_KEYWORD, 'Float'):
												  
							  
								  
										  
      func_def = res.register(self.function_def())
      if res.error: return res
      return res.success(func_def)
    elif tok.matches(TT_KEYWORD, 'program'):
      func_def = res.register(self.program_expr())
      if res.error: return res
      return res.success(func_def)
    elif tok.matches(TT_KEYWORD, 'main'):
      func_def = res.register(self.main_expr())
      if res.error: return res
      return res.success(func_def)

    return res.failure(InvalidSyntaxError(
      tok.pos_start, tok.pos_end,
      "Expected Int, Float, identifier, '+', '-', '(', '[', if', 'for', 'while', 'module'"
    ))

  def list_expr(self):
    res = ParseResult()
    element_nodes = []
    list_nodes = []
    pos_start = self.current_tok.pos_start.copy()

    #############################################################
    typeOfList = self.tokens[1].value
    #############################################################

    if self.current_tok.type != TT_LSQUARE:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected '['"
      ))
    #print(self.current_tok.type)
    res.register_advancement()
    self.advance()

    # Case list
    if self.current_tok.type != TT_LSQUARE:

      if self.current_tok.type == TT_RSQUARE:
        res.register_advancement()
        self.advance()
      else:
        element_nodes.append(res.register(self.expr()))
        if res.error:
          return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            "Expected ']', 'var', 'if', 'for', 'while', 'module', int, float, identifier, '+', '-', '(', '[' or 'not'"
          ))

        while self.current_tok.type == TT_COMMA:
          res.register_advancement()
          self.advance()

          element_nodes.append(res.register(self.expr()))
          if res.error: return res
          
        if self.current_tok.type != TT_RSQUARE:
          return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            f"Expected ',' or ']'"
          ))

        res.register_advancement()
        self.advance()
      


      return res.success(ListNode(
        element_nodes,
        pos_start,
        self.current_tok.pos_end.copy()
      ))
    
    else:
      # CASE MAT
      con = True
      # segundo [
      if self.current_tok.type != TT_LSQUARE:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected '['"
        ))
      #print("middle if", self.current_tok.type)
      res.register_advancement()
      self.advance()
      #print("before s if", self.current_tok.type)

      if self.current_tok.type == TT_RSQUARE:
        res.register_advancement()
        self.advance()
        #print("if second ]", self.current_tok.type)
      else:
        #print("tok else", self.current_tok.type)
        element_nodes.append(res.register(self.expr()))
        if res.error:
          return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            "Expected ']', 'var', 'if', 'for', 'while', 'module', Int, Float, identifier, '+', '-', '(', '[' or 'not'"
          ))

        while self.current_tok.type == TT_COMMA:
          res.register_advancement()
          self.advance()

          element_nodes.append(res.register(self.expr()))
          if res.error: return res
        
        # Primer  ] 
        if self.current_tok.type != TT_RSQUARE:
          return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            f"Expected ',' or ']'"
          ))

        res.register_advancement()
        self.advance()
      

      #print("tok before append", self.current_tok.type)


      element = ListNode(
        element_nodes,
        pos_start,
        self.current_tok.pos_end.copy()
      ) 
      list_nodes.append(element)
      #print(list_nodes)

      while self.current_tok.type == TT_COMMA:
        element_nodes = []
        res.register_advancement()
        self.advance()
        # segundo [
        if self.current_tok.type != TT_LSQUARE:
          return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            f"Expected '['"
          ))
        #print("middle if", self.current_tok.type)
        res.register_advancement()
        self.advance()
        #print("before s if", self.current_tok.type)

        if self.current_tok.type == TT_RSQUARE:
          res.register_advancement()
          self.advance()
          #print("if second ]", self.current_tok.type)
        else:
          #print("tok else", self.current_tok.type)
          element_nodes.append(res.register(self.expr()))
          if res.error:
            return res.failure(InvalidSyntaxError(
              self.current_tok.pos_start, self.current_tok.pos_end,
              "Expected ']', 'var', 'if', 'for', 'while', 'module', Int, Float, identifier, '+', '-', '(', '[' or 'not'"
            ))

          while self.current_tok.type == TT_COMMA:
            res.register_advancement()
            self.advance()

            element_nodes.append(res.register(self.expr()))
            if res.error: return res
          
          # Primer  ] 
          if self.current_tok.type != TT_RSQUARE:
            return res.failure(InvalidSyntaxError(
              self.current_tok.pos_start, self.current_tok.pos_end,
              f"Expected ',' or ']'"
            ))

          res.register_advancement()
          self.advance()
        

        #print("tok before append", self.current_tok.type)


        element = ListNode(
          element_nodes,
          pos_start,
          self.current_tok.pos_end.copy()
        ) 
        list_nodes.append(element)
        #print(list_nodes)
      # ] de fin de mat
      if self.current_tok.type != TT_RSQUARE:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected ']'"
        ))

      res.register_advancement()
      self.advance()

      return res.success(MatNode(
        list_nodes,
        pos_start,
        self.current_tok.pos_end.copy()
      )) 

  def if_expr(self):
    res = ParseResult()
    all_cases = res.register(self.if_expr_cases('if'))
    if res.error: return res
    cases, else_case = all_cases
    return res.success(IfNode(cases, else_case))

  # remove
  def if_expr_b(self):
    return self.if_expr_cases('ELIF')
    
  def if_expr_c(self):
    res = ParseResult()
    else_case = None

    if self.current_tok.matches(TT_KEYWORD, 'else'):
      res.register_advancement()
      self.advance()

      if self.current_tok.type == TT_FUNCLINE:
        res.register_advancement()
        self.advance()

        statements = res.register(self.statements())
        if res.error: return res
        else_case = (statements, True)

        if self.current_tok.matches(TT_KEYWORD, 'end'):
          res.register_advancement()
          self.advance()
        else:
          return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            "Expected 'end'"
          ))
      # Case there is no else 
      else:
        expr = res.register(self.statement())
        if res.error: return res
        else_case = (expr, False)

    return res.success(else_case)

  def if_expr_b_or_c(self):
    res = ParseResult()
    cases, else_case = [], None

    # remove 
    if self.current_tok.matches(TT_KEYWORD, 'elif'):
      all_cases = res.register(self.if_expr_b())
      if res.error: return res
      cases, else_case = all_cases
    else:
      else_case = res.register(self.if_expr_c())
      if res.error: return res
    
    return res.success((cases, else_case))

  def if_expr_cases(self, case_keyword):
    res = ParseResult()
    cases = []
    else_case = None

    if not self.current_tok.matches(TT_KEYWORD, case_keyword):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected '{case_keyword}'"
      ))

    res.register_advancement()
    self.advance()

    condition = res.register(self.expr())
    if res.error: return res

    if not self.current_tok.matches(TT_KEYWORD, 'then'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'then'"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type == TT_FUNCLINE:
      res.register_advancement()
      self.advance()

      statements = res.register(self.statements())
      if res.error: return res
      cases.append((condition, statements, True))

      if self.current_tok.matches(TT_KEYWORD, 'end'):
        res.register_advancement()
        self.advance()
      else:
        all_cases = res.register(self.if_expr_b_or_c())
        if res.error: return res
        new_cases, else_case = all_cases
        cases.extend(new_cases)
    else:
      expr = res.register(self.statement())
      if res.error: return res
      cases.append((condition, expr, False))

      all_cases = res.register(self.if_expr_b_or_c())
      if res.error: return res
      new_cases, else_case = all_cases
      cases.extend(new_cases)

    return res.success((cases, else_case))


  def main_expr(self):
    res = ParseResult()

    if not self.current_tok.matches(TT_KEYWORD, 'main'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'main'"
      ))

    res.register_advancement()
    self.advance()

    if not self.current_tok.type == TT_LPAREN:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected '('"
      ))

    res.register_advancement()
    self.advance()

    if not self.current_tok.type == TT_RPAREN:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected ')'"
      ))
    
    res.register_advancement()
    self.advance()

    sq1 = '{'
    if not self.current_tok.type == TT_LBRACE:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected {sq1} "
      ))

    if self.current_tok.type == TT_LBRACE:
      res.register_advancement()
      self.advance()

      body = res.register(self.statements())
      if res.error: return res
      sq = '}'

      if not self.current_tok.type == TT_RBRACE:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected {sq}"
        ))

      res.register_advancement()
      self.advance()

      return res.success(MainNode(body, False))

    body = res.register(self.statement())
    if res.error: return res

    return res.success(MainNode(body, False))

  def program_expr(self):
    res = ParseResult()

    if not self.current_tok.matches(TT_KEYWORD, 'program'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'program'"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type != TT_IDENTIFIER:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected identifier"
      ))
    program_name = self.current_tok
    
    res.register_advancement()
    self.advance()

    if self.current_tok.type != TT_NEWLINE:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected ';'"
      ))

    if self.current_tok.type == TT_NEWLINE:
      res.register_advancement()
      self.advance()

      body = res.register(self.statements())
      if res.error: return res

      res.register_advancement()
      self.advance()

      return res.success(ProgramNode(program_name, body, False))
    
    body = res.register(self.statement())
    if res.error: return res

    return res.success(ProgramNode(program_name, body, False))
      

  def for_expr(self):
    res = ParseResult()

    if not self.current_tok.matches(TT_KEYWORD, 'for'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'for'"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type != TT_IDENTIFIER:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected identifier"
      ))

    var_name = self.current_tok
    res.register_advancement()
    self.advance()

    if self.current_tok.type != TT_EQ:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected '='"
      ))
    
    res.register_advancement()
    self.advance()

    start_value = res.register(self.expr())
    if res.error: return res

    if not self.current_tok.matches(TT_KEYWORD, 'to'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'to'"
      ))
    
    res.register_advancement()
    self.advance()

    end_value = res.register(self.expr())
    if res.error: return res

    if self.current_tok.matches(TT_KEYWORD, 'step'):
      res.register_advancement()
      self.advance()

      step_value = res.register(self.expr())
      if res.error: return res
    else:
      step_value = None

    if not self.current_tok.matches(TT_KEYWORD, 'do'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'do'"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type == TT_FUNCLINE:
      res.register_advancement()
      self.advance()

      body = res.register(self.statements())
      if res.error: return res

      if not self.current_tok.matches(TT_KEYWORD, 'endFor'):
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected 'endFor'"
        ))

      res.register_advancement()
      self.advance()

      return res.success(ForNode(var_name, start_value, end_value, step_value, body, True))
    
    body = res.register(self.statement())
    if res.error: return res

    return res.success(ForNode(var_name, start_value, end_value, step_value, body, False))

  def while_expr(self):
    res = ParseResult()

    if not self.current_tok.matches(TT_KEYWORD, 'while'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'while'"
      ))

    res.register_advancement()
    self.advance()

    condition = res.register(self.expr())
    if res.error: return res

    if not self.current_tok.matches(TT_KEYWORD, 'do'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'do'"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type == TT_FUNCLINE:
      res.register_advancement()
      self.advance()

      body = res.register(self.statements())
      if res.error: return res

      if not self.current_tok.matches(TT_KEYWORD, 'endWhile'):
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected 'endWhile'"
        ))

      res.register_advancement()
      self.advance()

      return res.success(WhileNode(condition, body, True))
    
    body = res.register(self.statement())
    if res.error: return res

    return res.success(WhileNode(condition, body, False))
  ###############################
  def function_def(self):
    res = ParseResult()

    booll = False
    type_ = ''

    if self.current_tok.matches(TT_KEYWORD, 'void'):
      type_ = 'void'
      booll = True
    elif self.current_tok.matches(TT_KEYWORD, 'Int'):
      type_ = 'Int'
      booll = True
    elif self.current_tok.matches(TT_KEYWORD, 'Number'):
      type_ = 'Number'
      booll = True
    elif self.current_tok.matches(TT_KEYWORD, 'String'):
      type_ = 'String'
      booll = True
													  
					
				  
    elif self.current_tok.matches(TT_KEYWORD, 'Float'):
      type_ = 'Float'
      booll = True
    


    if not booll:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'type' module"
      ))
    
    res.register_advancement()
    self.advance()

    if not self.current_tok.matches(TT_KEYWORD, 'module'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'module'"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type == TT_IDENTIFIER:
      var_name_tok = self.current_tok
      res.register_advancement()
      self.advance()
      if self.current_tok.type != TT_LPAREN:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected '('"
        ))
    else:
      var_name_tok = None
      if self.current_tok.type != TT_LPAREN:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected identifier "
        ))
    
    res.register_advancement()
    self.advance()
    arg_name_toks = []

    if self.current_tok.type == TT_IDENTIFIER:
      arg_name_toks.append(self.current_tok)
      res.register_advancement()
      self.advance()
      
      while self.current_tok.type == TT_COMMA:
        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT_IDENTIFIER:
          return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            f"Expected identifier"
          ))

        arg_name_toks.append(self.current_tok)
        res.register_advancement()
        self.advance()
      
      if self.current_tok.type != TT_RPAREN:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected ',' or ')'"
        ))
    else:
      if self.current_tok.type != TT_RPAREN:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected identifier or ')'"
        ))

    res.register_advancement()
    self.advance()

    # remove 
    if self.current_tok.type == TT_ARROW:
      res.register_advancement()
      self.advance()

      body = res.register(self.expr())
      if res.error: return res

      return res.success(FuncDefNode(
        var_name_tok,
        arg_name_toks,
        body,
        True
      ))
    
    if self.current_tok.type != TT_FUNCLINE:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected '->' or ':'"
      ))

    res.register_advancement()
    self.advance()

    body = res.register(self.statements())
    if res.error: return res

    if not self.current_tok.matches(TT_KEYWORD, 'end'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'end'"
      ))

    res.register_advancement()
    self.advance()
    
    return res.success(FuncDefNode(
      var_name_tok,
      arg_name_toks,
      body,
      type_, 
      False
    ))

  ############################################
  # func_def espera module como input para crear una funcion o metodo 
  """
  def func_def(self):
    res = ParseResult()

    if not self.current_tok.matches(TT_KEYWORD, 'module'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'module'"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type == TT_IDENTIFIER:
      var_name_tok = self.current_tok
      res.register_advancement()
      self.advance()
      if self.current_tok.type != TT_LPAREN:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected '('"
        ))
    else:
      var_name_tok = None
      if self.current_tok.type != TT_LPAREN:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected identifier "
        ))
    
    res.register_advancement()
    self.advance()
    arg_name_toks = []

    if self.current_tok.type == TT_IDENTIFIER:
      arg_name_toks.append(self.current_tok)
      res.register_advancement()
      self.advance()
      
      while self.current_tok.type == TT_COMMA:
        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT_IDENTIFIER:
          return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            f"Expected identifier"
          ))

        arg_name_toks.append(self.current_tok)
        res.register_advancement()
        self.advance()
      
      if self.current_tok.type != TT_RPAREN:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected ',' or ')'"
        ))
    else:
      if self.current_tok.type != TT_RPAREN:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected identifier or ')'"
        ))

    res.register_advancement()
    self.advance()

    # remove 
    if self.current_tok.type == TT_ARROW:
      res.register_advancement()
      self.advance()

      body = res.register(self.expr())
      if res.error: return res

      return res.success(FuncDefNode(
        var_name_tok,
        arg_name_toks,
        body,
        True
      ))
    
    if self.current_tok.type != TT_FUNCLINE:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected '->' or ':'"
      ))

    res.register_advancement()
    self.advance()

    body = res.register(self.statements())
    if res.error: return res

    if not self.current_tok.matches(TT_KEYWORD, 'end'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'end'"
      ))

    res.register_advancement()
    self.advance()
    
    return res.success(FuncDefNode(
      var_name_tok,
      arg_name_toks,
      body,
      False
    ))
  """
  ###################################

  def bin_op(self, func_a, ops, func_b=None):
    if func_b == None:
      func_b = func_a
    
    res = ParseResult()
    left = res.register(func_a())
    if res.error: return res

    while self.current_tok.type in ops or (self.current_tok.type, self.current_tok.value) in ops:
      op_tok = self.current_tok
      res.register_advancement()
      self.advance()
      right = res.register(func_b())
      if res.error: return res
      left = BinOpNode(left, op_tok, right)

    return res.success(left)

#######################################
# RUNTIME RESULT
#######################################

class RTResult:
  def __init__(self):
    self.reset()

  def reset(self):
    self.value = None
    self.error = None
    self.func_return_value = None
    self.loop_should_continue = False
    self.loop_should_break = False

  def register(self, res):
    self.error = res.error
    self.func_return_value = res.func_return_value
    self.loop_should_continue = res.loop_should_continue
    self.loop_should_break = res.loop_should_break
    return res.value

  def success(self, value):
    self.reset()
    self.value = value
    return self

  def success_return(self, value):
    self.reset()
    self.func_return_value = value
    return self
  
  def success_continue(self):
    self.reset()
    self.loop_should_continue = True
    return self

  def success_break(self):
    self.reset()
    self.loop_should_break = True
    return self

  def failure(self, error):
    self.reset()
    self.error = error
    return self

  def should_return(self):
    # Note: this will allow you to continue and break outside the current function
    return (
      self.error or
      self.func_return_value or
      self.loop_should_continue or
      self.loop_should_break
    )

#######################################
# VALUES
#######################################

class Value:
  def __init__(self):
    self.set_pos()
    self.set_context()

  def set_pos(self, pos_start=None, pos_end=None):
    self.pos_start = pos_start
    self.pos_end = pos_end
    return self

  def set_context(self, context=None):
    self.context = context
    return self

  def added_to(self, other):
    return None, self.illegal_operation(other)

  def subbed_by(self, other):
    return None, self.illegal_operation(other)

  def multed_by(self, other):
    return None, self.illegal_operation(other)

  def dived_by(self, other):
    return None, self.illegal_operation(other)

  def powed_by(self, other):
    return None, self.illegal_operation(other)

  def get_comparison_eq(self, other):
    return None, self.illegal_operation(other)

  def get_comparison_ne(self, other):
    return None, self.illegal_operation(other)

  def get_comparison_lt(self, other):
    return None, self.illegal_operation(other)

  def get_comparison_gt(self, other):
    return None, self.illegal_operation(other)

  def get_comparison_lte(self, other):
    return None, self.illegal_operation(other)

  def get_comparison_gte(self, other):
    return None, self.illegal_operation(other)

  def anded_by(self, other):
    return None, self.illegal_operation(other)

  def ored_by(self, other):
    return None, self.illegal_operation(other)

  def notted(self, other):
    return None, self.illegal_operation(other)

  def execute(self, args):
    return RTResult().failure(self.illegal_operation())

  def copy(self):
    raise Exception('No copy method defined')

  def is_true(self):
    return False

  def illegal_operation(self, other=None):
    if not other: other = self
    return RTError(
      self.pos_start, other.pos_end,
      'Illegal operation',
      self.context
    )

class Number(Value):
  def __init__(self, value):
    super().__init__()
    self.value = value
    self.type = 'Number'

  def added_to(self, other):
    if isinstance(other, Number):
      return Number(self.value + other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def subbed_by(self, other):
    if isinstance(other, Number):
      return Number(self.value - other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def multed_by(self, other):
    if isinstance(other, Number):
      return Number(self.value * other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def dived_by(self, other):
    if isinstance(other, Number):
      if other.value == 0:
        return None, RTError(
          other.pos_start, other.pos_end,
          'Division by zero',
          self.context
        )

      return Number(self.value / other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def powed_by(self, other):
    if isinstance(other, Number):
      return Number(self.value ** other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def get_comparison_eq(self, other):
    if isinstance(other, Number):
      return Number(int(self.value == other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def get_comparison_ne(self, other):
    if isinstance(other, Number):
      return Number(int(self.value != other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def get_comparison_lt(self, other):
    if isinstance(other, Number):
      return Number(int(self.value < other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def get_comparison_gt(self, other):
    if isinstance(other, Number):
      return Number(int(self.value > other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def get_comparison_lte(self, other):
    if isinstance(other, Number):
      return Number(int(self.value <= other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def get_comparison_gte(self, other):
    if isinstance(other, Number):
      return Number(int(self.value >= other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def anded_by(self, other):
    if isinstance(other, Number):
      return Number(int(self.value and other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def ored_by(self, other):
    if isinstance(other, Number):
      return Number(int(self.value or other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def notted(self):
    return Number(1 if self.value == 0 else 0).set_context(self.context), None

  def copy(self):
    copy = Number(self.value)
    copy.set_pos(self.pos_start, self.pos_end)
    copy.set_context(self.context)
    return copy

  def is_true(self):
    return self.value != 0

  def __str__(self):
    return str(self.value)
  
  def __repr__(self):
    return str(self.value)

Number.null = Number(0)
Number.false = Number(0)
Number.true = Number(1)


class Float(Value):
  def __init__(self, value):
    super().__init__()
    self.value = value
    self.type = 'Float'

  def added_to(self, other):
    if isinstance(other, Float):
      return Float(self.value + other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def subbed_by(self, other):
    if isinstance(other, Float):
      return Float(self.value - other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def multed_by(self, other):
    if isinstance(other, Float):
      return Float(self.value * other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def dived_by(self, other):
    if isinstance(other, Float):
      if other.value == 0:
        return None, RTError(
          other.pos_start, other.pos_end,
          'Division by zero',
          self.context
        )

      return Float(self.value / other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def powed_by(self, other):
    if isinstance(other, Float):
      return Float(self.value ** other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def get_comparison_eq(self, other):
    if isinstance(other, Float):
      return Float(float(self.value == other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def get_comparison_ne(self, other):
    if isinstance(other, Float):
      return Float(float(self.value != other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def get_comparison_lt(self, other):
    if isinstance(other, Float):
      return Float(float(self.value < other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def get_comparison_gt(self, other):
    if isinstance(other, Float):
      return Float(float(self.value > other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def get_comparison_lte(self, other):
    if isinstance(other, Float):
      return Float(float(self.value <= other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def get_comparison_gte(self, other):
    if isinstance(other, Float):
      return Float(float(self.value >= other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def anded_by(self, other):
    if isinstance(other, Float):
      return Float(float(self.value and other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def ored_by(self, other):
    if isinstance(other, Float):
      return Float(float(self.value or other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def notted(self):
    return Float(1 if self.value == 0 else 0).set_context(self.context), None

  def copy(self):
    copy = Float(self.value)
    copy.set_pos(self.pos_start, self.pos_end)
    copy.set_context(self.context)
    return copy

  def is_true(self):
    return self.value != 0

  def __str__(self):
    return str(self.value)
  
  def __repr__(self):
    return str(self.value)


class Int(Value):
  def __init__(self, value):
    super().__init__()
    self.value = value
    self.type = 'Int'

  def added_to(self, other):
    if isinstance(other, Int):
      return Int(self.value + other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def subbed_by(self, other):
    if isinstance(other, Int):
      return Int(self.value - other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def multed_by(self, other):
    if isinstance(other, Int):
      return Int(self.value * other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def dived_by(self, other):
    if isinstance(other, Int):
      if other.value == 0:
        return None, RTError(
          other.pos_start, other.pos_end,
          'Division by zero',
          self.context
        )

      return Int(self.value / other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def powed_by(self, other):
    if isinstance(other, Int):
      return Int(self.value ** other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def get_comparison_eq(self, other):
    if isinstance(other, Int):
      return Int(int(self.value == other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def get_comparison_ne(self, other):
    if isinstance(other, Int):
      return Int(int(self.value != other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def get_comparison_lt(self, other):
    if isinstance(other, Int):
      return Int(int(self.value < other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def get_comparison_gt(self, other):
    if isinstance(other, Int):
      return Int(int(self.value > other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def get_comparison_lte(self, other):
    if isinstance(other, Int):
      return Int(int(self.value <= other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def get_comparison_gte(self, other):
    if isinstance(other, Int):
      return Int(int(self.value >= other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def anded_by(self, other):
    if isinstance(other, Int):
      return Int(int(self.value and other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def ored_by(self, other):
    if isinstance(other, Int):
      return Int(int(self.value or other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def notted(self):
    return Int(1 if self.value == 0 else 0).set_context(self.context), None

  def copy(self):
    copy = Int(self.value)
    copy.set_pos(self.pos_start, self.pos_end)
    copy.set_context(self.context)
    return copy

  def is_true(self):
    return self.value != 0

  def __str__(self):
    return str(self.value)
  
  def __repr__(self):
    return str(self.value)

Int.null = Int(0)
Int.false = Int(0)
Int.true = Int(1)


class String(Value):
  def __init__(self, value):
    super().__init__()
    self.value = value
    self.type = 'String'

  # concatena texto
  def added_to(self, other):
    if isinstance(other, String):
      return String(self.value + other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)
  
  def multed_by(self, other):
    if isinstance(other, Int):
      return String(self.value * other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def is_true(self):
    return len(self.value) > 0

  def copy(self):
    copy = String(self.value)
    copy.set_pos(self.pos_start, self.pos_end)
    copy.set_context(self.context)
    return copy

  def __str__(self):
    return self.value

  def __repr__(self):
    return f'"{self.value}"'


class List(Value):
  def __init__(self, elements):
    super().__init__()
    self.elements = elements
    self.type = 'List'
    self.typeOfList = ''
  
  def getElems(self):
    return self.elements
  
  def getLen(self):
    return len(self.elements)

  # agregar elemento a lista 1
  def added_to(self, other):
    print("self elements tipo: ", self)
    print("other tipo: ", other.type)
    new_list = self.copy()
    new_list.elements.append(other)
    return new_list, None

  # eliminar elm en N position 
  def subbed_by(self, other):
    if isinstance(other, Int):
      new_list = self.copy()
      try:
        new_list.elements.pop(other.value)
        return new_list, None
      except:
        return None, RTError(
          other.pos_start, other.pos_end,
          'Index out of bounds',
          self.context
        )
    else:
      return None, Value.illegal_operation(self, other)

  # concatena listas
  def multed_by(self, other):
    if isinstance(other, List):
      new_list = self.copy()
      new_list.elements.extend(other.elements)
      return new_list, None
    else:
      return None, Value.illegal_operation(self, other)
  
  # extract N elem from list
  # Ya funciona Asies 
  def dived_by(self, other):
    if isinstance(other, Int):
      try:
        return self.elements[other.value], None
      except:
        return None, RTError(
          other.pos_start, other.pos_end,
          'Element at this index could not be retrieved from list because index is out of bounds',
          self.context
        )
    else:
      return None, Value.illegal_operation(self, other)
  
  def setElem(self, index, value):
    if isinstance(index, Int):
      try:
          self.elements[index.value] = value.value
          return self.elements[index.value], None
      except:
        return None, RTError(
          other.pos_start, other.pos_end,
          'Element at this index could not be retrieved from list because index is out of bounds',
          self.context
        )
    else:
      return None, Value.illegal_operation(self, index)
      

  def copy(self):
    copy = List(self.elements)
    copy.set_pos(self.pos_start, self.pos_end)
    copy.set_context(self.context)
    return copy

  def __str__(self):
    return ", ".join([str(x) for x in self.elements])

  def __repr__(self):
    return f'[{", ".join([repr(x) for x in self.elements])}]'



class Mat(Value):
  def __init__(self, lists):
    super().__init__()
    self.lists = lists
    self.type = 'Mat'
  
  def getElems(self):
    return self.lists
  
  def getLen(self):
    return len(self.lists)

  # agregar list a mat
  def added_to(self, other):
    new_mat = self.copy()
    if isinstance(other, List):
      cont = new_mat.getLen()
      new_mat.lists.insert(cont, other)
      return new_mat, None
    else:
      return None, Value.illegal_operation(self, other)

  # eliminar elm en N position 
  def subbed_by(self, other):
    if isinstance(other, Int):
      new_mat = self.copy()
      try:
        new_mat.lists.pop(other.value)
        return new_mat, None
      except:
        return None, RTError(
          other.pos_start, other.pos_end,
          'Index out of bounds',
          self.context
        )
    else:
      return None, Value.illegal_operation(self, other)

  # concatena mat
  def multed_by(self, other):
    if isinstance(other, Mat):
      new_mat = self.copy()
      new_mat.lists.extend(other.lists)
      return new_mat, None
    else:
      return None, Value.illegal_operation(self, other)
  
  # extract N elem from Mat
  # Ya funciona Asies 
  def dived_by(self, other):
    if isinstance(other, Int):
      try:
        return self.lists[other.value], None
      except:
        return None, RTError(
          other.pos_start, other.pos_end,
          'Element at this index could not be retrieved from list because index is out of bounds',
          self.context
        )
    else:
      return None, Value.illegal_operation(self, other)
  
  def setMat(self, index, listA):
    if isinstance(index, Int):
      try:
          self.lists[index.value] = listA.elements
          return self.lists[index.value], None
      except:
        return None, RTError(
          other.pos_start, other.pos_end,
          'Element at this index could not be retrieved from list because index is out of bounds',
          self.context
        )
    else:
      return None, Value.illegal_operation(self, index)
      

  def copy(self):
    copy = Mat(self.lists)
    copy.set_pos(self.pos_start, self.pos_end)
    copy.set_context(self.context)
    return copy

  def __str__(self):
    return ", ".join([str(x) for x in self.lists])

  def __repr__(self):
    return f'[{", ".join([repr(x) for x in self.lists])}]'


class BaseFunction(Value):
  def __init__(self, name):
    super().__init__()
    self.name = name or "<anonymous>"

  def generate_new_context(self):
    new_context = Context(self.name, self.context, self.pos_start)
    new_context.symbol_stack = SymbolStack(new_context.parent.symbol_stack)
    return new_context

  def check_args(self, arg_names, args):
    res = RTResult()

    if len(args) > len(arg_names):
      return res.failure(RTError(
        self.pos_start, self.pos_end,
        f"{len(args) - len(arg_names)} cantidad de parametros inesperados en {self}",
        self.context
      ))
    
    if len(args) < len(arg_names):
      return res.failure(RTError(
        self.pos_start, self.pos_end,
        f"{len(arg_names) - len(args)} faltan params en {self}",
        self.context
      ))

    return res.success(None)

  def populate_args(self, arg_names, args, exec_ctx):
    for i in range(len(args)):
      arg_name = arg_names[i]
      arg_value = args[i]
      arg_value.set_context(exec_ctx)
      exec_ctx.symbol_stack.set(arg_name, arg_value)

  def check_and_populate_args(self, arg_names, args, exec_ctx):
    res = RTResult()
    res.register(self.check_args(arg_names, args))
    if res.should_return(): return res
    self.populate_args(arg_names, args, exec_ctx)
    return res.success(None)

class Function(BaseFunction):
  def __init__(self, name, body_node, type_, arg_names, should_auto_return):
    super().__init__(name)
    self.body_node = body_node
    self.arg_names = arg_names
    self.type_ = type_
    self.should_auto_return = should_auto_return

  def execute(self, args):
    res = RTResult() 
    interpreter = Interpreter()
    exec_ctx = self.generate_new_context()

    res.register(self.check_and_populate_args(self.arg_names, args, exec_ctx))
    if res.should_return(): return res

    value = res.register(interpreter.visit(self.body_node, exec_ctx))
    if res.should_return() and res.func_return_value == None: return res

    if self.type_ == 'void':
      if self.should_auto_return or res.func_return_value: 
        return res.failure(InvalidSyntaxError(
          self.body_node.pos_start, self.body_node.pos_end,
          "Void method can not return"
        ))
      return res.success(Int.null)

    if self.type_ == 'Int':
      ret_value = (value if self.should_auto_return else None) or res.func_return_value or Int.null
      
      if ret_value.type != 'Int':
        return res.failure(InvalidSyntaxError(
          ret_value.pos_start, ret_value.pos_end,
          "Method method can not return other type"
        ))
      return res.success(ret_value)

    if self.type_ == 'Float':
      ret_value = (value if self.should_auto_return else None) or res.func_return_value or Int.null
      
      if ret_value.type != 'Float':
        return res.failure(InvalidSyntaxError(
          ret_value.pos_start, ret_value.pos_end,
          "Method method can not return other type"
        ))
      return res.success(ret_value)


    
    if self.type_ == 'String':
      ret_value = (value if self.should_auto_return else None) or res.func_return_value or Int.null

      if ret_value.type != 'String':
        return res.failure(InvalidSyntaxError(
          ret_value.pos_start, ret_value.pos_end,
          "Method method can not return other type"
        ))
      return res.success(ret_value)
  


    #ret_value = (value if self.should_auto_return else None) or res.func_return_value or Number.null
    return res.success(Int.null)

  def copy(self):
    copy = Function(self.name, self.body_node, self.type_, self.arg_names, self.should_auto_return)
    copy.set_context(self.context)
    copy.set_pos(self.pos_start, self.pos_end)
    return copy

  def __repr__(self):
    return f"<function {self.name}>"


class BuiltInFunction(BaseFunction):
  def __init__(self, name):
    super().__init__(name)

  def execute(self, args):
    res = RTResult()
    exec_ctx = self.generate_new_context()

    method_name = f'execute_{self.name}'
    method = getattr(self, method_name, self.no_visit_method)

    res.register(self.check_and_populate_args(method.arg_names, args, exec_ctx))
    if res.should_return(): return res

    return_value = res.register(method(exec_ctx))
    if res.should_return(): return res
    return res.success(return_value)
  
  def no_visit_method(self, node, context):
    raise Exception(f'No execute_{self.name} method defined')

  def copy(self):
    copy = BuiltInFunction(self.name)
    copy.set_context(self.context)
    copy.set_pos(self.pos_start, self.pos_end)
    return copy

  def __repr__(self):
    return f"<built-in function {self.name}>"

  #####################################
  def execute_write(self, exec_ctx):
    print(str(exec_ctx.symbol_stack.get('value')))
    return RTResult().success(Int.null)
  execute_write.arg_names = ['value']
  
  def execute_read(self, exec_ctx):
    text = input()
    return RTResult().success(String(text))
  execute_read.arg_names = []

  def execute_read_int(self, exec_ctx):
    while True:
      text = input()
      try:
        number = int(text)
        break
      except ValueError:
        print(f"'{text}' must be an integer. Try again!")
    return RTResult().success(Int(number))
  execute_read_int.arg_names = []

  def execute_clear(self, exec_ctx):
    os.system('cls' if os.name == 'nt' else 'cls') 
    return RTResult().success(Int.null)
  execute_clear.arg_names = []

  def execute_is_Int(self, exec_ctx):
    is_Int = isinstance(exec_ctx.symbol_stack.get("value"), Int)
    return RTResult().success(Int.true if is_Int else Int.false)
  execute_is_Int.arg_names = ["value"]

  def execute_is_string(self, exec_ctx):
    is_number = isinstance(exec_ctx.symbol_stack.get("value"), String)
    return RTResult().success(Number.true if is_number else Number.false)
  execute_is_string.arg_names = ["value"]

  def execute_is_list(self, exec_ctx):
    is_number = isinstance(exec_ctx.symbol_stack.get("value"), List)
    return RTResult().success(Number.true if is_number else Number.false)
  execute_is_list.arg_names = ["value"]

  def execute_is_module(self, exec_ctx):
    is_number = isinstance(exec_ctx.symbol_stack.get("value"), BaseFunction)
    return RTResult().success(Number.true if is_number else Number.false)
  execute_is_module.arg_names = ["value"]

  def execute_append(self, exec_ctx):
    list_ = exec_ctx.symbol_stack.get("list")
    value = exec_ctx.symbol_stack.get("value")

    if not isinstance(list_, List):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "First argument must be list",
        exec_ctx
      ))

    list_.elements.append(value)
    return RTResult().success(Int.null)
  execute_append.arg_names = ["list", "value"]

  def execute_pop(self, exec_ctx):
    list_ = exec_ctx.symbol_stack.get("list")
    index = exec_ctx.symbol_stack.get("index")

    if not isinstance(list_, List):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "First argument must be list",
        exec_ctx
      ))

    if not isinstance(index, Int):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "Second argument must be Int",
        exec_ctx
      ))

    try:
      element = list_.elements.pop(index.value)
    except:
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        'Element at this index could not be removed from list because index is out of bounds',
        exec_ctx
      ))
    return RTResult().success(element)
  execute_pop.arg_names = ["list", "index"]

  def execute_extend(self, exec_ctx):
    listA = exec_ctx.symbol_stack.get("listA")
    listB = exec_ctx.symbol_stack.get("listB")

    if not isinstance(listA, List):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "First argument must be list",
        exec_ctx
      ))

    if not isinstance(listB, List):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "Second argument must be list",
        exec_ctx
      ))

    listA.elements.extend(listB.elements)
    return RTResult().success(Int.null)
  execute_extend.arg_names = ["listA", "listB"]

  def execute_len(self, exec_ctx):
    list_ = exec_ctx.symbol_stack.get("list")

    if not isinstance(list_, List):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "Argument must be list",
        exec_ctx
      ))

    return RTResult().success(Int(len(list_.elements)))
  execute_len.arg_names = ["list"]

  def execute_run(self, exec_ctx):
    fn = exec_ctx.symbol_stack.get("fn")

    if not isinstance(fn, String):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "Second argument must be String",
        exec_ctx
      ))

    fn = fn.value

    try:
      with open(fn, "r") as f:
        script = f.read()
    except Exception as e:
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        f"Failed to load script \"{fn}\"\n" + str(e),
        exec_ctx
      ))

    _, error = run(fn, script)
    
    if error:
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        f"Failed to finish executing script \"{fn}\"\n" +
        error.as_string(),
        exec_ctx
      ))

    return RTResult().success(Int.null)
  execute_run.arg_names = ["fn"]

  ############################################################################
  def execute_setList(self, exec_ctx):
    listA = exec_ctx.symbol_stack.get("listA")
    index = exec_ctx.symbol_stack.get("index")
    value = exec_ctx.symbol_stack.get("value")


    if not isinstance(listA, List):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "Argument must be list",
        exec_ctx
      ))
    if not isinstance(value, Int):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "Argument must be Int",
        exec_ctx
      ))
    if not isinstance(index, Int):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "Argument must be number",
        exec_ctx
      ))

    try:
													   

												
      co = listA.elements[index.value].copy()
      #print(co.pos_start, "val: ", co.value, "end: ", co.pos_end)
      co.value = value.value
      #print(co.pos_start, "val: ", co.value, "end: ", co.pos_end)

      listA.elements.pop(index.value)
      listA.elements.insert(index.value, co)
    except:
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        'Index fuera de limites de lista xd ',
        exec_ctx
      ))
    return RTResult().success(Int.null)
  execute_setList.arg_names = ["listA", "index", "value"]
  #####################################################################

  def execute_setMat(self, exec_ctx):
    MatA = exec_ctx.symbol_stack.get("MatA")
    index = exec_ctx.symbol_stack.get("index")
    listA = exec_ctx.symbol_stack.get("listA")


    if not isinstance(MatA, Mat):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "First argument must be Mat",
        exec_ctx
      ))
    if not isinstance(index, Int):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "Second argument must be Int",
        exec_ctx
      ))
    if not isinstance(listA, List):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "Last argument must be list",
        exec_ctx
      ))

    try:
      co = MatA.lists[index.value].copy()
      #print(co.pos_start, "val: ", co.value, "end: ", co.pos_end)
      co.elements = listA.elements
      #print(co.pos_start, "val: ", co.value, "end: ", co.pos_end)

      MatA.lists.pop(index.value)
      MatA.lists.insert(index.value, co)
    except:
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        'Index fuera de limites de lista xd ',
        exec_ctx
      ))
    return RTResult().success(Int.null)
  execute_setMat.arg_names = ["MatA", "index", "listA"]
  
  #########################################################################
  def execute_circle(self, exec_ctx):
    radius = exec_ctx.symbol_stack.get("value")

    if not isinstance(radius, Int):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "Argument must be Int",
        exec_ctx
      ))
  
    aux= str(radius)
    aux = int(aux)
    turtle_circle(aux)
    return(RTResult().success(Int.null))
  execute_circle.arg_names = ["value"]

  def execute_square(self, exec_ctx):
    sq = exec_ctx.symbol_stack.get("value")

    if not isinstance(sq, Int):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "Argument must be Int",
        exec_ctx
      ))
    
    aux= str(sq)
    aux = int(aux)
    turtle_square(aux)
    return(RTResult().success(Int.null))
  execute_square.arg_names = ["value"]

  def execute_dot(self, exec_ctx):
    dot = exec_ctx.symbol_stack.get("value")

    if not isinstance(dot, Int):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "Argument must be Int",
        exec_ctx
      ))
    
    aux= str(dot)
    aux = int(aux)
    turtle_dot(aux)
    return(RTResult().success(Int.null))
  execute_dot.arg_names = ["value"]

  def execute_penup(self, exec_ctx):
    aTurtle.penup() 
    return(RTResult().success(Int.null))
  execute_penup.arg_names = []

  def execute_pendown(self, exec_ctx):
    aTurtle.pendown() 
    return(RTResult().success(Int.null))
  execute_pendown.arg_names = []

  def execute_forward(self, exec_ctx):
    distance = exec_ctx.symbol_stack.get("value")

    if not isinstance(distance, Int):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "Argument must be Int",
        exec_ctx
      ))
    
    aux= str(distance)
    aux = int(aux)
    aTurtle.forward(aux)
    return(RTResult().success(Int.null))
  execute_forward.arg_names = ["value"]

  def execute_backward(self, exec_ctx):
    distance = exec_ctx.symbol_stack.get("value")

    if not isinstance(distance, Int):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "Argument must be Int",
        exec_ctx
      ))
    
    aux= str(distance)
    aux = int(aux)
    aTurtle.backward(aux)
    return(RTResult().success(Int.null))
  execute_backward.arg_names = ["value"]

  def execute_right(self, exec_ctx):
    angle = exec_ctx.symbol_stack.get("value")

    if not isinstance(angle, Int):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "Angle must be Int",
        exec_ctx
      ))
    
    aux= str(angle)
    aux = int(aux)
    aTurtle.right(aux)
    return(RTResult().success(Int.null))
  execute_right.arg_names = ["value"]

  def execute_left(self, exec_ctx):
    angle = exec_ctx.symbol_stack.get("value")

    if not isinstance(angle, Int):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "Angle must be Int",
        exec_ctx
      ))
    
    aux= str(angle)
    aux = int(aux)
    aTurtle.left(aux)
    return(RTResult().success(Int.null))
  execute_left.arg_names = ["value"]

  def execute_goto(self, exec_ctx):
    x = exec_ctx.symbol_stack.get("x")
    y = exec_ctx.symbol_stack.get("y")

    if not isinstance(x, Int):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "X argument must be Int",
        exec_ctx
      ))
    if not isinstance(y, Int):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "Y argument must be Int",
        exec_ctx
      ))
    auxX= str(x)
    auxX = int(auxX)
    auxY= str(y)
    auxY = int(auxY)

    aTurtle.goto(auxX, auxY)
    return(RTResult().success(Int.null))
  execute_goto.arg_names = ["x", "y"]

  def execute_home(self, exec_ctx):
    aTurtle.home() 
    return(RTResult().success(Int.null))
  execute_home.arg_names = []

  def execute_bgcolor(self, exec_ctx):
    color = exec_ctx.symbol_stack.get("value")

    if not isinstance(color, String):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "Color must be String",
        exec_ctx
      ))
    
    aux= str(color)
    turtle.bgcolor(aux)
    return(RTResult().success(Int.null))
  execute_bgcolor.arg_names = ["value"]

  def execute_turtlecolor(self, exec_ctx):
    color = exec_ctx.symbol_stack.get("value")

    if not isinstance(color, String):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "Color must be String",
        exec_ctx
      ))
    
    aux= str(color)
    aTurtle.fillcolor(aux)
    return(RTResult().success(Int.null))
  execute_turtlecolor.arg_names = ["value"]

  def execute_title(self, exec_ctx):
    title = exec_ctx.symbol_stack.get("value")

    if not isinstance(title, String):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "title must be String",
        exec_ctx
      ))
    
    aux= str(title)
    turtle.title(aux)
    return(RTResult().success(Int.null))
  execute_title.arg_names = ["value"]

  def execute_pensize(self, exec_ctx):
    size = exec_ctx.symbol_stack.get("value")

    if not isinstance(size, Int):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "size must be Int",
        exec_ctx
      ))
    
    aux= str(size)
    aux = int(aux)
    aTurtle.pensize(aux)
    return(RTResult().success(Int.null))
  execute_pensize.arg_names = ["value"]

  def execute_turtleundo(self, exec_ctx):
    aTurtle.undo() 
    return(RTResult().success(Int.null))
  execute_turtleundo.arg_names = []

  def execute_turtleclear(self, exec_ctx):
    aTurtle.clear() 
    return(RTResult().success(Int.null))
  execute_turtleclear.arg_names = []

  def execute_turtlereset(self, exec_ctx):
    aTurtle.reset() 
    return(RTResult().success(Int.null))
  execute_turtlereset.arg_names = []

  def execute_stamp(self, exec_ctx):
    aTurtle.stamp() 
    return(RTResult().success(Int.null))
  execute_stamp.arg_names = []

  









BuiltInFunction.write       = BuiltInFunction("write")
BuiltInFunction.read       = BuiltInFunction("read")
BuiltInFunction.read_int    = BuiltInFunction("read_int")
BuiltInFunction.clear       = BuiltInFunction("clear")
BuiltInFunction.is_Int   = BuiltInFunction("is_Int")
BuiltInFunction.is_string   = BuiltInFunction("is_string")
BuiltInFunction.is_list     = BuiltInFunction("is_list")
BuiltInFunction.is_module   = BuiltInFunction("is_module")
BuiltInFunction.append      = BuiltInFunction("append")
BuiltInFunction.pop         = BuiltInFunction("pop")
BuiltInFunction.extend      = BuiltInFunction("extend")
BuiltInFunction.len					= BuiltInFunction("len")
BuiltInFunction.setList     = BuiltInFunction("setList")
BuiltInFunction.setMat     = BuiltInFunction("setMat")
BuiltInFunction.run					= BuiltInFunction("run")

BuiltInFunction.circle       = BuiltInFunction("circle")
BuiltInFunction.square      = BuiltInFunction("square")
BuiltInFunction.dot      = BuiltInFunction("dot")
BuiltInFunction.penup      = BuiltInFunction("penup")
BuiltInFunction.pendown      = BuiltInFunction("pendown")
BuiltInFunction.forward      = BuiltInFunction("forward")
BuiltInFunction.backward      = BuiltInFunction("backward")
BuiltInFunction.right      = BuiltInFunction("right")
BuiltInFunction.left      = BuiltInFunction("left")
BuiltInFunction.home      = BuiltInFunction("home")
BuiltInFunction.goto      = BuiltInFunction("goto")
BuiltInFunction.bgcolor      = BuiltInFunction("bgcolor")
BuiltInFunction.turtlecolor      = BuiltInFunction("turtlecolor")
BuiltInFunction.title      = BuiltInFunction("title")
BuiltInFunction.pensize      = BuiltInFunction("pensize")
BuiltInFunction.turtleundo      = BuiltInFunction("turtleundo")
BuiltInFunction.turtleclear      = BuiltInFunction("turtleclear")
BuiltInFunction.turtlereset     = BuiltInFunction("turtlereset")
BuiltInFunction.stamp     = BuiltInFunction("stamp")




#######################################
# CONTEXT
#######################################

class Context:
  def __init__(self, display_name, parent=None, parent_entry_pos=None):
    self.display_name = display_name
    self.parent = parent
    self.parent_entry_pos = parent_entry_pos
    self.symbol_stack = None

#######################################
# SYMBOL TABLE
#######################################

class SymbolStack:
  def __init__(self, parent=None):
    self.symbols = {}
    self.parent = parent

  def get(self, name):
    value = self.symbols.get(name, None)
    if value == None and self.parent:
      return self.parent.get(name)
    return value
  
  def exists(self, name):
    value = self.symbols.get(name, None)
    if value == None:
      return False
    return True

  def set(self, name, value):
    self.symbols[name] = value
  
  def tableLength(self):
    return len(self.symbols)

  def remove(self, name):
    del self.symbols[name]

#######################################
# INTERPRETER
#######################################

class Interpreter:
  def visit(self, node, context):
    method_name = f'visit_{type(node).__name__}'
    method = getattr(self, method_name, self.no_visit_method)
    return method(node, context)

  def no_visit_method(self, node, context):
    raise Exception(f'No visit_{type(node).__name__} method defined')

  ############################################

  def visit_NumberNode(self, node, context):
    return RTResult().success(
      Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
    )
  
  def visit_IntNode(self, node, context):
    return RTResult().success(
      Int(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
    )

  def visit_FloatNode(self, node, context):
    return RTResult().success(
      Float(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
    )

  def visit_StringNode(self, node, context):
    return RTResult().success(
      String(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
    )


  def visit_ListNode(self, node, context):
    res = RTResult()
    elements = []

    for element_node in node.element_nodes:
      elements.append(res.register(self.visit(element_node, context)))
      if res.should_return(): return res


    return res.success(
      List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
    )
  

  def visit_MatNode(self, node, context):
    res = RTResult()
    lists = []

    for element_node in node.list_nodes:
      lists.append(res.register(self.visit(element_node, context)))
      if res.should_return(): return res

    return res.success(
      Mat(lists).set_context(context).set_pos(node.pos_start, node.pos_end)
    )
  
  def visit_VarAccessNode(self, node, context):
    res = RTResult()
    var_name = node.var_name_tok.value
    value = context.symbol_stack.get(var_name)

    if not value:
      return res.failure(RTError(
        node.pos_start, node.pos_end,
        f"Variable '{var_name}' no definida",
        context
      ))

    value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
    return res.success(value)


  def visit_VarReassignNode(self, node, context):
    res = RTResult()
    var_name = node.var_name_tok.value
    value = res.register(self.visit(node.value_node, context))
    if res.should_return(): return res

    #if context.symbol_stack.exists(var_name):
    context.symbol_stack.set(var_name, value)
    return res.success(value)


  def visit_VarAssignNode(self, node, context):
    res = RTResult()
    var_name = node.var_name_tok.value
    value = res.register(self.visit(node.value_node, context))
    if res.should_return(): return res

    context.symbol_stack.set(var_name, value)
    return res.success(value)

  def visit_BinOpNode(self, node, context):
    res = RTResult()
    left = res.register(self.visit(node.left_node, context))
    if res.should_return(): return res
    right = res.register(self.visit(node.right_node, context))
    if res.should_return(): return res

    if node.op_tok.type == TT_PLUS:
      result, error = left.added_to(right)
    elif node.op_tok.type == TT_MINUS:
      result, error = left.subbed_by(right)
    elif node.op_tok.type == TT_MUL:
      result, error = left.multed_by(right)
    elif node.op_tok.type == TT_DIV:
      result, error = left.dived_by(right)
    elif node.op_tok.type == TT_POW:
      result, error = left.powed_by(right)
    elif node.op_tok.type == TT_EE:
      result, error = left.get_comparison_eq(right)
    elif node.op_tok.type == TT_NE:
      result, error = left.get_comparison_ne(right)
    elif node.op_tok.type == TT_LT:
      result, error = left.get_comparison_lt(right)
    elif node.op_tok.type == TT_GT:
      result, error = left.get_comparison_gt(right)
    elif node.op_tok.type == TT_LTE:
      result, error = left.get_comparison_lte(right)
    elif node.op_tok.type == TT_GTE:
      result, error = left.get_comparison_gte(right)
    elif node.op_tok.matches(TT_KEYWORD, 'and'):
      result, error = left.anded_by(right)
    elif node.op_tok.matches(TT_KEYWORD, 'or'):
      result, error = left.ored_by(right)

    if error:
      return res.failure(error)
    else:
      return res.success(result.set_pos(node.pos_start, node.pos_end))
      #return res.success(result)

  def visit_UnaryOpNode(self, node, context):
    res = RTResult()
    number = res.register(self.visit(node.node, context))
    if res.should_return(): return res

    error = None

    if node.op_tok.type == TT_MINUS:
      number, error = number.multed_by(Int(-1))
    elif node.op_tok.matches(TT_KEYWORD, 'not'):
      number, error = number.notted()

    if error:
      return res.failure(error)
    else:
      return res.success(number.set_pos(node.pos_start, node.pos_end))

  def visit_IfNode(self, node, context):
    res = RTResult()

    for condition, expr, should_return_null in node.cases:
      condition_value = res.register(self.visit(condition, context))
      if res.should_return(): return res

      if condition_value.is_true():
        expr_value = res.register(self.visit(expr, context))
        if res.should_return(): return res
        return res.success(Int.null if should_return_null else expr_value)

    if node.else_case:
      expr, should_return_null = node.else_case
      expr_value = res.register(self.visit(expr, context))
      if res.should_return(): return res
      return res.success(Int.null if should_return_null else expr_value)

    return res.success(Int.null)

  def visit_MainNode(self, node, context):
    res = RTResult()
    elements = []
    
    body_node = node.body_node

    value = res.register(self.visit(node.body_node, context))
    if res.should_return() and res.loop_should_continue == False and res.loop_should_break == False: return res

    elements.append(value)


    return res.success(Int.null)
  
  def visit_ProgramNode(self, node, context):
    res = RTResult()
    elements = [] 

    program_name = node.program_name.value if node.program_name else None
  

    body_node = node.body_node

    value = res.register(self.visit(node.body_node, context))
    if res.should_return() and res.loop_should_continue == False and res.loop_should_break == False: return res
    
    elements.append(value)

    return res.success(Int.null)

  def visit_ForNode(self, node, context):
    res = RTResult()
    elements = []

    start_value = res.register(self.visit(node.start_value_node, context))
    if res.should_return(): return res

    end_value = res.register(self.visit(node.end_value_node, context))
    #print("end val: ", end_value.type)
    if res.should_return(): return res

    if node.step_value_node:
      step_value = res.register(self.visit(node.step_value_node, context))
      if res.should_return(): return res
    else:
      step_value = Int(1)

    i = start_value.value

    if step_value.value >= 0:
      condition = lambda: i < end_value.value
    else:
      condition = lambda: i > end_value.value
    
    while condition():
      context.symbol_stack.set(node.var_name_tok.value, Int(i))
      i += step_value.value

      value = res.register(self.visit(node.body_node, context))
      if res.should_return() and res.loop_should_continue == False and res.loop_should_break == False: return res
      
      if res.loop_should_continue:
        continue
      
      if res.loop_should_break:
        break

      elements.append(value)

    return res.success(
      Int.null if node.should_return_null else
      List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
    )

  def visit_WhileNode(self, node, context):
    res = RTResult()
    elements = []

    while True:
      condition = res.register(self.visit(node.condition_node, context))
      if res.should_return(): return res

      if not condition.is_true():
        break

      value = res.register(self.visit(node.body_node, context))
      if res.should_return() and res.loop_should_continue == False and res.loop_should_break == False: return res

      if res.loop_should_continue:
        continue
      
      if res.loop_should_break:
        break

      elements.append(value)

    return res.success(
      Int.null if node.should_return_null else
      List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
    )


  def visit_FuncDefNode(self, node, context):
    res = RTResult()

    func_name = node.var_name_tok.value if node.var_name_tok else None
    body_node = node.body_node
    type_ = node.type_
    arg_names = [arg_name.value for arg_name in node.arg_name_toks]
    #func_value = Function(func_name, body_node, arg_names, node.should_auto_return).set_context(context).set_pos(node.pos_start, node.pos_end)
    func_value = Function(func_name, body_node, type_, arg_names, node.should_auto_return).set_context(context).set_pos(node.pos_start, node.pos_end)
    
    if node.var_name_tok:
      context.symbol_stack.set(func_name, func_value)

    return res.success(func_value)

  def visit_CallNode(self, node, context):
    res = RTResult()
    args = []

    value_to_call = res.register(self.visit(node.node_to_call, context))
    if res.should_return(): return res
    value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

    for arg_node in node.arg_nodes:
      args.append(res.register(self.visit(arg_node, context)))
      if res.should_return(): return res

    return_value = res.register(value_to_call.execute(args))
    if res.should_return(): return res
    return_value = return_value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
    return res.success(return_value)

  def visit_returnNode(self, node, context):
    res = RTResult()

    if node.node_to_return:
      value = res.register(self.visit(node.node_to_return, context))
      if res.should_return(): return res
    else:
      value = Int.null
    
    return res.success_return(value)

  def visit_ContinueNode(self, node, context):
    return RTResult().success_continue()

  def visit_BreakNode(self, node, context):
    return RTResult().success_break()

#######################################
# RUN
#######################################

global_symbol_stack = SymbolStack()
global_symbol_stack.set("NULL", Int.null)
global_symbol_stack.set("FALSE", Int.false)
global_symbol_stack.set("TRUE", Int.true)
global_symbol_stack.set("write", BuiltInFunction.write)
global_symbol_stack.set("read", BuiltInFunction.read)
global_symbol_stack.set("read_int", BuiltInFunction.read_int)
global_symbol_stack.set("CLEAR", BuiltInFunction.clear)
global_symbol_stack.set("CLS", BuiltInFunction.clear)
global_symbol_stack.set("IS_INT", BuiltInFunction.is_Int)
global_symbol_stack.set("IS_STR", BuiltInFunction.is_string)
global_symbol_stack.set("IS_LIST", BuiltInFunction.is_list)
global_symbol_stack.set("IS_MODULE", BuiltInFunction.is_module)
global_symbol_stack.set("APPEND", BuiltInFunction.append)
global_symbol_stack.set("POP", BuiltInFunction.pop)
global_symbol_stack.set("EXTEND", BuiltInFunction.extend)
global_symbol_stack.set("len", BuiltInFunction.len)
global_symbol_stack.set("setList", BuiltInFunction.setList)
global_symbol_stack.set("setMat", BuiltInFunction.setMat)
global_symbol_stack.set("RUN", BuiltInFunction.run)
global_symbol_stack.set("circle", BuiltInFunction.circle)
global_symbol_stack.set("square", BuiltInFunction.square)
global_symbol_stack.set("dot", BuiltInFunction.dot)
global_symbol_stack.set("penup", BuiltInFunction.penup)
global_symbol_stack.set("pendown", BuiltInFunction.pendown)
global_symbol_stack.set("forward", BuiltInFunction.forward)
global_symbol_stack.set("backward", BuiltInFunction.backward)
global_symbol_stack.set("right", BuiltInFunction.right)
global_symbol_stack.set("left", BuiltInFunction.left)
global_symbol_stack.set("home", BuiltInFunction.home)
global_symbol_stack.set("goto", BuiltInFunction.goto)
global_symbol_stack.set("bgcolor", BuiltInFunction.bgcolor)
global_symbol_stack.set("turtlecolor", BuiltInFunction.turtlecolor)
global_symbol_stack.set("title", BuiltInFunction.title)
global_symbol_stack.set("pensize", BuiltInFunction.pensize)
global_symbol_stack.set("turtleundo", BuiltInFunction.turtleundo)
global_symbol_stack.set("turtleclear", BuiltInFunction.turtleclear)
global_symbol_stack.set("turtlereset", BuiltInFunction.turtlereset)
global_symbol_stack.set("stamp", BuiltInFunction.stamp)




def run(fn, text):
  # Generate tokens
  lexer = Lexer(fn, text)
  tokens, error = lexer.make_tokens()
  if error: return None, error
  
  # Generate AST
  parser = Parser(tokens)
  ast = parser.parse()
  if ast.error: return None, ast.error

  # Run program
  interpreter = Interpreter()
  context = Context('<program>')
  context.symbol_stack = global_symbol_stack
  result = interpreter.visit(ast.node, context)

  start_Turtle()

  return result.value, result.error
