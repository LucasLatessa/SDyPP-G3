import redis
import json

from Shared.config import REDIS_HOST, REDIS_PORT, REDIS_LIST_KEY_NAME, DIFFICULT_PREFIX


class RedisUtils:
    # Conexion con redis cuando se cree la instancia
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, db=0):
        self.redis_client = redis.StrictRedis(host=host, port=port, db=0)

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
