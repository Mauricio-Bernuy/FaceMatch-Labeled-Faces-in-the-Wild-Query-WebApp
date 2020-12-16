# BD2-P2-H2

# Proyecto 2 - Hito 2 | Rtree - Face Recognition

## Introducción
El reconocimiento facial es una tecnología en constante crecimiento. Sus varios usos ha llevado a un gran número de aplicaciones, como el reconocimiento de si dos personas en imágenes separadas son la misma o no. A través del procesamiento de imágenes, se puede sacar un conjunto de personas que presentan el mayor nivel de similitud a una inicial, proceso cuya aplicación tiene distintas fromas de ser llevado a cabo. 

En este proyecto, se pretentedá realizar una búsqueda de las imágenes más similares a una inicial a través de el KNN search en una estructura árbol conocida como R-Tree.

## Marco Teórico
La estructura principal de este trabajo, el Rtree, tiene una estructura basada en conjuntos de vectores, tal que los mismos son los más cercanos entre ellos, donde cada conjunto tiene un tamaño máximo de elementos que lo conforman. En forma de índice, cada uno de estos elementos puede contener más elementos de forma que en la búsqueda reducimos el problema de búsqueda en un factor M, donde M es el número máximo de sub elementos por conjunto. Los elementos individuales utilizados en esta ocasión  vendrían a ser vectores de 128 dimensiones que son los vectores característicos obtenidos de FaceRecognition de python, donde obtenemos vectores que representan de forma única las características de un rostro. Aquellos que tengan características similares tendrán valores similares en sus 128 dimensiones, haciendo que el rtree los mantenga cercanos.
Finalmente, también hacemos uso de colas de prioridad para poder hacer algoritmos secuenciales, usando los mismos vectores característicos de los rostros y computando sus distancias con la mismaa librería FaceRecognition.

### Face Recognition
"Face-Recognition" es la librería de python utilizada en este trabajo para leer, reconocer e identificar los rostros de las imagenes utilizadas. En su mayor parte las funciones ya estan implementadas como "load_image_file" o "face_encodings", que nos ayudan con la parte más pesada del reconocimiento. Otra función muy importante que utilizamos continuamente es la de "face_distance", que devuelve la distancia entre un rostro y una lista de rostros y, con esos resultados, podemos armar nuestras estructuras guiándonos de la similitud entre los inputs de rostros.

### Construcción de Rtree
La implementación del Rtree se hace a través de la librería de python "rtree", en la cuál tenemos que definir ciertas propiedades para poder utilizar. Para esta estructura, se necesita definir especialmente la dimensionalidad de los elementos y el M mencionado previamente para definir un límite de elementos por nodo. Para este trabajo, definimos un M de 3 y una dimensionalidad de acuerdo a los vectores característicos, que sería igual a 128.
En cuanto a la población de la estructura misma, se hizo un algoritmo que recorre un arbol de carpetas que contienen varias imagenes de distintas personas, que son sometidas al las funciones de Face Recognition y son agregados al Rtree. Una vez la estructura ha sido construida, podemos usar la funcion "nearest" tambien implementada por la libreria "rtree" para encontrar los k vecinos más cercanos que, durante todo el trabajo, se toma como los 8 vecinos más cercanos.

### Cola de prioridad

Para la cola de prioridad se utilizó la librería de python "heapq" que nos permite convertir un arreglo a un maxheap. Para hacer uso de esta estructura, usamos la funcion "face_distance" con los rostros ya encontrados y recorremos linealmente cada una de las distancias, manteniendo en el heap la inversa de cada una para poder finalmente tener los más cercanos (por tener menor distancia), y mantenemos el mismo número de k elementos en la estructura como pares (relevancia, dirección de archivo). Para el término del algoritmo, tendremos un arreglo con k elementos que se puede ordenar de mayor a menor para representar un orden de más relevante a menos relevante y las respectivas direcciones de las imagenes en el directorio para poder retornar y mostrar estos rostros como resultados.

### Construcción de las Encodificaciones
Debido al fuerte costo computacional de operar la función de *face_encoding*, se eligió usar el concepto de multiprocessing para dividir la tarea de construcción en 8 hilos distintos, logrando mejorar inmensamente el tiempo de ejecución de esta fase del programa.

### Almacenamiento de Encodificaciones

Se utilizó la librería Pickle para guardar la lista de encodificaciones de face_recognition en archivos de datos, los cuales pueden ser cargados en cualquier momento para acelerar el tiempo de ejecucion del programa. Se creo un archivo *gen_indexes.py* para crear los tamaños de indice mostrados en los resultados.

![](https://i.imgur.com/lTXoN4W.png)


## Implementación & Resultados

En este repositorio, se encuentran dos implementaciones del KNN, y se mostrarán las diferencias de tiempos entre ambas, dependiendo de la cantidad de muestras utilizadas. En la siguiente tabla, se ve una comparacion de la eficiencia entre ambos metodos.

![](https://i.imgur.com/gNbvizw.png)

Esta tabla nos demuestra que el R-Tree es mas lento a una implemetacion secuencial del algoritmo, aunque a grandes rasgos, esta diferencia es casi insignificante, pues en el peor de los casos, igual hay una diferencia de menos de 0.01 segundos entre las implementaciones, la cual va favoreciendo cada vez mas a la implementación en R-tree.

### Aplicación
Para hacer la aplicacion web, se utilizo "Flask", un framework de python, asi como HTML y la libreria de Bootstrap. Flask nos permitio tener una comunicacion con las demas partes del progrma de forma eficiente, por lo que lo usamos para el backend.

La aplicación misma recibe o una imagen o un texto que realiza una búsqueda (se explica mejor en el siguiente inciso). Estos funcionarán como el input de rostro que se quiere relacionar con lo que se tenga en las estructuras implementadas. Estas, utilizando Flask, son enviadas al backend donde se usan las funciones de Face Recognition para hallar su vector característico y luego solo se usa la función "nearest" para hallar los 8 más cercanos. La dirección de estos 8 elementos es enviado al frontend, tal que este puede leerlos y mostrar las imagenes como resultados en un lado.
![](https://i.imgur.com/Hw7OhNt.png)

![](https://i.imgur.com/MxeWS7Z.png)

## Búsqueda en Wikipedia

Además de poder enviar una imagen a la aplicación por medio de carga de archivos, nos pareció interesante el permitir la búsqueda de algun personaje arbitrario para utilizar nuestra página. Para eso se planeó usar la librería [bing-image-downloader](https://pypi.org/project/bing-image-downloader/), la cual nos brinda un API para realizar *queries* a través de ese motor de búsqueda, devolviéndonos una imagen acorde a un input dado. Esta tuvo que ser modificada ligeramente para permitir la descarga de urls conteniendo caracteres como tildes y dialisis, puesto que estos no fueron considerados por su desarrollador. Se hace uso también del advanced search query de Bing para obtener resultados provenientes únicamente de Wikipedia (añadiendo al comienzo de una búsqueda 'site:wikipedia.org'), visto que esto logró darnos los resultados más precisos.
![](https://i.imgur.com/3zuJTOw.png)


## Conclusiones

En conclusion, se puede ver que nuestra implementación tuvo un contraste en los tiempos de búsqueda que si bien son mínimos, demuestran que los rostros como vectores de características complejos no son eficientes de utilizar en un rtree tradicional. Esto se deberá principalmente a lo que es conocido como la maldición de dimensionalidad, que dice que la complejidad del algoritmo o estructura como en este caso es el rtree aumentará considerablemente o se hará menos eficiente mientras más dimensiones tenga sus elementos, como sería un rostro de 128 dimensiones. Es importante recordar que se han usado varias librerias de Python, las cuales, si bien agilizan el desarrollo de las aplicaciones deseadas, pueden tener un impacto en la eficiencia de las estructuras existentes, pues sus implementaciones son privadas.

Este trabajo nos ayuda a evaluar las distintas formas de llevar a cabo el algoritmo KNN, y ver como este se desarrolla en distintas estructuras. Para un trabajo futuro, se puede plantear mejoras o soluciones a la maldición de dimensionalidad para explotar al máximo la eficiencia de algunas estructuras o también directamente probar con otras, para ver cual es, finalmente, la más eficiente y sugerible de usar a grande escala. 
