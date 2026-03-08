import tkinter as tk
from vista import InterfazJarras

if __name__ == "__main__":
    ventana_principal = tk.Tk()
    app = InterfazJarras(ventana_principal)
    ventana_principal.mainloop()
