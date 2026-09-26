_LIBERAR_SI_PROPIO = """
if redis.call('GET', KEYS[1]) == ARGV[1] then
    return redis.call('DEL', KEYS[1])
end
return 0
"""


def liberar_reserva(redis_connection, clave, token):
    return bool(redis_connection.eval(_LIBERAR_SI_PROPIO, 1, clave, token))