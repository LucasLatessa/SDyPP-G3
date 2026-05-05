"""
Configuración centralizada de logging para toda la aplicación.
"""

import logging

# ----------------------------------------------------------------------
#                         CONFIGURACIONES
# ----------------------------------------------------------------------

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
LOG_LEVEL = logging.INFO

# ----------------------------------------------------------------------
#                            FUNCIONES
# ----------------------------------------------------------------------

def get_logger(name: str) -> logging.Logger:
    """
    Retorna un logger configurado con el formato estándar del sistema.

    :param name: Nombre del módulo
    :return: Instancia de Logger
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(LOG_FORMAT)
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        logger.setLevel(LOG_LEVEL)

    return logger