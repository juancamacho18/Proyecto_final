class Contexto:
    """
    Gestión de contexto de ejecución con scope completo:
    - Variables globales: accesibles desde cualquier lugar
    - Variables locales: específicas de cada scope (función, bloque, ciclo)
    - Cada estructura mantiene su propio registro de variables
    """
    
    def __init__(self):
        # Scope global (siempre presente)
        self.scope_global = {}
        
        # Pila de scopes locales (cada elemento es un diccionario)
        # Cada función, bloque, ciclo tiene su propio scope
        self.scopes_locales = []
        
        # Diccionario de funciones definidas
        self.funciones = {}
        
        # Pila de llamadas (para debugging y recursión)
        self.call_stack = []
        
        # Registro de tipos de scope (para debugging)
        self.tipos_scope = []  # 'funcion', 'ciclo', 'condicional', 'bloque'
    
    # gestion de variables globales

    def definir_global(self, nombre, valor):
        """Define o actualiza una variable en el scope global"""
        self.scope_global[nombre] = valor
    
    def obtener_global(self, nombre):
        """Obtiene una variable del scope global"""
        if nombre not in self.scope_global:
            raise NameError(f"Variable global '{nombre}' no está definida")
        return self.scope_global[nombre]
    
    def existe_global(self, nombre):
        """Verifica si una variable existe en el scope global"""
        return nombre in self.scope_global
    
    def listar_globales(self):
        """Retorna todas las variables globales"""
        return self.scope_global.copy()
    
    # gestión de variables locales
    
    def definir_local(self, nombre, valor):
        """
        Define una variable en el scope local actual
        Si no hay scope local, la define como global
        """
        if len(self.scopes_locales) > 0:
            self.scopes_locales[-1][nombre] = valor
        else:
            self.scope_global[nombre] = valor
    
    def obtener_local(self, nombre):
        """
        Obtiene una variable del scope local actual
        (sin buscar en otros scopes)
        """
        if len(self.scopes_locales) > 0:
            scope_actual = self.scopes_locales[-1]
            if nombre not in scope_actual:
                raise NameError(f"Variable local '{nombre}' no está definida en este scope")
            return scope_actual[nombre]
        else:
            return self.obtener_global(nombre)
    
    def existe_local(self, nombre):
        """Verifica si una variable existe en el scope local actual"""
        if len(self.scopes_locales) > 0:
            return nombre in self.scopes_locales[-1]
        return nombre in self.scope_global
    
    def listar_locales(self):
        """Retorna todas las variables del scope local actual"""
        if len(self.scopes_locales) > 0:
            return self.scopes_locales[-1].copy()
        return {}
    
    # gestion de variables (búsqueda en cascada)

    def definir_variable(self, nombre, valor):
        """
        Define una variable en el scope actual
        - Si estamos en un scope local, la define allí
        - Si estamos en scope global, la define como global
        """
        self.definir_local(nombre, valor)
    
    def obtener_variable(self, nombre):
        """
        Busca una variable siguiendo la jerarquía de scopes:
        1. Busca en el scope local actual
        2. Busca en scopes locales externos (de afuera hacia adentro)
        3. Busca en el scope global
        4. Si no existe, lanza error
        """
        # Buscar en scopes locales (del más interno al más externo)
        for scope in reversed(self.scopes_locales):
            if nombre in scope:
                return scope[nombre]
        
        # Buscar en scope global
        if nombre in self.scope_global:
            return self.scope_global[nombre]
        
        # No encontrada
        raise NameError(f"Variable '{nombre}' no está definida")
    
    def existe_variable(self, nombre):
        """Verifica si una variable existe en algún scope"""
        # Buscar en scopes locales
        for scope in reversed(self.scopes_locales):
            if nombre in scope:
                return True
        
        # Buscar en scope global
        return nombre in self.scope_global
    
    def actualizar_variable(self, nombre, valor):
        """
        Actualiza una variable existente:
        - Busca en scopes locales primero
        - Luego en scope global
        - Si no existe en ningún lado, la crea en el scope actual
        """
        # Buscar en scopes locales (del más interno al más externo)
        for scope in reversed(self.scopes_locales):
            if nombre in scope:
                scope[nombre] = valor
                return
        
        # Buscar en scope global
        if nombre in self.scope_global:
            self.scope_global[nombre] = valor
            return
        
        # Si no existe, crearla en el scope actual
        self.definir_variable(nombre, valor)
    
    def forzar_global(self, nombre, valor):
        """
        Declara explícitamente una variable como global
        (útil para la palabra clave 'global' en tu DSL)
        """
        self.scope_global[nombre] = valor

    # gestion de scopes
    
    def entrar_scope(self, tipo='bloque'):
        """
        Crea un nuevo scope local
        tipo: 'funcion', 'ciclo', 'condicional', 'bloque'
        """
        self.scopes_locales.append({})
        self.tipos_scope.append(tipo)
    
    def salir_scope(self):
        """Sale del scope local actual"""
        if len(self.scopes_locales) > 0:
            self.scopes_locales.pop()
            self.tipos_scope.pop()
        else:
            raise RuntimeError("No se puede salir del scope global")
    
    def obtener_scope_actual(self):
        """Retorna el diccionario del scope actual"""
        if len(self.scopes_locales) > 0:
            return self.scopes_locales[-1].copy()
        return self.scope_global.copy()
    
    def obtener_tipo_scope_actual(self):
        """Retorna el tipo del scope actual"""
        if len(self.tipos_scope) > 0:
            return self.tipos_scope[-1]
        return 'global'
    
    def nivel_scope(self):
        """Retorna el nivel actual de anidamiento (0 = global)"""
        return len(self.scopes_locales)
    
    def en_scope_global(self):
        """Verifica si estamos en el scope global"""
        return len(self.scopes_locales) == 0
    
    # gestion de funciones
    
    def definir_funcion(self, nombre, parametros, cuerpo_ctx):
        """
        Define una función
        parametros: lista de nombres de parámetros
        cuerpo_ctx: contexto de ANTLR con el cuerpo de la función
        """
        self.funciones[nombre] = {
            'parametros': parametros,
            'cuerpo': cuerpo_ctx,
            'nombre': nombre,
            'es_recursiva': False
        }
    
    def obtener_funcion(self, nombre):
        """Obtiene la definición de una función"""
        if nombre not in self.funciones:
            raise NameError(f"Función '{nombre}' no está definida")
        return self.funciones[nombre]
    
    def existe_funcion(self, nombre):
        """Verifica si una función existe"""
        return nombre in self.funciones
    
    def marcar_recursiva(self, nombre):
        """Marca una función como recursiva (para optimización/debugging)"""
        if nombre in self.funciones:
            self.funciones[nombre]['es_recursiva'] = True
    
    # gestión de llamadas
    
    def entrar_llamada(self, nombre_funcion, argumentos):
        """Registra una llamada a función"""
        self.call_stack.append({
            'funcion': nombre_funcion,
            'argumentos': argumentos,
            'variables_locales': {}
        })
    
    def salir_llamada(self):
        """Sale de una llamada a función"""
        if self.call_stack:
            return self.call_stack.pop()
        return None
    
    def profundidad_llamada(self):
        """Retorna la profundidad actual del call stack"""
        return len(self.call_stack)
    
    def obtener_llamada_actual(self):
        """Obtiene información de la llamada actual"""
        if self.call_stack:
            return self.call_stack[-1]
        return None
    
    def mostrar_call_stack(self):
        """Muestra el call stack actual (útil para debugging)"""
        print("\n--- Call Stack ---")
        if len(self.call_stack) == 0:
            print("  (vacío)")
        for i, llamada in enumerate(self.call_stack):
            print(f"  {i}: {llamada['funcion']}({llamada['argumentos']})")
        print()
    
    # tutoriales de debugg
    
    def mostrar_variables(self, detallado=False):
        """Muestra todas las variables en todos los scopes"""
        print("\n--- Variables ---")
        
        # Variables globales
        print("SCOPE GLOBAL:")
        if len(self.scope_global) == 0:
            print("  (vacío)")
        for nombre, valor in self.scope_global.items():
            tipo_val = type(valor).__name__
            valor_str = str(valor) if len(str(valor)) < 50 else str(valor)[:47] + "..."
            if detallado:
                print(f"  {nombre} = {valor_str} ({tipo_val})")
            else:
                print(f"  {nombre} = {valor_str}")
        
        # Variables locales
        if len(self.scopes_locales) > 0:
            print("\nSCOPES LOCALES:")
            for i, (scope, tipo) in enumerate(zip(self.scopes_locales, self.tipos_scope)):
                print(f"\n  Nivel {i+1} ({tipo}):")
                if len(scope) == 0:
                    print("    (vacío)")
                for nombre, valor in scope.items():
                    tipo_val = type(valor).__name__
                    valor_str = str(valor) if len(str(valor)) < 50 else str(valor)[:47] + "..."
                    if detallado:
                        print(f"    {nombre} = {valor_str} ({tipo_val})")
                    else:
                        print(f"    {nombre} = {valor_str}")
        print()
    
    def mostrar_funciones(self):
        """Muestra todas las funciones definidas"""
        print("\n--- Funciones Definidas ---")
        if len(self.funciones) == 0:
            print("  (ninguna)")
        for nombre, info in self.funciones.items():
            params = ', '.join(info['parametros'])
            recursiva = " [RECURSIVA]" if info['es_recursiva'] else ""
            print(f"  {nombre}({params}){recursiva}")
        print()
    
    def mostrar_estado_completo(self):
        """Muestra el estado completo del contexto"""
        print("\n" + "="*60)
        print("ESTADO DEL CONTEXTO")
        print("="*60)
        
        print(f"Nivel de scope: {self.nivel_scope()}")
        print(f"Tipo de scope actual: {self.obtener_tipo_scope_actual()}")
        print(f"Profundidad de llamadas: {self.profundidad_llamada()}")
        
        self.mostrar_variables()
        self.mostrar_funciones()
        
        if len(self.call_stack) > 0:
            self.mostrar_call_stack()
        
        print("="*60 + "\n")
    
    def verificar_variable_sombreada(self, nombre):
        """
        Verifica si una variable está siendo sombreada
        (definida en múltiples scopes)
        """
        apariciones = []
        
        # Verificar en global
        if nombre in self.scope_global:
            apariciones.append(('global', self.scope_global[nombre]))
        
        # Verificar en scopes locales
        for i, scope in enumerate(self.scopes_locales):
            if nombre in scope:
                apariciones.append((f'local_nivel_{i+1}', scope[nombre]))
        
        if len(apariciones) > 1:
            print(f"\n⚠️  ADVERTENCIA: Variable '{nombre}' sombreada:")
            for tipo, valor in apariciones:
                print(f"   En {tipo}: {valor}")
            print()
        
        return len(apariciones) > 1
    
    # gestion de estado
    
    def limpiar(self):
        """Limpia todo el contexto (mantiene solo scope global vacío)"""
        self.scope_global = {}
        self.scopes_locales = []
        self.funciones = {}
        self.call_stack = []
        self.tipos_scope = []
    
    def limpiar_locales(self):
        """Limpia solo los scopes locales, mantiene globales"""
        self.scopes_locales = []
        self.tipos_scope = []
        self.call_stack = []
    
    def exportar_estado(self):
        """Exporta el estado actual del contexto"""
        return {
            'variables_globales': self.scope_global.copy(),
            'n_variables_globales': len(self.scope_global),
            'variables_locales_actual': self.obtener_scope_actual(),
            'n_variables_locales': len(self.obtener_scope_actual()),
            'funciones': list(self.funciones.keys()),
            'n_funciones': len(self.funciones),
            'nivel_scope': self.nivel_scope(),
            'tipo_scope': self.obtener_tipo_scope_actual(),
            'profundidad_llamadas': self.profundidad_llamada()
        }
    
    def importar_globales(self, diccionario):
        """Importa variables al scope global"""
        for nombre, valor in diccionario.items():
            self.scope_global[nombre] = valor
    
    def __str__(self):
        """Representación en string del contexto"""
        return (f"Contexto(globales={len(self.scope_global)}, "
                f"locales={sum(len(s) for s in self.scopes_locales)}, "
                f"funciones={len(self.funciones)}, "
                f"nivel={self.nivel_scope()})")


class MemoriaDataframes:
    """
    Gestión de dataframes/tablas para operaciones de ML
    Similar a pandas pero simplificado
    """
    
    def __init__(self):
        self.dataframes = {}
    
    def crear_dataframe(self, nombre, datos, columnas=None):
        """
        Crea un dataframe
        datos: lista de listas o diccionario
        """
        if isinstance(datos, dict):
            # Convertir diccionario a formato estándar
            columnas = list(datos.keys())
            n_filas = len(datos[columnas[0]])
            datos_lista = []
            for i in range(n_filas):
                fila = [datos[col][i] for col in columnas]
                datos_lista.append(fila)
            datos = datos_lista
        
        # Determinar columnas si no se proporcionan
        if not columnas:
            if datos and len(datos) > 0:
                columnas = [f'col_{i}' for i in range(len(datos[0]))]
            else:
                columnas = []

        self.dataframes[nombre] = {
            'datos': datos,
            'columnas': columnas,
            'n_filas': len(datos),
            'n_columnas': len(datos[0]) if datos else 0
        }
    
    def obtener_dataframe(self, nombre):
        """Obtiene un dataframe"""
        if nombre not in self.dataframes:
            raise KeyError(f"Dataframe '{nombre}' no existe")
        return self.dataframes[nombre]
    
    def obtener_columna(self, nombre_df, nombre_columna):
        """Obtiene una columna de un dataframe"""
        df = self.obtener_dataframe(nombre_df)
        
        if nombre_columna not in df['columnas']:
            raise KeyError(f"Columna '{nombre_columna}' no existe")
        
        idx = df['columnas'].index(nombre_columna)
        return [fila[idx] for fila in df['datos']]
    
    def filtrar(self, nombre_df, condicion_func):
        """Filtra filas de un dataframe"""
        df = self.obtener_dataframe(nombre_df)
        datos_filtrados = [fila for fila in df['datos'] if condicion_func(fila)]
        
        return {
            'datos': datos_filtrados,
            'columnas': df['columnas'],
            'n_filas': len(datos_filtrados),
            'n_columnas': df['n_columnas']
        }
    
    def mostrar(self, nombre_df, n_filas=5):
        """Muestra las primeras n filas de un dataframe"""
        df = self.obtener_dataframe(nombre_df)
        
        print(f"\n--- Dataframe: {nombre_df} ---")
        print(f"Shape: ({df['n_filas']}, {df['n_columnas']})")
        print(f"Columnas: {df['columnas']}")
        print()
        
        # Mostrar encabezados
        header = " | ".join([f"{col:>10}" for col in df['columnas']])
        print(header)
        print("-" * len(header))
        
        # Mostrar datos
        for i, fila in enumerate(df['datos'][:n_filas]):
            row = " | ".join([f"{str(val):>10}" for val in fila])
            print(row)
        
        if df['n_filas'] > n_filas:
            print(f"... ({df['n_filas'] - n_filas} filas más)")
        print()
    
    def listar_dataframes(self):
        """Lista todos los dataframes en memoria"""
        print("\n--- Dataframes en Memoria ---")
        for nombre, df in self.dataframes.items():
            print(f"  {nombre}: {df['n_filas']} filas x {df['n_columnas']} columnas")
        print()
    
    def eliminar_dataframe(self, nombre):
        """Elimina un dataframe de memoria"""
        if nombre in self.dataframes:
            del self.dataframes[nombre]
            return True
        return False
    
    def limpiar(self):
        """Elimina todos los dataframes"""
        self.dataframes = {}


class GestorModelos:
    """
    Gestión de modelos de Machine Learning entrenados
    """
    
    def __init__(self):
        self.modelos = {}
    
    def guardar_modelo(self, nombre, modelo, tipo, metricas=None):
        """
        Guarda un modelo entrenado
        tipo: 'perceptron', 'mlp', 'kmeans', 'regresion', etc.
        """
        self.modelos[nombre] = {
            'modelo': modelo,
            'tipo': tipo,
            'metricas': metricas if metricas else {},
            'timestamp': None
        }
    
    def obtener_modelo(self, nombre):
        """Obtiene un modelo guardado"""
        if nombre not in self.modelos:
            raise KeyError(f"Modelo '{nombre}' no existe")
        return self.modelos[nombre]['modelo']
    
    def obtener_info_modelo(self, nombre):
        """Obtiene información completa de un modelo"""
        if nombre not in self.modelos:
            raise KeyError(f"Modelo '{nombre}' no existe")
        return self.modelos[nombre]
    
    def listar_modelos(self):
        """Lista todos los modelos guardados"""
        print("\n--- Modelos Entrenados ---")
        for nombre, info in self.modelos.items():
            print(f"  {nombre} ({info['tipo']})")
            if info['metricas']:
                for metrica, valor in info['metricas'].items():
                    print(f"    - {metrica}: {valor}")
        print()
    
    def eliminar_modelo(self, nombre):
        """Elimina un modelo"""
        if nombre in self.modelos:
            del self.modelos[nombre]
            return True
        return False
    
    def comparar_modelos(self, nombres_modelos, metrica='precision'):
        """Compara varios modelos según una métrica"""
        print(f"\n--- Comparación de Modelos (por {metrica}) ---")
        resultados = []
        
        for nombre in nombres_modelos:
            if nombre in self.modelos:
                info = self.modelos[nombre]
                valor = info['metricas'].get(metrica, 'N/A')
                resultados.append((nombre, valor))
        
        # Ordenar por métrica
        resultados_validos = [(n, v) for n, v in resultados if v != 'N/A']
        resultados_validos.sort(key=lambda x: x[1], reverse=True)
        
        for nombre, valor in resultados_validos:
            print(f"  {nombre}: {valor}")
        print()
        
        if resultados_validos:
            mejor = resultados_validos[0]
            print(f"Mejor modelo: {mejor[0]} con {metrica}={mejor[1]}")
        print()
    
    def limpiar(self):
        """Elimina todos los modelos"""
        self.modelos = {}