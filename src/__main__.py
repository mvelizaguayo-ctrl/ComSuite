from . import main as _main


def run():
    """Entrypoint para python -m src
    Delegamos en la función main definida en el módulo principal del proyecto.
    """

    # Llamar a la función main del módulo raíz
    _main.main()


if __name__ == "__main__":
    run()
