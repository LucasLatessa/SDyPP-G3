# Hit #3

#### Cree un mini programa con SDK (python, node, por ejemplo) que liste (terminal) de forma simple y muestre el estado de las instancias (máquinas virtuales) existentes.

##### - [id] instancia id 1 | prendida
##### - [id] instancia id 2 | en pausa
##### - [id] instancia id 3 | terminada

#### Que permita que 1 instancia se:
##### - Inicie, 
##### - Pause, 
##### - Reinicie
##### - Termine (eliminar) su Instancia (*)

#### ¿Qué pasa con el estado de terraform si hago terminate?

#### Hacer un dibujo explicativo de lo sucedido.

Primero creamos 3 instancias usando terraform.

![Paso1](https://github.com/LucasLatessa/SDyPP-G3/assets/63746351/7ae52f4e-d826-4828-94ee-6f3f640f42d5)

Luego, ejecutamos el programa python para borrar la instancia 2

![Paso2](https://github.com/LucasLatessa/SDyPP-G3/assets/63746351/114a1144-a1fe-4d5a-b97d-f302e29a8aa6)

Cuando hago "terminate" desde el programa y quiero hacer "terraform show" para ver el estado actual de los recursos gestionar, Terraform no tendra conocimiento de que la instancia fue eliminada, haciendo que no pueda gestionarla de forma eficiente, ya que Terraform gestiona los recursos de la infraestructura manteniendo un estado interno que rastrea el estado actual del recurso. 

![Paso3](https://github.com/LucasLatessa/SDyPP-G3/assets/63746351/8d497554-a517-4a00-809f-114b92ef5a1d)

Si vuelvo a ejecutar el terraform plan, Terraform comparar el estado actual de la infraestructura con la configuracion declarada en los archivos '.tf', generando un nuevo plan de accion que describa los cambios necesarios para hacer que el estado actual coincida con la configuracion declarada.
Luego, ejecuto el terraform apply para proceder con la aplicacion de los cambios

![Paso4](https://github.com/LucasLatessa/SDyPP-G3/assets/63746351/08db51ff-837c-41ab-83a3-1c6e3ce09c80)

En nuestro ejemplo, terraform se percata de que la instancia 2 no existe dentro de la infraestructura, generando el plan de accion para crearla nuevamente.


