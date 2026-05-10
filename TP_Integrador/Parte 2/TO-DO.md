- DOCUMENTACION COMPLETA (ENTRE TODOS)

- Quitar valores arbitrarios, definir porque elegimos esos valores: (LUCAS)
  MAX_RANDOM = sys.maxsize-1 #4294967296
  DIFFICULT_PREFIX = "00000000"
  STRING_CHAIN = "a18b"

  WORKER_TIMEOUT = 5 * 60 # 5 minutos
  BLOQUES_MINIMOS_DISMINUIR_PREFIJO = 5
  MINIMO_PROMEDIO_DISMINUIR_PREFIJO = 1

- Tenemos que saber que hacer frente a todos los casos posibles, incluso si no estan especificados en el codigo. (ENTRE TODOS)

- Que pasa si se cae un worker en medio del proceso de resolver un desafio? si hay un solo worker y se cae, se envia un nuevo desafio? (RECEPCION DE ACK AL COORDINADOR, MATEO)
   
- Metricas de todo. (ENTRE TODOS)

X PROPERTY Y TRANSFERENCIAS NFT (validacion en /transferencias) (JOSUE)
  Falta:
    Validar si TX_NFT es valida (tiene que haber un property primero)
    No hay workers -> El pool debe hacer algo
  X Vista front (genesis abajo)
    Diagrama en Miro
    Pulir front en cuanto a lectura


- Test gpu(vast.ia) MATEO
- Test cpu(google cloud) JOUSE

firma con argumentos: JSON.stringify("data": {  
    "monto"  : 2480,
    "origen" : "pub_key_a",
    "destino": "pub_key_b"
  }),
  private key de origen

{
  "data": {  
    "monto"  : 2480,
    "origen" : "pub_key_a",
    "destino": "pub_key_b",
  },
  "type": "TX",
  "sign": ""
}

{
  "data": {  
    "nft"  : "00000000000...",
    "owner": "pub_key_a"
  },
  "type": "PROPERTY",
  "sign": "",
  "timestamp": 1778283476778,
}

{
  "data": {  
    "nft"  : "00000000000...",
    "origen" : "pub_key_a",
    "destino": "pub_key_b",
  },
  "type": "TX_NFT",
  "sign": ""
}
