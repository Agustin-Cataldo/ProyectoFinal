stock_productos = {'enlatados': [], 'frutas': [], 'congelados': [], 'panaderia': []}
stock_cantidades = {'enlatados': [], 'frutas': [], 'congelados': [], 'panaderia': []}
def inicializar():
    "Deja los diccionarios de stock vacíos, listos para cargar productos."
    for categoria in stock_productos:
        stock_productos[categoria] = []
    for categoria in stock_cantidades:
        stock_cantidades[categoria] = []
def cargar_stock():
    categoria = input("Categoría (enlatados, frutas, congelados, panaderia): ").lower()
    if categoria in stock_productos:
        producto = input("Producto a añadir: ")
        cantidad = int(input("Cantidad: "))
        stock_productos[categoria].append(producto)
        stock_cantidades[categoria].append(cantidad)
        print("Producto cargado.")
    else:
        print("Categoría inválida.")
def mostrar_stock():
    print("--- PRODUCTOS ---")
    for categoria in stock_productos:
        print(categoria, ":", stock_productos[categoria])
    print("--- CANTIDADES ---")
    for categoria in stock_cantidades:
        print(categoria, ":", stock_cantidades[categoria])
def contar(lista_productos):
    total = 0
    for cantidad in lista_productos:
        total = total + cantidad
    print("Cantidad de productos:", len(lista_productos))
    print("Suma de las cantidades:", total)