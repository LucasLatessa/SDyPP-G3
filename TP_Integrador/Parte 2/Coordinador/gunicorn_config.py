bind = "0.0.0.0:5000"
workers = 1
preload_app = False


def post_worker_init(worker):
    from Coordinador.processor import iniciar_procesador

    worker.procesador_bloques = iniciar_procesador()


def worker_exit(server, worker):
    from Coordinador.processor import detener_procesador

    control = getattr(worker, "procesador_bloques", None)

    if control is not None:
        detener_procesador(control)