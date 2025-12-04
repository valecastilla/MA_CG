from mesa import Model
from mesa.discrete_space import OrthogonalMooreGrid
from .agent import *
import json
from .estructuras import *

class Car(CellAgent):
    """
    Agent that moves following a route while avoiding collisions.
    - Rodea obstáculos fijos
    - Rebasa o espera a otros carros
    - Respeta semáforos
    """
    grafo_mapa = []
    
    def __init__(self, model, cell, ruta):
        """
        Creates a new car agent.
        Args:
            model: Model reference for the agent
            cell: The initial position of the agent
            ruta: Route to follow
        """
        super().__init__(model)
        self.cell = cell
        self.estadoMovimiento = ""
        self.direccionMovimiento = ""
        self.ruta = ruta
        self.debe_eliminarse = False
        self.nodoactual = ""
        self.indexActual = 0
        self.direction = ""
        self.isNodoFinal = False
        self.nodofinal = GlobalGraph.obtener_nodo_por_id(self.ruta[len(self.ruta) - 1]["nodo_id"])
        self.direcionPatitas = ""
        self.estadoAnterior = ""
        self.xf, self.yf = self.ruta[len(self.ruta) - 1]["posicion"]
        self.x, self.y = self.cell.coordinate
        self.esperando = False
        self.intentos_rebase = 0
        self.max_intentos_rebase = 3
        
        print(f"Ruta: {self.ruta}")
        print(f"Nodo final: {self.nodofinal}")
        
        # Inicializar la primera dirección
        if len(self.ruta) > 1:
            self.direccionMovimiento = self.ruta[1]["direccion"]
    
    def obtener_vecinos(self):
        """
        Obtiene todas las celdas vecinas organizadas por dirección.
        """
        if self.cell is None:
            return None
            
        next_moves = self.cell.neighborhood
        x, y = self.cell.coordinate
        
        vecinos = {
            "izquierda": None,
            "derecha": None,
            "arriba": None,
            "abajo": None,
            "izquierdaAbajo": None,
            "derechaAbajo": None,
            "derechaArriba": None,
            "izquierdaArriba": None,
        }
        
        for vecino in next_moves:
            if vecino is None:
                continue
            
            cx, cy = vecino.coordinate
            
            # Solo considerar celdas transitables
            if not any(isinstance(a, (Road, Destination)) for a in vecino.agents):
                continue
            
            if (cx, cy) == (x - 1, y):
                vecinos["izquierda"] = vecino
            elif (cx, cy) == (x + 1, y):
                vecinos["derecha"] = vecino
            elif (cx, cy) == (x, y + 1):
                vecinos["arriba"] = vecino
            elif (cx, cy) == (x, y - 1):
                vecinos["abajo"] = vecino
            elif (cx, cy) == (x - 1, y - 1):
                vecinos["izquierdaAbajo"] = vecino
            elif (cx, cy) == (x + 1, y - 1):
                vecinos["derechaAbajo"] = vecino
            elif (cx, cy) == (x + 1, y + 1):
                vecinos["derechaArriba"] = vecino
            elif (cx, cy) == (x - 1, y + 1):
                vecinos["izquierdaArriba"] = vecino
        
        return vecinos
    
    def tiene_semaforo_rojo(self, celda):
        """
        Verifica si hay un semáforo en rojo en la celda dada.
        """
        if celda is None:
            return False
        
        semaforo = next((a for a in celda.agents if isinstance(a, Traffic_Light)), None)
        return semaforo is not None and not semaforo.state
    
    def celda_tiene_carro(self, celda):
        """
        Verifica si una celda tiene otro carro.
        """
        if celda is None:
            return False
        
        return any(isinstance(a, Car) for a in celda.agents)
    
    def celda_tiene_obstaculo_fijo(self, celda):
        """
        Verifica si una celda tiene un obstáculo fijo (no móvil).
        """
        if celda is None:
            return True
        
        return any(isinstance(a, Obstacle) for a in celda.agents)
    
    def buscar_ruta_alternativa_obstaculos(self, direccion_principal, vecinos):
        """
        Busca una ruta alternativa para RODEAR obstáculos fijos.
        Intenta encontrar un camino libre hacia el objetivo evitando obstáculos.
        """
        x, y = self.cell.coordinate
        xf, yf = self.xf, self.yf
        
        # Determinar hacia dónde debe ir finalmente
        objetivo_x = "derecha" if x < xf else "izquierda" if x > xf else None
        objetivo_y = "arriba" if y < yf else "abajo" if y > yf else None
        
        opciones_rodear = {
            "Arriba": [
                ("derecha", ["Derecha", "Arriba"]),  # Ir por la derecha primero
                ("izquierda", ["Izquierda", "Arriba"])  # Ir por la izquierda
            ],
            "Abajo": [
                ("derecha", ["Derecha", "Abajo"]),
                ("izquierda", ["Izquierda", "Abajo"])
            ],
            "Derecha": [
                ("arriba", ["Arriba", "Derecha"]),
                ("abajo", ["Abajo", "Derecha"])
            ],
            "Izquierda": [
                ("arriba", ["Arriba", "Izquierda"]),
                ("abajo", ["Abajo", "Izquierda"])
            ]
        }
        
        if direccion_principal not in opciones_rodear:
            return None
        
        for lateral, direcciones_permitidas in opciones_rodear[direccion_principal]:
            celda_lateral = vecinos.get(lateral)
            
            if celda_lateral is None:
                continue
            
            # Verificar que esté libre de obstáculos fijos Y carros
            if self.celda_tiene_obstaculo_fijo(celda_lateral) or self.celda_tiene_carro(celda_lateral):
                continue
            
            # Verificar que sea un camino válido (Road)
            road_lateral = next((a for a in celda_lateral.agents if isinstance(a, Road)), None)
            if road_lateral and road_lateral.direction in direcciones_permitidas:
                print(f"🔀 Rodeando obstáculo por {lateral}")
                return lateral
        
        return None
    
    def intentar_rebasar_carro(self, direccion_principal, vecinos):
        """
        Intenta REBASAR un carro por las diagonales.
        Solo se usa cuando hay otro CARRO bloqueando.
        """
        if self.intentos_rebase >= self.max_intentos_rebase:
            print(f"⚠️ Máximo de intentos de rebase alcanzado ({self.max_intentos_rebase})")
            return None
        
        opciones_rebase = {
            "Arriba": [
                ("derechaArriba", "derecha"),
                ("izquierdaArriba", "izquierda")
            ],
            "Abajo": [
                ("derechaAbajo", "derecha"),
                ("izquierdaAbajo", "izquierda")
            ],
            "Derecha": [
                ("derechaArriba", "arriba"),
                ("derechaAbajo", "abajo")
            ],
            "Izquierda": [
                ("izquierdaArriba", "arriba"),
                ("izquierdaAbajo", "abajo")
            ]
        }
        
        if direccion_principal not in opciones_rebase:
            return None
        
        for diagonal, lateral in opciones_rebase[direccion_principal]:
            celda_diagonal = vecinos.get(diagonal)
            celda_lateral = vecinos.get(lateral)
            
            if celda_diagonal is None or celda_lateral is None:
                continue
            
            # Verificar que ambas celdas estén libres (sin carros ni obstáculos)
            if (self.celda_tiene_carro(celda_diagonal) or 
                self.celda_tiene_obstaculo_fijo(celda_diagonal) or
                self.celda_tiene_carro(celda_lateral) or 
                self.celda_tiene_obstaculo_fijo(celda_lateral)):
                continue
            
            # Verificar que sean Roads válidos
            road_diagonal = next((a for a in celda_diagonal.agents if isinstance(a, Road)), None)
            road_lateral = next((a for a in celda_lateral.agents if isinstance(a, Road)), None)
            
            if road_diagonal and road_lateral:
                print(f"🏎️ Rebasando carro por {diagonal}")
                self.intentos_rebase += 1
                return diagonal
        
        return None
    
    def seguirRuta(self):
        """
        Lógica principal para seguir la ruta evitando colisiones.
        """
        if self.cell is None:
            print("Error: self.cell es None")
            return
        
        vecinos = self.obtener_vecinos()
        if vecinos is None:
            return
        
        x, y = self.cell.coordinate
        xf, yf = self.xf, self.yf
        
        # Verificar si llegó a destino
        if x == xf and y == yf:
            print(f"🎯 Carro llegó a destino en posición ({xf}, {yf})")
            self.debe_eliminarse = True
            return
        
        # Actualizar dirección en intersecciones
        intersection = next((a for a in self.cell.agents if isinstance(a, Intersection)), None)
        
        if intersection is not None:
            print(f"🔀 En intersección: {intersection.idNodoInter}")
            for index, nodo in enumerate(self.ruta):
                if nodo.get("nodo_id") == intersection.idNodoInter:
                    self.nodoactual, self.indexActual = nodo, index
                    break
            
            if self.indexActual + 1 < len(self.ruta):
                siguiente_nodo = self.ruta[self.indexActual + 1]
                print(f"➡️ Siguiente dirección: {siguiente_nodo['direccion']}")
                
                if siguiente_nodo["nodo_id"] == self.nodofinal.id:
                    self.isNodoFinal = True
                    print("🏁 Llegó al nodo final")
                
                self.direccionMovimiento = siguiente_nodo["direccion"]
                self.intentos_rebase = 0  # Reset intentos al cambiar de nodo
            else:
                print("🏁 Llegó al final de la ruta")
                self.isNodoFinal = True
                return
        
        # Mapeo de direcciones a celdas
        mapa_direcciones = {
            "Arriba": vecinos["arriba"],
            "Abajo": vecinos["abajo"],
            "Derecha": vecinos["derecha"],
            "Izquierda": vecinos["izquierda"],
            "derechaArriba": vecinos["derechaArriba"],
            "izquierdaArriba": vecinos["izquierdaArriba"],
            "derechaAbajo": vecinos["derechaAbajo"],
            "izquierdaAbajo": vecinos["izquierdaAbajo"]
        }
        
        # Ajuste fino en nodo final
        if self.isNodoFinal:
            if self.direccionMovimiento in ["Arriba", "Abajo"] and y == yf:
                self.direccionMovimiento = "Derecha" if x < xf else "Izquierda"
            elif self.direccionMovimiento in ["Derecha", "Izquierda"] and x == xf:
                self.direccionMovimiento = "Arriba" if y < yf else "Abajo"
        
        # Obtener celda destino
        celda_destino = mapa_direcciones.get(self.direccionMovimiento)
        
        if celda_destino is None:
            print(f"⚠️ No hay celda en dirección {self.direccionMovimiento}")
            return
        
        # Verificar semáforo rojo
        if self.tiene_semaforo_rojo(celda_destino):
            print("🚦 Detenido por semáforo en rojo")
            self.esperando = True
            return
        
        # CASO 1: Obstáculo fijo detectado → RODEAR
        if self.celda_tiene_obstaculo_fijo(celda_destino):
            print(f"🚧 Obstáculo fijo detectado en {self.direccionMovimiento}")
            
            # Buscar ruta alternativa para rodear
            direccion_rodear = self.buscar_ruta_alternativa_obstaculos(self.direccionMovimiento, vecinos)
            
            if direccion_rodear:
                celda_destino = mapa_direcciones.get(direccion_rodear)
                if celda_destino and not self.celda_tiene_carro(celda_destino):
                    self.esperando = False
                    self.move_to(celda_destino)
                    return
            
            # Si no puede rodear, detenerse
            print("🛑 No se puede rodear el obstáculo, esperando...")
            self.esperando = True
            return
        
        # CASO 2: Carro detectado → INTENTAR REBASAR o ESPERAR
        if self.celda_tiene_carro(celda_destino):
            print(f"🚗 Carro detectado en {self.direccionMovimiento}")
            
            # Intentar rebasar
            direccion_rebase = self.intentar_rebasar_carro(self.direccionMovimiento, vecinos)
            
            if direccion_rebase:
                celda_destino = mapa_direcciones.get(direccion_rebase)
                if celda_destino:
                    self.esperando = False
                    self.move_to(celda_destino)
                    return
            
            # Si no puede rebasar, ESPERAR
            print("⏸️ Esperando a que el carro avance")
            self.esperando = True
            return
        
        # Movimiento normal
        self.esperando = False
        self.intentos_rebase = 0  # Reset cuando se mueve exitosamente
        self.move_to(celda_destino)
        print(f"✅ Movimiento exitoso a {self.direccionMovimiento}")
    
    def step(self):
        """
        Ejecuta un paso de la simulación.
        """
        if self.debe_eliminarse:
            try:
                # Remover de la celda
                if self.cell is not None:
                    self.cell.remove_agent(self)
                
                # Remover del modelo
                if self in self.model.agents:
                    self.model.agents.remove(self)
                
                print("✅ Carro eliminado correctamente")
                return
            except Exception as e:
                print(f"⚠️ Error al eliminar carro: {e}")
                return
        
        self.seguirRuta()