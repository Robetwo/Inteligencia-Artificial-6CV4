import customtkinter as ctk
from gui import GameGUI

def main():
    # Inicializar la raíz usando CustomTkinter
    root = ctk.CTk()

    # Manejo de DPI (seguro para cualquier SO)
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    app = GameGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()