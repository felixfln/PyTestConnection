import tkinter as tk
from src.ui.app import InternetQualityApp

def main():
    root = tk.Tk()
    app = InternetQualityApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
