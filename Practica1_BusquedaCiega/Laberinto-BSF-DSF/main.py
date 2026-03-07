import tkinter as tk
from ui import MazeSolverApp

def main():
    root = tk.Tk()              # Crea la ventana en blanco
    app = MazeSolverApp(root)   # El constructor arma toda la interfaz sobre ella
    root.mainloop()             # Enciende el motor para escuchar los clics

if __name__ == "__main__":
    main()
