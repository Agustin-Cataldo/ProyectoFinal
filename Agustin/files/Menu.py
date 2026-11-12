def mostrar_menu():
    print("\n--- MENÚ ---")
    print("1. Cargar stock")
    print("2. Mostrar total del stock")
    print("3. Mostrar cantidad de productos")
    print("4. Salir")
    opcion = int(input("Elija una opción: "))
    return opcion
def pedir_categoria():
    categoria = input("Tipo de producto a contar (enlatados, frutas, congelados, panaderia): ").lower()
    return categoria
