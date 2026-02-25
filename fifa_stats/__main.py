from fifa_stats.app.main import iniciar_servico


def start():
    print(__package__, " started.")
    iniciar_servico()


if __name__ == "__main__":
    start()