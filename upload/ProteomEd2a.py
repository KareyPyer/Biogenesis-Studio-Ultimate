#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  🧬 PROTEOMEDITOR v2.0 — Bio-Hacking JSON Editor & Scientific Visualizer     ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║  NOUVEAUTÉS v2.0 :                                                           ║
║  • Visualisation Matplotlib intégrée (Thème Sombre)                          ║
║  • Graphe de dépendances NetworkX (Opérons & Héritage)                       ║
║  • Heatmap des marqueurs épigénétiques                                       ║
║  • Mini-simulateur d'évolution cellulaire                                    ║
║  • Normalisation robuste des clés JSON (gestion des espaces superflus)       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import json
import re
import random
import hashlib
import webbrowser
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
import tkinter as tk
from tkinter import *
from tkinter import ttk, filedialog, messagebox, font as tkfont
from tkinter.scrolledtext import ScrolledText

# Bibliothèques de visualisation scientifique
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import networkx as nx

# =============================================================================
# THEME "BIO-HACKING LAB"
# =============================================================================
class BioTheme:
    BG_DARK = "#0a0f0f"
    BG_PANEL = "#0f1515"
    BG_EDITOR = "#0c1212"
    BG_TREE = "#0a0f0f"
    ACCENT_PRIMARY = "#00ff9d"      # Néon vert (ADN)
    ACCENT_SECONDARY = "#00d4ff"    # Cyan (électrophorèse)
    ACCENT_WARNING = "#ffcc00"      # Jaune (biohazard)
    ACCENT_DANGER = "#ff3366"       # Rouge (apoptose)
    ACCENT_PURPLE = "#b84dff"       # Violet (épigénétique)
    TEXT_PRIMARY = "#e0f2fe"
    TEXT_SECONDARY = "#8ba3b8"
    TEXT_MUTED = "#4a6a7a"
    BORDER = "#1a2a2a"
    SUCCESS = "#00cc66"
    ERROR = "#ff4444"
    
    FONT_MAIN = ("Consolas", 10)
    FONT_CODE = ("Consolas", 10)
    FONT_HEADER = ("Courier New", 12, "bold")
    FONT_TERMINAL = ("Courier New", 9)

# =============================================================================
# UTILITAIRE DE NORMALISATION JSON
# =============================================================================
class JsonNormalizer:
    @staticmethod
    def clean_keys(obj):
        """Nettoie les espaces superflus dans les clés JSON (ex: 'global ' -> 'global')"""
        if isinstance(obj, dict):
            return {k.strip(): JsonNormalizer.clean_keys(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [JsonNormalizer.clean_keys(item) for item in obj]
        return obj

# =============================================================================
# LOGGER DE LABO
# =============================================================================
class LabLogger:
    def __init__(self, text_widget):
        self.text = text_widget
        self.text.config(state=NORMAL)
        self.text.delete(1.0, END)
        self.text.config(state=DISABLED)

    def log(self, msg, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        icons = {
            "INFO": "🧪", "SUCCESS": "✅", "WARNING": "⚠️",
            "ERROR": "❌", "MUTATION": "🧬", "VALIDATION": "🔬", "SIM": "📈"
        }
        icon = icons.get(level, "📟")
        colors = {
            "INFO": BioTheme.TEXT_SECONDARY,
            "SUCCESS": BioTheme.SUCCESS,
            "WARNING": BioTheme.ACCENT_WARNING,
            "ERROR": BioTheme.ERROR,
            "MUTATION": BioTheme.ACCENT_PRIMARY,
            "VALIDATION": BioTheme.ACCENT_SECONDARY,
            "SIM": BioTheme.ACCENT_PURPLE
        }
        color = colors.get(level, BioTheme.TEXT_PRIMARY)
        self.text.config(state=NORMAL)
        self.text.insert(END, f"[{timestamp}] {icon} {msg}\n", ("log", color))
        self.text.see(END)
        self.text.config(state=DISABLED)
        self.text.tag_config("log", font=BioTheme.FONT_TERMINAL)
        self.text.tag_config("log", foreground=color)

    def info(self, msg): self.log(msg, "INFO")
    def success(self, msg): self.log(msg, "SUCCESS")
    def warning(self, msg): self.log(msg, "WARNING")
    def error(self, msg): self.log(msg, "ERROR")
    def mutation(self, msg): self.log(msg, "MUTATION")
    def validation(self, msg): self.log(msg, "VALIDATION")
    def sim(self, msg): self.log(msg, "SIM")

# =============================================================================
# ANALYSEUR DE MÉTRIQUES AVANCÉ
# =============================================================================
class ProteomeAnalyzer:
    @staticmethod
    def analyze(data):
        stats = {}
        stats["proteins_count"] = len(data.get("proteins", []))
        stats["operons_count"] = len(data.get("operons", []))
        stats["plasmids_count"] = len(data.get("plasmids", []))
        stats["transposons_count"] = len(data.get("global_transposons", []))
        
        # Phases cellulaires
        phases = [p.get("meta", {}).get("cell_phase", "unknown").strip() for p in data.get("proteins", [])]
        stats["phases"] = dict(Counter(phases))
        
        # Niveaux d'expression et poids
        stats["expression_data"] = []
        for p in data.get("proteins", []):
            meta = p.get("meta", {})
            stats["expression_data"].append({
                "id": p.get("id", "unknown").strip(),
                "weight": float(meta.get("weight", 1.0)),
                "expression": float(meta.get("expression_level", 1.0))
            })
            
        # Marqueurs épigénétiques
        marker_protein_map = defaultdict(list)
        for p in data.get("proteins", []):
            prot_id = p.get("id", "unknown").strip()
            for marker in p.get("epigenetic_markers", []):
                marker_protein_map[marker.strip()].append(prot_id)
        stats["epigenetic_heatmap"] = marker_protein_map
        
        return stats

# =============================================================================
# VISUALISATEUR SCIENTIFIQUE (MATPLOTLIB + NETWORKX)
# =============================================================================
class ProteomeVisualizer:
    def __init__(self, parent, data):
        self.data = data
        self.win = Toplevel(parent)
        self.win.title("🔬 VISUALISATION SCIENTIFIQUE DU PROTÉOME")
        self.win.geometry("1000x700")
        self.win.configure(bg=BioTheme.BG_DARK)
        self.win.transient(parent)
        
        # Notebook pour les onglets
        self.notebook = ttk.Notebook(self.win)
        self.notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Style du notebook
        style = ttk.Style()
        style.configure("TNotebook", background=BioTheme.BG_DARK)
        style.configure("TNotebook.Tab", background=BioTheme.BG_PANEL, foreground=BioTheme.TEXT_PRIMARY, font=BioTheme.FONT_MAIN)
        style.map("TNotebook.Tab", background=[("selected", BioTheme.BG_EDITOR)], foreground=[("selected", BioTheme.ACCENT_PRIMARY)])

        self._create_phase_tab()
        self._create_expression_tab()
        self._create_network_tab()
        self._create_heatmap_tab()
        self._create_simulation_tab()

    def _setup_plot_style(self, fig, ax, title):
        fig.patch.set_facecolor(BioTheme.BG_DARK)
        ax.set_facecolor(BioTheme.BG_PANEL)
        ax.tick_params(colors=BioTheme.TEXT_SECONDARY)
        ax.title.set_color(BioTheme.ACCENT_PRIMARY)
        ax.title.set_fontsize(14)
        ax.title.set_fontweight('bold')
        for spine in ax.spines.values():
            spine.set_color(BioTheme.BORDER)

    def _create_phase_tab(self):
        tab = Frame(self.notebook, bg=BioTheme.BG_DARK)
        self.notebook.add(tab, text="📊 Phases Cellulaires")
        
        stats = ProteomeAnalyzer.analyze(self.data)
        phases = stats["phases"]
        
        fig = Figure(figsize=(8, 6), dpi=100)
        ax = fig.add_subplot(111)
        self._setup_plot_style(fig, ax, "Distribution des Phases Cellulaires")
        
        colors = [BioTheme.ACCENT_PRIMARY, BioTheme.ACCENT_SECONDARY, BioTheme.ACCENT_PURPLE, BioTheme.ACCENT_WARNING, BioTheme.ACCENT_DANGER]
        ax.pie(phases.values(), labels=phases.keys(), autopct='%1.1f%%', 
               colors=colors[:len(phases)], startangle=90, textprops={'color': BioTheme.TEXT_PRIMARY})
        
        canvas = FigureCanvasTkAgg(fig, master=tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)

    def _create_expression_tab(self):
        tab = Frame(self.notebook, bg=BioTheme.BG_DARK)
        self.notebook.add(tab, text="📈 Expression vs Poids")
        
        stats = ProteomeAnalyzer.analyze(self.data)
        expr_data = stats["expression_data"]
        
        fig = Figure(figsize=(8, 6), dpi=100)
        ax = fig.add_subplot(111)
        self._setup_plot_style(fig, ax, "Niveau d'Expression en fonction du Poids Moléculaire")
        
        x = [d["weight"] for d in expr_data]
        y = [d["expression"] for d in expr_data]
        labels = [d["id"] for d in expr_data]
        
        ax.scatter(x, y, color=BioTheme.ACCENT_SECONDARY, s=80, alpha=0.8)
        for i, txt in enumerate(labels):
            ax.annotate(txt, (x[i], y[i]), fontsize=8, color=BioTheme.TEXT_MUTED, xytext=(5, 5), textcoords='offset points')
        
        ax.set_xlabel("Poids (Weight)", color=BioTheme.TEXT_PRIMARY)
        ax.set_ylabel("Niveau d'Expression", color=BioTheme.TEXT_PRIMARY)
        ax.grid(True, color=BioTheme.BORDER, linestyle='--', alpha=0.5)
        
        canvas = FigureCanvasTkAgg(fig, master=tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)

    def _create_network_tab(self):
        tab = Frame(self.notebook, bg=BioTheme.BG_DARK)
        self.notebook.add(tab, text="🕸️ Graphe de Dépendances")
        
        fig = Figure(figsize=(8, 6), dpi=100)
        ax = fig.add_subplot(111)
        self._setup_plot_style(fig, ax, "Réseau de Régulation et d'Héritage")
        ax.axis('off')
        
        G = nx.DiGraph()
        
        # Ajout des relations d'opérons (répression)
        for op in self.data.get("operons", []):
            op_id = op.get("id", "").strip()
            G.add_node(op_id, type='operon')
            repressor = op.get("repressor")
            if repressor:
                G.add_edge(op_id, repressor.strip(), relation='represses')
                
        # Ajout des relations d'héritage de protéines
        for prot in self.data.get("proteins", []):
            prot_id = prot.get("id", "").strip()
            G.add_node(prot_id, type='protein')
            extends = prot.get("extends")
            if extends:
                G.add_edge(extends.strip(), prot_id, relation='inherits')
                
        # Dessin du graphe
        pos = nx.spring_layout(G, k=0.5, iterations=50)
        
        # Nœuds Opérons
        operon_nodes = [n for n, attr in G.nodes(data=True) if attr.get('type') == 'operon']
        nx.draw_networkx_nodes(G, pos, nodelist=operon_nodes, node_color=BioTheme.ACCENT_WARNING, node_shape='s', node_size=800, ax=ax)
        
        # Nœuds Protéines
        protein_nodes = [n for n, attr in G.nodes(data=True) if attr.get('type') == 'protein']
        nx.draw_networkx_nodes(G, pos, nodelist=protein_nodes, node_color=BioTheme.ACCENT_PRIMARY, node_shape='o', node_size=600, ax=ax)
        
        # Arêtes
        nx.draw_networkx_edges(G, pos, edge_color=BioTheme.TEXT_SECONDARY, arrows=True, arrowsize=15, ax=ax)
        nx.draw_networkx_labels(G, pos, font_size=8, font_color=BioTheme.TEXT_PRIMARY, font_family="Consolas", ax=ax)
        
        canvas = FigureCanvasTkAgg(fig, master=tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)

    def _create_heatmap_tab(self):
        tab = Frame(self.notebook, bg=BioTheme.BG_DARK)
        self.notebook.add(tab, text="🧬 Heatmap Épigénétique")
        
        stats = ProteomeAnalyzer.analyze(self.data)
        heatmap_data = stats["epigenetic_heatmap"]
        
        if not heatmap_data:
            Label(tab, text="Aucun marqueur épigénétique trouvé.", fg=BioTheme.TEXT_MUTED, bg=BioTheme.BG_DARK, font=BioTheme.FONT_MAIN).pack(pady=20)
            return

        markers = list(heatmap_data.keys())[:15] # Limite à 15 pour la lisibilité
        proteins = list(set(p for prots in heatmap_data.values() for p in prots))[:20]
        
        # Matrice binaire
        matrix = []
        for prot in proteins:
            row = [1 if prot in heatmap_data.get(marker, []) else 0 for marker in markers]
            matrix.append(row)
            
        fig = Figure(figsize=(10, 6), dpi=100)
        ax = fig.add_subplot(111)
        self._setup_plot_style(fig, ax, "Présence des Marqueurs Épigénétiques par Protéine")
        
        cax = ax.imshow(matrix, cmap='Greens', aspect='auto')
        ax.set_xticks(range(len(markers)))
        ax.set_xticklabels(markers, rotation=45, ha='right', fontsize=8, color=BioTheme.TEXT_PRIMARY)
        ax.set_yticks(range(len(proteins)))
        ax.set_yticklabels(proteins, fontsize=8, color=BioTheme.TEXT_PRIMARY)
        
        fig.colorbar(cax, ax=ax, label="Présence (1) / Absence (0)")
        
        canvas = FigureCanvasTkAgg(fig, master=tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)

    def _create_simulation_tab(self):
        tab = Frame(self.notebook, bg=BioTheme.BG_DARK)
        self.notebook.add(tab, text="📈 Simulation d'Évolution")
        
        fig = Figure(figsize=(8, 6), dpi=100)
        ax = fig.add_subplot(111)
        self._setup_plot_style(fig, ax, "Simulation: État Cellulaire & Entropie (50 Générations)")
        
        # Paramètres de simulation tirés du JSON
        global_cfg = self.data.get("global", self.data.get("global ", {}))
        mutation_rate = float(global_cfg.get("mutation_rate", 0.03))
        
        generations = list(range(51))
        state_var = [5.0]
        entropy = [0.0]
        
        for i in range(1, 51):
            # Simulation simplifiée basée sur les règles du JSON
            change = random.uniform(-1.5, 1.5)
            if random.random() < mutation_rate:
                change += random.choice([-3, 3]) # Saut de mutation
            
            new_state = max(0, min(12, state_var[-1] + change))
            state_var.append(new_state)
            entropy.append(entropy[-1] + abs(change) * 0.1)
            
        ax.plot(generations, state_var, color=BioTheme.ACCENT_PRIMARY, linewidth=2, label="State Variable")
        ax.plot(generations, entropy, color=BioTheme.ACCENT_DANGER, linewidth=2, linestyle='--', label="Entropy Accumulation")
        
        ax.set_xlabel("Génération", color=BioTheme.TEXT_PRIMARY)
        ax.set_ylabel("Valeur", color=BioTheme.TEXT_PRIMARY)
        ax.legend(facecolor=BioTheme.BG_PANEL, edgecolor=BioTheme.BORDER, labelcolor=BioTheme.TEXT_PRIMARY)
        ax.grid(True, color=BioTheme.BORDER, linestyle='--', alpha=0.5)
        
        canvas = FigureCanvasTkAgg(fig, master=tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)


# =============================================================================
# ÉDITEUR JSON AVANCÉ (Inchangé mais conservé pour la complétude)
# =============================================================================
class JsonEditor(ScrolledText):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.config(bg=BioTheme.BG_EDITOR, fg=BioTheme.TEXT_PRIMARY,
                    insertbackground=BioTheme.ACCENT_PRIMARY,
                    font=BioTheme.FONT_CODE, relief=FLAT, bd=0,
                    selectbackground=BioTheme.ACCENT_SECONDARY,
                    selectforeground=BioTheme.BG_DARK)
        self._setup_tags()
        self.bind("<KeyRelease>", self._on_key_release)

    def _setup_tags(self):
        self.tag_config("key", foreground=BioTheme.ACCENT_PRIMARY)
        self.tag_config("string", foreground=BioTheme.ACCENT_WARNING)
        self.tag_config("number", foreground=BioTheme.ACCENT_SECONDARY)
        self.tag_config("boolean", foreground=BioTheme.ACCENT_PURPLE)
        self.tag_config("null", foreground=BioTheme.TEXT_MUTED)
        self.tag_config("bracket", foreground=BioTheme.TEXT_SECONDARY)

    def _on_key_release(self, event=None):
        self._colorize()

    def _colorize(self):
        for tag in ["key", "string", "number", "boolean", "null", "bracket"]:
            self.tag_remove(tag, "1.0", END)
        content = self.get("1.0", END)
        for match in re.finditer(r'"([^"]+)"\s*:', content):
            self.tag_add("key", f"1.0 + {match.start()}c", f"1.0 + {match.end()}c")
        for match in re.finditer(r':\s*"([^"]+)"', content):
            self.tag_add("string", f"1.0 + {match.start()}c", f"1.0 + {match.end()}c")
        for match in re.finditer(r':\s*(\d+(?:\.\d+)?)', content):
            self.tag_add("number", f"1.0 + {match.start()}c", f"1.0 + {match.end()}c")
        for match in re.finditer(r':\s*(true|false)', content):
            self.tag_add("boolean", f"1.0 + {match.start()}c", f"1.0 + {match.end()}c")

    def get_json(self):
        try:
            content = self.get("1.0", END)
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON invalide: {e}")

    def set_json(self, data):
        self.delete("1.0", END)
        self.insert("1.0", json.dumps(data, indent=2, ensure_ascii=False))
        self._colorize()

# =============================================================================
# INTERFACE PRINCIPALE
# =============================================================================
class ProteomEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("🧬 PROTEOMEDITOR v2.0 — Bio-Hacking Interface")
        self.root.geometry("1400x850")
        self.root.configure(bg=BioTheme.BG_DARK)
        self.current_file = None
        self.data = None
        self._setup_ui()
        self.logger = LabLogger(self.console)
        self.logger.info("ProteomEditor v2.0 démarré — Modules de visualisation scientifique chargés.")

    def _setup_ui(self):
        self._setup_menu()
        self._setup_toolbar()
        
        main_panel = PanedWindow(self.root, bg=BioTheme.BG_DARK, sashwidth=3, sashrelief=RAISED)
        main_panel.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        left_panel = Frame(main_panel, bg=BioTheme.BG_DARK)
        main_panel.add(left_panel, width=350)
        self.tree = self._create_tree(left_panel)
        
        right_panel = Frame(main_panel, bg=BioTheme.BG_DARK)
        main_panel.add(right_panel, width=1050)
        
        editor_frame = LabelFrame(right_panel, text="✏️ ÉDITEUR JSON", font=BioTheme.FONT_HEADER,
                                  fg=BioTheme.ACCENT_SECONDARY, bg=BioTheme.BG_PANEL, bd=2, relief=SOLID)
        editor_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        self.editor = JsonEditor(editor_frame, wrap=NONE, height=25)
        self.editor.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        console_frame = LabelFrame(right_panel, text="📟 CONSOLE DE LABORATOIRE", font=BioTheme.FONT_HEADER,
                                   fg=BioTheme.ACCENT_WARNING, bg=BioTheme.BG_PANEL, bd=2, relief=SOLID)
        console_frame.pack(fill=BOTH, expand=False, padx=10, pady=10)
        self.console = Text(console_frame, height=8, bg=BioTheme.BG_EDITOR,
                            fg=BioTheme.TEXT_SECONDARY, font=BioTheme.FONT_TERMINAL, relief=FLAT, wrap=WORD)
        self.console.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        self.status_bar = Label(self.root, text="⚡ PRÊT", bg=BioTheme.BG_PANEL,
                                fg=BioTheme.ACCENT_PRIMARY, font=("Consolas", 9), anchor=W, padx=10)
        self.status_bar.pack(fill=X, side=BOTTOM)

    def _create_tree(self, parent):
        frame = LabelFrame(parent, text="🧬 ARBRE DU PROTÉOME", font=BioTheme.FONT_HEADER,
                           fg=BioTheme.ACCENT_PRIMARY, bg=BioTheme.BG_PANEL, bd=2, relief=SOLID)
        frame.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)
        tree = ttk.Treeview(frame, show="tree")
        tree.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        tree.config(yscrollcommand=scrollbar.set)
        
        style = ttk.Style()
        style.configure("Treeview", background=BioTheme.BG_TREE, foreground=BioTheme.TEXT_SECONDARY,
                        fieldbackground=BioTheme.BG_TREE, font=BioTheme.FONT_MAIN)
        style.configure("Treeview.Heading", foreground=BioTheme.ACCENT_PRIMARY,
                        background=BioTheme.BG_PANEL, font=BioTheme.FONT_HEADER)
        return tree

    def _setup_menu(self):
        menubar = Menu(self.root, bg=BioTheme.BG_PANEL, fg=BioTheme.TEXT_PRIMARY,
                       activebackground=BioTheme.ACCENT_SECONDARY, activeforeground=BioTheme.BG_DARK)
        self.root.config(menu=menubar)
        
        file_menu = Menu(menubar, tearoff=0, bg=BioTheme.BG_PANEL, fg=BioTheme.TEXT_PRIMARY)
        file_menu.add_command(label="📂 Charger", command=self._load_file, accelerator="Ctrl+O")
        file_menu.add_command(label="💾 Sauvegarder", command=self._save_file, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="❌ Quitter", command=self.root.quit)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        
        edit_menu = Menu(menubar, tearoff=0, bg=BioTheme.BG_PANEL, fg=BioTheme.TEXT_PRIMARY)
        edit_menu.add_command(label="🔍 Valider", command=self._validate)
        edit_menu.add_command(label="🧹 Nettoyer & Normaliser", command=self._clean)
        edit_menu.add_command(label="🧬 Mutation contrôlée...", command=self._mutate)
        menubar.add_cascade(label="Édition", menu=edit_menu)
        
        view_menu = Menu(menubar, tearoff=0, bg=BioTheme.BG_PANEL, fg=BioTheme.TEXT_PRIMARY)
        view_menu.add_command(label="🔬 Visualisation Scientifique", command=self._show_visualization)
        menubar.add_cascade(label="Affichage", menu=view_menu)

        self.root.bind("<Control-o>", lambda e: self._load_file())
        self.root.bind("<Control-s>", lambda e: self._save_file())

    def _setup_toolbar(self):
        toolbar = Frame(self.root, bg=BioTheme.BG_PANEL, height=45)
        toolbar.pack(fill=X, padx=0, pady=0)
        toolbar.pack_propagate(False)
        buttons = [
            ("🧬 CHARGER", self._load_file, BioTheme.ACCENT_PRIMARY),
            ("💾 SAUVEGARDER", self._save_file, BioTheme.ACCENT_SECONDARY),
            ("🔬 VISUALISER", self._show_visualization, BioTheme.ACCENT_PURPLE),
            ("🧹 NETTOYER", self._clean, BioTheme.ACCENT_WARNING),
            ("🧬 MUTATION", self._mutate, BioTheme.ACCENT_DANGER),
        ]
        for text, cmd, color in buttons:
            btn = Button(toolbar, text=text, command=cmd, bg=BioTheme.BG_EDITOR, fg=color,
                         activebackground=color, activeforeground=BioTheme.BG_DARK,
                         relief=FLAT, font=("Consolas", 9, "bold"), cursor="hand2", padx=12, pady=6)
            btn.pack(side=LEFT, padx=3, pady=5)

    def _load_file(self):
        path = filedialog.askopenfilename(title="Charger configuration protéome", filetypes=[("JSON", "*.json"), ("Tous", "*.*")])
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
                # Normalisation cruciale pour gérer les espaces dans les clés du JSON fourni
                self.data = JsonNormalizer.clean_keys(raw_data)
                self.current_file = path
                self.editor.set_json(self.data)
                self._update_tree()
                self.logger.success(f"Chargé et normalisé: {Path(path).name}")
                self.status_bar.config(text=f"📁 {path}")
            except Exception as e:
                self.logger.error(f"Erreur chargement: {e}")

    def _save_file(self):
        if not self.current_file:
            return
        try:
            self.data = self.editor.get_json()
            with open(self.current_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            self.logger.success(f"Sauvegardé: {Path(self.current_file).name}")
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde: {e}")

    def _update_tree(self):
        self.tree.delete(*self.tree.get_children())
        root = self.tree.insert("", "end", text="🧬 PROTÉOME", open=True)
        
        prot_node = self.tree.insert(root, "end", text=f"🔬 PROTÉINES ({len(self.data.get('proteins', []))})", open=True)
        for prot in self.data.get("proteins", []):
            phase = prot.get("meta", {}).get("cell_phase", "?").strip()
            self.tree.insert(prot_node, "end", text=f"{prot['id']} [{phase}]")
            
        op_node = self.tree.insert(root, "end", text=f"🎛️ OPÉRONS ({len(self.data.get('operons', []))})", open=True)
        for op in self.data.get("operons", []):
            self.tree.insert(op_node, "end", text=op["id"])

    def _validate(self):
        if not self.data:
            self.logger.warning("Aucune donnée chargée")
            return
        # Validation simplifiée pour l'exemple
        if "proteins" in self.data and "operons" in self.data:
            self.logger.success("✅ Validation structurelle réussie")
        else:
            self.logger.error("❌ Structure JSON invalide")

    def _clean(self):
        if not self.data:
            return
        self.data = JsonNormalizer.clean_keys(self.data)
        self.editor.set_json(self.data)
        self.logger.success("Nettoyage et normalisation des clés JSON effectués")

    def _mutate(self):
        if not self.data:
            return
        # Simulation d'une mutation simple pour l'exemple
        if "proteins" in self.data and len(self.data["proteins"]) > 0:
            prot = random.choice(self.data["proteins"])
            prot["meta"]["expression_level"] = round(random.uniform(0.1, 2.0), 2)
            self.editor.set_json(self.data)
            self.logger.mutation(f"Mutation appliquée: Expression de {prot['id']} modifiée à {prot['meta']['expression_level']}")

    def _show_visualization(self):
        if not self.data:
            self.logger.warning("Veuillez charger un protéome avant de visualiser.")
            return
        self.logger.info("Génération des modules de visualisation scientifique...")
        ProteomeVisualizer(self.root, self.data)

# =============================================================================
# MAIN
# =============================================================================
def main():
    root = Tk()
    app = ProteomEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()