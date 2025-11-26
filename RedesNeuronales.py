from Matrices import Matrices
from Aritmetica import Aritmetica

class RedesNeuronales:
    """
    Implementación de redes neuronales para clasificación y predicción
    sin usar librerías externas
    """
    # funciones de activación

    @staticmethod
    def sigmoid(x):
        """Función sigmoide: 1 / (1 + e^(-x))"""
        if x >= 0:
            return 1.0 / (1.0 + Aritmetica.raiz(2.718281828459045, -x))
        else:
            exp_x = 2.718281828459045 ** x
            return exp_x / (1.0 + exp_x)
    
    @staticmethod
    def sigmoid_derivada(x):
        """Derivada de la función sigmoide"""
        s = RedesNeuronales.sigmoid(x)
        return s * (1 - s)
    
    @staticmethod
    def relu(x):
        """Función ReLU: max(0, x)"""
        return max(0, x)
    
    @staticmethod
    def relu_derivada(x):
        """Derivada de ReLU"""
        return 1 if x > 0 else 0
    
    @staticmethod
    def tanh(x):
        """Función tangente hiperbólica"""
        e_pos = 2.718281828459045 ** x
        e_neg = 2.718281828459045 ** (-x)
        return (e_pos - e_neg) / (e_pos + e_neg)
    
    @staticmethod
    def tanh_derivada(x):
        """Derivada de tanh"""
        t = RedesNeuronales.tanh(x)
        return 1 - t * t
    
    @staticmethod
    def softmax(x_lista):
        """Función softmax para clasificación multiclase"""
        exp_valores = []
        max_val = max(x_lista)
        
        # Restar max para estabilidad numérica
        for x in x_lista:
            exp_valores.append(2.718281828459045 ** (x - max_val))
        
        suma = sum(exp_valores)
        return [val / suma for val in exp_valores]

    # perceptrón simple

    @staticmethod
    def perceptron_simple(X, y, tasa_aprendizaje=0.1, epocas=100):
        """
        Perceptrón simple para clasificación binaria
        X: Lista de listas (características)
        y: Lista de etiquetas (0 o 1)
        """
        n_muestras = len(X)
        n_caracteristicas = len(X[0])
        
        # Inicializar pesos y sesgo
        pesos = [0.0] * n_caracteristicas
        sesgo = 0.0
        
        # Entrenar
        for epoca in range(epocas):
            errores = 0
            for i in range(n_muestras):
                # Calcular predicción
                z = sesgo
                for j in range(n_caracteristicas):
                    z += pesos[j] * X[i][j]
                
                prediccion = 1 if z >= 0 else 0
                
                # Actualizar pesos si hay error
                error = y[i] - prediccion
                if error != 0:
                    errores += 1
                    sesgo += tasa_aprendizaje * error
                    for j in range(n_caracteristicas):
                        pesos[j] += tasa_aprendizaje * error * X[i][j]
            
            if errores == 0:
                print(f"Convergencia alcanzada en época {epoca + 1}")
                break
        
        return {"pesos": pesos, "sesgo": sesgo}
    
    @staticmethod
    def predecir_perceptron(modelo, X):
        """Predice usando un perceptrón entrenado"""
        predicciones = []
        pesos = modelo["pesos"]
        sesgo = modelo["sesgo"]
        
        for muestra in X:
            z = sesgo
            for j in range(len(muestra)):
                z += pesos[j] * muestra[j]
            predicciones.append(1 if z >= 0 else 0)
        
        return predicciones

    # perceptrón multicapa (MLP)

    @staticmethod
    def crear_mlp(n_entrada, n_oculta, n_salida):
        """
        Crea un perceptrón multicapa con una capa oculta
        """
        # Inicializar pesos aleatoriamente (usando una semilla simple)
        pesos_entrada_oculta = []
        for i in range(n_entrada):
            fila = []
            for j in range(n_oculta):
                # Inicialización simple entre -0.5 y 0.5
                peso = ((i * 7 + j * 13) % 100) / 100.0 - 0.5
                fila.append(peso)
            pesos_entrada_oculta.append(fila)
        
        pesos_oculta_salida = []
        for i in range(n_oculta):
            fila = []
            for j in range(n_salida):
                peso = ((i * 11 + j * 17) % 100) / 100.0 - 0.5
                fila.append(peso)
            pesos_oculta_salida.append(fila)
        
        sesgo_oculta = [0.1] * n_oculta
        sesgo_salida = [0.1] * n_salida
        
        return {
            "pesos_entrada_oculta": pesos_entrada_oculta,
            "pesos_oculta_salida": pesos_oculta_salida,
            "sesgo_oculta": sesgo_oculta,
            "sesgo_salida": sesgo_salida,
            "n_entrada": n_entrada,
            "n_oculta": n_oculta,
            "n_salida": n_salida
        }
    
    @staticmethod
    def forward_mlp(red, entrada):
        """Propagación hacia adelante en el MLP"""
        # Capa oculta
        oculta = []
        for j in range(red["n_oculta"]):
            suma = red["sesgo_oculta"][j]
            for i in range(red["n_entrada"]):
                suma += entrada[i] * red["pesos_entrada_oculta"][i][j]
            oculta.append(RedesNeuronales.sigmoid(suma))
        
        # Capa de salida
        salida = []
        for j in range(red["n_salida"]):
            suma = red["sesgo_salida"][j]
            for i in range(red["n_oculta"]):
                suma += oculta[i] * red["pesos_oculta_salida"][i][j]
            salida.append(RedesNeuronales.sigmoid(suma))
        
        return {"oculta": oculta, "salida": salida}
    
    @staticmethod
    def entrenar_mlp(red, X, y, tasa_aprendizaje=0.1, epocas=1000, verbose=False):
        """
        Entrena el MLP usando backpropagation
        y: debe ser lista de listas para multiclase (one-hot encoding)
        """
        n_muestras = len(X)
        
        for epoca in range(epocas):
            error_total = 0
            
            for muestra_idx in range(n_muestras):
                entrada = X[muestra_idx]
                objetivo = y[muestra_idx] if isinstance(y[muestra_idx], list) else [y[muestra_idx]]
                
                # Forward pass
                resultado = RedesNeuronales.forward_mlp(red, entrada)
                oculta = resultado["oculta"]
                salida = resultado["salida"]
                
                # Calcular error
                for i in range(len(salida)):
                    error_total += (objetivo[i] - salida[i]) ** 2
                
                # Backpropagation
                # Gradiente de la capa de salida
                delta_salida = []
                for j in range(red["n_salida"]):
                    error = objetivo[j] - salida[j]
                    delta_salida.append(error * salida[j] * (1 - salida[j]))
                
                # Gradiente de la capa oculta
                delta_oculta = []
                for j in range(red["n_oculta"]):
                    error = 0
                    for k in range(red["n_salida"]):
                        error += delta_salida[k] * red["pesos_oculta_salida"][j][k]
                    delta_oculta.append(error * oculta[j] * (1 - oculta[j]))
                
                # Actualizar pesos capa oculta -> salida
                for i in range(red["n_oculta"]):
                    for j in range(red["n_salida"]):
                        red["pesos_oculta_salida"][i][j] += tasa_aprendizaje * delta_salida[j] * oculta[i]
                
                for j in range(red["n_salida"]):
                    red["sesgo_salida"][j] += tasa_aprendizaje * delta_salida[j]
                
                # Actualizar pesos entrada -> oculta
                for i in range(red["n_entrada"]):
                    for j in range(red["n_oculta"]):
                        red["pesos_entrada_oculta"][i][j] += tasa_aprendizaje * delta_oculta[j] * entrada[i]
                
                for j in range(red["n_oculta"]):
                    red["sesgo_oculta"][j] += tasa_aprendizaje * delta_oculta[j]
            
            if verbose and (epoca + 1) % 100 == 0:
                print(f"Época {epoca + 1}/{epocas}, Error: {error_total / n_muestras}")
        
        return red
    
    @staticmethod
    def predecir_mlp(red, X):
        """Predice usando el MLP entrenado"""
        predicciones = []
        for muestra in X:
            resultado = RedesNeuronales.forward_mlp(red, muestra)
            salida = resultado["salida"]
            
            # Para clasificación binaria
            if len(salida) == 1:
                predicciones.append(1 if salida[0] >= 0.5 else 0)
            else:
                # Para multiclase, elegir la clase con mayor probabilidad
                max_idx = 0
                max_val = salida[0]
                for i in range(1, len(salida)):
                    if salida[i] > max_val:
                        max_val = salida[i]
                        max_idx = i
                predicciones.append(max_idx)
        
        return predicciones

    # regresión lineal(para predicción)

    @staticmethod
    def regresion_lineal_multiple(X, y):
        """
        Regresión lineal múltiple usando ecuaciones normales
        X: matriz de características (n_muestras x n_características)
        y: vector de valores objetivo
        """
        n_muestras = len(X)
        n_caracteristicas = len(X[0])
        
        # Añadir columna de unos para el término independiente
        X_extended = []
        for i in range(n_muestras):
            fila = [1.0] + X[i]
            X_extended.append(fila)
        
        # Calcular X^T
        X_T = Matrices.transpuesta(X_extended)
        
        # Calcular X^T * X
        XTX = Matrices.multiplicar_matrices(X_T, X_extended)
        
        # Calcular X^T * y
        y_matriz = [[val] for val in y]
        XTy = Matrices.multiplicar_matrices(X_T, y_matriz)
        
        # Calcular (X^T * X)^-1
        try:
            XTX_inv = Matrices.inversa(XTX)
        except:
            print("Error: No se puede calcular la inversa, matriz singular")
            return None
        
        # Calcular coeficientes: w = (X^T * X)^-1 * X^T * y
        coeficientes_matriz = Matrices.multiplicar_matrices(XTX_inv, XTy)
        coeficientes = [fila[0] for fila in coeficientes_matriz]
        
        return {
            "sesgo": coeficientes[0],
            "coeficientes": coeficientes[1:],
            "n_caracteristicas": n_caracteristicas
        }
    
    @staticmethod
    def predecir_regresion(modelo, X):
        """Predice usando regresión lineal entrenada"""
        predicciones = []
        sesgo = modelo["sesgo"]
        coefs = modelo["coeficientes"]
        
        for muestra in X:
            pred = sesgo
            for i in range(len(muestra)):
                pred += coefs[i] * muestra[i]
            predicciones.append(pred)
        
        return predicciones

    # metricas de evaluacion

    @staticmethod
    def precision(y_verdadero, y_predicho):
        """Calcula la precisión de clasificación"""
        correctos = 0
        for i in range(len(y_verdadero)):
            if y_verdadero[i] == y_predicho[i]:
                correctos += 1
        return correctos / len(y_verdadero)
    
    @staticmethod
    def error_cuadratico_medio(y_verdadero, y_predicho):
        """Calcula el MSE para problemas de regresión"""
        suma_errores = 0
        for i in range(len(y_verdadero)):
            suma_errores += (y_verdadero[i] - y_predicho[i]) ** 2
        return suma_errores / len(y_verdadero)
    
    @staticmethod
    def matriz_confusion(y_verdadero, y_predicho, n_clases=2):
        """Calcula la matriz de confusión"""
        matriz = [[0 for _ in range(n_clases)] for _ in range(n_clases)]
        
        for i in range(len(y_verdadero)):
            real = y_verdadero[i]
            pred = y_predicho[i]
            matriz[real][pred] += 1
        
        return matriz
    
    @staticmethod
    def dividir_datos(X, y, proporcion_entrenamiento=0.8):
        """Divide datos en conjunto de entrenamiento y prueba"""
        n_muestras = len(X)
        n_entrenamiento = int(n_muestras * proporcion_entrenamiento)
        
        X_train = X[:n_entrenamiento]
        X_test = X[n_entrenamiento:]
        y_train = y[:n_entrenamiento]
        y_test = y[n_entrenamiento:]
        
        return X_train, X_test, y_train, y_test