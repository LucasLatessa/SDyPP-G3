# HIT 8

Se realizo uan preuba con dos gpu y otra con cpu, la idea es que intenten buscar un resultado imposible unas 2908200, estos son los resultados:

Este fue el comando a ejecutar, resultados:
GTX 970: Tiempo de ejecución total: 6.066 segundos (3.539629 segundos)
RTX 3060: Tiempo de ejecución total: 9.438 segundos (1.609292 segundos)

AMD Ryzen 5 3500: Tiempo de ejecución total: 7.364 segundos

Como se observa, a diferencia de lo que se creia, la cpu tuvo un buen tiempo en relacion a la 970, mientras que la placa mas potente, la 3060, se queda atras.
Si bien esto escapa de la logica, era lo esperado. Por mas que la idea es ejecutar todo dentro de la gpu, eso es una tarea que no se puede realizar, por lo que
la cpu tiene mucho impacto en los dos primeros test, sumado a que la cpu de la 3060 es mucho menos potente en relacion a las otras dos, lo mismo para con los puertos
PCI-express.
A pesar de eso, si solo tenemos en cuenta el tiempo de la gpu en los dos primeros casos, podemos ver lo que si deberia ocurrir, la 3060 hizo su trabajo mucho mas rapido en relacion 
a la 970 y la cpu. 