grammar Calc;

COMMENT: '//' ~( '\r' | '\n' )* -> skip;


WS: [ \t\r\n]+ -> skip;

INT   : [0-9]+;
FLOAT : [0-9]+ '.' [0-9]+;
IDENT : [a-zA-Z][0-9a-zA-Z]*;

PLUS  : '+';
MINUS : '-';
EQ    : '=';
SEMI  : ';';

expr
    : left=expr op=(PLUS | MINUS) right=expr            # binary
    | INT      # number
    | FLOAT    # float
    | IDENT    # var
    ;

statement
    : 'print' name=IDENT SEMI                                  # printvar
    | vartype=('int' | 'double') name=IDENT EQ value=expr SEMI # declaration
    ;

program: statement* EOF;
