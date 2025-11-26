## proyecto final

# Intérprete DSL para Machine Learning

Este proyecto implementa un **Lenguaje de Dominio Específico (DSL)** diseñado para facilitar tareas de Machine Learning, manipulación de datos, operaciones matemáticas y visualización, todo implementado en Python utilizando **ANTLR4**.

### 🧠 Machine Learning
Implementaciones nativas (desde cero) de algoritmos clásicos:
- **Supervisado**: 
  - Regresión Lineal Múltiple
  - Perceptrón Simple
  - Perceptrón Multicapa (MLP) con Backpropagation
- **No Supervisado**:
  - K-Means Clustering
  - DBSCAN
  - Clustering Jerárquico
- **Gestión de Modelos**: Guardado y carga de modelos, evaluación de métricas (precisión, MSE, matriz de confusión).

### Visualización
- Gráficos renderizados directamente en la consola (ASCII art):
  - Líneas, Dispersión (Scatter), Barras, Histogramas.
  - Visualización de funciones matemáticas.

### Utilidades
- **Manejo de Archivos**: Lectura/Escritura de texto plano y CSV.
- **Estructuras de Datos**: Listas, Matrices y Dataframes en memoria.
- **Matemáticas**: Operaciones matriciales y funciones aritméticas avanzadas.

### Lenguaje
- Variables con alcance global y local (`var`, `global`).
- Control de flujo: `if`, `elif`, `else`, `for`, `while`.
- Funciones definidas por el usuario (soporte para recursión).
- Tipado dinámico.

## 📋 Requisitos

- Python 3.x
- Runtime de ANTLR4 para Python:
  ```bash
  pip install antlr4-python3-runtime
  ```

## Generación del Parser

Los archivos generados por ANTLR4 no se incluyen en el repositorio. Para generarlos, necesitas tener ANTLR4 instalado y ejecutar el siguiente comando en la raíz del proyecto:

```bash
antlr4 -Dlanguage=Python3 -visitor DSL.g4
```

Esto generará los archivos `DSLLexer.py`, `DSLParser.py`, `DSLVisitor.py` y sus tokens correspondientes.

## 📂 Estructura del Proyecto

- `main.py`: Punto de entrada principal para ejecutar scripts.
- `visitor.py`: Implementación del patrón Visitor que ejecuta la lógica del DSL.
- `DSL.g4`: Gramática del lenguaje (ANTLR4).
- `librerias/`: Módulos de soporte (implementación pura en Python).
  - `RedesNeuronales.py`: Algoritmos de ML.
  - `Agrupamiento.py`: Algoritmos de clustering.
  - `Contexto.py`: Gestión de memoria y scopes.
  - `Graficos.py`: Motor de renderizado ASCII.
  - `ManejoArchivos.py`: I/O.
  - `Matrices.py` y `Aritmetica.py`: Núcleo matemático.

## ▶️ Uso

1. Crea un archivo con tu código DSL (por ejemplo, `prueba.txt`).
2. Ejecuta el intérprete:

```bash
python main.py
```

*Nota: Por defecto, `main.py` busca ejecutar `prueba.txt`.

## 💡 Ejemplos de Sintaxis

### Hola Mundo y Variables
```bash
var mensaje = "Hola DSL";
print(mensaje);

var x = 10;
var y = 20;
print(x + y);
```

### Machine Learning (K-Means)
```bash
// Definir datos
var datos = [[1,1], [1,2], [10,10], [10,11]];

// Entrenar modelo
km = kmeans(data=datos, k=2);

// Ver resultados
print(km);
```

### Funciones y Control de Flujo
```bash
function factorial(n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

for i in range(1, 6) {
    print("Factorial de " + i + ": " + factorial(i));
}
```

### Gráficos
```bash
var x = [1, 2, 3, 4, 5];
var y = [1, 4, 9, 16, 25];
plot(x=x, y=y, title="Parábola");
```
