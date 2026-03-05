import tkinter as tk

class DynamicGraph(tk.Canvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.data_points = []
        self.max_val = 100
        self._setup_axes()

    def _setup_axes(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 10: w = 400
        if h < 10: h = 200
        
        # Draw background
        self.create_rectangle(0, 0, w, h, fill="#1e1e1e", outline="")
        
        # Draw grid
        for i in range(1, 5):
            y = h - (h / 5) * i
            self.create_line(0, y, w, y, fill="#333333", dash=(4, 4))

    def update_graph(self, value):
        self.data_points.append(value)
        if len(self.data_points) > 50:
            self.data_points.pop(0)
            
        self.max_val = max(max(self.data_points, default=10), 10)
        self._draw_line()

    def _draw_line(self):
        self._setup_axes()
        w, h = self.winfo_width(), self.winfo_height()
        if not self.data_points: return
        
        points = []
        dx = w / max(len(self.data_points)-1, 1)
        for i, val in enumerate(self.data_points):
            x = i * dx
            y = h - (val / self.max_val) * (h * 0.8) - (h * 0.1)
            points.extend([x, y])
            
        if len(points) >= 4:
            self.create_line(points, fill="#00ffcc", width=2, smooth=True)

    def clear(self):
        self.data_points = []
        self._setup_axes()
