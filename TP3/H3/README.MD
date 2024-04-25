# Hit #3
Cree un mini programa con SDK (python, node, por ejemplo) que liste (terminal) de forma simple y muestre el estado de las instancias (máquinas virtuales) existentes.

[id] instancia id 1 | prendida
[id] instancia id 2 | en pausa
[id] instancia id 3 | terminada

Que permita que 1 instancia se:
    Inicie, 
    Pause, 
    Reinicie
    Termine (eliminar) su Instancia (*)

¿Qué pasa con el estado de terraform si hago terminate?

    Revisar estado

Cuando hago "terminate" desde el programa y quiero hacer "terraform show" para ver el estado actual de los recursos gestionar, Terraform no tendra conocimiento de que la instancia fue eliminada, haciendo que no pueda gestionarla de forma eficiente, ya que Terraform gestiona los recursos de la infraestructura manteniendo un estado interno que rastrea el estado actual del recurso. 

En nuestro ejemplo creamos 3 instancias con terraform, que luego la instancia 2 sera eliminado por el programa de python. Cuando ejecuto un "terraform show" la instancia 2 seria considera todavia por terraform.
    
    Explicar qué pasa cuando vuelvo a correr Terraform plan / apply.

Si vuelvo a ejecutar el terraform plan, Terraform comparar el estado actual de la infraestructura con la configuracion declarada en los archivos '.tf', generando un nuevo plan de accion que describa los cambios necesarios para hacer que el estado actual coincida con la configuracion declarada.
Luego, ejecuto el terraform apply para proceder con la aplicacion de los cambios

En nuestro ejemplo, terraform se percata de que la instancia 2 no existe dentro de la infraestructura, generando el plan de accion para crearla nuevamente.

Hacer un dibujo explicativo de lo sucedido.
