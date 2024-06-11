# https://github.com/nvidia/cccl


 Este repositorio de github se creó con el objetivo de crear un kit de herramientas llamado CCCL, que incorpora tres librerías de cuda: Thrust, CUB y Libcudacxx.
La idea es ayudar a los desarrolladores de cuda a la hora de utilizar líneas de comando, permitiendo ingresar datos de entrada desde la propia consola
al ejecutar el programa. Ej:
    CCCL_Option options[] = {
        {"blocks", 'b', "Número de bloques", 1, NULL, CCCL_INT},
        {"threads", 't', "Número de hilos por bloque", 1, NULL, CCCL_INT},
        {NULL}
    };
 Esta porción de código le permite al usuario que ingrese el número de bloques e hilos de esta forma:
./programa --blocks 2 --threads 32, en su defecto será 1
 El repositorio se actualiza prácticamente todos los días.


# Thrust


 Esta librería le permite al desarrollador desligarse de ciertas funcionalidades que provee thrust, como es el manejo de vectores y otras estructuras de dato, algoritmos de    
transformación y reducción, etc. Sumado a esto también permite crear variables en GPU de forma más sencilla. Ej:
    thrust::host_vector<int> h_vec(4);
    h_vec[0] = 10; h_vec[1] = 3; h_vec[2] = 6; h_vec[3] = 1;
    thrust::device_vector<int> d_vec = h_vec;
    thrust::sort(d_vec.begin(), d_vec.end());
    thrust::copy(d_vec.begin(), d_vec.end(), h_vec.begin());


Lo que se logra en el ejemplo es crear un vector en cpu, asignar elementos, pasarlo a la gpu, ordenarlo utilizando gpu y por último pasar el resultado a cpu, todo esto en 5 líneas de código. Todo esto es posible gracias al uso de iteradores, existen distintos tipos y en el ejemplo se puede ver una forma de utilizarlos, con d_vec.begin() se obtiene
el primer elemento del vector, y con d_vec.end() el último.


# Ejemplo thrust


 En el script creado se está generando un vector con números aleatorios y se los ordena utilizando la GPU y la librería Thrust.
Dicha librería estaba disponible con CUDA, por lo que compilo como corresponde, sin la necesidad de instalar nada.


# CUDA “a pelo” vs thrust/cccl


 Existe una diferencia clara en cuanto a utilizar CUDA "a pelo" y usar thrust/cccl, principalmente en la facilidad de uso y, en ciertos casos, optimización.
Al utilizar la librería se pueden hacer cosas como esto:
    thrust::sequence(H.begin(), H.end());
sin la necesidad de crear un kernel propio, la librería se encarga de setear los elementos de H en orden.
Esta idea de las librerías se utiliza siempre, en cualquier lenguaje de programación, y en este tipo de lenguajes que requiere el uso de GPU,
Es sumamente útil al tercerizar esas funciones.
 Si uno quisiera, puede realizar esta función de forma propia, quizás sea distinta a la que provee la librería debido al contexto, sin embargo, si lo que se desea hacer lo permite
la librería, es totalmente recomendado utilizarla.
 Al igual que el ejemplo mostrado arriba, existen otros algoritmos de transformación que provee thrust, thrust::fill, thrust::replace o thrust::transform.
 Así como algoritmos de transformación, también tenemos los de reducción tales como thrust::reduce, thrust::reduce_by_key o thrust::transform_reduce, esto genera un único
valor obtenido a partir de un vector. Y como éstas existen otras funciones como thrust::device_vector::iterator , thrust::zip_iterator (ligadas a los iteradores), thrust::sort (reordenamiento), etc.
 En conclusión, el uso de la librería depende de lo que se desee hacer, quizás uno no requiera utilizar ninguna de sus funciones, quizás las requiera todas, quizás algunas o quizás
deba crear las suyas propias, cada uno debería tener claro si vale o no vale la pena su utilización.







