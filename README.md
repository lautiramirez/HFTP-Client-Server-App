# Laboratorio 2: HFTP - Aplicación Cliente/Servidor

El objetivo del laboratorio es aplicar la comunicación cliente/servidor por medio de la programación de *sockets* desde la perspectiva del servidor, empleando el protocolo llamado *Home-made File Transfer Protocol* (HFTP) que garantiza una entrega segura, libre de errores y en orden de todas las transacciones debido a que está basado en TCP.

## Proceso de desarrollo

El desarrollo del proyecto fue realizado en junto por los integrantes del grupo, es decir, que se estuvo en común acuerdo sobre todas las decisiones de la implementación del servidor.

Al principio realizamos un análisis exploratorio del *kickstart* para poder entender la estructura del servidor y ver las tareas que realizaban cada uno de los archivos `.py` entregados por la cátedra. Luego de eso recurrimos a diversas páginas de internet para consultar sobre el funcionamiento del módulo *socket* de *python*.

Primero codeamos la conexión del server en el archivo `server.py`, la primera tarea fue crear el *socket* para ello hay que definir su tipo, como nuestro protocolo se basa en TCP usamos el que viene por defecto en la función `socket.socket`, luego de esto hay que indicarle en qué puerto se va a mantener a la escucha el servidor para esto se usa el método `bind`, que lo referenciamos con una tupla que contiene el *host* y el puerto. Por otra parte, utilizamos `listen` para hacer que el socket acepte conexiones entrantes y `accept` para que comience a escuchar, esta última instrucción se tiene que encontrar dentro de un `while` infinito debido a que el server tiene que ser capaz de escuchar todo el tiempo el pedido de cualquier cliente.

Luego procedimos a implementar el archivo `connection.py` donde se encuentran funciones que se encargan de satisfacer los pedidos del cliente hasta que termina la conexión. Esta parte al principio fue media confusa, pero realizamos pruebas con un *script* que simulaba a un cliente para poder darnos cuenta que hacia cada función. La estructura del código al principio fue media caótica (tipo *spaghetti*) pero luego de lograr cumplir los requerimientos de funcionalidad se procedió a modularizar todo en funciones auxiliares para que la lectura sea más amena.

Por último, resolvimos punto estrella para que nuestro servidor pueda atender múltiples clientes a la vez, esto será explicado con más profundidad en la sección de **preguntas a responder**.

Cabe resaltar que nos fue de gran ayuda Telnet para poder probar las funcionalidades de nuestro programa.
## Modo de ejecución

Una vez clonado el repositorio desde *bitbuket*, debemos escribir las siguientes instrucciones por línea de comando para ejecutar el servidor:

```
> $ cd redes22lab2g12/

> $ python3 server.py
```

Para poder ejecutar el cliente, en otra terminal ejecutamos:

```
> $ python3 client.py '0.0.0.0'
```
## Testing

Para poner a prueba nuestro servidor y ver si cumple los requisitos necesarios, la cátedra nos provee de unos *test* que están pensados para evaluar si un programa tiene un cierto comportamiento específico.

Para ejecutarlos primero se debe correr el servidor:

```
> $ python3 server.py
```

 y luego en otra términal el archivo server-test.py

```
> $ python3 server-test.py
```
## Preguntas a responder
1. ¿Qué estrategias existen para poder implementar este mismo servidor pero con capacidad de atender múltiples clientes simultáneamente? Investigue y responda brevemente qué cambios serían necesario en el diseño del código.

En python se pueden crear nuevos procesos mediante *forks* y otras funciones como `popen2.popen2` de forma que nuestro programa pueda realizar varias tareas de forma paralela. Sin embargo el cambio de contexto puede ser relativamente lento y ocupar muchos recursos para poder mantenerlo. Es por ello que nosotros usamos *threads*, o hilos de ejecución, estos se ejecutan dentro de un proceso, y los *threads* del proceso comparten recursos entre si, es decir, que el sistema operativo necesita menos recursos para crearlos y gestionarlos por ende el cambio de contexto es más rápido. También tiene la ventaja de que es más sencillo compartir información entre ellos debido a que comparten el mismo espacio de memoria global.

La implementación de multicliente fue realizada con el módulo `thread`, el cual contiene una clase `Thread` para crear los hilos de ejecución. También hay que definir un método `run` donde se encuentra el código que ejecutara nuestro *thread*. Por último para que el hilo comience a ejecutar su código basta con crear una instancia de la clase que definimos y llamar a su método `start` y entonces el código del hilo principal y el del que acabamos de crear se ejecutaran de forma concurrente.

2. Pruebe ejecutar el servidor en una máquina del laboratorio, mientras utiliza el cliente desde otra, hacia la ip de la máquina servidor. ¿Qué diferencia hay si se corre el servidor desde la IP "*localhost*", "127.0.0.1" o la ip "0.0.0.0"?

La dirección IP 127.0.0.1, también llamada *loopback*, es exclusivamente para uso *localhost*, está dirección se utiliza para establecer una conexión IP con la misma máquina o computadora que utiliza el usuario final.

Por otra parte 0.0.0.0 es una dirección no enrutable, es decir, que no se encuentra ligada a ninguna dirección remota en particular. En el contexto de los servidores significa todas las direcciones IPv4. Básicamente es el marcador de posición sin dirección en particular, por ejemplo si un *host* tiene dos direcciones IP, 192.168.1.1 y 10.1.2.1, y un servidor que se ejecuta en el *host* escucha en 0.0.0.0, será accesible en ambas direcciones IP.

Entonces cuando un servicio está a la escucha en 0.0.0.0 significa que el servicio está a la escucha en todas las interfaces de red configuradas, cuando está a la escucha en 127.0.0.1 el servicio sólo está vinculado a la interfaz loopback.


## Integrantes del grupo:

* Castellaro, Agustín.
* Mansilla, Kevin Gaston.
* Ramirez, Lautaro.

## Referencias
- https://duenaslerin.com/tico2/pdfs/python-para-todos.pdf
- https://docs.python.org/es/3/howto/sockets.html
- https://rico-schmidt.name/pymotw-3/socket/tcp.html
- https://www.thefastcode.com/es-eur/article/what-is-the-difference-between-127-0-0-1-and-0-0-0-0
