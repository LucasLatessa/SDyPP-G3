# HIT 8

Se realizó una prueba con dos gpu y otra con cpu, la idea es que intenten buscar un resultado imposible unas 2908200, estos son los resultados:

Este fue el comando a ejecutar, resultados:
GTX 970: Tiempo de ejecución total: 6.066 segundos (3.539629 segundos)
RTX 3060: Tiempo de ejecución total: 9.438 segundos (1.609292 segundos)

AMD Ryzen 5 3500: Tiempo de ejecución total: 7.364 segundos

Como se observa, a diferencia de lo que se creía, la cpu tuvo un buen tiempo en relación a la 970, mientras que la placa más potente, la 3060, se quedó atrás.
Si bien esto escapa de la lógica, era lo esperado. Por más que la idea es ejecutar todo dentro de la gpu, eso es una tarea que no se puede realizar, por lo que
la cpu tiene mucho impacto en los dos primeros test, sumado a que la cpu de la 3060 es mucho menos potente en relación a las otras dos, lo mismo para con los puertos
PCI-express.
A pesar de eso, si solo tenemos en cuenta el tiempo de la gpu en los dos primeros casos, podemos ver lo que sí debería ocurrir, la 3060 hizo su trabajo mucho más rápido en relación
a la 970 y la cpu.
