import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime
from ..engines.manager import EngineManager
from ..utils.persistence import PersistenceManager
from ..utils.calculator import QualityCalculator
from .components.graph import DynamicGraph

class InternetQualityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PyTestConnection - Qualidade da Internet")
        self.root.geometry("900x700")
        self.root.configure(bg="#121212")

        self.engine_manager = EngineManager()
        self.persistence = PersistenceManager()
        self.calculator = QualityCalculator()

        self._setup_styles()
        self._create_widgets()
        self._load_history()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#121212")
        style.configure("TLabel", background="#121212", foreground="#ffffff", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground="#00ffcc")
        style.configure("TButton", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", background="#1e1e1e", foreground="#ffffff", fieldbackground="#1e1e1e", rowheight=25)
        style.map("Treeview", background=[('selected', '#00ffcc')], foreground=[('selected', '#121212')])

    def _create_widgets(self):
        # Main Container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 4.1 Painel Principal
        results_frame = ttk.LabelFrame(main_frame, text=" Resultados da Medição ", padding="10")
        results_frame.pack(fill=tk.X, pady=5)

        self.lbl_download = ttk.Label(results_frame, text="Download: -- Mbps", style="Header.TLabel")
        self.lbl_download.grid(row=0, column=0, padx=20, pady=10)

        self.lbl_upload = ttk.Label(results_frame, text="Upload: -- Mbps", style="Header.TLabel")
        self.lbl_upload.grid(row=0, column=1, padx=20, pady=10)

        self.lbl_ping = ttk.Label(results_frame, text="Ping: -- ms")
        self.lbl_ping.grid(row=1, column=0)

        self.lbl_jitter = ttk.Label(results_frame, text="Jitter: -- ms")
        self.lbl_jitter.grid(row=1, column=1)

        self.lbl_grade = ttk.Label(results_frame, text="Nota: --", font=("Segoe UI", 24, "bold"), foreground="#ffd700")
        self.lbl_grade.grid(row=0, rowspan=2, column=2, padx=30)

        # Graph
        self.graph = DynamicGraph(results_frame, height=150, highlightthickness=0)
        self.graph.grid(row=2, column=0, columnspan=3, sticky="ew", pady=10)

        # 4.2 Botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)

        self.btn_measure = ttk.Button(btn_frame, text="MEDIR AGORA", command=self._start_measurement)
        self.btn_measure.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        self.btn_clear = ttk.Button(btn_frame, text="LIMPAR REGISTROS", command=self._clear_ui)
        self.btn_clear.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        # Checklist
        check_frame = ttk.LabelFrame(main_frame, text=" Adequação de Uso ", padding="10")
        check_frame.pack(fill=tk.X, pady=5)

        self.checks = {}
        scenarios = [
            ("social_media", "Redes Sociais"),
            ("hd_streaming", "Streaming HD"),
            ("video_conference", "Video Conferência"),
            ("gaming", "Jogos Online"),
            ("4k_streaming", "4K (Ultra HD)"),
            ("heavy_downloads", "Downloads Pesados")
        ]
        for i, (key, label) in enumerate(scenarios):
            var = tk.BooleanVar(value=False)
            cb = tk.Checkbutton(check_frame, text=label, variable=var, state="disabled", bg="#121212", fg="#ffffff", selectcolor="#1e1e1e", disabledforeground="#666666")
            cb.grid(row=i//3, column=i%3, sticky="w", padx=20)
            self.checks[key] = var

        # 4.3 Lista de Registros
        history_frame = ttk.LabelFrame(main_frame, text=" Histórico de Medições ", padding="10")
        history_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        columns = ("date", "time", "download", "upload", "ping", "grade")
        self.tree = ttk.Treeview(history_frame, columns=columns, show="headings")
        self.tree.heading("date", text="Data")
        self.tree.heading("time", text="Hora")
        self.tree.heading("download", text="Download")
        self.tree.heading("upload", text="Upload")
        self.tree.heading("ping", text="Ping")
        self.tree.heading("grade", text="Nota")
        
        self.tree.column("date", width=100)
        self.tree.column("time", width=80)
        self.tree.column("download", width=100)
        self.tree.column("upload", width=100)
        self.tree.column("ping", width=80)
        self.tree.column("grade", width=80)

        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

    def _start_measurement(self):
        self.btn_measure.config(state="disabled")
        self.graph.clear()
        threading.Thread(target=self._measurement_task, daemon=True).start()

    def _measurement_task(self):
        try:
            def sync_callback(m_type, value):
                self.root.after(0, lambda: self.graph.update_graph(value))
                if m_type == "download":
                    self.root.after(0, lambda: self.lbl_download.config(text=f"Download: {value:.2f} Mbps"))
                elif m_type == "upload":
                    self.root.after(0, lambda: self.lbl_upload.config(text=f"Upload: {value:.2f} Mbps"))
                elif m_type == "ping":
                    self.root.after(0, lambda: self.lbl_ping.config(text=f"Ping: {value:.2f} ms"))

            results = self.engine_manager.run_measurement(callback=sync_callback)
            
            # Calculate quality
            score = self.calculator.calculate_score(results)
            scenarios = self.calculator.evaluate_scenarios(results, score)
            
            # Update UI
            self.root.after(0, lambda: self._update_final_results(results, score, scenarios))
            
            # Persistence
            now = datetime.now()
            record = {
                "date": now.strftime("%d/%m/%Y"),
                "time": now.strftime("%H:%M:%S"),
                "download": results["download"],
                "upload": results["upload"],
                "ping": results["ping"],
                "jitter": results["jitter"],
                "packet_loss": results.get("packet_loss", 0),
                "server": results["server"],
                "interface": results["interface"],
                "ip": results["ip"],
                "grade": score,
                **scenarios
            }
            self.persistence.save_record(record)
            self.root.after(0, self._load_history)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Erro na Medição", str(e)))
        finally:
            self.root.after(0, lambda: self.btn_measure.config(state="normal"))

    def _update_final_results(self, results, score, scenarios):
        self.lbl_download.config(text=f"Download: {results['download']:.2f} Mbps")
        self.lbl_upload.config(text=f"Upload: {results['upload']:.2f} Mbps")
        self.lbl_ping.config(text=f"Ping: {results['ping']:.2f} ms")
        self.lbl_jitter.config(text=f"Jitter: {results['jitter']:.2f} ms")
        self.lbl_grade.config(text=f"Nota: {score}")
        
        for key, val in scenarios.items():
            if key in self.checks:
                self.checks[key].set(bool(val))

    def _load_history(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        records = self.persistence.load_records()
        for r in records:
            self.tree.insert("", tk.END, values=(
                r.get("Date"), r.get("Time"), r.get("Download"), 
                r.get("Upload"), r.get("Ping"), r.get("Grade")
            ))

    def _clear_ui(self):
        self._clear_history_file()
        self._load_history()
        self.lbl_download.config(text="Download: -- Mbps")
        self.lbl_upload.config(text="Upload: -- Mbps")
        self.lbl_ping.config(text="Ping: -- ms")
        self.lbl_jitter.config(text="Jitter: -- ms")
        self.lbl_grade.config(text="Nota: --")
        for var in self.checks.values():
            var.set(False)
        self.graph.clear()

    def _clear_history_file(self):
        if os.path.exists("data/data.txt"):
            with open("data/data.txt", "w", encoding="utf-8") as f:
                f.write("Date|Time|Download|Upload|Ping|Jitter|PacketLoss|Server|Interface|IP|SocialMedia|HDStreaming|VideoConf|Gaming|4K|HeavyDocs|Grade\n")
