class Matrices:
    #Mostrar matriz
    @staticmethod
    def mostrar_matriz(A):
        for filas in A:
            print(filas)
            
    #Sumar matrices
    @staticmethod
    def sumar_matrices(A, B):
        filas, columnas=len(A), len(A[0])  
        resultado=[]
        for i in range(filas):
            fila=[]
            for j in range(columnas):
                fila.append(A[i][j]+B[i][j])
            resultado.append(fila)
        return resultado
    
    #Restar matrices
    @staticmethod
    def resta_matrices(A, B):
        filas, columnas=len(A), len(A[0]) 
        resultado=[]
        for i in range(filas):
            fila=[]
            for j in range(columnas):
                fila.append(A[i][j]-B[i][j])
            resultado.append(fila)
        return resultado
    
    #Multiplicar por escalar
    @staticmethod
    def multiplicar_escalar(A, k):
        return [[elem*k for elem in fila] for fila in A]
    
    #Multiplicar matrices
    @staticmethod
    def multiplicar_matrices(A, B):
        filas_A, columnas_A=len(A), len(A[0])
        filas_B, columnas_B=len(B), len(B[0])

        if columnas_A!=filas_B:
            raise ValueError("columnas de A != filas de B")

        resultado=[[0 for _ in range(columnas_B)] for _ in range(filas_A)]

        for i in range(filas_A):
            for j in range(columnas_B):
                for k in range(columnas_A):
                    resultado[i][j]+=A[i][k]*B[k][j]
        return resultado
    
    #Calcular transpuesta
    @staticmethod
    def transpuesta(x):
        filas, columnas=len(x), len(x[0])
        resultado=[]
        for j in range(columnas):
            fila=[]
            for i in range(filas):
                fila.append(x[i][j])
            resultado.append(fila)
        return resultado
    
    #Calcular inversa
    @staticmethod
    def inversa(x):
        n=len(x)
        for fila in x:
            if len(fila)!=n:
                raise ValueError("la matriz no es cuadrada")

        A=[fila[:] for fila in x]
        I=[[1 if i==j else 0 for j in range(n)] for i in range(n)]

        for i in range(n):
            pivote=A[i][i]
            if pivote==0:
                for k in range(i+1, n):
                    if A[k][i]!=0:
                        A[i], A[k]=A[k], A[i]
                        I[i], I[k]=I[k], I[i]
                        pivote = A[i][i]
                        break
                else:
                    raise ValueError("La matriz no tiene inversa")

            for j in range(n):
                A[i][j]/=pivote
                I[i][j]/=pivote

            for k in range(n):
                if k !=i:
                    factor=A[k][i]
                    for j in range(n):
                        A[k][j]-=factor*A[i][j]
                        I[k][j]-=factor*I[i][j]

        return I
    
    