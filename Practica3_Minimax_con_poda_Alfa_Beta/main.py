import tkinter as tk
from gui import GameGUI

def main():
    root = tk.Tk()

    # Para sistemas Windows o Linux (como WSL renderizado con servidor X),
    # esto fuerza un estilo más limpio si el sistema operativo lo permite.
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass  # Ignorar en sistemas no Windows o si falla

    app = GameGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()