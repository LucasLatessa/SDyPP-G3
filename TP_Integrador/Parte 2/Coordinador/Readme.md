# Coordinador

El Coordinador es el componente central del sistema encargado de:

- Recibir transacciones
- Agruparlas en bloques
- Enviar desafíos a los workers (Proof of Work)
- Validar bloques resueltos
- Persistir la blockchain en Redis

## Arquitectura

El sistema sigue una arquitectura distribuida basada en eventos:

* **Flask API:** Recepción de transacciones y resultados
* **RabbitMQ:** Mensajería entre coordinador y workers
* **Redis:** Persistencia de la blockchain
* **Workers:** Resolución del desafío (minería)

## Estructura de archivos
```text
├── app.py
├── config.py
│
├── api/
│   └── routes.py
│
├── services/
│   └── blockchain_service.py
│
├── messaging/
│   └── rabbitmq.py
│
├── workers/
│   └── paquete_processor.py
│
├── utils/
│   └── hash_utils.py
│
├── storage/
│   └── redis_client.py
│
└── requirements.txt
```

## Funcionamiento

### 1. Recepcion de transacciones

Endpoint 

```
POST /transaccion
```

* Recibe una transacción en formato JSON
* La envía a la cola transacciones en RabbitMQ

Formato de transaciones:

```
{
    "origen": "a",
    "destino":"b",
    "monto":123
}
```

### 2. Procesamiento de paquetes

Un proceso en segundo plano consume transacciones en bloques (por defecto 10), generando un bloque con metadata y enviandolo al exchange block_challenge

### 3. Resolución del desafío (Workers)

Los workers:
- Reciben el bloque desde RabbitMQ
- Intentan resolver el desafío (hash válido)
- Devuelven el resultado al coordinador

### 4. Resolución del desafío (Workers)

Endpoint 

```
POST /tarea_worker
```

El coordinador verifica que el hash sea correcto y valida que el bloque no exista. De ser asi, enlaza con el bloque anterior y lo guarda en redis.

## Endpoints disponibles

| Método | Endpoint      | Descripción                       |
| ------ | ------------- | --------------------------------- |
| POST   | /transaccion  | Encola una nueva transacción      |
| POST   | /tarea_worker | Recibe bloque resuelto por worker |
| GET    | /status       | Estado del servidor               |
| GET    | /bloques/<block_id>/estado       | Estado de un bloque, si existe o no en redis. Este endpoint es consultado por los Workers               |

## Ejecucion local

Instalar dependencias:
```
pip install -r requirements.txt
```
Ejecutar el coordinador:
```
python app.py
```

## Ejecucion con Docker (entorno local)

Crear imagen
```
docker build . -t coordinador   
```

Ejecutar contenedor
```
docker run -p 5000:5000 -e RABBIT_HOST=host.docker.internal -e REDIS_HOST=host.docker.internal coordinador
```


