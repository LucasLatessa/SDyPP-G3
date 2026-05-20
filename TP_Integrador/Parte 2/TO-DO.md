- Que pasa si se cae un worker en medio del proceso de resolver un desafio? si hay un solo worker y se cae, se envia un nuevo desafio? (RECEPCION DE ACK AL COORDINADOR, MATEO)

- Metricas de todo. (ENTRE TODOS)

firma con argumentos: JSON.stringify("data": {  
 "monto" : 2480,
"origen" : "pub_key_a",
"destino": "pub_key_b"
}),
private key de origen

{
"data": {  
 "monto" : 2480,
"origen" : "pub_key_a",
"destino": "pub_key_b",
},
"type": "TX",
"sign": ""
}

{
"data": {  
 "nft" : "00000000000...",
"owner": "pub_key_a"
},
"type": "PROPERTY",
"sign": "",
"timestamp": 1778283476778,
}

{
"data": {  
 "nft" : "00000000000...",
"origen" : "pub_key_a",
"destino": "pub_key_b",
},
"type": "TX_NFT",
"sign": ""
}

PROBLEMA CONCURRENCIA:
usuario A registara nft 123, mientras se resuelve la tarea, B registra tambien nft 123
como esta implementado, se valida antes de ingresar a la cola, contra el redis
por lo tanto si todavia no esta en redis pasa validacion -> se van las dos transacciones a la blockchain