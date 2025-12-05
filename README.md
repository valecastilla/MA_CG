# Movilidad Urbana
## MultiAgents and Computer Graphics project

### Integrantes:
Valentina Castilla Melgoza  
Darío Cuauhtémoc Peña Mariano

### Aclaracion*
Darío se confundio y también termino usando la cuenta de github de la computadora que me presto, entonces algunos de mis commits estan hechos desde la cuenta de Darío y no hay manera de distinguir los commits por cuenta:(. Todos los commits que hizo cada quien solo se pueden ver por las ramas en las que trabajo cada una principalmente las ramas vale y dario.

### Objetivo
El reto consiste en proponer una solución al problema de movilidad urbana en México, mediante un enfoque que reduzca la congestión vehicular al simular de manera gráfica el tráfico, representando la salida de un sistema multi agentes.  

![traficocdmx](https://cloudfront-us-east-1.images.arcpublishing.com/elfinanciero/QBA6VNNOZJA43GEUXV6UFTX4K4.jpg)


## Instrucciones para correr el servidor local y la aplicación

### Paso 1: Iniciar el backend de Python

Iniciar la simulación:

1.  Abrir la terminal en la raiz del repositorio.
2.  Crear un ambiente virtual (solo al correr el servidor por 1ra vez):
```bash
 python3.13 -m venv .agents
```
3.  Activar el ambiente virtual:
```bash
source .agents/bin/activate
```
4.  Instalar dependencias necesarias (solo al correr el servidor por 1ra vez):
```bash
pip install -U "mesa[all]"
pip install flask flask_cors
```
5.  Ir a la carpeta trafficBase.
6.  Correr el servidor de flask.
```bash
python agents_server.py
```

- El servidor esta corriendo en (http://localhost:8585). **Checar que este corriendo en ese puerto.**

### Paso 2: Correr la aplicación en WebGL

1. Ir a la carpeta de AgentsVisualization.
2. Asegurarse de instalar las dependencias con `npm i`.
3. Correr el servidor vite:
```
npx vite
```

- Si todo esta corriendo, la simulación se debería ver en la siguiente página: http://localhost:5173/visualization/index.html
