from Aritmetica import Aritmetica

class Agrupamiento:
    """
    Implementación de algoritmos de agrupamiento (clustering)
    sin usar librerías externas
    """

    # funciones auxiliares

    @staticmethod
    def distancia_euclidiana(punto1, punto2):
        """Calcula la distancia euclidiana entre dos puntos"""
        suma = 0
        for i in range(len(punto1)):
            suma += (punto1[i] - punto2[i]) ** 2
        return Aritmetica.raiz(suma, 2)
    
    @staticmethod
    def distancia_manhattan(punto1, punto2):
        """Calcula la distancia de Manhattan entre dos puntos"""
        suma = 0
        for i in range(len(punto1)):
            suma += abs(punto1[i] - punto2[i])
        return suma
    
    @staticmethod
    def calcular_centroide(puntos):
        """Calcula el centroide (promedio) de un conjunto de puntos"""
        if len(puntos) == 0:
            return None
        
        n_dimensiones = len(puntos[0])
        centroide = [0.0] * n_dimensiones
        
        for punto in puntos:
            for i in range(n_dimensiones):
                centroide[i] += punto[i]
        
        for i in range(n_dimensiones):
            centroide[i] /= len(puntos)
        
        return centroide
    
    # k-means
 
    @staticmethod
    def kmeans(datos, k, max_iteraciones=100, tolerancia=0.0001):
        """
        Algoritmo K-Means para agrupamiento
        datos: Lista de puntos (cada punto es una lista de valores)
        k: Número de clusters
        """
        n_muestras = len(datos)
        n_dimensiones = len(datos[0])
        
        # Inicializar centroides aleatoriamente (tomando k puntos del dataset)
        centroides = []
        paso = n_muestras // k
        for i in range(k):
            idx = (i * paso) % n_muestras
            centroides.append(datos[idx][:])  # Copia del punto
        
        asignaciones = [-1] * n_muestras
        
        for iteracion in range(max_iteraciones):
            # Asignar cada punto al centroide más cercano
            for i in range(n_muestras):
                min_distancia = float('inf')
                cluster_asignado = 0
                
                for j in range(k):
                    distancia = Agrupamiento.distancia_euclidiana(datos[i], centroides[j])
                    if distancia < min_distancia:
                        min_distancia = distancia
                        cluster_asignado = j
                
                asignaciones[i] = cluster_asignado
            
            # Calcular nuevos centroides
            nuevos_centroides = []
            convergio = True
            
            for j in range(k):
                # Obtener puntos del cluster j
                puntos_cluster = []
                for i in range(n_muestras):
                    if asignaciones[i] == j:
                        puntos_cluster.append(datos[i])
                
                if len(puntos_cluster) > 0:
                    nuevo_centroide = Agrupamiento.calcular_centroide(puntos_cluster)
                else:
                    # Si un cluster está vacío, mantener el centroide anterior
                    nuevo_centroide = centroides[j]
                
                # Verificar convergencia
                distancia_movimiento = Agrupamiento.distancia_euclidiana(centroides[j], nuevo_centroide)
                if distancia_movimiento > tolerancia:
                    convergio = False
                
                nuevos_centroides.append(nuevo_centroide)
            
            centroides = nuevos_centroides
            
            if convergio:
                print(f"K-Means convergió en iteración {iteracion + 1}")
                break
        
        return {
            "centroides": centroides,
            "asignaciones": asignaciones,
            "k": k
        }
    
    @staticmethod
    def predecir_kmeans(modelo, nuevos_datos):
        """Asigna nuevos puntos a los clusters existentes"""
        centroides = modelo["centroides"]
        k = modelo["k"]
        predicciones = []
        
        for punto in nuevos_datos:
            min_distancia = float('inf')
            cluster_asignado = 0
            
            for j in range(k):
                distancia = Agrupamiento.distancia_euclidiana(punto, centroides[j])
                if distancia < min_distancia:
                    min_distancia = distancia
                    cluster_asignado = j
            
            predicciones.append(cluster_asignado)
        
        return predicciones
    
    # dbscan
    
    @staticmethod
    def dbscan(datos, epsilon, min_puntos):
        """
        Algoritmo DBSCAN para agrupamiento basado en densidad
        epsilon: Radio de vecindad
        min_puntos: Número mínimo de puntos para formar un cluster
        """
        n_muestras = len(datos)
        etiquetas = [-1] * n_muestras  # -1 significa no visitado
        cluster_id = 0
        
        def obtener_vecinos(punto_idx):
            """Encuentra todos los vecinos dentro de epsilon"""
            vecinos = []
            for i in range(n_muestras):
                if Agrupamiento.distancia_euclidiana(datos[punto_idx], datos[i]) <= epsilon:
                    vecinos.append(i)
            return vecinos
        
        def expandir_cluster(punto_idx, vecinos, cluster_id):
            """Expande un cluster desde un punto núcleo"""
            etiquetas[punto_idx] = cluster_id
            i = 0
            while i < len(vecinos):
                vecino_idx = vecinos[i]
                
                if etiquetas[vecino_idx] == -1:  # No visitado
                    etiquetas[vecino_idx] = cluster_id
                    nuevos_vecinos = obtener_vecinos(vecino_idx)
                    
                    if len(nuevos_vecinos) >= min_puntos:
                        # Añadir nuevos vecinos a la lista
                        for nv in nuevos_vecinos:
                            if nv not in vecinos:
                                vecinos.append(nv)
                
                elif etiquetas[vecino_idx] == -2:  # Ruido
                    etiquetas[vecino_idx] = cluster_id
                
                i += 1
        
        # Procesar cada punto
        for punto_idx in range(n_muestras):
            if etiquetas[punto_idx] != -1:
                continue  # Ya fue visitado
            
            vecinos = obtener_vecinos(punto_idx)
            
            if len(vecinos) < min_puntos:
                etiquetas[punto_idx] = -2  # Marcar como ruido
            else:
                expandir_cluster(punto_idx, vecinos, cluster_id)
                cluster_id += 1
        
        return {
            "etiquetas": etiquetas,
            "n_clusters": cluster_id,
            "epsilon": epsilon,
            "min_puntos": min_puntos
        }
    
    # agrupamiento jerárquico
    
    @staticmethod
    def agrupamiento_jerarquico(datos, n_clusters, metodo='simple'):
        """
        Agrupamiento jerárquico aglomerativo
        metodo: 'simple' (single linkage), 'completo' (complete linkage), 'promedio' (average linkage)
        """
        n_muestras = len(datos)
        
        # Inicializar: cada punto es su propio cluster
        clusters = [[i] for i in range(n_muestras)]
        
        # Matriz de distancias (solo calculamos triángulo superior)
        distancias = {}
        for i in range(n_muestras):
            for j in range(i + 1, n_muestras):
                dist = Agrupamiento.distancia_euclidiana(datos[i], datos[j])
                distancias[(i, j)] = dist
        
        def calcular_distancia_clusters(cluster1, cluster2):
            """Calcula distancia entre dos clusters"""
            distancias_pares = []
            for i in cluster1:
                for j in cluster2:
                    if i < j:
                        distancias_pares.append(distancias.get((i, j), float('inf')))
                    elif i > j:
                        distancias_pares.append(distancias.get((j, i), float('inf')))
            
            if len(distancias_pares) == 0:
                return float('inf')
            
            if metodo == 'simple':
                return min(distancias_pares)
            elif metodo == 'completo':
                return max(distancias_pares)
            else:  # promedio
                return sum(distancias_pares) / len(distancias_pares)
        
        # Aglomerar hasta tener n_clusters
        while len(clusters) > n_clusters:
            # Encontrar par de clusters más cercanos
            min_distancia = float('inf')
            par_mas_cercano = (0, 1)
            
            for i in range(len(clusters)):
                for j in range(i + 1, len(clusters)):
                    dist = calcular_distancia_clusters(clusters[i], clusters[j])
                    if dist < min_distancia:
                        min_distancia = dist
                        par_mas_cercano = (i, j)
            
            # Fusionar clusters
            i, j = par_mas_cercano
            nuevo_cluster = clusters[i] + clusters[j]
            
            # Eliminar clusters antiguos y añadir nuevo
            clusters_nuevos = []
            for idx in range(len(clusters)):
                if idx != i and idx != j:
                    clusters_nuevos.append(clusters[idx])
            clusters_nuevos.append(nuevo_cluster)
            clusters = clusters_nuevos
        
        # Crear asignaciones
        asignaciones = [-1] * n_muestras
        for cluster_id, cluster in enumerate(clusters):
            for punto_idx in cluster:
                asignaciones[punto_idx] = cluster_id
        
        return {
            "asignaciones": asignaciones,
            "n_clusters": n_clusters,
            "clusters": clusters
        }

    # métricas de evaluación

    @staticmethod
    def inercia(datos, modelo_kmeans):
        """Calcula la inercia (suma de distancias cuadradas a centroides)"""
        centroides = modelo_kmeans["centroides"]
        asignaciones = modelo_kmeans["asignaciones"]
        
        inercia_total = 0
        for i in range(len(datos)):
            cluster = asignaciones[i]
            distancia = Agrupamiento.distancia_euclidiana(datos[i], centroides[cluster])
            inercia_total += distancia ** 2
        
        return inercia_total
    
    @staticmethod
    def coeficiente_silueta(datos, asignaciones):
        """
        Calcula el coeficiente de silueta promedio
        Valores cercanos a 1 indican buen agrupamiento
        """
        n_muestras = len(datos)
        siluetas = []
        
        # Identificar clusters únicos
        clusters_unicos = []
        for asig in asignaciones:
            if asig not in clusters_unicos and asig >= 0:
                clusters_unicos.append(asig)
        
        for i in range(n_muestras):
            if asignaciones[i] < 0:  # Punto de ruido
                continue
            
            cluster_actual = asignaciones[i]
            
            # Calcular a(i): distancia promedio a puntos del mismo cluster
            puntos_mismo_cluster = []
            for j in range(n_muestras):
                if i != j and asignaciones[j] == cluster_actual:
                    puntos_mismo_cluster.append(j)
            
            if len(puntos_mismo_cluster) == 0:
                continue
            
            a_i = 0
            for j in puntos_mismo_cluster:
                a_i += Agrupamiento.distancia_euclidiana(datos[i], datos[j])
            a_i /= len(puntos_mismo_cluster)
            
            # Calcular b(i): menor distancia promedio a puntos de otros clusters
            b_i = float('inf')
            for otro_cluster in clusters_unicos:
                if otro_cluster == cluster_actual:
                    continue
                
                puntos_otro_cluster = []
                for j in range(n_muestras):
                    if asignaciones[j] == otro_cluster:
                        puntos_otro_cluster.append(j)
                
                if len(puntos_otro_cluster) == 0:
                    continue
                
                dist_promedio = 0
                for j in puntos_otro_cluster:
                    dist_promedio += Agrupamiento.distancia_euclidiana(datos[i], datos[j])
                dist_promedio /= len(puntos_otro_cluster)
                
                if dist_promedio < b_i:
                    b_i = dist_promedio
            
            # Calcular silueta para el punto i
            if b_i == float('inf'):
                continue
            
            s_i = (b_i - a_i) / max(a_i, b_i)
            siluetas.append(s_i)
        
        if len(siluetas) == 0:
            return 0
        
        return sum(siluetas) / len(siluetas)