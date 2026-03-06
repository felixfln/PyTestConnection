import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime
import os
import sys
from typing import Dict, Any, List, Optional, Callable, Union

from ..engines.manager import EngineManager
from ..utils.persistence import PersistenceManager
from ..utils.calculator import QualityCalculator
from ..utils.logger import logger
from .components.graph import DynamicGraph
from ..constants import COLORS, VERSION, APP_TITLE, WINDOW_SIZE, SEMAPHORE_COLORS


# Módulo da Interface Principal

class InternetQualityApp:
    # Class-level type hints for attributes
    root: tk.Tk
    engine_manager: EngineManager
    persistence: PersistenceManager
    calculator: QualityCalculator
    current_records: List[Dict[str, Any]]
    is_measuring: bool
    
    # UI Components
    canvas: tk.Canvas
    scrollbar: ttk.Scrollbar
    scrollable_frame: tk.Frame
    main_container: tk.Frame
    progress: ttk.Progressbar
    lbl_status: tk.Label
    lbl_download: tk.Label
    lbl_upload: tk.Label
    lbl_ping: tk.Label
    lbl_jitter: tk.Label
    lbl_grade: tk.Label
    lbl_interface: tk.Label
    lbl_connection_type: tk.Label
    lbl_ip_server: tk.Label
    graph: DynamicGraph
    btn_measure: tk.Button
    btn_clear: tk.Button
    tree: ttk.Treeview
    adequacy_items: Dict[str, tk.Label]

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.configure(bg=COLORS["bg"])

        logger.info("Iniciando aplicação PyTestConnection")
        self.engine_manager = EngineManager()
        self.persistence = PersistenceManager()
        self.calculator = QualityCalculator()
        self.current_records = []

        self._apply_theme()
        self._setup_main_scroll()
        self._create_widgets()
        self._load_history()

    def _apply_theme(self) -> None:
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background=COLORS["bg"])
        style.configure("Vertical.TScrollbar", troughcolor=COLORS["bg"], background=COLORS["card"], borderwidth=0, arrowsize=10)
        style.configure("TProgressbar", thickness=15, troughcolor=COLORS["card"], background=COLORS["accent"], borderwidth=0)
        
        style.configure("Treeview", 
                        background=COLORS["card"], 
                        foreground=COLORS["text"], 
                        fieldbackground=COLORS["card"], 
                        rowheight=35,
                        borderwidth=0,
                        font=("Segoe UI", 9))
        style.configure("Treeview.Heading", 
                        background=COLORS["bg"], 
                        foreground=COLORS["accent"], 
                        font=("Segoe UI", 9, "bold"),
                        borderwidth=0)
        style.map("Treeview", background=[('selected', COLORS["accent_dim"])])

    def _setup_main_scroll(self) -> None:
        self.canvas = tk.Canvas(self.root, bg=COLORS["bg"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview, style="Vertical.TScrollbar")
        self.scrollable_frame = tk.Frame(self.canvas, bg=COLORS["bg"])

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Mouse wheel
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    def _create_widgets(self) -> None:
        self.main_container = tk.Frame(self.scrollable_frame, bg=COLORS["bg"])
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        # Header
        header = tk.Frame(self.main_container, bg=COLORS["bg"])
        header.pack(fill=tk.X, pady=(0, 10))
        tk.Label(header, text="PYTEST", bg=COLORS["bg"], fg=COLORS["text"], font=("Segoe UI", 24, "bold")).pack(side=tk.LEFT)
        tk.Label(header, text="CONNECTION", bg=COLORS["bg"], fg=COLORS["accent"], font=("Segoe UI", 24, "bold")).pack(side=tk.LEFT, padx=5)
        
        # Progress
        self.progress = ttk.Progressbar(self.main_container, orient=tk.HORIZONTAL, mode='determinate', style="TProgressbar")
        self.progress.pack(fill=tk.X, pady=(0, 10))
        self.lbl_status = tk.Label(self.main_container, text="Aguardando início...", bg=COLORS["bg"], fg=COLORS["accent"], font=("Segoe UI", 10, "bold"))
        self.lbl_status.pack()

        # Stats Card
        card = tk.Frame(self.main_container, bg=COLORS["card"], padx=30, pady=30, highlightbackground=COLORS["accent_dim"], highlightthickness=1)
        card.pack(fill=tk.X, pady=10)

        left = tk.Frame(card, bg=COLORS["card"])
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Speed Row
        speeds = tk.Frame(left, bg=COLORS["card"])
        speeds.pack(fill=tk.X)
        self.lbl_download = tk.Label(speeds, text="-- Mbps", bg=COLORS["card"], fg=COLORS["accent"], font=("Segoe UI", 36, "bold"))
        self.lbl_download.pack(side=tk.LEFT)
        tk.Label(speeds, text="DOWNLOAD", bg=COLORS["card"], fg=COLORS["text_dim"], font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(5, 40), pady=(15, 0))
        
        self.lbl_upload = tk.Label(speeds, text="-- Mbps", bg=COLORS["card"], fg=COLORS["ul"], font=("Segoe UI", 36, "bold"))
        self.lbl_upload.pack(side=tk.LEFT)
        tk.Label(speeds, text="UPLOAD", bg=COLORS["card"], fg=COLORS["text_dim"], font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=5, pady=(15, 0))

        # Latency Row
        latency = tk.Frame(left, bg=COLORS["card"])
        latency.pack(fill=tk.X, pady=(20, 0))
        self.lbl_ping = tk.Label(latency, text="Ping: -- ms", bg=COLORS["card"], fg=COLORS["text"], font=("Segoe UI", 12))
        self.lbl_ping.pack(side=tk.LEFT, padx=(0, 30))
        self.lbl_jitter = tk.Label(latency, text="Jitter: -- ms", bg=COLORS["card"], fg=COLORS["text"], font=("Segoe UI", 12))
        self.lbl_jitter.pack(side=tk.LEFT)

        # Right Side (Grade & Extra Info)
        right = tk.Frame(card, bg=COLORS["card"])
        right.pack(side=tk.RIGHT, padx=10)
        self.lbl_grade = tk.Label(right, text="--", bg=COLORS["card"], fg=COLORS["success"], font=("Segoe UI", 64, "bold"))
        self.lbl_grade.pack()
        self.lbl_interface = tk.Label(right, text="Interface: --", bg=COLORS["card"], fg=COLORS["text_dim"], font=("Segoe UI", 9))
        self.lbl_interface.pack()
        self.lbl_connection_type = tk.Label(right, text="Conexão: --", bg=COLORS["card"], fg=COLORS["text_dim"], font=("Segoe UI", 9))
        self.lbl_connection_type.pack()
        self.lbl_ip_server = tk.Label(right, text="IP: -- | Servidor: --", bg=COLORS["card"], fg="#64748b", font=("Segoe UI", 8))
        self.lbl_ip_server.pack(pady=(5, 0))

        # Graph
        self.graph = DynamicGraph(self.main_container, height=220, highlightthickness=0)
        self.graph.pack(fill=tk.X, pady=15)

        # Buttons
        btns = tk.Frame(self.main_container, bg=COLORS["bg"])
        btns.pack(fill=tk.X, pady=5)
        self.btn_measure = tk.Button(btns, text="INICIAR AVALIAÇÃO", command=self._start_measurement, bg=COLORS["accent"], fg=COLORS["bg"], font=("Segoe UI", 12, "bold"), bd=0, padx=25, pady=12, activebackground=COLORS["accent_dim"], cursor="hand2")
        self.btn_measure.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.btn_clear = tk.Button(btns, text="LIMPAR RESULTADOS", command=self._clear_ui, bg=COLORS["card"], fg=COLORS["text"], font=("Segoe UI", 12, "bold"), bd=0, padx=25, pady=12, activebackground="#334155", cursor="hand2")
        self.btn_clear.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Adequacy
        adequacy = tk.Frame(self.main_container, bg=COLORS["bg"])
        adequacy.pack(fill=tk.X, pady=15)
        grid = tk.Frame(adequacy, bg=COLORS["bg"])
        grid.pack(fill=tk.X)
        scenarios = [("social_media", "Redes Sociais"), ("hd_streaming", "Streaming HD"), ("video_conference", "Videochamadas"), ("gaming", "Jogos Online"), ("4k_streaming", "Streaming 4K"), ("heavy_downloads", "Downloads Pesados")]
        self.adequacy_items = {}
        for i, (key, label) in enumerate(scenarios):
            f = tk.Frame(grid, bg=COLORS["card"], padx=15, pady=10, highlightbackground="#334155", highlightthickness=1)
            f.grid(row=i//3, column=i%3, sticky="nsew", padx=4, pady=4)
            grid.grid_columnconfigure(i%3, weight=1)
            tk.Label(f, text=label, bg=COLORS["card"], fg=COLORS["text"]).pack(side=tk.LEFT)
            ind = tk.Label(f, text="●", bg=COLORS["card"], fg="#475569", font=("Segoe UI", 16))
            ind.pack(side=tk.RIGHT)
            self.adequacy_items[key] = ind

        # Table
        self.table_cols = [
            ("Data", "DATA"), ("Hora", "HORA"), ("Download", "DOWNLOAD"), 
            ("Upload", "UPLOAD"), ("Ping", "PING"), ("Jitter", "JITTER"), 
            ("Interface", "PROVEDOR"), ("Conexão", "CONEXÃO"), ("Nota", "NOTA")
        ]
        cols = [c[0] for c in self.table_cols]
        self.tree = ttk.Treeview(self.main_container, columns=cols, show="headings", style="Treeview", height=8)
        for col, head in self.table_cols:
            self.tree.heading(col, text=head)
            self.tree.column(col, width=90, anchor="center")
        self.tree.column("Interface", width=120)
        self.tree.column("Conexão", width=120)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

    def _start_measurement(self) -> None:
        self._clear_ui() # Resetar tudo antes de começar, como solicitado
        self.btn_measure.config(state="disabled")
        self.btn_clear.config(state="disabled")
        self.progress['value'] = 0
        self.lbl_status.config(text="Avaliando conexão...")
        threading.Thread(target=self._measurement_task, daemon=True).start()

    def _measurement_task(self) -> None:
        try:
            def callback(m_type: str, val: Any) -> None:
                if m_type == "progress": self.root.after(0, lambda: self.progress.config(value=val))
                elif m_type == "download":
                    self.root.after(0, lambda: self.graph.update_graph(dl_val=val))
                    self.root.after(0, lambda: self.lbl_download.config(text=f"{val:.2f} Mbps"))
                elif m_type == "upload":
                    self.root.after(0, lambda: self.graph.update_graph(ul_val=val))
                    self.root.after(0, lambda: self.lbl_upload.config(text=f"{val:.2f} Mbps"))
                elif m_type == "ping": self.root.after(0, lambda: self.lbl_ping.config(text=f"Ping: {val:.2f} ms"))

            results = self.engine_manager.run_measurement(callback=callback)
            score = self.calculator.calculate_score(results)
            scenarios = self.calculator.evaluate_scenarios(results, score)
            
            self.root.after(0, lambda: self._update_ui(results, score, scenarios))
            
            now = datetime.now()
            record: Dict[str, Any] = {
                "date": now.strftime("%d/%m/%Y"), "time": now.strftime("%H:%M:%S"),
                "download": results["download"], "upload": results["upload"],
                "ping": results["ping"], "jitter": results.get("jitter", 0),
                "server": results["server"], "interface": results.get("interface", "--"),
                "connection_type": results.get("connection_type", "--"),
                "ip": results.get("ip", "--"), "grade": score, **scenarios
            }
            self.persistence.save_record(record)
            self.root.after(0, self._load_history)
        except Exception as e:
            logger.error(f"Erro durante tarefa de medição: {e}")
            self.root.after(0, lambda: messagebox.showerror("Erro de Rede", str(e)))
        finally:
            self.root.after(0, lambda: [self.btn_measure.config(state="normal"), self.btn_clear.config(state="normal"), self.lbl_status.config(text="Teste finalizado")])

    def _update_ui(self, res: Dict[str, Any], score: Union[int, str], scen: Dict[str, int]) -> None:
        # Mapeamento de cor e adjetivo baseado na pontuação 0-100
        score_val = int(score) if str(score).isdigit() else 0
        if score_val >= 95: text, color = "EXCELENTE", COLORS["success"]
        elif score_val >= 80: text, color = "MUITO BOA", COLORS["accent"]
        elif score_val >= 60: text, color = "ESTÁVEL", "#94a3b8"
        elif score_val >= 40: text, color = "LIMITADA", COLORS["ul"]
        else: text, color = "INSTÁVEL", COLORS["error"]

        self.lbl_download.config(text=f"{res['download']:.2f} Mbps")
        self.lbl_upload.config(text=f"{res['upload']:.2f} Mbps")
        self.lbl_ping.config(text=f"Ping: {res['ping']:.2f} ms")
        
        jit = res.get('jitter', 0)
        self.lbl_jitter.config(text=f"Jitter: {jit:.2f} ms" if jit > 0 else "Jitter: --")
        
        self.lbl_grade.config(text=str(score), fg=color)
        self.lbl_interface.config(text=f"STATUS: {text} | ISP: {res.get('interface', '--')}", fg=color)
        self.lbl_connection_type.config(text=f"CONEXÃO: {res.get('connection_type', '--')}")
        
        self.lbl_ip_server.config(text=f"IP: {res.get('ip', '--')} | Servidor: {res.get('server', '--')}")
        
        for k, v in scen.items():
            if k in self.adequacy_items:
                level = int(v) if str(v).isdigit() else 0
                self.adequacy_items[k].config(fg=SEMAPHORE_COLORS.get(level, COLORS["error"]))

    def _load_history(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        self.current_records = self.persistence.load_records()
        for i, r in enumerate(self.current_records):
            vals = [r.get(c[0], r.get(c[0].lower(), "--")) for c in self.table_cols]
            self.tree.insert("", tk.END, iid=str(i), values=vals)

    def _on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        r = self.current_records[int(sel[0])]
        try:
            res = {
                "download": float(r.get("Download", 0)), "upload": float(r.get("Upload", 0)),
                "ping": float(r.get("Ping", 0)), "jitter": float(r.get("Jitter", 0)),
                "ip": r.get("IP", "--"), "server": r.get("Servidor", "--"), 
                "interface": r.get("Interface", "--"), "connection_type": r.get("Conexão", "--")
            }
            score = r.get("Nota", "0")
            scen = {
                "social_media": r.get("RedesSociais", 0), "hd_streaming": r.get("StreamingHD", 0),
                "video_conference": r.get("VideoConf", 0), "gaming": r.get("Gaming", 0),
                "4k_streaming": r.get("Streaming4K", 0), "heavy_downloads": r.get("DownloadsPesados", 0)
            }
            self.graph.clear()
            self.graph.update_graph(dl_val=0, ul_val=0)
            self.graph.update_graph(dl_val=res["download"], ul_val=res["upload"])
            self._update_ui(res, score, scen)
        except: pass

    def _clear_ui(self):
        self.lbl_download.config(text="-- Mbps")
        self.lbl_upload.config(text="-- Mbps")
        self.lbl_ping.config(text="Ping: -- ms")
        self.lbl_jitter.config(text="Jitter: -- ms")
        self.lbl_grade.config(text="--")
        self.lbl_interface.config(text="Interface: --")
        self.lbl_connection_type.config(text="Conexão: --")
        self.lbl_ip_server.config(text="IP: -- | Servidor: --")
        self.graph.clear()
        self.graph.update_graph(dl_val=0, ul_val=0) # Resetar gráfico
        for i in self.adequacy_items.values(): i.config(fg="#475569")
        self.progress['value'] = 0
        self.lbl_status.config(text="Resultados limpos")
        self.tree.selection_set(()) # Desmarcar item selecionado na lista
