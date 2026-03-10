import tkinter as tk
from tkinter import ttk, messagebox, font, filedialog
from PIL import Image, ImageTk
import threading
from datetime import datetime
import os
import sys
from typing import Dict, Any, List, Optional, Tuple, Callable, Union

from ..engines.manager import EngineManager
from ..utils.persistence import PersistenceManager
from ..utils.calculator import QualityCalculator
from ..utils.logger import logger
from .components.graph import DynamicGraph
from ..constants import COLORS, VERSION, APP_TITLE, WINDOW_SIZE, SEMAPHORE_COLORS, SCHEDULER_ICON_PATH, ICON_PATH


# Módulo da Interface Principal

class InternetQualityApp:
    # Class-level type hints for attributes
    root: tk.Tk
    engine_manager: EngineManager
    persistence: PersistenceManager
    calculator: QualityCalculator
    current_records: List[Dict[str, Any]]
    is_measuring: bool
    
    # Scheduling State
    schedule_active: bool
    schedule_interval: int
    schedule_unit: str  # "Minuto(s)" ou "Segundo(s)"
    schedule_is_deep: bool
    next_run: Optional[datetime]
    schedule_modal: Optional[tk.Toplevel]
    
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
    lbl_packet_loss: tk.Label
    lbl_grade: tk.Label
    lbl_interface: tk.Label
    lbl_connection_type: tk.Label
    lbl_ip_server: tk.Label
    graph: DynamicGraph
    btn_measure: tk.Button
    btn_deep_measure: tk.Button
    btn_schedule: tk.Button
    btn_clear: tk.Button
    btn_logs: tk.Button
    tree: ttk.Treeview
    table_cols: List[Tuple[str, str]]
    adequacy_items: Dict[str, tk.Label]
    logo_img: Optional[ImageTk.PhotoImage]

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
        self.is_measuring = False
        self.logo_img = None

        # Configurações iniciais do Agendamento (Default da Issue)
        self.schedule_active = False
        self.schedule_interval = 1
        self.schedule_unit = "Minuto(s)"
        self.schedule_is_deep = False
        self.next_run = None
        self.schedule_modal = None

        self._apply_theme()
        self._setup_main_scroll()
        self._create_widgets()
        self._load_history()
        
        # Inicia o loop de monitoramento de agendamentos (roda a cada ~1 segundo invisivelmente)
        self.root.after(1000, self._check_schedule)

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
        
        # App Icon
        try:
            if os.path.exists(ICON_PATH):
                original = Image.open(ICON_PATH)
                # O ICO pode ter múltiplas camadas, pegamos a maior ou a que desejamos
                resized = original.resize((40, 40), Image.Resampling.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(resized)
                icon_lbl = tk.Label(header, image=self.logo_img, bg=COLORS["bg"])
                icon_lbl.pack(side=tk.LEFT, padx=(0, 12))
        except Exception as e:
            logger.warning(f"Erro ao carregar ícone do topo: {e}")

        # Modern Fonts Check
        title_font_bold = ("Rubik", 24, "bold") if "Rubik" in font.families() else ("Segoe UI Variable Display", 24, "bold")
        title_font_reg = ("Rubik", 24) if "Rubik" in font.families() else ("Segoe UI Variable Display", 24)

        tk.Label(header, text="PyTest", bg=COLORS["bg"], fg=COLORS["text"], font=title_font_bold).pack(side=tk.LEFT)
        tk.Label(header, text="Connection", bg=COLORS["bg"], fg=COLORS["accent"], font=title_font_reg).pack(side=tk.LEFT, padx=2)
        
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
        self.lbl_jitter.pack(side=tk.LEFT, padx=(0, 30))
        self.lbl_packet_loss = tk.Label(latency, text="Perda de pacotes: --", bg=COLORS["card"], fg=COLORS["text"], font=("Segoe UI", 12))
        self.lbl_packet_loss.pack(side=tk.LEFT)

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
        self.btn_measure = tk.Button(btns, text="TESTE RÁPIDO", command=lambda: self._start_measurement(deep_test=False), bg=COLORS["accent"], fg=COLORS["bg"], font=("Segoe UI", 12, "bold"), bd=0, padx=15, pady=12, activebackground=COLORS["accent_dim"], cursor="hand2")
        self.btn_measure.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.btn_deep_measure = tk.Button(btns, text="TESTE PROFUNDO", command=lambda: self._start_measurement(deep_test=True), bg="#8b5cf6", fg=COLORS["bg"], font=("Segoe UI", 12, "bold"), bd=0, padx=15, pady=12, activebackground="#7c3aed", cursor="hand2")
        self.btn_deep_measure.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.btn_schedule = tk.Button(btns, text="AGENDAMENTO INATIVO", command=self._open_schedule_modal, bg=COLORS["card"], fg=COLORS["error"], font=("Segoe UI", 12, "bold"), bd=0, padx=15, pady=12, activebackground="#334155", cursor="hand2")
        self.btn_schedule.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.btn_clear = tk.Button(btns, text="LIMPAR", command=self._clear_ui, bg=COLORS["card"], fg=COLORS["text"], font=("Segoe UI", 12, "bold"), bd=0, padx=15, pady=12, activebackground="#334155", cursor="hand2")
        self.btn_clear.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.btn_logs = tk.Button(btns, text="VER LOGS", command=self._view_logs, bg=COLORS["card"], fg=COLORS["accent"], font=("Segoe UI", 12, "bold"), bd=0, padx=15, pady=12, activebackground="#334155", cursor="hand2")
        self.btn_logs.pack(side=tk.LEFT, fill=tk.X, expand=True)

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

        # Table with dedicated Scrollbar
        history_frame = tk.Frame(self.main_container, bg=COLORS["bg"])
        history_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))

        self.table_cols = [
            ("Data", "DATA"), ("Hora", "HORA"), ("Download", "DOWNLOAD"), 
            ("Upload", "UPLOAD"), ("Ping", "PING"), ("Jitter", "JITTER"), 
            ("PerdaPacotes", "PERDA"), ("Interface", "PROVEDOR"), ("Conexão", "CONEXÃO"), ("Nota", "NOTA")
        ]
        cols = [c[0] for c in self.table_cols]
        self.tree = ttk.Treeview(history_frame, columns=cols, show="headings", style="Treeview", height=8)
        
        # Scrollbar for Treeview
        tree_scroll = ttk.Scrollbar(history_frame, orient="vertical", command=self.tree.yview, style="Vertical.TScrollbar")
        self.tree.configure(yscrollcommand=tree_scroll.set)
        
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        for col, head in self.table_cols:
            self.tree.heading(col, text=head)
            self.tree.column(col, width=90, anchor="center")
        self.tree.column("Interface", width=120)
        self.tree.column("Conexão", width=120)
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

    def _start_measurement(self, deep_test: bool = False, force_close_modal: bool = False) -> None:
        # Quando acionado via automação agendada, garantimos a destruição e interrupção da modal e árvore
        if force_close_modal and self.schedule_modal and self.schedule_modal.winfo_exists():
            self.schedule_modal.destroy()
            self.schedule_modal = None
            
        self._clear_ui() # Resetar tudo antes de começar, como solicitado
        self.btn_measure.config(state="disabled")
        self.btn_deep_measure.config(state="disabled")
        self.btn_schedule.config(state="disabled")
        self.btn_clear.config(state="disabled")
        self.is_measuring = True
        self.progress['value'] = 0
        status_text = "Avaliando conexão (Teste Profundo)..." if deep_test else "Avaliando conexão..."
        self.lbl_status.config(text=status_text)
        threading.Thread(target=self._measurement_task, args=(deep_test,), daemon=True).start()

    def _measurement_task(self, deep_test: bool) -> None:
        try:
            def callback(m_type: str, val: Any) -> None:
                if m_type == "progress": self.root.after(0, lambda: self.progress.config(value=val))
                elif m_type == "status": self.root.after(0, lambda: self.lbl_status.config(text=val))
                elif m_type == "download":
                    self.root.after(0, lambda: self.graph.update_graph(dl_val=val))
                    self.root.after(0, lambda: self.lbl_download.config(text=f"{val:.2f} Mbps"))
                elif m_type == "upload":
                    self.root.after(0, lambda: self.graph.update_graph(ul_val=val))
                    self.root.after(0, lambda: self.lbl_upload.config(text=f"{val:.2f} Mbps"))
                elif m_type == "ping": self.root.after(0, lambda: self.lbl_ping.config(text=f"Ping: {val:.2f} ms"))
                elif m_type == "jitter": self.root.after(0, lambda: self.lbl_jitter.config(text=f"Jitter: {val:.2f} ms"))
                elif m_type == "packet_loss": self.root.after(0, lambda: self.lbl_packet_loss.config(text=f"Perda de pacotes: {val}"))
                elif m_type == "connection_type": self.root.after(0, lambda: self.lbl_connection_type.config(text=f"CONEXÃO: {val}"))
                elif m_type == "interface": self.root.after(0, lambda: self.lbl_interface.config(text=f"ISP: {val}"))
                elif m_type == "ip": self.root.after(0, lambda: self._update_ip_server(ip=val))
                elif m_type == "server": self.root.after(0, lambda: self._update_ip_server(server=val))

            results = self.engine_manager.run_measurement(callback=callback, deep_test=deep_test)

            # Barreira: Não salvar resultados com qualquer métrica zerada
            zero_metrics = [k for k in ("download", "upload", "ping", "jitter") if results.get(k, 0) <= 0]
            if zero_metrics:
                desc = ", ".join(zero_metrics)
                logger.warning(f"Resultado descartado: métricas zeradas ({desc}).")
                self.root.after(0, lambda: self.lbl_status.config(
                    text="Teste falhou — resultado inconsistente descartado."))
                return

            score = self.calculator.calculate_score(results)
            scenarios = self.calculator.evaluate_scenarios(results, score)
            
            self.root.after(0, lambda: self._update_ui(results, score, scenarios))
            
            now = datetime.now()
            record: Dict[str, Any] = {
                "date": now.strftime("%d/%m/%Y"), "time": now.strftime("%H:%M:%S"),
                "download": results["download"], "upload": results["upload"],
                "ping": results["ping"], "jitter": results.get("jitter", 0),
                "packet_loss": results.get("packet_loss", "0/10 (0%)"),
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
            self.is_measuring = False
            self.root.after(0, lambda: [
                self.btn_measure.config(state="normal"), 
                self.btn_deep_measure.config(state="normal"),
                self.btn_schedule.config(state="normal"),
                self.btn_clear.config(state="normal"),
                self.btn_logs.config(state="normal"),
                self.lbl_status.config(text="Teste finalizado")
            ])

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
        
        loss = res.get('packet_loss', '--')
        self.lbl_packet_loss.config(text=f"Perda de pacotes: {loss}")
        
        self.lbl_grade.config(text=str(score), fg=color)
        self.lbl_interface.config(text=f"STATUS: {text} | ISP: {res.get('interface', '--')}", fg=color)
        self.lbl_connection_type.config(text=f"CONEXÃO: {res.get('connection_type', '--')}")
        
        self.lbl_ip_server.config(text=f"IP: {res.get('ip', '--')} | Servidor: {res.get('server', '--')}")
        
    def _update_ip_server(self, ip: Optional[str] = None, server: Optional[str] = None) -> None:
        current = self.lbl_ip_server.cget("text")
        # Formato: "IP: -- | Servidor: --"
        parts = current.split(" | ")
        curr_ip = parts[0].replace("IP: ", "") if len(parts) > 0 else "--"
        curr_server = parts[1].replace("Servidor: ", "") if len(parts) > 1 else "--"
        
        new_ip = ip if ip else curr_ip
        new_server = server if server else curr_server
        self.lbl_ip_server.config(text=f"IP: {new_ip} | Servidor: {new_server}")

    def _update_ui(self, res: Dict[str, Any], score: Union[int, str], scen: Dict[str, int]) -> None:
        # Mapeamento de cor e adjetivo
        score_val = int(score) if str(score).isdigit() else 0
        if score_val >= 95: text, color = "EXCELENTE", COLORS["success"]
        elif score_val >= 80: text, color = "MUITO BOA", COLORS["accent"]
        elif score_val >= 60: text, color = "ESTÁVEL", "#94a3b8"
        elif score_val >= 40: text, color = "LIMITADA", COLORS["ul"]
        else: text, color = "INSTÁVEL", COLORS["error"]

        self.lbl_download.config(text=f"{res['download']:.2f} Mbps")
        self.lbl_upload.config(text=f"{res['upload']:.2f} Mbps")
        self.lbl_ping.config(text=f"Ping: {res['ping']:.2f} ms")
        self.lbl_jitter.config(text=f"Jitter: {res.get('jitter', 0):.2f} ms")
        self.lbl_packet_loss.config(text=f"Perda de pacotes: {res.get('packet_loss', '--')}")
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
        if self.is_measuring:
            self.tree.selection_set(())
            return
        sel = self.tree.selection()
        if not sel: return
        r = self.current_records[int(sel[0])]
        try:
            res = {
                "download": float(r.get("Download", 0)), "upload": float(r.get("Upload", 0)),
                "ping": float(r.get("Ping", 0)), "jitter": float(r.get("Jitter", 0)),
                "packet_loss": r.get("PerdaPacotes", "--"),
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
        self.lbl_packet_loss.config(text="Perda de pacotes: --")
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

    def _view_logs(self):
        """Abre seletor para escolher qual log visualizar diretamente."""
        from ..constants import LOG_DIR

        # Abre o diálogo padrão do Windows para selecionar o arquivo .log
        log_file = filedialog.askopenfilename(
            initialdir=LOG_DIR,
            title="Selecionar Log para Visualização",
            filetypes=[("Arquivos de Log", "*.log"), ("Todos os arquivos", "*.*")]
        )
        
        if not log_file: # Usuário cancelou
            return

        try:
            # Como agora o log é texto puro, abrimos diretamente no editor padrão
            os.startfile(log_file)
            logger.info(f"Visualizando log: {os.path.basename(log_file)}")
        except Exception as e:
            logger.error(f"Erro ao abrir arquivo de log: {e}")
            messagebox.showerror("Erro de I/O", f"Não foi possível abrir este arquivo: {e}")

    def _calculate_next_run(self, from_time: datetime, interval: int, unit: str) -> datetime:
        from datetime import timedelta
        if unit == "Hora(s)":
            base = from_time.replace(minute=0, second=0, microsecond=0)
            next_t = base + timedelta(hours=interval)
            if next_t <= from_time:
                next_t += timedelta(hours=interval)
            return next_t
        else: # Minutos
            base = from_time.replace(second=0, microsecond=0)
            minutes_to_add = interval - (base.minute % interval)
            next_t = base + timedelta(minutes=minutes_to_add)
            if next_t <= from_time:
                next_t += timedelta(minutes=interval)
            return next_t

    def _check_schedule(self) -> None:
        """Loop infinito invisível do Tkinter acionado a cada 1 segundo para o relógio de agendamento"""
        self.root.after(1000, self._check_schedule) # Programa o próximo pulso
        
        if not self.schedule_active or not self.next_run:
            return
            
        now = datetime.now()
        # Fallback in case type checker thinks it is None
        next_run_val = self.next_run
        if next_run_val and now >= next_run_val:
            # A hora chegou. 
            if self.is_measuring:
                # Conflito: O usuário já está rodando um teste manualmente. Ignite/Skip run.
                logger.info("Agendamento bloqueado para não intervir no teste manual (skip this run).")
            else:
                # Caminho Limpo: Dispare o teste. 
                logger.info(f"Executando agendamento autônomo. Teste Profundo: {self.schedule_is_deep}")
                # Passa a flag par fechar possíveis modais abertas
                self._start_measurement(deep_test=self.schedule_is_deep, force_close_modal=True)
            
            # Independentemente se foi skippado (usuário ocupado) ou rodado, agenda o próximo horário previsto
            self.next_run = self._calculate_next_run(datetime.now(), self.schedule_interval, self.schedule_unit)

    def _open_schedule_modal(self) -> None:
        if self.schedule_modal and self.schedule_modal.winfo_exists():
            self.schedule_modal.focus_set()
            return
            
        self.schedule_modal = tk.Toplevel(self.root)
        self.schedule_modal.title("Configurar Agendamento")
        
        # Define o ícone da janela secundária
        try:
            if os.path.exists(SCHEDULER_ICON_PATH):
                self.schedule_modal.iconbitmap(SCHEDULER_ICON_PATH)
        except Exception as e:
            logger.warning(f"Não foi possível carregar o ícone de agendamento: {e}")

        self.schedule_modal.geometry("350x450")
        self.schedule_modal.configure(bg=COLORS["bg"])
        self.schedule_modal.resizable(False, False)
        
        # Center Modal
        self.root.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() / 2) - (350 / 2)
        y = self.root.winfo_y() + (self.root.winfo_height() / 2) - (450 / 2)
        self.schedule_modal.geometry(f"+{int(x)}+{int(y)}")
        
        # Make modal block main window
        self.schedule_modal.transient(self.root)
        self.schedule_modal.grab_set()
        
        # UI Elements
        container = tk.Frame(self.schedule_modal, bg=COLORS["bg"], padx=20, pady=20)
        container.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(container, text="Agendamento de Testes", font=("Segoe UI", 16, "bold"), bg=COLORS["bg"], fg=COLORS["text"]).pack(pady=(0, 20))
        
        # === Intervalo e Unidade ===
        frame_time = tk.Frame(container, bg=COLORS["bg"])
        frame_time.pack(fill=tk.X, pady=10)
        tk.Label(frame_time, text="Intervalo de Execução:", font=("Segoe UI", 10), bg=COLORS["bg"], fg=COLORS["text_dim"]).pack(anchor="w")
        
        entry_frame = tk.Frame(frame_time, bg=COLORS["bg"])
        entry_frame.pack(fill=tk.X, pady=5)
        
        var_interval = tk.StringVar(value=str(self.schedule_interval))
        entry_interval = tk.Entry(entry_frame, textvariable=var_interval, width=5, font=("Segoe UI", 12), justify="center")
        entry_interval.pack(side=tk.LEFT, padx=(0, 10))
        
        def adjust_interval(delta):
            try:
                current = int(var_interval.get())
            except ValueError:
                current = 1
            max_val = 24 if var_unit.get() == "Hora(s)" else 60
            new_val = max(1, min(current + delta, max_val))
            var_interval.set(str(new_val))
                
        tk.Button(entry_frame, text="-", command=lambda: adjust_interval(-1), width=2, bg=COLORS["card"], fg=COLORS["text"]).pack(side=tk.LEFT, padx=2)
        tk.Button(entry_frame, text="+", command=lambda: adjust_interval(1), width=2, bg=COLORS["card"], fg=COLORS["text"]).pack(side=tk.LEFT, padx=(2, 10))
        
        var_unit = tk.StringVar(value=self.schedule_unit)
        combo_unit = ttk.Combobox(entry_frame, textvariable=var_unit, values=["Minuto(s)", "Hora(s)"], state="readonly", width=12, font=("Segoe UI", 10))
        combo_unit.pack(side=tk.LEFT)
        
        def sanitize_interval(*args):
            val_str = var_interval.get()
            if not val_str:
                return
            clean_str = "".join(filter(str.isdigit, val_str))
            if clean_str != val_str:
                var_interval.set(clean_str)
                return
            if clean_str:
                val = int(clean_str)
                max_val = 24 if var_unit.get() == "Hora(s)" else 60
                if val > max_val:
                    var_interval.set(str(max_val))

        var_interval.trace_add("write", sanitize_interval)
        var_unit.trace_add("write", sanitize_interval)
        
        # === Tipo de Teste ===
        frame_type = tk.Frame(container, bg=COLORS["bg"])
        frame_type.pack(fill=tk.X, pady=15)
        tk.Label(frame_type, text="Tipo de Teste:", font=("Segoe UI", 10), bg=COLORS["bg"], fg=COLORS["text_dim"]).pack(anchor="w")
        
        var_is_deep = tk.BooleanVar(value=self.schedule_is_deep)
        tk.Radiobutton(frame_type, text="Teste Rápido", variable=var_is_deep, value=False, bg=COLORS["bg"], fg=COLORS["text"], selectcolor=COLORS["card"], activebackground=COLORS["bg"]).pack(anchor="w", pady=2)
        tk.Radiobutton(frame_type, text="Teste Profundo", variable=var_is_deep, value=True, bg=COLORS["bg"], fg=COLORS["text"], selectcolor=COLORS["card"], activebackground=COLORS["bg"]).pack(anchor="w", pady=2)

        # === Status ===
        frame_status = tk.Frame(container, bg=COLORS["bg"])
        frame_status.pack(fill=tk.X, pady=15)
        tk.Label(frame_status, text="Status do Agendamento:", font=("Segoe UI", 10), bg=COLORS["bg"], fg=COLORS["text_dim"]).pack(anchor="w")
        
        var_status = tk.BooleanVar(value=self.schedule_active)
        tk.Checkbutton(frame_status, text="Ativo", variable=var_status, bg=COLORS["bg"], fg=COLORS["text"], selectcolor=COLORS["card"], activebackground=COLORS["bg"]).pack(anchor="w", pady=2)

        # === Botões de Ação ===
        frame_actions = tk.Frame(container, bg=COLORS["bg"])
        frame_actions.pack(fill=tk.X, side=tk.BOTTOM, pady=10)
        
        # === Preview Label ===
        lbl_preview = tk.Label(container, text="", font=("Segoe UI", 9, "italic"), bg=COLORS["bg"], fg=COLORS["accent"])
        lbl_preview.pack(side=tk.BOTTOM, pady=(0, 20))

        def update_preview(*args):
            if not self.schedule_modal or not self.schedule_modal.winfo_exists():
                return
                
            if not var_status.get():
                lbl_preview.config(text="")
            else:
                try:
                    interval_val = int(var_interval.get())
                    if interval_val < 1: interval_val = 1
                except ValueError:
                    interval_val = 1
                    
                unit = var_unit.get()
                max_val = 24 if unit == "Hora(s)" else 60
                interval_val = min(interval_val, max_val)
                    
                predicted = self._calculate_next_run(datetime.now(), interval_val, unit)
                lbl_preview.config(text=f"Próxima execução: {predicted.strftime('%d/%m/%Y %H:%M')}")
                
            # Loop recursivo para garantir que a hora fique atualizando e rodando
            self.schedule_modal.after(1000, update_preview)

        var_interval.trace_add("write", lambda *args: update_preview())
        var_unit.trace_add("write", lambda *args: update_preview())
        var_status.trace_add("write", lambda *args: update_preview())
        update_preview()

        def save_changes():
            try:
                interval_val = int(var_interval.get())
                if interval_val < 1: interval_val = 1
            except ValueError:
                interval_val = 1
                
            unit = var_unit.get()
            max_val = 24 if unit == "Hora(s)" else 60
            interval_val = min(interval_val, max_val)
            
            self.schedule_interval = interval_val
            self.schedule_unit = unit
            self.schedule_is_deep = var_is_deep.get()
            self.schedule_active = var_status.get()
            
            if self.schedule_active:
                self.next_run = self._calculate_next_run(datetime.now(), self.schedule_interval, self.schedule_unit)
                self.btn_schedule.config(text="AGENDAMENTO ATIVO", fg=COLORS["success"]) # Update Main Button Color
            else:
                self.next_run = None
                self.btn_schedule.config(text="AGENDAMENTO INATIVO", fg=COLORS["error"]) # Reflete na UI
                
            logger.info(f"Agendamento atualizado. Ativo: {self.schedule_active}, Intevalo: {self.schedule_interval} {self.schedule_unit}")
            self.schedule_modal.destroy()
            self.schedule_modal = None

        def cancel_changes():
            self.schedule_modal.destroy()
            self.schedule_modal = None
            
        tk.Button(frame_actions, text="OK", command=save_changes, bg=COLORS["accent"], fg=COLORS["bg"], font=("Segoe UI", 10, "bold"), width=12, bd=0).pack(side=tk.RIGHT, padx=5)
        tk.Button(frame_actions, text="Cancelar", command=cancel_changes, bg=COLORS["card"], fg=COLORS["text"], font=("Segoe UI", 10), width=12, bd=0).pack(side=tk.RIGHT, padx=5)
        
        # Aguarda a janela ser fechada e libera
        self.schedule_modal.wait_window()

