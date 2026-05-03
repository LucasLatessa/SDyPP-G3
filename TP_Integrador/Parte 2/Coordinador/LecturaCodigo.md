Coordinador.py:

Procesamiento de paquetes:

  90: max_random=sys.maxsize-1
  92: El prefijo surge de redis
  98: "base_string_chain": "A4FC"

Prefijo:
  135-140: Funcion que inicializa el prefijo en redis

Recibir Transaciones (149-185)
  - Campo signature (no se que es aun)
  - Usuario universal
  - Clave publica

Verificar signature (209-238)

Balance por usuario (240-261)

Balance Universal (264-278)

Comprobar que existe la key del usuario (286-292)

-> Ajustar prefijo coordinador (295-323)

-> Recibir tarea
  329-334: Reduce el prefijo en base a un parametro tiempo (timeout)
  341-343: Tiempo de resolucion del worker
  359: Consultar_maestro()
  362: Ajustar_prefijo_coordinador(tiempo_resolucion)
  388: Recompensas
  391-416: Si es usuario, envia recompesas

Metricas (430-464)

Token-valido (467-476)

Registrar-clave (479-499)

-> Bloque-genesis (501-523)

Cargar-clave-privada (526-531)

Firmar-mensaje (533-546)

Clave-universal (548-591)

-> Consultar-maestro (593-617)

main de ellos (624-638)