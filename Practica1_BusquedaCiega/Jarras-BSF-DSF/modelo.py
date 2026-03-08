class ProblemaJarras:
    """
    Modela las reglas, los estados (cuánta agua hay) y
    las transiciones (qué movimientos son válidos) del acertijo de las jarras.
    """

    # ============================================ Parte 1 =====================================================
    # ====================================== Las Reglas del juego ==============================================

    # El constructor define los límites del problema.
    # Recibe la capacidad máxima de la Jarra 1 (cap1), la Jarra 2 (cap2)
    # y la meta que queremos alcanzar (objetivo).

    def __init__(self, cap1, cap2, objetivo):
        self.cap1 = cap1
        self.cap2 = cap2
        self.objetivo = objetivo

        # El estado siempre será una tupla (agua_en_jarra_1, agua_en_jarra_2).

        self.estado_inicial = (0, 0) # Al inicio del acertijo, ambas jarras están vacías.

    def es_posible(self):

        # Validación de solución para descartar imposibles.

        # Si se quieren medir 5 litros, pero las jarras son de 2 y de 3 litros. Es imposible
        # La cantidad objetivo NUNCA puede ser mayor que la jarra más grande que se tiene.

        return self.objetivo <= max(self.cap1, self.cap2)

    # ================================================ Parte 2 =================================================
    # ========================================= La Condición de Meta ============================================

    def es_objetivo(self, estado):

        # Verifica si el estado actual cumple con el objetivo.
        # El BuscadorAlgoritmos comprueba a cada estado que saque de la pila (frontera).

        # El estado es una tupla: estado[0] es la Jarra 1, estado[1] es la Jarra 2.
        # Si cualquiera de las dos jarras tiene exactamente la cantidad de agua objetiva, termina.

        return estado[0] == self.objetivo or estado[1] == self.objetivo

    # ============================================ Parte 3 ============================================
    # ========================================== Transiciones =========================================

    def obtener_sucesores(self, estado):

        #Genera y devuelve el "Árbol de Decisiones".
        #Según el estado actual de las jarras analiza qué movimientos se pueden hacer

        # Desempaquetamos la tupla
        # 'x' es el agua actual en la Jarra 1.
        # 'y' es el agua actual en la Jarra 2.

        x, y = estado

        # Aquí guardaremos todos los "futuros posibles" (estados resultantes)
        sucesores = []

        # ------------------------------ MOVIMIENTOS BÁSICOS ------------------------------------------
        # ----------------------------- Llenar y Vaciar a tope ----------------------------------------

        # 1. Llenar Jarra 1 desde la llave de agua.
        # Solo tiene sentido si la jarra no está ya llena.
        # Resultado: La Jarra 1 pasa a su tope (cap1), la Jarra 2 se queda como estaba (y).
        if x < self.cap1:
            sucesores.append((self.cap1, y))

        # 2. Llenar Jarra 2 desde la llave de agua.
        if y < self.cap2:
            sucesores.append((x, self.cap2))

        # 3. Vaciar Jarra 1.
        # Solo tiene sentido si tiene algo de agua (x > 0).
        # Resultado: La Jarra 1 queda en 0, la Jarra 2 intacta.
        if x > 0:
            sucesores.append((0, y))

        # 4. Vaciar Jarra 2 .
        if y > 0:
            sucesores.append((x, 0))

        # --------------------------- MOVIMIENTOS COMPLEJOS --------------------------------------
        # ----------------------------- Trasvasar el agua ----------------------------------------

        # 5. Verter agua de la Jarra 1 hacia la Jarra 2
        # Solo se puede si hay agua en la 1 (x > 0) Y si le cabe agua a la 2 (y < cap2).
        if x > 0 and y < self.cap2:

            # Solo puedo pasar lo que tengo en la Jarra 1 (x)
            # O el espacio vacío que le queda a la Jarra 2 (cap2 - y).
            # Se detiene cuando pase el MENOR de esos dos valores (min).

            cantidad = min(x, self.cap2 - y)

            # Al sucesor le restamos el agua a la que donó (x - cantidad)
            # y se la sumamos a la que recibió (y + cantidad).

            sucesores.append((x - cantidad, y + cantidad))

        # 6. Verter agua de la Jarra 2 hacia la Jarra 1
        # La misma lógica, pero a la inversa.
        if y > 0 and x < self.cap1:
            cantidad = min(y, self.cap1 - x)
            sucesores.append((x + cantidad, y - cantidad))

        # Finalmente, le devolvemos la lista completa de futuros posibles al BuscadorAlgoritmos
        # para que los añada a su frontera (si es que no los ha visitado antes).
        return sucesores
