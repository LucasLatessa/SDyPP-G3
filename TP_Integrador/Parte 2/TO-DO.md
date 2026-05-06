- Control del topico de Rabbit (a veces no los levanta el Worker)
- Revisar la competencia entre workers
- Pool de transaciones
- 0 consumidores en Pool_manager

Disminuir prefix si ningun worker encontro en Nonce en menos de 10min
Aumentar Prefix si tardo menos de 5 minutos (promedio) en encontrar los ultimos 5 nonce
- Aumentar prefijo:
	303: Si se resolvió muy rápido

- Disminuir prefijo:
	307: Resolvióau