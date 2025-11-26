class Graficos:

    @staticmethod
    def _min(lista):
        m = lista[0]
        for x in lista:
            if x < m:
                m = x
        return m

    @staticmethod
    def _max(lista):
        m = lista[0]
        for x in lista:
            if x > m:
                m = x
        return m

    @staticmethod
    def _round(x, n=0):
        factor = 10 ** n
        if x >= 0:
            return int(x * factor + 0.5) / factor
        else:
            return int(x * factor - 0.5) / factor

    @staticmethod
    def _linspace(a, b, n):
        paso = (b - a) / (n - 1)
        return [a + i * paso for i in range(n)]

    @staticmethod
    def _transformar_coordenadas(x, y, xmin, xmax, ymin, ymax, ancho, alto):
        """Transforma coordenadas reales a posiciones en el lienzo ASCII"""
        if xmax - xmin == 0:
            xn = ancho // 2
        else:
            xn = int((x - xmin) / (xmax - xmin) * (ancho - 1))
        
        if ymax - ymin == 0:
            yn = alto // 2
        else:
            yn = int((y - ymin) / (ymax - ymin) * (alto - 1))
        
        return xn, yn

    @staticmethod
    def _dibujar_linea(lienzo, x1, y1, x2, y2, alto, caracter='*'):
        """Dibuja una línea entre dos puntos usando el algoritmo de Bresenham"""
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        
        err = dx - dy
        
        x, y = x1, y1
        
        while True:
            if 0 <= x < len(lienzo[0]) and 0 <= alto - y - 1 < alto:
                lienzo[alto - y - 1][x] = caracter
            
            if x == x2 and y == y2:
                break
            
            e2 = 2 * err
            
            if e2 > -dy:
                err -= dy
                x += sx
            
            if e2 < dx:
                err += dx
                y += sy

    @staticmethod
    def plot(x, y, ancho=80, alto=25, titulo="Gráfico de línea", mostrar_ejes=True):
        """Dibuja una gráfica de línea ASCII con puntos conectados"""
        if len(x) != len(y):
            raise ValueError("Las listas x e y deben tener la misma longitud")
        
        xmin, xmax = Graficos._min(x), Graficos._max(x)
        ymin, ymax = Graficos._min(y), Graficos._max(y)
        
        # Crear lienzo
        lienzo = [[" " for _ in range(ancho)] for _ in range(alto)]
        
        # Dibujar ejes si se solicita
        if mostrar_ejes:
            # Eje X (horizontal) en y=0 si está en rango
            if ymin <= 0 <= ymax:
                _, y0 = Graficos._transformar_coordenadas(xmin, 0, xmin, xmax, ymin, ymax, ancho, alto)
                for i in range(ancho):
                    lienzo[alto - y0 - 1][i] = "-"
            
            # Eje Y (vertical) en x=0 si está en rango
            if xmin <= 0 <= xmax:
                x0, _ = Graficos._transformar_coordenadas(0, ymin, xmin, xmax, ymin, ymax, ancho, alto)
                for i in range(alto):
                    lienzo[i][x0] = "|"
        
        # Transformar y dibujar líneas entre puntos consecutivos
        puntos = []
        for i in range(len(x)):
            xn, yn = Graficos._transformar_coordenadas(x[i], y[i], xmin, xmax, ymin, ymax, ancho, alto)
            puntos.append((xn, yn))
        
        # Conectar puntos con líneas
        for i in range(len(puntos) - 1):
            Graficos._dibujar_linea(lienzo, puntos[i][0], puntos[i][1], 
                                   puntos[i+1][0], puntos[i+1][1], alto, '*')
        
        # Marcar los puntos de datos originales
        for (xn, yn) in puntos:
            if 0 <= xn < ancho and 0 <= yn < alto:
                lienzo[alto - yn - 1][xn] = "●"
        
        # Imprimir resultado
        print("\n" + "="*ancho)
        print(titulo.center(ancho))
        print("="*ancho)
        for fila in lienzo:
            print("".join(fila))
        print("-"*ancho)
        print(f"x ∈ [{Graficos._round(xmin,2)}, {Graficos._round(xmax,2)}]  " +
              f"y ∈ [{Graficos._round(ymin,2)}, {Graficos._round(ymax,2)}]")
        print()

    @staticmethod
    def scatter(x, y, ancho=80, alto=25, titulo="Dispersión", caracter="*"):
        """Gráfico de dispersión ASCII"""
        if len(x) != len(y):
            raise ValueError("Las listas x e y deben tener la misma longitud")
        
        xmin, xmax = Graficos._min(x), Graficos._max(x)
        ymin, ymax = Graficos._min(y), Graficos._max(y)
        
        # Crear lienzo
        lienzo = [[" " for _ in range(ancho)] for _ in range(alto)]
        
        # Dibujar puntos
        for i in range(len(x)):
            xn, yn = Graficos._transformar_coordenadas(x[i], y[i], xmin, xmax, ymin, ymax, ancho, alto)
            if 0 <= xn < ancho and 0 <= yn < alto:
                lienzo[alto - yn - 1][xn] = caracter
        
        # Imprimir resultado
        print("\n" + "="*ancho)
        print(titulo.center(ancho))
        print("="*ancho)
        for fila in lienzo:
            print("".join(fila))
        print("-"*ancho)
        print(f"x ∈ [{Graficos._round(xmin,2)}, {Graficos._round(xmax,2)}]  " +
              f"y ∈ [{Graficos._round(ymin,2)}, {Graficos._round(ymax,2)}]")
        print()

    @staticmethod
    def bar(etiquetas, valores, ancho=60, titulo="Gráfico de barras"):
        """Gráfico de barras horizontal en ASCII mejorado"""
        if len(etiquetas) != len(valores):
            raise ValueError("Las listas deben tener la misma longitud")
        
        vmax = Graficos._max(valores)
        vmin = Graficos._min(valores)
        
        # Si hay valores negativos, ajustar escala
        if vmin < 0:
            escala = ancho / (vmax - vmin)
            punto_cero = int(-vmin * escala)
        else:
            escala = ancho / vmax
            punto_cero = 0
        
        # Encontrar ancho máximo de etiqueta
        max_etiqueta = 0
        for etiq in etiquetas:
            if len(str(etiq)) > max_etiqueta:
                max_etiqueta = len(str(etiq))
        
        print("\n" + "="*(ancho + max_etiqueta + 15))
        print(titulo.center(ancho + max_etiqueta + 15))
        print("="*(ancho + max_etiqueta + 15))
        
        for i in range(len(etiquetas)):
            # Calcular longitud de barra
            if vmin < 0:
                barras = int((valores[i] - vmin) * escala)
            else:
                barras = int(valores[i] * escala)
            
            # Formatear etiqueta
            etiq_format = str(etiquetas[i]).rjust(max_etiqueta)
            
            # Dibujar barra
            if vmin < 0:
                # Con valores negativos
                if valores[i] >= 0:
                    espacios = " " * punto_cero
                    barra = "█" * (barras - punto_cero)
                    print(f"{etiq_format} |{espacios}{barra} {Graficos._round(valores[i],1)}")
                else:
                    barra = "█" * (punto_cero - barras)
                    espacios = " " * (barras)
                    print(f"{etiq_format} |{espacios}{barra}| {Graficos._round(valores[i],1)}")
            else:
                # Solo valores positivos
                barra = "█" * barras
                print(f"{etiq_format} | {barra} {Graficos._round(valores[i],1)}")
        
        print("-"*(ancho + max_etiqueta + 15))
        print()

    @staticmethod
    def regresion_lineal(x, y, titulo="Regresión Lineal", ancho=80, alto=25):
        """Dibuja regresión lineal con línea de ajuste"""
        if len(x) != len(y):
            raise ValueError("Las listas x e y deben tener la misma longitud")
        
        n = len(x)
        media_x = sum(x) / n
        media_y = sum(y) / n
        
        # Calcular pendiente y ordenada
        numerador = sum((x[i] - media_x) * (y[i] - media_y) for i in range(n))
        denominador = sum((x[i] - media_x) ** 2 for i in range(n))
        
        if denominador == 0:
            raise ValueError("No se puede calcular regresión")
        
        m = numerador / denominador
        b = media_y - m * media_x
        
        xmin, xmax = Graficos._min(x), Graficos._max(x)
        ymin, ymax = Graficos._min(y), Graficos._max(y)
        
        # Crear lienzo
        lienzo = [[" " for _ in range(ancho)] for _ in range(alto)]
        
        # Dibujar línea de regresión
        x_linea = []
        y_linea = []
        for i in range(ancho):
            x_real = xmin + i / (ancho - 1) * (xmax - xmin)
            y_real = m * x_real + b
            x_linea.append(x_real)
            y_linea.append(y_real)
        
        # Dibujar la línea de regresión
        for i in range(len(x_linea) - 1):
            xn1, yn1 = Graficos._transformar_coordenadas(x_linea[i], y_linea[i], 
                                                         xmin, xmax, ymin, ymax, ancho, alto)
            xn2, yn2 = Graficos._transformar_coordenadas(x_linea[i+1], y_linea[i+1], 
                                                         xmin, xmax, ymin, ymax, ancho, alto)
            Graficos._dibujar_linea(lienzo, xn1, yn1, xn2, yn2, alto, '-')
        
        # Dibujar puntos de datos originales
        for i in range(n):
            xn, yn = Graficos._transformar_coordenadas(x[i], y[i], xmin, xmax, ymin, ymax, ancho, alto)
            if 0 <= xn < ancho and 0 <= yn < alto:
                lienzo[alto - yn - 1][xn] = "●"
        
        # Imprimir resultado
        print("\n" + "="*ancho)
        print(titulo.center(ancho))
        print("="*ancho)
        for fila in lienzo:
            print("".join(fila))
        print("-"*ancho)
        print(f"Ecuación: y = {Graficos._round(m,3)}x + {Graficos._round(b,3)}")
        print(f"x ∈ [{Graficos._round(xmin,2)}, {Graficos._round(xmax,2)}]  " +
              f"y ∈ [{Graficos._round(ymin,2)}, {Graficos._round(ymax,2)}]")
        print()

    @staticmethod
    def histograma(datos, bins=10, ancho=60, titulo="Histograma"):
        """Crea un histograma de los datos"""
        dmin = Graficos._min(datos)
        dmax = Graficos._max(datos)
        
        # Crear bins
        rango = dmax - dmin
        ancho_bin = rango / bins
        
        # Contar frecuencias
        frecuencias = [0] * bins
        etiquetas = []
        
        for dato in datos:
            bin_idx = int((dato - dmin) / ancho_bin)
            if bin_idx >= bins:
                bin_idx = bins - 1
            frecuencias[bin_idx] += 1
        
        # Crear etiquetas de rangos
        for i in range(bins):
            inicio = dmin + i * ancho_bin
            fin = inicio + ancho_bin
            etiquetas.append(f"{Graficos._round(inicio,1)}-{Graficos._round(fin,1)}")
        
        # Usar función bar para mostrar
        Graficos.bar(etiquetas, frecuencias, ancho, titulo)

    @staticmethod
    def funcion(func, x_inicio, x_fin, n_puntos=100, ancho=80, alto=25, titulo="Gráfico de función"):
        """Grafica una función matemática en un rango"""
        x = []
        y = []
        
        paso = (x_fin - x_inicio) / (n_puntos - 1)
        for i in range(n_puntos):
            xi = x_inicio + i * paso
            try:
                yi = func(xi)
                x.append(xi)
                y.append(yi)
            except:
                pass  # Ignorar puntos donde la función no está definida
        
        if len(x) == 0:
            print("Error: La función no produjo valores válidos en el rango dado")
            return
        
        Graficos.plot(x, y, ancho, alto, titulo)