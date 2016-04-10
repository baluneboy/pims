
# parsetab.py
# This file is automatically generated. Do not edit.
_tabversion = '3.8'

_lr_method = 'LALR'

_lr_signature = '954EE22A79DC429CE06F75ED53192C33'
    
_lr_action_items = {'$end':([1,2,3,5,9,14,15,16,17,18,19,20,],[-10,-9,0,-2,-10,-7,-1,-8,-3,-6,-4,-5,]),'RPAREN':([2,8,9,14,16,17,18,19,20,],[-9,16,-10,-7,-8,-3,-6,-4,-5,]),'DIVIDE':([1,2,5,8,9,14,15,16,17,18,19,20,],[-10,-9,11,11,-10,-7,11,-8,11,-6,11,-5,]),'EQUALS':([1,],[7,]),'NUMBER':([0,4,6,7,10,11,12,13,],[2,2,2,2,2,2,2,2,]),'PLUS':([1,2,5,8,9,14,15,16,17,18,19,20,],[-10,-9,10,10,-10,-7,10,-8,-3,-6,-4,-5,]),'LPAREN':([0,4,6,7,10,11,12,13,],[4,4,4,4,4,4,4,4,]),'TIMES':([1,2,5,8,9,14,15,16,17,18,19,20,],[-10,-9,13,13,-10,-7,13,-8,13,-6,13,-5,]),'MINUS':([0,1,2,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,],[6,-10,-9,6,12,6,6,12,-10,6,6,6,6,-7,12,-8,-3,-6,-4,-5,]),'NAME':([0,4,6,7,10,11,12,13,],[1,9,9,9,9,9,9,9,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'expression':([0,4,6,7,10,11,12,13,],[5,8,14,15,17,18,19,20,]),'statement':([0,],[3,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> statement","S'",1,None,None,None),
  ('statement -> NAME EQUALS expression','statement',3,'p_statement_assign','ply_yacc.py',63),
  ('statement -> expression','statement',1,'p_statement_expr','ply_yacc.py',67),
  ('expression -> expression PLUS expression','expression',3,'p_expression_binop','ply_yacc.py',71),
  ('expression -> expression MINUS expression','expression',3,'p_expression_binop','ply_yacc.py',72),
  ('expression -> expression TIMES expression','expression',3,'p_expression_binop','ply_yacc.py',73),
  ('expression -> expression DIVIDE expression','expression',3,'p_expression_binop','ply_yacc.py',74),
  ('expression -> MINUS expression','expression',2,'p_expression_uminus','ply_yacc.py',81),
  ('expression -> LPAREN expression RPAREN','expression',3,'p_expression_group','ply_yacc.py',85),
  ('expression -> NUMBER','expression',1,'p_expression_number','ply_yacc.py',89),
  ('expression -> NAME','expression',1,'p_expression_name','ply_yacc.py',93),
]
