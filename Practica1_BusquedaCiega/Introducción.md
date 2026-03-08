En esta sección se exploraran los conceptos de algoritmos de búsqueda ciega.
Específicamente la búsqueda en profundidad (DFS) y la búsqueda en amplitud (BFS).

Los siguientes códigos implementan algoritmos DFS y BFS para resuelver problemas usando estos algoritmos.
Miden y analizan los tiempos de ejecución y el consumo de memoria y se presentan soluciones en una interfaz gráfica fácil de usar.

Entendiendo los Algoritmos:

1. Búsqueda en profundidad (DFS): Este algoritmo explora en la medida de lo posible a lo largo de cada rama antes de retroceder.
																	Utiliza recursividad y pilas para resolver el problema.

2. Búsqueda en Amplitud (BFS): Este algoritmo explora todos los nodos vecinos en la profundidad actual antes de pasar a nodos en el siguiente nivel de profundidad.
															 Utiliza una cola para realizar sus operaciones.

Problemas:

A. Laberintos

		Genera laberintos al azar de tamaños 10x10, 20x20 y 50x50.
		Implementa los algoritmos para encontrar un camino a través de cada laberinto.
		La implementación pueda manejar diferentes tamaños.

B. El problema de las jarras

		Es un problema clásico de medir agua usando dos garrafas de capacidades diferentes.
		Los algoritmos tratan de encontrar una solución a este problema. Se definin los estados y las transiciones de las jarras.

C. El problema de los 8 puzles

		Consiste en un rompecabezas con una cuadrícula de 3x3, con 8 fichas numeradas y un espacio vacío.
		El objetivo es organizar las fichas en un orden específico.
		Usando DFS y BFS para resolver el acertijo. Se representa el estado del rompecabezas y los posibles movimientos.

Medición del rendimiento
Para cada algoritmo y problema, se mide:

Tiempo de ejecución: Registrar cuánto tiempo tarda cada algoritmo en encontrar una solución.
										 Se usan funciones integradas en el lenguaje de programación para medir el tiempo.

Consumo de memoria: Analizar cuánta memoria utiliza cada algoritmo durante la ejecución.
										Se rastrea el tamaño de la pila o cola utilizada en cada problema.
