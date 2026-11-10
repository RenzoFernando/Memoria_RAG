"""Chat de consola con memoria a corto, medio y largo plazo."""
from gestor import GestorMemoria


def main():
    gestor = GestorMemoria()
    print("Chat con memoria. Escriba 'salir' para terminar.\n")
    while True:
        texto = input("Usted: ").strip()
        if texto.lower() in {"salir", "exit"}:
            gestor.cerrar_sesion()
            print("Sesión guardada. Hasta pronto.")
            break
        if texto:
            print(f"Asistente: {gestor.conversar(texto)}\n")


if __name__ == "__main__":
    main()
