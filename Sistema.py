import Menu
import Gestion_stock
def main():
    Gestion_stock.inicializar()
    opcion = 0
    while opcion != 4:
        opcion = Menu.mostrar_menu()
        if opcion == 1:
            Gestion_stock.cargar_stock()
        elif opcion == 2:
            Gestion_stock.mostrar_stock()
        elif opcion == 3:
            categoria = Menu.pedir_categoria()
            if categoria in Gestion_stock.stock_cantidades:
                Gestion_stock.contar(Gestion_stock.stock_cantidades[categoria])
            else:
                print("Categoría inválida.")
        elif opcion == 4:
            print("Chau!")
        else:
            print("Opción inválida.")
if __name__ == "__main__":
    main()
