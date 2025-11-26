grammar DSL;

programa: sentencia* EOF;

sentencia
    : declaracion
    | asignacion
    | expresion ';'
    | condicional
    | ciclo
    | funcionDef
    | retorno
    | impresion
    | operacionML
    | operacionArchivos
    | operacionGrafico
    | bloque
    ;

declaracion
    : 'var' ID '=' expresion ';'
    | 'global' ID '=' expresion ';'
    ;

asignacion
    : ID '=' expresion ';'
    | ID '[' expresion ']' '=' expresion ';'                    // asignación a elemento de lista
    | ID '[' expresion ']' '[' expresion ']' '=' expresion ';'  // asignación a elemento de matriz
    ;

condicional
    : 'if' '(' expresion ')' bloque ('elif' '(' expresion ')' bloque)* ('else' bloque)?
    ;

ciclo
    : cicloFor
    | cicloWhile
    ;

cicloFor
    : 'for' ID 'in' 'range' '(' expresion (',' expresion (',' expresion)?)? ')' bloque
    | 'for' ID 'in' expresion bloque
    ;

cicloWhile
    : 'while' '(' expresion ')' bloque
    ;

bloque
    : '{' sentencia* '}'
    ;

funcionDef
    : 'function' ID '(' parametros? ')' bloque
    ;

parametros
    : ID (',' ID)*
    ;

retorno
    : 'return' expresion? ';'
    ;

expresion
    : expresion '**' expresion                              // potencia
    | expresion ('*' | '/' | '%') expresion                 // multiplicación, división, módulo
    | expresion ('+' | '-') expresion                       // suma, resta
    | expresion ('<' | '<=' | '>' | '>=' | '==' | '!=') expresion  // comparación
    | expresion ('and' | 'or') expresion                    // lógicos
    | 'not' expresion                                       // negación
    | '-' expresion                                         // negativo
    | '(' expresion ')'                                     // paréntesis
    | funcionLlamada                                        // llamada a función
    | expresion '[' expresion ']'                           // indexación de lista/matriz
    | expresion '[' expresion ']' '[' expresion ']'         // indexación de matriz 2D
    | expresion '[' expresion ':' expresion ']'             // slicing
    | lista                                                 // lista literal
    | matriz                                                // matriz literal
    | ID                                                    // identificador
    | NUMERO                                                // número
    | STRING                                                // cadena
    | BOOLEAN                                               // booleano
    ;

funcionLlamada
    : ID '(' argumentos? ')'
    ;

argumentos
    : expresion (',' expresion)*
    ;

lista
    : '[' (expresion (',' expresion)*)? ']'
    ;

matriz
    : '[' lista (',' lista)* ']'
    ;

impresion
    : 'print' '(' expresion ')' ';'
    | 'show' '(' expresion ')' ';'
    ;
operacionML
    : regresionLineal
    | perceptronSimple
    | mlpCrear
    | mlpEntrenar
    | mlpPredecir
    | kmeans
    | dbscan
    | jerarquico
    | predecirModelo
    | evaluarModelo
    ;

regresionLineal
    : 'regresion_lineal' '(' 
        'X=' expresion ',' 
        'y=' expresion 
      ')' ';'
    | ID '=' 'regresion_lineal' '(' 
        'X=' expresion ',' 
        'y=' expresion 
      ')' ';'
    ;

perceptronSimple
    : 'perceptron' '(' 
        'X=' expresion ',' 
        'y=' expresion 
        (',' 'lr=' expresion)? 
        (',' 'epochs=' expresion)? 
      ')' ';'
    | ID '=' 'perceptron' '(' 
        'X=' expresion ',' 
        'y=' expresion 
        (',' 'lr=' expresion)? 
        (',' 'epochs=' expresion)? 
      ')' ';'
    ;

mlpCrear
    : ID '=' 'mlp' '(' 
        'input=' expresion ',' 
        'hidden=' expresion ',' 
        'output=' expresion 
      ')' ';'
    ;

mlpEntrenar
    : 'train' '(' 
        ID ',' 
        'X=' expresion ',' 
        'y=' expresion 
        (',' 'lr=' expresion)? 
        (',' 'epochs=' expresion)? 
      ')' ';'
    ;

mlpPredecir
    : 'predict' '(' ID ',' expresion ')' ';'
    | ID '=' 'predict' '(' ID ',' expresion ')' ';'
    ;
kmeans
    : 'kmeans' '(' 
        'data=' expresion ',' 
        'k=' expresion 
        (',' 'max_iter=' expresion)? 
      ')' ';'
    | ID '=' 'kmeans' '(' 
        'data=' expresion ',' 
        'k=' expresion 
        (',' 'max_iter=' expresion)? 
      ')' ';'
    ;
dbscan
    : 'dbscan' '(' 
        'data=' expresion ',' 
        'eps=' expresion ',' 
        'min_pts=' expresion 
      ')' ';'
    | ID '=' 'dbscan' '(' 
        'data=' expresion ',' 
        'eps=' expresion ',' 
        'min_pts=' expresion 
      ')' ';'
    ;

jerarquico
    : 'hierarchical' '(' 
        'data=' expresion ',' 
        'n_clusters=' expresion 
        (',' 'method=' STRING)? 
      ')' ';'
    | ID '=' 'hierarchical' '(' 
        'data=' expresion ',' 
        'n_clusters=' expresion 
        (',' 'method=' STRING)? 
      ')' ';'
    ;

predecirModelo
    : ID '=' 'predict_model' '(' ID ',' expresion ')' ';'
    ;
evaluarModelo
    : 'evaluate' '(' 
        'y_true=' expresion ',' 
        'y_pred=' expresion 
        (',' 'metric=' STRING)? 
      ')' ';'
    | ID '=' 'evaluate' '(' 
        'y_true=' expresion ',' 
        'y_pred=' expresion 
        (',' 'metric=' STRING)? 
      ')' ';'
    ;

operacionArchivos
    : leerArchivo
    | escribirArchivo
    | leerCSV
    | escribirCSV
    | guardarModelo
    | cargarModelo
    ;

leerArchivo
    : ID '=' 'read_file' '(' STRING ')' ';'
    | ID '=' 'read_lines' '(' STRING ')' ';'
    ;

escribirArchivo
    : 'write_file' '(' STRING ',' expresion ')' ';'
    | 'append_file' '(' STRING ',' expresion ')' ';'
    ;

leerCSV
    : ID '=' 'read_csv' '(' 
        STRING 
        (',' 'delimiter=' STRING)? 
        (',' 'header=' BOOLEAN)? 
      ')' ';'
    ;

escribirCSV
    : 'write_csv' '(' 
        STRING ',' 
        'data=' expresion 
        (',' 'header=' expresion)? 
      ')' ';'
    ;

guardarModelo
    : 'save_model' '(' ID ',' STRING ')' ';'
    ;

cargarModelo
    : ID '=' 'load_model' '(' STRING ')' ';'
    ;

operacionGrafico
    : graficoLinea
    | graficoDispersion
    | graficoBarra
    | graficoHistograma
    | graficoRegresion
    | graficoFuncion
    ;

graficoLinea
    : 'plot' '(' 
        'x=' expresion ',' 
        'y=' expresion 
        (',' 'title=' STRING)? 
        (',' 'width=' expresion)? 
        (',' 'height=' expresion)? 
      ')' ';'
    ;

graficoDispersion
    : 'scatter' '(' 
        'x=' expresion ',' 
        'y=' expresion 
        (',' 'title=' STRING)? 
      ')' ';'
    ;

graficoBarra
    : 'bar' '(' 
        'labels=' expresion ',' 
        'values=' expresion 
        (',' 'title=' STRING)? 
      ')' ';'
    ;

graficoHistograma
    : 'histogram' '(' 
        'data=' expresion 
        (',' 'bins=' expresion)? 
        (',' 'title=' STRING)? 
      ')' ';'
    ;

graficoRegresion
    : 'plot_regression' '(' 
        'x=' expresion ',' 
        'y=' expresion 
        (',' 'title=' STRING)? 
      ')' ';'
    ;

graficoFuncion
    : 'plot_function' '(' 
        'func=' ID ',' 
        'start=' expresion ',' 
        'end=' expresion 
        (',' 'points=' expresion)? 
        (',' 'title=' STRING)? 
      ')' ';'
    ;

// Palabras reservadas
IF: 'if';
ELIF: 'elif';
ELSE: 'else';
FOR: 'for';
WHILE: 'while';
IN: 'in';
FUNCTION: 'function';
RETURN: 'return';
VAR: 'var';
GLOBAL: 'global';
PRINT: 'print';
RANGE: 'range';

// Operadores
PLUS: '+';
MINUS: '-';
MULT: '*';
DIV: '/';
MOD: '%';
POW: '**';
EQ: '==';
NEQ: '!=';
LT: '<';
LTE: '<=';
GT: '>';
GTE: '>=';
AND: 'and';
OR: 'or';
NOT: 'not';
ASSIGN: '=';

// Delimitadores
LPAREN: '(';
RPAREN: ')';
LBRACE: '{';
RBRACE: '}';
LBRACKET: '[';
RBRACKET: ']';
SEMICOLON: ';';
COMMA: ',';
COLON: ':';
DOT: '.';

// Literales
BOOLEAN: 'true' | 'false' | 'True' | 'False';

NUMERO
    : [0-9]+ ('.' [0-9]+)?
    | '.' [0-9]+
    ;

STRING
    : '"' (~["\r\n] | '\\' .)* '"'
    | '\'' (~['\r\n] | '\\' .)* '\''
    ;

ID: [a-zA-Z_][a-zA-Z0-9_]*;

// Espacios en blanco y comentarios
WS: [ \t\r\n]+ -> skip;

COMMENT: ('//' | '#') ~[\r\n]* -> skip;

BLOCK_COMMENT: '/*' .*? '*/' -> skip;