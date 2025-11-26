class ManejoArchivos:
    """
    Librería para manejo de archivos de texto, CSV y datos
    sin usar librerías externas
    """
    
    # ===================================================
    # OPERACIONES BÁSICAS DE ARCHIVOS
    # ===================================================
    
    @staticmethod
    def leer_archivo(ruta):
        """Lee todo el contenido de un archivo de texto"""
        try:
            with open(ruta, 'r', encoding='utf-8') as archivo:
                contenido = archivo.read()
            return contenido
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo '{ruta}'")
            return None
        except Exception as e:
            print(f"Error al leer archivo: {e}")
            return None
    
    @staticmethod
    def leer_lineas(ruta):
        """Lee un archivo y devuelve una lista de líneas"""
        try:
            with open(ruta, 'r', encoding='utf-8') as archivo:
                lineas = []
                for linea in archivo:
                    lineas.append(linea.rstrip('\n\r'))
            return lineas
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo '{ruta}'")
            return None
        except Exception as e:
            print(f"Error al leer archivo: {e}")
            return None
    
    @staticmethod
    def escribir_archivo(ruta, contenido, modo='w'):
        """
        Escribe contenido en un archivo
        modo: 'w' para sobreescribir, 'a' para añadir
        """
        try:
            with open(ruta, modo, encoding='utf-8') as archivo:
                archivo.write(contenido)
            return True
        except Exception as e:
            print(f"Error al escribir archivo: {e}")
            return False
    
    @staticmethod
    def añadir_linea(ruta, linea):
        """Añade una línea al final de un archivo"""
        try:
            with open(ruta, 'a', encoding='utf-8') as archivo:
                archivo.write(linea + '\n')
            return True
        except Exception as e:
            print(f"Error al añadir línea: {e}")
            return False
    
    @staticmethod
    def existe_archivo(ruta):
        """Verifica si un archivo existe"""
        try:
            with open(ruta, 'r') as archivo:
                pass
            return True
        except FileNotFoundError:
            return False
        except Exception:
            return False
    
    @staticmethod
    def borrar_contenido(ruta):
        """Borra todo el contenido de un archivo"""
        return ManejoArchivos.escribir_archivo(ruta, '', modo='w')
    
    # ===================================================
    # OPERACIONES CON CSV
    # ===================================================
    
    @staticmethod
    def leer_csv(ruta, delimitador=',', tiene_encabezado=True):
        """
        Lee un archivo CSV y devuelve una estructura de datos
        Retorna: {'encabezados': [...], 'datos': [[...], [...], ...]}
        """
        lineas = ManejoArchivos.leer_lineas(ruta)
        if lineas is None:
            return None
        
        if len(lineas) == 0:
            return {'encabezados': [], 'datos': []}
        
        # Parsear CSV manualmente
        filas = []
        for linea in lineas:
            fila = ManejoArchivos._parsear_linea_csv(linea, delimitador)
            filas.append(fila)
        
        if tiene_encabezado:
            encabezados = filas[0]
            datos = filas[1:]
        else:
            encabezados = []
            datos = filas
        
        return {
            'encabezados': encabezados,
            'datos': datos,
            'n_filas': len(datos),
            'n_columnas': len(datos[0]) if len(datos) > 0 else 0
        }
    
    @staticmethod
    def _parsear_linea_csv(linea, delimitador):
        """Parsea una línea CSV manejando comillas"""
        campos = []
        campo_actual = ""
        dentro_comillas = False
        
        i = 0
        while i < len(linea):
            caracter = linea[i]
            
            if caracter == '"':
                dentro_comillas = not dentro_comillas
            elif caracter == delimitador and not dentro_comillas:
                campos.append(campo_actual.strip())
                campo_actual = ""
            else:
                campo_actual += caracter
            
            i += 1
        
        # Añadir último campo
        campos.append(campo_actual.strip())
        return campos
    
    @staticmethod
    def escribir_csv(ruta, datos, encabezados=None, delimitador=','):
        """
        Escribe datos en formato CSV
        datos: Lista de listas [[fila1], [fila2], ...]
        """
        try:
            with open(ruta, 'w', encoding='utf-8') as archivo:
                # Escribir encabezados si existen
                if encabezados:
                    linea = delimitador.join([str(h) for h in encabezados])
                    archivo.write(linea + '\n')
                
                # Escribir datos
                for fila in datos:
                    linea = delimitador.join([str(campo) for campo in fila])
                    archivo.write(linea + '\n')
            
            return True
        except Exception as e:
            print(f"Error al escribir CSV: {e}")
            return False
    
    @staticmethod
    def obtener_columna(csv_data, nombre_columna=None, indice_columna=None):
        """
        Extrae una columna de datos CSV
        Puede usar nombre de columna o índice
        """
        if csv_data is None:
            return None
        
        encabezados = csv_data['encabezados']
        datos = csv_data['datos']
        
        # Determinar índice de columna
        if nombre_columna is not None:
            if nombre_columna not in encabezados:
                print(f"Error: Columna '{nombre_columna}' no encontrada")
                return None
            indice = encabezados.index(nombre_columna)
        elif indice_columna is not None:
            indice = indice_columna
        else:
            print("Error: Debe especificar nombre_columna o indice_columna")
            return None
        
        # Extraer columna
        columna = []
        for fila in datos:
            if indice < len(fila):
                columna.append(fila[indice])
        
        return columna
    
    @staticmethod
    def filtrar_filas(csv_data, columna, condicion):
        """
        Filtra filas según una condición
        condicion: función que recibe un valor y retorna True/False
        """
        if csv_data is None:
            return None
        
        # Obtener índice de columna
        if isinstance(columna, str):
            indice = csv_data['encabezados'].index(columna)
        else:
            indice = columna
        
        # Filtrar
        filas_filtradas = []
        for fila in csv_data['datos']:
            if indice < len(fila) and condicion(fila[indice]):
                filas_filtradas.append(fila)
        
        return {
            'encabezados': csv_data['encabezados'],
            'datos': filas_filtradas,
            'n_filas': len(filas_filtradas),
            'n_columnas': csv_data['n_columnas']
        }
    
    @staticmethod
    def convertir_columna_a_numeros(columna):
        """Convierte una columna de strings a números"""
        numeros = []
        for valor in columna:
            try:
                # Intentar convertir a float
                if '.' in str(valor):
                    numeros.append(float(valor))
                else:
                    numeros.append(int(valor))
            except ValueError:
                print(f"Advertencia: No se pudo convertir '{valor}' a número")
                numeros.append(0)
        return numeros
    
    # ===================================================
    # OPERACIONES CON DATOS NUMÉRICOS
    # ===================================================
    
    @staticmethod
    def guardar_lista(ruta, lista, formato='txt'):
        """
        Guarda una lista en un archivo
        formato: 'txt' (uno por línea) o 'csv' (separado por comas)
        """
        try:
            with open(ruta, 'w', encoding='utf-8') as archivo:
                if formato == 'txt':
                    for elemento in lista:
                        archivo.write(str(elemento) + '\n')
                elif formato == 'csv':
                    linea = ','.join([str(e) for e in lista])
                    archivo.write(linea + '\n')
            return True
        except Exception as e:
            print(f"Error al guardar lista: {e}")
            return False
    
    @staticmethod
    def cargar_lista(ruta, tipo='float', formato='txt', delimitador=','):
        """
        Carga una lista desde un archivo
        tipo: 'float', 'int', 'str'
        formato: 'txt' o 'csv'
        """
        lineas = ManejoArchivos.leer_lineas(ruta)
        if lineas is None:
            return None
        
        lista = []
        
        if formato == 'txt':
            # Un elemento por línea
            for linea in lineas:
                if linea.strip():
                    lista.append(ManejoArchivos._convertir_tipo(linea.strip(), tipo))
        elif formato == 'csv':
            # Elementos separados por delimitador
            for linea in lineas:
                if linea.strip():
                    elementos = linea.split(delimitador)
                    for elem in elementos:
                        if elem.strip():
                            lista.append(ManejoArchivos._convertir_tipo(elem.strip(), tipo))
        
        return lista
    
    @staticmethod
    def guardar_matriz(ruta, matriz):
        """Guarda una matriz en formato CSV"""
        return ManejoArchivos.escribir_csv(ruta, matriz)
    
    @staticmethod
    def cargar_matriz(ruta, tipo='float'):
        """Carga una matriz desde un archivo CSV"""
        csv_data = ManejoArchivos.leer_csv(ruta, tiene_encabezado=False)
        if csv_data is None:
            return None
        
        matriz = []
        for fila in csv_data['datos']:
            fila_convertida = []
            for valor in fila:
                fila_convertida.append(ManejoArchivos._convertir_tipo(valor, tipo))
            matriz.append(fila_convertida)
        
        return matriz
    
    @staticmethod
    def _convertir_tipo(valor, tipo):
        """Convierte un valor al tipo especificado"""
        try:
            if tipo == 'int':
                return int(valor)
            elif tipo == 'float':
                return float(valor)
            else:
                return str(valor)
        except ValueError:
            print(f"Advertencia: No se pudo convertir '{valor}' a {tipo}")
            if tipo == 'int':
                return 0
            elif tipo == 'float':
                return 0.0
            else:
                return ""
    
    # ===================================================
    # UTILIDADES
    # ===================================================
    
    @staticmethod
    def contar_lineas(ruta):
        """Cuenta el número de líneas en un archivo"""
        lineas = ManejoArchivos.leer_lineas(ruta)
        return len(lineas) if lineas else 0
    
    @staticmethod
    def buscar_en_archivo(ruta, texto_buscar):
        """Busca un texto en un archivo y devuelve las líneas donde aparece"""
        lineas = ManejoArchivos.leer_lineas(ruta)
        if lineas is None:
            return []
        
        lineas_encontradas = []
        for i, linea in enumerate(lineas):
            if texto_buscar in linea:
                lineas_encontradas.append({
                    'numero': i + 1,
                    'contenido': linea
                })
        
        return lineas_encontradas
    
    @staticmethod
    def reemplazar_en_archivo(ruta, texto_buscar, texto_reemplazo):
        """Reemplaza texto en un archivo"""
        contenido = ManejoArchivos.leer_archivo(ruta)
        if contenido is None:
            return False
        
        nuevo_contenido = contenido.replace(texto_buscar, texto_reemplazo)
        return ManejoArchivos.escribir_archivo(ruta, nuevo_contenido, modo='w')
    
    @staticmethod
    def mostrar_archivo(ruta, num_lineas=None):
        """Muestra el contenido de un archivo en consola"""
        lineas = ManejoArchivos.leer_lineas(ruta)
        if lineas is None:
            return
        
        print(f"\n--- Contenido de '{ruta}' ---")
        lineas_a_mostrar = lineas[:num_lineas] if num_lineas else lineas
        
        for i, linea in enumerate(lineas_a_mostrar, 1):
            print(f"{i:4d} | {linea}")
        
        if num_lineas and len(lineas) > num_lineas:
            print(f"... ({len(lineas) - num_lineas} líneas más)")
        print()
    
    @staticmethod
    def estadisticas_csv(csv_data):
        """Muestra estadísticas de un archivo CSV"""
        if csv_data is None:
            return
        
        print("\n--- Estadísticas del CSV ---")
        print(f"Número de filas: {csv_data['n_filas']}")
        print(f"Número de columnas: {csv_data['n_columnas']}")
        print(f"Encabezados: {csv_data['encabezados']}")
        
        # Mostrar primeras filas
        print("\nPrimeras 5 filas:")
        for i, fila in enumerate(csv_data['datos'][:5]):
            print(f"  {i+1}: {fila}")
        print()