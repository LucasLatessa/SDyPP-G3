from Shared.utils.logger import get_logger

logger = get_logger(__name__)


def disminuir_prefijo(redis_client, max_ceros=None):
    prefijo = redis_client.get_prefijo()

    if max_ceros is None:
        # Comportamiento original: quitar un cero.
        nuevo_prefijo = prefijo[1:]
    else:
        # Si ya tiene esa longitud o menos, queda igual.
        nuevo_prefijo = prefijo[:max_ceros]

    if nuevo_prefijo != prefijo:
        redis_client.set_prefijo(nuevo_prefijo)
        logger.info(
            "Prefijo DISMINUIDO actualizado: %s -> %s",
            prefijo,
            nuevo_prefijo,
        )

    return nuevo_prefijo