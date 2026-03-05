import tkinter as tk

class DynamicGraph(tk.Canvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.dl_points = []
        self.ul_points = []
        self.max_val = 10
        self.bg_color = "#0f172a"
        self.grid_color = "#1e293b"
        self.dl_line_color = "#22d3ee" # Ciano
        self.ul_line_color = "#fbbf24" # Âmbar
        self.font = ("Segoe UI", 9)
        self.bind("<Configure>", lambda e: self._setup_axes())

    def _setup_axes(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 10: w = 400
        if h < 10: h = 200
        
        # Fundo
        self.create_rectangle(0, 0, w, h, fill=self.bg_color, outline="")
        
        # Grid horizontal (Velocidade)
        for i in range(1, 6):
            y = h - (h / 6) * i
            self.create_line(45, y, w, y, fill=self.grid_color, width=1)
            val = (self.max_val / 6) * i
            self.create_text(5, y, text=f"{val:.0f}", fill="#94a3b8", anchor="w", font=self.font)

        # Grid vertical (Tempo)
        for i in range(1, 11):
            x = 45 + ((w - 45) / 11) * i
            self.create_line(x, 0, x, h, fill=self.grid_color, width=1)

        # Legenda
        self.create_text(w-10, h-20, text="Mbps", fill="#94a3b8", anchor="e", font=self.font)
        self.create_text(60, 15, text="● Download", fill=self.dl_line_color, anchor="w", font=self.font)
        self.create_text(160, 15, text="● Upload", fill=self.ul_line_color, anchor="w", font=self.font)

    def update_graph(self, dl_val=None, ul_val=None):
        if dl_val is not None:
            self.dl_points.append(dl_val)
        if ul_val is not None:
            self.ul_points.append(ul_val)
            
        # Limita a 60 pontos (1 minuto a 1 amostra/seg ou similar)
        if len(self.dl_points) > 60: self.dl_points.pop(0)
        if len(self.ul_points) > 60: self.ul_points.pop(0)
            
        all_vals = [v for v in (self.dl_points + self.ul_points) if v is not None]
        curr_max = max(all_vals, default=10)
        
        if curr_max > self.max_val * 0.9 or curr_max < self.max_val * 0.4:
            self.max_val = max(curr_max * 1.3, 10)
            self._setup_axes()
        
        self._draw_lines()

    def _draw_lines(self):
        self.delete("line")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 10: w = 400
        if h < 10: h = 200
        start_x = 45
        
        # Download
        if len(self.dl_points) >= 2:
            points = []
            dx = (w - start_x) / (len(self.dl_points)-1)
            for i, val in enumerate(self.dl_points):
                x = start_x + (i * dx)
                y = h - (val / self.max_val) * (h * 0.8) - (h * 0.1)
                points.extend([x, y])
            self.create_line(points, fill=self.dl_line_color, width=3, smooth=True, tags="line", splinesteps=12)

        # Upload
        if len(self.ul_points) >= 2:
            points = []
            dx = (w - start_x) / (len(self.ul_points)-1)
            for i, val in enumerate(self.ul_points):
                x = start_x + (i * dx)
                y = h - (val / self.max_val) * (h * 0.8) - (h * 0.1)
                points.extend([x, y])
            self.create_line(points, fill=self.ul_line_color, width=3, smooth=True, tags="line", splinesteps=12)

    def clear(self):
        self.dl_points = []
        self.ul_points = []
        self._setup_axes()
