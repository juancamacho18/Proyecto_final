from antlr4 import *
from DSLParser import DSLParser
from DSLVisitor import DSLVisitor
from librerias.Contexto import Contexto, MemoriaDataframes, GestorModelos
from librerias.RedesNeuronales import RedesNeuronales
from librerias.Agrupamiento import Agrupamiento
from librerias.Graficos import Graficos
from librerias.ManejoArchivos import ManejoArchivos
from librerias.Matrices import Matrices
from librerias.Aritmetica import Aritmetica

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class Visitor(DSLVisitor):
    def __init__(self):
        self.contexto = Contexto()
        self.dataframes = MemoriaDataframes()
        self.modelos = GestorModelos()
        
    def visitPrograma(self, ctx:DSLParser.ProgramaContext):
        return self.visitChildren(ctx)

    def visitSentencia(self, ctx:DSLParser.SentenciaContext):
        return self.visitChildren(ctx)

    def visitBloque(self, ctx:DSLParser.BloqueContext):
        self.contexto.entrar_scope('bloque')
        try:
            for sentencia in ctx.sentencia():
                self.visit(sentencia)
        finally:
            self.contexto.salir_scope()

    # --- Declaración y Asignación ---

    def visitDeclaracion(self, ctx:DSLParser.DeclaracionContext):
        nombre = ctx.ID().getText()
        valor = self.visit(ctx.expresion())
        
        if ctx.getChild(0).getText() == 'global':
            self.contexto.definir_global(nombre, valor)
        else:
            self.contexto.definir_variable(nombre, valor)
        return valor

    def visitAsignacion(self, ctx:DSLParser.AsignacionContext):
        nombre = ctx.ID().getText()
        valor = self.visit(ctx.expresion(0)) # El valor a asignar siempre es la primera expresión en la regla (o la última, depende de la gramática, let's check)
        # Wait, let's check the grammar for asignacion
        # asignacion : ID '=' expresion ';'
        #            | ID '[' expresion ']' '=' expresion ';'
        #            | ID '[' expresion ']' '[' expresion ']' '=' expresion ';'
        
        if ctx.getChildCount() == 4: # ID '=' expresion ';'
            valor = self.visit(ctx.expresion(0))
            self.contexto.actualizar_variable(nombre, valor)
            
        elif ctx.getChildCount() == 7: # ID '[' expresion ']' '=' expresion ';'
            indice = self.visit(ctx.expresion(0))
            valor = self.visit(ctx.expresion(1))
            lista = self.contexto.obtener_variable(nombre)
            if isinstance(lista, list):
                if 0 <= indice < len(lista):
                    lista[indice] = valor
                else:
                    print(f"Error: Índice {indice} fuera de rango para lista '{nombre}'")
            else:
                print(f"Error: Variable '{nombre}' no es una lista")
                
        elif ctx.getChildCount() == 10: # ID '[' expresion ']' '[' expresion ']' '=' expresion ';'
            fila = self.visit(ctx.expresion(0))
            col = self.visit(ctx.expresion(1))
            valor = self.visit(ctx.expresion(2))
            matriz = self.contexto.obtener_variable(nombre)
            if isinstance(matriz, list) and isinstance(matriz[0], list):
                if 0 <= fila < len(matriz) and 0 <= col < len(matriz[0]):
                    matriz[fila][col] = valor
                else:
                    print(f"Error: Índices [{fila}][{col}] fuera de rango para matriz '{nombre}'")
            else:
                print(f"Error: Variable '{nombre}' no es una matriz")
        
        return valor

    # --- Control Flow ---

    def visitCondicional(self, ctx:DSLParser.CondicionalContext):
        # 'if' '(' expresion ')' bloque ('elif' '(' expresion ')' bloque)* ('else' bloque)?
        condicion = self.visit(ctx.expresion(0))
        if condicion:
            self.visit(ctx.bloque(0))
            return

        # Check elifs
        # The grammar structure for elif is a bit complex in the list of children.
        # Let's iterate through children to find elifs
        i = 1
        expr_idx = 1
        bloque_idx = 1
        
        while i < ctx.getChildCount():
            child = ctx.getChild(i)
            if child.getText() == 'elif':
                cond_elif = self.visit(ctx.expresion(expr_idx))
                expr_idx += 1
                if cond_elif:
                    self.visit(ctx.bloque(bloque_idx))
                    return
                bloque_idx += 1
            elif child.getText() == 'else':
                self.visit(ctx.bloque(bloque_idx))
                return
            i += 1

    def visitCicloFor(self, ctx:DSLParser.CicloForContext):
        # 'for' ID 'in' 'range' '(' expresion (',' expresion (',' expresion)?)? ')' bloque
        # 'for' ID 'in' expresion bloque
        nombre_var = ctx.ID().getText()
        
        if ctx.getChild(3).getText() == 'range':
            start = 0
            step = 1
            if len(ctx.expresion()) == 1:
                stop = self.visit(ctx.expresion(0))
            elif len(ctx.expresion()) == 2:
                start = self.visit(ctx.expresion(0))
                stop = self.visit(ctx.expresion(1))
            else:
                start = self.visit(ctx.expresion(0))
                stop = self.visit(ctx.expresion(1))
                step = self.visit(ctx.expresion(2))
            
            iterable = range(int(start), int(stop), int(step))
        else:
            iterable = self.visit(ctx.expresion(0))
            
        self.contexto.entrar_scope('ciclo')
        try:
            # Definir la variable de iteración en el scope del ciclo
            self.contexto.definir_local(nombre_var, 0) 
            
            for val in iterable:
                self.contexto.actualizar_variable(nombre_var, val)
                try:
                    self.visit(ctx.bloque())
                except Exception as e:
                    # Aquí podríamos manejar break/continue si el DSL lo soportara
                    raise e
        finally:
            self.contexto.salir_scope()

    def visitCicloWhile(self, ctx:DSLParser.CicloWhileContext):
        self.contexto.entrar_scope('ciclo')
        try:
            while self.visit(ctx.expresion()):
                try:
                    self.visit(ctx.bloque())
                except Exception as e:
                    raise e
        finally:
            self.contexto.salir_scope()

    # --- Funciones ---

    def visitFuncionDef(self, ctx:DSLParser.FuncionDefContext):
        nombre = ctx.ID().getText()
        parametros = []
        if ctx.parametros():
            parametros = [x.getText() for x in ctx.parametros().ID()]
        
        self.contexto.definir_funcion(nombre, parametros, ctx.bloque())
        return None

    def visitRetorno(self, ctx:DSLParser.RetornoContext):
        valor = None
        if ctx.expresion():
            valor = self.visit(ctx.expresion())
        raise ReturnException(valor)

    def visitFuncionLlamada(self, ctx:DSLParser.FuncionLlamadaContext):
        nombre = ctx.ID().getText()
        if not self.contexto.existe_funcion(nombre):
            print(f"Error: Función '{nombre}' no definida")
            return None
            
        funcion_info = self.contexto.obtener_funcion(nombre)
        parametros = funcion_info['parametros']
        cuerpo = funcion_info['cuerpo']
        
        argumentos = []
        if ctx.argumentos():
            argumentos = [self.visit(e) for e in ctx.argumentos().expresion()]
            
        if len(argumentos) != len(parametros):
            print(f"Error: Función '{nombre}' espera {len(parametros)} argumentos, se recibieron {len(argumentos)}")
            return None
            
        # Crear nuevo scope para la función
        self.contexto.entrar_llamada(nombre, argumentos)
        self.contexto.entrar_scope('funcion')
        
        try:
            # Asignar argumentos a parámetros
            for param, arg in zip(parametros, argumentos):
                self.contexto.definir_local(param, arg)
                
            # Ejecutar cuerpo
            self.visit(cuerpo)
            
        except ReturnException as e:
            return e.value
        finally:
            self.contexto.salir_scope()
            self.contexto.salir_llamada()
            
        return None

    # --- Expresiones ---

    def visitExpresion(self, ctx:DSLParser.ExpresionContext):
        # Literales
        if ctx.NUMERO():
            return float(ctx.NUMERO().getText())
        if ctx.STRING():
            return ctx.STRING().getText()[1:-1] # Quitar comillas
        if ctx.BOOLEAN():
            return ctx.BOOLEAN().getText() == 'true' or ctx.BOOLEAN().getText() == 'True'
        if ctx.ID():
            return self.contexto.obtener_variable(ctx.ID().getText())
        if ctx.lista():
            return self.visit(ctx.lista())
        if ctx.matriz():
            return self.visit(ctx.matriz())
        if ctx.funcionLlamada():
            return self.visit(ctx.funcionLlamada())
            
        # Paréntesis (3 hijos: '(' expr ')')
        if ctx.getChildCount() == 3 and ctx.getChild(0).getText() == '(':
            return self.visit(ctx.expresion(0))
            
        # Operaciones unarias (2 hijos)
        if ctx.getChildCount() == 2:
            op = ctx.getChild(0).getText()
            val = self.visit(ctx.expresion(0))
            if op == '-': return -val
            if op == 'not': return not val
            
        # Operaciones binarias (3 hijos)
        if ctx.getChildCount() == 3:
            left = self.visit(ctx.expresion(0))
            right = self.visit(ctx.expresion(1))
            op = ctx.getChild(1).getText()
            
            if op == '**': return left ** right
            if op == '*': return left * right
            if op == '/': return left / right
            if op == '%': return left % right
            if op == '+':
                if isinstance(left, str) or isinstance(right, str):
                    return str(left) + str(right)
                return left + right
            if op == '-': return left - right
            if op == '<': return left < right
            if op == '<=': return left <= right
            if op == '>': return left > right
            if op == '>=': return left >= right
            if op == '==': return left == right
            if op == '!=': return left != right
            if op == 'and': return left and right
            if op == 'or': return left or right

        # Indexación de lista/matriz (4 hijos: expr '[' expr ']')
        if ctx.getChildCount() == 4:
            if ctx.getChild(1).getText() == '[':
                obj = self.visit(ctx.expresion(0))
                idx = self.visit(ctx.expresion(1))
                if isinstance(obj, list):
                    return obj[int(idx)]
                return None

        # Slicing (6 hijos: expr '[' expr ':' expr ']')
        if ctx.getChildCount() == 6:
            if ctx.getChild(1).getText() == '[' and ctx.getChild(3).getText() == ':':
                lista = self.visit(ctx.expresion(0))
                inicio = self.visit(ctx.expresion(1))
                fin = self.visit(ctx.expresion(2))
                return lista[int(inicio):int(fin)]
                
        # Indexación matriz 2D (7 hijos: expr '[' expr ']' '[' expr ']')
        if ctx.getChildCount() == 7:
             matriz = self.visit(ctx.expresion(0))
             fila = self.visit(ctx.expresion(1))
             col = self.visit(ctx.expresion(2))
             return matriz[int(fila)][int(col)]

        return None

    def visitLista(self, ctx:DSLParser.ListaContext):
        elementos = []
        if ctx.expresion():
            elementos = [self.visit(e) for e in ctx.expresion()]
        return elementos

    def visitMatriz(self, ctx:DSLParser.MatrizContext):
        filas = []
        if ctx.lista():
            filas = [self.visit(l) for l in ctx.lista()]
        return filas

    def visitImpresion(self, ctx:DSLParser.ImpresionContext):
        valor = self.visit(ctx.expresion())
        if ctx.getChild(0).getText() == 'print':
            print(valor)
        elif ctx.getChild(0).getText() == 'show':
            # 'show' podría ser para dataframes o matrices de forma más bonita
            if isinstance(valor, list):
                if len(valor) > 0 and isinstance(valor[0], list):
                    Matrices.mostrar_matriz(valor)
                else:
                    print(valor)
            else:
                print(valor)
        return None

    # --- Machine Learning ---

    def visitRegresionLineal(self, ctx:DSLParser.RegresionLinealContext):
        # 'regresion_lineal' '(' 'X=' expresion ',' 'y=' expresion ')' ';'
        X = self.visit(ctx.expresion(0))
        y = self.visit(ctx.expresion(1))
        
        modelo = RedesNeuronales.regresion_lineal_multiple(X, y)
        
        if ctx.ID(): # Asignación a variable
            nombre = ctx.ID().getText()
            self.contexto.definir_variable(nombre, modelo)
            self.modelos.guardar_modelo(nombre, modelo, 'regresion_lineal')
        
        return modelo

    def visitPerceptronSimple(self, ctx:DSLParser.PerceptronSimpleContext):
        X = self.visit(ctx.expresion(0))
        y = self.visit(ctx.expresion(1))
        lr = 0.1
        epochs = 100
        
        # Buscar argumentos opcionales
        # La gramática es un poco laxa, así que asumiremos orden o buscaremos por nombre si fuera posible,
        # pero el parser ya valida la estructura.
        # (',' 'lr=' expresion)? (',' 'epochs=' expresion)?
        
        # Necesitamos saber qué expresiones corresponden a qué.
        # ctx.expresion() devuelve una lista.
        # 0: X, 1: y
        # Si hay 3, puede ser lr o epochs? No, la gramática tiene tokens literales 'lr='
        
        # Vamos a iterar sobre los hijos para encontrar los valores correctos
        idx_expr = 2
        for i in range(ctx.getChildCount()):
            child = ctx.getChild(i)
            if child.getText() == 'lr=':
                lr = self.visit(ctx.expresion(idx_expr))
                idx_expr += 1
            elif child.getText() == 'epochs=':
                epochs = self.visit(ctx.expresion(idx_expr))
                idx_expr += 1
                
        modelo = RedesNeuronales.perceptron_simple(X, y, lr, int(epochs))
        
        if ctx.ID():
            nombre = ctx.ID().getText()
            self.contexto.definir_variable(nombre, modelo)
            self.modelos.guardar_modelo(nombre, modelo, 'perceptron')
            
        return modelo

    def visitMlpCrear(self, ctx:DSLParser.MlpCrearContext):
        nombre = ctx.ID().getText()
        inp = self.visit(ctx.expresion(0))
        hidden = self.visit(ctx.expresion(1))
        out = self.visit(ctx.expresion(2))
        
        modelo = RedesNeuronales.crear_mlp(int(inp), int(hidden), int(out))
        self.contexto.definir_variable(nombre, modelo)
        self.modelos.guardar_modelo(nombre, modelo, 'mlp')
        return modelo

    def visitMlpEntrenar(self, ctx:DSLParser.MlpEntrenarContext):
        nombre = ctx.ID().getText()
        modelo = self.contexto.obtener_variable(nombre)
        X = self.visit(ctx.expresion(0))
        y = self.visit(ctx.expresion(1))
        lr = 0.1
        epochs = 1000
        
        idx_expr = 2
        for i in range(ctx.getChildCount()):
            child = ctx.getChild(i)
            if child.getText() == 'lr=':
                lr = self.visit(ctx.expresion(idx_expr))
                idx_expr += 1
            elif child.getText() == 'epochs=':
                epochs = self.visit(ctx.expresion(idx_expr))
                idx_expr += 1
                
        modelo_entrenado = RedesNeuronales.entrenar_mlp(modelo, X, y, lr, int(epochs), verbose=True)
        self.contexto.actualizar_variable(nombre, modelo_entrenado)
        return modelo_entrenado

    def visitMlpPredecir(self, ctx:DSLParser.MlpPredecirContext):
        # 'predict' '(' ID ',' expresion ')' ';'
        # ID '=' 'predict' '(' ID ',' expresion ')' ';'
        
        # El ID del modelo es el primer ID en los argumentos o el segundo si hay asignación
        ids = ctx.ID()
        if len(ids) == 1:
            nombre_modelo = ids[0].getText()
            var_destino = None
        else:
            var_destino = ids[0].getText()
            nombre_modelo = ids[1].getText()
            
        modelo = self.contexto.obtener_variable(nombre_modelo)
        X = self.visit(ctx.expresion(0))
        
        # Determinar tipo de modelo para saber qué función usar
        # Podríamos guardar el tipo en el modelo o inferirlo
        # GestorModelos guarda el tipo
        try:
            info = self.modelos.obtener_info_modelo(nombre_modelo)
            tipo = info['tipo']
        except:
            # Si no está en gestor, asumir MLP o intentar inferir
            tipo = 'mlp'
            
        if tipo == 'mlp':
            preds = RedesNeuronales.predecir_mlp(modelo, X)
        elif tipo == 'perceptron':
            preds = RedesNeuronales.predecir_perceptron(modelo, X)
        elif tipo == 'regresion_lineal':
            preds = RedesNeuronales.predecir_regresion(modelo, X)
        else:
            preds = []
            
        if var_destino:
            self.contexto.definir_variable(var_destino, preds)
            
        return preds
        
    def visitPredecirModelo(self, ctx:DSLParser.PredecirModeloContext):
        # ID '=' 'predict_model' '(' ID ',' expresion ')' ';'
        var_destino = ctx.ID(0).getText()
        nombre_modelo = ctx.ID(1).getText()
        X = self.visit(ctx.expresion())
        
        modelo = self.contexto.obtener_variable(nombre_modelo)
        info = self.modelos.obtener_info_modelo(nombre_modelo)
        tipo = info['tipo']
        
        if tipo == 'mlp':
            preds = RedesNeuronales.predecir_mlp(modelo, X)
        elif tipo == 'perceptron':
            preds = RedesNeuronales.predecir_perceptron(modelo, X)
        elif tipo == 'regresion_lineal':
            preds = RedesNeuronales.predecir_regresion(modelo, X)
        elif tipo == 'kmeans':
            preds = Agrupamiento.predecir_kmeans(modelo, X)
        else:
            print(f"Tipo de modelo '{tipo}' no soporta predicción estándar")
            preds = []
            
        self.contexto.definir_variable(var_destino, preds)
        return preds

    def visitEvaluarModelo(self, ctx:DSLParser.EvaluarModeloContext):
        y_true = self.visit(ctx.expresion(0))
        y_pred = self.visit(ctx.expresion(1))
        metric = 'accuracy'
        
        if ctx.STRING():
            metric = ctx.STRING().getText()[1:-1]
            
        resultado = 0
        if metric == 'accuracy' or metric == 'precision':
            resultado = RedesNeuronales.precision(y_true, y_pred)
        elif metric == 'mse':
            resultado = RedesNeuronales.error_cuadratico_medio(y_true, y_pred)
        elif metric == 'confusion_matrix':
            resultado = RedesNeuronales.matriz_confusion(y_true, y_pred)
            
        if ctx.ID():
            self.contexto.definir_variable(ctx.ID().getText(), resultado)
        else:
            print(f"Evaluación ({metric}): {resultado}")
            
        return resultado

    def visitKmeans(self, ctx:DSLParser.KmeansContext):
        data = self.visit(ctx.expresion(0))
        k = self.visit(ctx.expresion(1))
        max_iter = 100
        
        if ctx.getChildCount() > 8: # Hay max_iter
             # Buscar donde está max_iter
             # Similar logic to perceptron
             pass # Simplification: assume standard order or just use default for now if complex
             
        # Parsing manual de argumentos opcionales
        idx_expr = 2
        for i in range(ctx.getChildCount()):
            child = ctx.getChild(i)
            if child.getText() == 'max_iter=':
                max_iter = self.visit(ctx.expresion(idx_expr))
                
        modelo = Agrupamiento.kmeans(data, int(k), int(max_iter))
        
        if ctx.ID():
            nombre = ctx.ID().getText()
            self.contexto.definir_variable(nombre, modelo)
            self.modelos.guardar_modelo(nombre, modelo, 'kmeans')
            
        return modelo

    def visitDbscan(self, ctx:DSLParser.DbscanContext):
        data = self.visit(ctx.expresion(0))
        eps = self.visit(ctx.expresion(1))
        min_pts = self.visit(ctx.expresion(2))
        
        modelo = Agrupamiento.dbscan(data, float(eps), int(min_pts))
        
        if ctx.ID():
            nombre = ctx.ID().getText()
            self.contexto.definir_variable(nombre, modelo)
            self.modelos.guardar_modelo(nombre, modelo, 'dbscan')
            
        return modelo

    def visitJerarquico(self, ctx:DSLParser.JerarquicoContext):
        data = self.visit(ctx.expresion(0))
        n_clusters = self.visit(ctx.expresion(1))
        method = 'simple'
        
        if ctx.STRING():
            method = ctx.STRING().getText()[1:-1]
            
        modelo = Agrupamiento.agrupamiento_jerarquico(data, int(n_clusters), method)
        
        if ctx.ID():
            nombre = ctx.ID().getText()
            self.contexto.definir_variable(nombre, modelo)
            self.modelos.guardar_modelo(nombre, modelo, 'jerarquico')
            
        return modelo

    # --- Archivos ---

    def visitLeerArchivo(self, ctx:DSLParser.LeerArchivoContext):
        nombre_var = ctx.ID().getText()
        ruta = ctx.STRING().getText()[1:-1]
        
        if ctx.getChild(2).getText() == 'read_file':
            contenido = ManejoArchivos.leer_archivo(ruta)
        else:
            contenido = ManejoArchivos.leer_lineas(ruta)
            
        self.contexto.definir_variable(nombre_var, contenido)
        return contenido

    def visitEscribirArchivo(self, ctx:DSLParser.EscribirArchivoContext):
        ruta = ctx.STRING().getText()[1:-1]
        contenido = self.visit(ctx.expresion())
        
        if ctx.getChild(0).getText() == 'write_file':
            ManejoArchivos.escribir_archivo(ruta, str(contenido))
        else:
            ManejoArchivos.añadir_linea(ruta, str(contenido))
        return None

    def visitLeerCSV(self, ctx:DSLParser.LeerCSVContext):
        nombre_var = ctx.ID().getText()
        ruta = ctx.STRING(0).getText()[1:-1]
        delimiter = ','
        header = True
        
        # Argumentos opcionales
        for i in range(ctx.getChildCount()):
            child = ctx.getChild(i)
            if child.getText() == 'delimiter=':
                delimiter = ctx.STRING(1).getText()[1:-1]
            elif child.getText() == 'header=':
                header = ctx.BOOLEAN().getText() == 'true'
                
        data = ManejoArchivos.leer_csv(ruta, delimiter, header)
        
        # Convertir a formato numérico si es posible para facilitar ML
        # Esto es una mejora automática
        if data:
            datos_num = []
            for fila in data['datos']:
                fila_num = ManejoArchivos.convertir_columna_a_numeros(fila)
                datos_num.append(fila_num)
            
            # Guardamos tanto la estructura raw como una versión numérica simplificada si se pide
            # Por ahora guardamos la estructura completa o solo los datos?
            # El DSL parece esperar listas de listas para ML.
            # Vamos a devolver la lista de listas numérica por defecto para facilitar uso
            self.contexto.definir_variable(nombre_var, datos_num)
            
            # También podríamos guardar el objeto completo en otra variable o en metadatos
            self.dataframes.crear_dataframe(nombre_var, datos_num, data['encabezados'])
            
        return data

    def visitEscribirCSV(self, ctx:DSLParser.EscribirCSVContext):
        ruta = ctx.STRING().getText()[1:-1]
        data = self.visit(ctx.expresion(0))
        header = None
        
        if len(ctx.expresion()) > 1:
            header = self.visit(ctx.expresion(1))
            
        # Manejar header booleano
        if isinstance(header, bool):
            if header and len(data) > 0:
                # Generar headers por defecto: col_0, col_1, ...
                header = [f"col_{i}" for i in range(len(data[0]))]
            else:
                header = None
            
        ManejoArchivos.escribir_csv(ruta, data, header)
        return None

    def visitGuardarModelo(self, ctx:DSLParser.GuardarModeloContext):
        # No implementado persistencia real en GestorModelos (solo memoria), 
        # pero podríamos usar pickle si quisiéramos.
        # Por ahora solo imprime confirmación.
        print(f"Modelo guardado (simulado): {ctx.STRING().getText()}")
        return None

    def visitCargarModelo(self, ctx:DSLParser.CargarModeloContext):
        nombre_var = ctx.ID().getText()
        archivo = ctx.STRING().getText()
        print(f"Modelo cargado (simulado): {archivo}")
        
        # Simular carga de modelo
        modelo_simulado = {"tipo": "modelo_cargado", "archivo": archivo}
        self.contexto.definir_variable(nombre_var, modelo_simulado)
        return None

    # --- Gráficos ---

    def visitGraficoLinea(self, ctx:DSLParser.GraficoLineaContext):
        x = self.visit(ctx.expresion(0))
        y = self.visit(ctx.expresion(1))
        title = "Gráfico de Línea"
        
        if ctx.STRING():
            title = ctx.STRING().getText()[1:-1]
            
        Graficos.plot(x, y, titulo=title)
        return None

    def visitGraficoDispersion(self, ctx:DSLParser.GraficoDispersionContext):
        x = self.visit(ctx.expresion(0))
        y = self.visit(ctx.expresion(1))
        title = "Dispersión"
        
        if ctx.STRING():
            title = ctx.STRING().getText()[1:-1]
            
        Graficos.scatter(x, y, titulo=title)
        return None

    def visitGraficoBarra(self, ctx:DSLParser.GraficoBarraContext):
        labels = self.visit(ctx.expresion(0))
        values = self.visit(ctx.expresion(1))
        title = "Barras"
        
        if ctx.STRING():
            title = ctx.STRING().getText()[1:-1]
            
        Graficos.bar(labels, values, titulo=title)
        return None

    def visitGraficoHistograma(self, ctx:DSLParser.GraficoHistogramaContext):
        data = self.visit(ctx.expresion(0))
        bins = 10
        title = "Histograma"
        
        if len(ctx.expresion()) > 1:
            bins = int(self.visit(ctx.expresion(1)))
            
        if ctx.STRING():
            title = ctx.STRING().getText()[1:-1]
            
        Graficos.histograma(data, bins, titulo=title)
        return None

    def visitGraficoRegresion(self, ctx:DSLParser.GraficoRegresionContext):
        x = self.visit(ctx.expresion(0))
        y = self.visit(ctx.expresion(1))
        title = "Regresión"
        
        if ctx.STRING():
            title = ctx.STRING().getText()[1:-1]
            
        Graficos.regresion_lineal(x, y, titulo=title)
        return None
        
    def visitGraficoFuncion(self, ctx:DSLParser.GraficoFuncionContext):
        func_name = ctx.ID().getText()
        start = self.visit(ctx.expresion(0))
        end = self.visit(ctx.expresion(1))
        title = "Función"
        
        if ctx.STRING():
            title = ctx.STRING().getText()[1:-1]
            
        # Necesitamos un wrapper para llamar a la función del DSL desde Python
        def func_wrapper(x):
            # Llamar a la función definida en el DSL
            # Esto es tricky porque necesitamos el contexto.
            # Podemos usar visitFuncionLlamada simulado o invocar directamente.
            
            if not self.contexto.existe_funcion(func_name):
                return 0
                
            funcion_info = self.contexto.obtener_funcion(func_name)
            parametros = funcion_info['parametros']
            cuerpo = funcion_info['cuerpo']
            
            # Asumimos función de 1 argumento
            if len(parametros) != 1:
                return 0
                
            self.contexto.entrar_llamada(func_name, [x])
            self.contexto.entrar_scope('funcion')
            self.contexto.definir_local(parametros[0], x)
            
            res = 0
            try:
                self.visit(cuerpo)
            except ReturnException as e:
                res = e.value
            finally:
                self.contexto.salir_scope()
                self.contexto.salir_llamada()
            return res

        Graficos.funcion(func_wrapper, start, end, titulo=title)
        return None
