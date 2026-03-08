import tkinter as tk
from vista import InterfazPuzzle

def main():
    # Creamos la ventana base
    root = tk.Tk()
    app = InterfazPuzzle(root)
    root.mainloop()

if __name__ == "__main__":
    main()
