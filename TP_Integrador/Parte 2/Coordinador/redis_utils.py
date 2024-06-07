import redis
import json

class RedisUtils:
    #Conexion con redis cuando se cree la instancia
    def __init__(self, host='localhost',port=6379,db=0,password="grupo03"):
        self.redis_client = redis.StrictRedis(host=host, port=port, db=0, password=password)

    #Publicar el mensaje al inicio de la lista
    def publicar(self,mensaje, list_key='blockchain'):
        mensaje_json = json.dumps(mensaje) # Convierte el mensaje a formato JSON
        self.redis_client.lpush(list_key, mensaje_json) # Inserta el mensaje al inicio de la lista

    #Recupero los ultimos mensajes, en base al count (osea, recupera los ultimos 10)
    def get_ultimos_mensajes(self, list_key='blockchain',count=10):
        mensaje_json = self.redis_client.lrange(list_key, 0, count - 1) # Recupera los últimos 10 mensajes
        return [json.loads(msg) for msg in mensaje_json] # Convierte cada mensaje de JSON a un objeto de Python
    
    #Recupera el ultimo elemento de la lista en Redis
    def get_ultimo(self, list_key='blockchain'):
        latest_element_json = self.redis_client.lindex(list_key, 0)  # Recupera el elemento en la posición 0 (el más reciente)
        if latest_element_json:
            return json.loads(latest_element_json)  # Convierte el elemento de JSON a un objeto de Python si existe
        return None  # Retorna None si la lista está vacía
    
    #Verifica si existe ese ID en la lista de Redis
    def exists_id(self, id, list_key='blockchain'):
        messages_json = self.redis_client.lrange(list_key, 0, -1)  # Recupera todos los mensajes de la lista
        for msg_json in messages_json:
            msg = json.loads(msg_json)  # Convierte cada mensaje de JSON a un objeto de Python
            if 'id' in msg and msg['id'] == id:  # Verifica si el mensaje contiene el ID especificado
                return True
        return False