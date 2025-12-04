from mesa import Model
from mesa.discrete_space import OrthogonalMooreGrid
from .agent import *
import json
from .estructuras import *

class Car(CellAgent):

    grafo_mapa = []
    
    def __init__(self, model, cell, ruta):
       
       
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
        self.direcionPatitas = "Derecha"
        self.estadoAnterior = ""
        self.xf, self.yf = self.ruta[len(self.ruta) - 1]["posicion"]
        self.x, self.y = self.cell.coordinate
        self.esperando = False
        self.intentos_rebase = 0
        self.max_intentos_rebase = 3
        
        #print(f"Ruta: {self.ruta}")
        #print(f"Nodo final: {self.nodofinal}")
        
        # Inicializar la primera dirección de la ruta
        if len(self.ruta) > 1:
            self.direccionMovimiento = self.ruta[1]["direccion"]
    
    def obtener_vecinos(self):
        
        #Obtiene todas las celdas vecinas organizadas por dirección.
        
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
            
            # Solo considerar celdas que se peuden mover
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
        
        if celda is None:
            return False
        
        semaforo = next((a for a in celda.agents if isinstance(a, Traffic_Light)), None)
        return semaforo is not None and not semaforo.state
    
    def celda_tiene_carro(self, celda):
        
        if celda is None:
            return False
        
        return any(isinstance(a, Car) for a in celda.agents)
    
    def celda_tiene_obstaculo_fijo(self, celda):
       
        if celda is None:
            return True
        
        return any(isinstance(a, Obstacle) for a in celda.agents)
    
    def buscar_ruta_alternativa_obstaculos(self, direccion_principal, vecinos):
        #busca alternativa si ecuentra obstaculo
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
            
            if self.celda_tiene_obstaculo_fijo(celda_lateral) or self.celda_tiene_carro(celda_lateral):
                continue
            
            # Verificar que sea un camino
            road_lateral = next((a for a in celda_lateral.agents if isinstance(a, Road)), None)
            if road_lateral and road_lateral.direction in direcciones_permitidas:
            
                return lateral
        
        return None
    
    def intentar_rebasar_carro(self, direccion_principal, vecinos):
        
        if self.intentos_rebase >= self.max_intentos_rebase:
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
            
            # Verificar que ambas celdas esten libres 
            if (self.celda_tiene_carro(celda_diagonal) or 
                self.celda_tiene_obstaculo_fijo(celda_diagonal) or
                self.celda_tiene_carro(celda_lateral) or 
                self.celda_tiene_obstaculo_fijo(celda_lateral)):
                continue
            
            # Verificar que sean Roads vlidos
            road_diagonal = next((a for a in celda_diagonal.agents if isinstance(a, Road)), None)
            road_lateral = next((a for a in celda_lateral.agents if isinstance(a, Road)), None)
            
            if road_diagonal and road_lateral:
                
                self.intentos_rebase += 1
                return diagonal
        
        return None
    
    def seguirRuta(self):
        
        if self.cell is None:
            return
        roadPatitas= next((a for a in self.cell.agents if isinstance(a, Road)), None)

        if roadPatitas !=None:
            self.direcionPatitas = roadPatitas.direction
        
        vecinos = self.obtener_vecinos()
        if vecinos is None:
            return
        
        x, y = self.cell.coordinate
        xf, yf = self.xf, self.yf
        
        # Verificar si llegó a destino
        if x == xf and y == yf:
            DatosGlobales.restarHuevos()
            self.debe_eliminarse = True
            return
        
        # Actualizar dirección en intersecciones
        intersection = next((a for a in self.cell.agents if isinstance(a, Intersection)), None)
        
        if intersection is not None:
            for index, nodo in enumerate(self.ruta):
                if nodo.get("nodo_id") == intersection.idNodoInter:
                    self.nodoactual, self.indexActual = nodo, index
                    break
            
            if self.indexActual + 1 < len(self.ruta):
                siguiente_nodo = self.ruta[self.indexActual + 1]
                
                if siguiente_nodo["nodo_id"] == self.nodofinal.id:
                    self.isNodoFinal = True
                
                self.direccionMovimiento = siguiente_nodo["direccion"]
                self.intentos_rebase = 0 
            else:
                #ultimo tramo de la ruta
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
        
        if self.isNodoFinal:
            if self.direccionMovimiento in ["Arriba", "Abajo"] and y == yf:
                self.direccionMovimiento = "Derecha" if x < xf else "Izquierda"
            elif self.direccionMovimiento in ["Derecha", "Izquierda"] and x == xf:
                self.direccionMovimiento = "Arriba" if y < yf else "Abajo"
        
        # Obtener celda destino
        celda_destino = mapa_direcciones.get(self.direccionMovimiento)
        
        if celda_destino is None:
            return
        
        # Verificar semáforo rojo
        if self.tiene_semaforo_rojo(celda_destino):
            self.esperando = True
            return
        
        # Rodear
        if self.celda_tiene_obstaculo_fijo(celda_destino):
            
            # Buscar ruta alternativa para rodear
            direccion_rodear = self.buscar_ruta_alternativa_obstaculos(self.direccionMovimiento, vecinos)
            
            if direccion_rodear:
                celda_destino = mapa_direcciones.get(direccion_rodear)
                if celda_destino and not self.celda_tiene_carro(celda_destino):
                    self.esperando = False
                    self.move_to(celda_destino)
                    return
            
            # detener
            self.esperando = True
            return
        
        # CARRO DETECTADO
        if self.celda_tiene_carro(celda_destino):
            
            # Intentar rebasar
            direccion_rebase = self.intentar_rebasar_carro(self.direccionMovimiento, vecinos)
            
            if direccion_rebase:
                celda_destino = mapa_direcciones.get(direccion_rebase)
                if celda_destino:
                    self.esperando = False
                    self.move_to(celda_destino)
                    return
            
            
            self.esperando = True
            return
        
        # Movimiento normal
        self.esperando = False
        self.intentos_rebase = 0  # Reset cuando se mueve exitosamente
        self.move_to(celda_destino)
    
    def step(self):

        if self.debe_eliminarse:
            try:
                # Remover de la celda
                if self.cell is not None:
                    self.cell.remove_agent(self)
                
                # Remover del modelo
                if self in self.model.agents:
                    self.model.agents.remove(self)
                
                return
            except Exception as e:
                return
        
        self.seguirRuta()