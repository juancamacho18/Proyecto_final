class Aritmetica(object):  
    #calcular raiz
    @staticmethod
    def raiz(a, b=2):
        return a**(1/b)
    
    #calcular logaritmo
    @staticmethod
    def logaritmo(b, a, tol=1e-6):
        if a<=0 or b==1 or b<=0:
            raise ValueError("Valores invalidos")
        bajo, alto=0,100
        while alto-bajo>tol:
            medio=(bajo+alto)/2
            if b**medio<a:
                bajo=medio
            else:
                alto=medio
        return (bajo+alto)/2
    
    #calcular ln
    @staticmethod
    def ln(a, tol=1e-6):
        if a<=0:
            raise ValueError("El argumento debe ser positivo")
        e=2.718281828459045
        bajo, alto=0, 100
        while alto-bajo>tol:
            medio=(bajo+alto)/2
            if e**medio<a:
                bajo=medio
            else:
                alto=medio
        return (bajo+alto)/2
    
    #calcular factorial
    @staticmethod
    def factorial(x):
        if x<0:
            raise ValueError("No se aceptan numeros negativos")
        elif x==0 or x==1:
            return 1
        else:
            return x*Aritmetica.factorial(x-1)
        
    #redondear un valor decimal
    @staticmethod
    def redondear(x, dec=0):
        factor=10**dec
        if x>0:
            return int(x*factor+0.5)/factor
        else:
            return int(x*factor-0.5)/factor
        
    #truncar un decimal
    @staticmethod
    def truncar(x, dec=0):
        factor=10**dec
        return int(x*factor)/factor
    
    #conversion
    @staticmethod
    def _grados_a_radianes(x):
        pi=3.141592653589793
        return x*pi/180
    
    #calcular seno
    @staticmethod
    def seno(x, modo='rad', n=10):
        if modo=='deg':
            x=Aritmetica._grados_a_radianes(x)
        elif modo!='rad':
            raise ValueError("Modo no valido")
        
        sin=0
        for k in range(n):
            sin+=((-1)**k)*(x**(2*k+1))/Aritmetica.factorial(2*k+1)
        return sin
    
    #calcular coseno
    @staticmethod
    def coseno(x, modo='rad', n=10):
        if modo=='deg':
            x=Aritmetica._grados_a_radianes(x)
        elif modo!='rad':
            raise ValueError("Modo no valido")
        
        cos=0
        for k in range(n):
            cos+=((-1)**k)*(x**(2*k))/Aritmetica.factorial(2*k)
        return cos
    
    #calcular tangente
    @staticmethod
    def tangente(x, modo='rad', n=10):
        if modo=='deg':
            x=Aritmetica._grados_a_radianes(x)
        elif modo!='rad':
            raise ValueError("Modo no valido")
        
        sin=Aritmetica.seno(x)
        cos=Aritmetica.coseno(x)
        if cos<0:
            raise ValueError("tangente indefinida")
        return sin/cos
            
