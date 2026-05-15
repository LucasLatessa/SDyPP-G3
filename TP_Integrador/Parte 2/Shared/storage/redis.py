import redis
import json
import time
import os 
from Shared.config import REDIS_HOST, REDIS_PORT, REDIS_LIST_KEY_NAME, DIFFICULT_PREFIX, PROCESSING_BLOCK_KEY, REDIS_PASSWORD

class RedisUtils:
    # Conexion con redis cuando se cree la instancia
    def __init__(self, host=REDIS_HOST, password=REDIS_PASSWORD, port=REDIS_PORT, db=0):
        self.redis_client = redis.StrictRedis(
            host=host, 
            port=port, 
            db=db, 
            password=password,
        )

    # Publicar el mensaje al inicio de la lista
    def publicar(self, mensaje, list_key=REDIS_LIST_KEY_NAME):
        try:
            # print("[REDIS] Mensaje a guardar")
            # print(mensaje)
            mensaje_json = json.dumps(mensaje)  # Convierte el mensaje a formato JSON
            self.redis_client.lpush(
                list_key, mensaje_json
            )  # Inserta el mensaje al inicio de la lista
        except Exception as e:
            print(e)

    # Recupero los ultimos mensajes, en base al count (osea, recupera los ultimos 10)
    def get_ultimos_mensajes(self, list_key=REDIS_LIST_KEY_NAME, count=10):
        mensaje_json = self.redis_client.lrange(
            list_key, 0, count - 1
        )  # Recupera los últimos 10 mensajes
        return [
            json.loads(msg) for msg in mensaje_json
        ]  # Convierte cada mensaje de JSON a un objeto de Python

    # Recupera el ultimo elemento de la lista en Redis
    def get_ultimo(self, list_key=REDIS_LIST_KEY_NAME):
        latest_element_json = self.redis_client.lindex(
            list_key, 0
        )  # Recupera el elemento en la posición 0 (el más reciente)
        if latest_element_json:
            return json.loads(
                latest_element_json
            )  # Convierte el elemento de JSON a un objeto de Python si existe
        return None  # Retorna None si la lista está vacía

    # Recupera todos los mensajes almacenados en Redis
    def getAllTransactions(self, list_key=REDIS_LIST_KEY_NAME):
        messages_json = self.redis_client.lrange(list_key, 0, -1)
        return [json.loads(msg) for msg in messages_json]

    # Verifica si existe ese ID en la lista de Redis
    def exists_id(self, id, list_key=REDIS_LIST_KEY_NAME):
        messages_json = self.redis_client.lrange(
            list_key, 0, -1
        )  # Recupera todos los mensajes de la lista
        for msg_json in messages_json:
            msg = json.loads(
                msg_json
            )  # Convierte cada mensaje de JSON a un objeto de Python
            if (
                "id" in msg and msg["id"] == id
            ):  # Verifica si el mensaje contiene el ID especificado
                return True
        return False
  
    def get_prefijo(self):
      return self.redis_client.get('prefix_key').decode("utf-8")
    
    def set_prefijo(self,prefijo):
      self.redis_client.set('prefix_key', prefijo)
  
    def inicializar_prefijo(self):
      if self.redis_client.get('prefix_key') is None:
        self.redis_client.set('prefix_key', DIFFICULT_PREFIX)  # Valor inicial por defecto
        print(f"Prefijo inicial insertado en Redis: {DIFFICULT_PREFIX}")
      else:
        print("Prefijo ya presente en Redis:", self.get_prefijo())

    def get_bloque_en_proceso(self):
        raw = self.redis_client.get(PROCESSING_BLOCK_KEY)
        if not raw:
            return None
        return json.loads(raw)


    def guardar_bloque_en_proceso(self, bloque, rangos):
        actual = self.get_bloque_en_proceso()
        attempt = 1

        if actual and actual.get("id") == bloque["id"]:
            attempt = actual.get("attempt", 0) + 1

        estado = {
            "id": bloque["id"],
            "status": "PROCESSING",
            "reprocess": False,
            "reason": None,
            "attempt": attempt,
            "total_tasks": len(rangos),
            "completed_tasks": 0,
            "found": False,
            "ranges": [
                {
                    "start": start,
                    "end": end,
                    "status": "PENDING",
                }
                for start, end in rangos
            ],
            "block": bloque,
            "updated_at": time.time(),
        }

        self.redis_client.set(PROCESSING_BLOCK_KEY, json.dumps(estado))


    def marcar_reproceso_bloque(self, reason):
        estado = self.get_bloque_en_proceso()
        if not estado:
            return

        estado["status"] = "REPROCESS"
        estado["reprocess"] = True
        estado["reason"] = reason
        estado["updated_at"] = time.time()

        self.redis_client.set(PROCESSING_BLOCK_KEY, json.dumps(estado))


    def registrar_tarea_sin_solucion(self, block_id, start, end, worker_id=None):
        estado = self.get_bloque_en_proceso()
        rango_encontrado = False

        if not estado or estado.get("id") != block_id:
            return False

        for rango in estado["ranges"]:
            if rango["start"] == start and rango["end"] == end:
                rango_encontrado = True

                if rango["status"] == "PENDING":
                    rango["status"] = "DONE_NOT_FOUND"
                    rango["worker_id"] = worker_id
                    rango["finished_at"] = time.time()
                    estado["completed_tasks"] += 1
                break
            
        if not rango_encontrado:
            return False

        if estado["completed_tasks"] >= estado["total_tasks"] and not estado["found"]:
            estado["status"] = "REPROCESS"
            estado["reprocess"] = True
            estado["reason"] = "NONCE_NOT_FOUND"

        estado["updated_at"] = time.time()
        self.redis_client.set(PROCESSING_BLOCK_KEY, json.dumps(estado))

        return True


    def limpiar_bloque_en_proceso(self, block_id):
        estado = self.get_bloque_en_proceso()

        if estado and estado.get("id") == block_id:
            self.redis_client.delete(PROCESSING_BLOCK_KEY)

    def marcar_reproceso_si_expirado(self, timeout_seconds):
        estado = self.get_bloque_en_proceso()

        if not estado or estado.get("status") != "PROCESSING":
            return False

        updated_at = estado.get("updated_at")
        if updated_at is None:
            return False

        if time.time() - float(updated_at) < timeout_seconds:
            return False

        estado["status"] = "REPROCESS"
        estado["reprocess"] = True
        estado["reason"] = "WORKERS_TIMEOUT"
        estado["updated_at"] = time.time()

        self.redis_client.set(PROCESSING_BLOCK_KEY, json.dumps(estado))
        return True
    
    def actualizar_updated_at(self,block_id):
        estado = self.get_bloque_en_proceso()

        if (not estado) or (estado.get("id") != block_id):
          return False
        
        if estado.get("status") != "PROCESSING":
          return False
        
        estado["updated_at"] = time.time()
        self.redis_client.set(PROCESSING_BLOCK_KEY, json.dumps(estado))
        return True

