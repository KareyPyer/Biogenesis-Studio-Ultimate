#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════════╗
║  🧬 PROTEOMEDITOR v2.0 — Bio-Hacking JSON Editor for Proteome Configuration     ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║                                                                                  ║
║  v1.0 Features:                                                                  ║
║  • Charger / Sauvegarder / Exporter                                              ║
║  • Arborescence interactive du protéome                                          ║
║  • Éditeur JSON avec coloration syntaxique                                       ║
║  • Validateur structurel (schéma personnalisé)                                   ║
║  • Nettoyeur (supprime commentaires, formate)                                    ║
║  • Analyseur de métriques (statistiques du protéome)                             ║
║  • Mode "Mutation" — altérations aléatoires contrôlées                           ║
║  • Console de logs style laboratoire                                             ║
║                                                                                  ║
║  v2.0 Gap Upgrade — Visualisation scientifique & Analyse avancée :               ║
║  • 🔬 Dashboard de visualisation matplotlib (4 graphes simultanés)              ║
║  • 🕸️  Graphe de dépendances interactif (NetworkX)                              ║
║  • 📈 Simulateur d'évolution cellulaire (trajectoire d'état sur N générations)  ║
║  • 🗺️  Heat Map expression_level × weight par protéine                          ║
║  • 🍰 Distribution des phases cellulaires (pie + bar)                           ║
║  • 🌡️  Radar chart des métriques globales                                       ║
║  • ⚖️  Comparateur de deux configurations (diff visuel)                         ║
║  • 🔍 Recherche/filtre dans l'arbre et l'éditeur                                ║
║  • 📄 Export rapport scientifique HTML                                           ║
║  • 🏷️  Statistiques épigénétiques enrichies                                     ║
╚══════════════════════════════════════════════════════════════════════════════════╝
"""

import json
import re
import random
import hashlib
import webbrowser
import copy
import difflib
import io
import base64
from pathlib import Path
from datetime import datetime
from collections import Counter
from tkinter import *
from tkinter import ttk, filedialog, messagebox, font as tkfont
from tkinter.scrolledtext import ScrolledText

# Scientific visualization stack
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec
import numpy as np

# Graph engine
import networkx as nx

# =============================================================================
# THEME "BIO-HACKING LAB"
# =============================================================================
class BioTheme:
    BG_DARK      = "#0a0f0f"
    BG_PANEL     = "#0f1515"
    BG_EDITOR    = "#0c1212"
    BG_TREE      = "#0a0f0f"
    ACCENT_PRIMARY   = "#00ff9d"
    ACCENT_SECONDARY = "#00d4ff"
    ACCENT_WARNING   = "#ffcc00"
    ACCENT_DANGER    = "#ff3366"
    ACCENT_PURPLE    = "#b84dff"
    TEXT_PRIMARY     = "#e0f2fe"
    TEXT_SECONDARY   = "#8ba3b8"
    TEXT_MUTED       = "#4a6a7a"
    BORDER           = "#1a2a2a"
    SUCCESS          = "#00cc66"
    ERROR            = "#ff4444"

    FONT_MAIN    = ("Consolas", 10)
    FONT_CODE    = ("Consolas", 10)
    FONT_HEADER  = ("Courier New", 12, "bold")
    FONT_TERMINAL= ("Courier New", 9)

    # Matplotlib theme colors
    MPL_BG       = "#0c1212"
    MPL_AX_BG    = "#0f1515"
    MPL_GRID     = "#1a2a2a"
    MPL_TEXT     = "#e0f2fe"
    MPL_PALETTE  = ["#00ff9d","#00d4ff","#b84dff","#ff3366","#ffcc00",
                    "#00cc66","#ff9944","#44aaff","#ff44aa","#aaff44"]

# =============================================================================
# MATPLOTLIB STYLE HELPER
# =============================================================================
def apply_bio_style():
    """Configure matplotlib avec le thème Bio-Hacking"""
    plt.rcParams.update({
        "figure.facecolor":  BioTheme.MPL_BG,
        "axes.facecolor":    BioTheme.MPL_AX_BG,
        "axes.edgecolor":    BioTheme.BORDER,
        "axes.labelcolor":   BioTheme.TEXT_SECONDARY,
        "axes.titlecolor":   BioTheme.ACCENT_PRIMARY,
        "xtick.color":       BioTheme.TEXT_MUTED,
        "ytick.color":       BioTheme.TEXT_MUTED,
        "text.color":        BioTheme.TEXT_PRIMARY,
        "grid.color":        BioTheme.MPL_GRID,
        "grid.alpha":        0.5,
        "legend.facecolor":  BioTheme.BG_PANEL,
        "legend.edgecolor":  BioTheme.BORDER,
        "legend.labelcolor": BioTheme.TEXT_PRIMARY,
        "font.family":       "monospace",
        "font.size":         9,
    })

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
        icons  = {"INFO":"🧪","SUCCESS":"✅","WARNING":"⚠️",
                  "ERROR":"❌","MUTATION":"🧬","VALIDATION":"🔬","VIZ":"📊"}
        colors = {"INFO": BioTheme.TEXT_SECONDARY, "SUCCESS": BioTheme.SUCCESS,
                  "WARNING": BioTheme.ACCENT_WARNING, "ERROR": BioTheme.ERROR,
                  "MUTATION": BioTheme.ACCENT_PRIMARY, "VALIDATION": BioTheme.ACCENT_SECONDARY,
                  "VIZ": BioTheme.ACCENT_PURPLE}
        icon  = icons.get(level, "📟")
        color = colors.get(level, BioTheme.TEXT_PRIMARY)
        self.text.config(state=NORMAL)
        self.text.insert(END, f"[{timestamp}] {icon} {msg}\n")
        self.text.tag_add(f"c{timestamp}", "end-2l", "end-1l")
        self.text.tag_config(f"c{timestamp}", foreground=color, font=BioTheme.FONT_TERMINAL)
        self.text.see(END)
        self.text.config(state=DISABLED)

    def info(self, msg):        self.log(msg, "INFO")
    def success(self, msg):     self.log(msg, "SUCCESS")
    def warning(self, msg):     self.log(msg, "WARNING")
    def error(self, msg):       self.log(msg, "ERROR")
    def mutation(self, msg):    self.log(msg, "MUTATION")
    def validation(self, msg):  self.log(msg, "VALIDATION")
    def viz(self, msg):         self.log(msg, "VIZ")

# =============================================================================
# VALIDATEUR DE SCHÉMA
# =============================================================================
class ProteomeValidator:
    REQUIRED_TOP    = ["schema_version","project","description","global",
                       "operons","plasmids","global_transposons","proteins"]
    REQUIRED_GLOBAL = ["language","state_var","entropy_var","max_recursion_depth",
                       "mutation_rate","cell_generation"]

    @classmethod
    def validate(cls, data):
        errors, warnings = [], []
        for req in cls.REQUIRED_TOP:
            if req not in data:
                errors.append(f"Champ racine manquant: {req}")
        if "global" in data:
            for req in cls.REQUIRED_GLOBAL:
                if req not in data["global"]:
                    warnings.append(f"Champ global manquant: {req}")
        if "proteins" in data and isinstance(data["proteins"], list):
            prot_ids = set()
            for i, prot in enumerate(data["proteins"]):
                if "id" not in prot:
                    errors.append(f"Protéine #{i}: champ 'id' manquant")
                else:
                    if prot["id"] in prot_ids:
                        errors.append(f"ID dupliqué: {prot['id']}")
                    prot_ids.add(prot["id"])
                if "template" not in prot and "extends" not in prot:
                    warnings.append(f"Protéine {prot.get('id', i)}: ni template ni extends")
        if "operons" in data:
            op_ids = set()
            for op in data["operons"]:
                if "id" not in op:
                    errors.append("Opéron sans ID")
                else:
                    if op["id"] in op_ids:
                        errors.append(f"Opéron dupliqué: {op['id']}")
                    op_ids.add(op["id"])
                if "promoter_condition" not in op:
                    warnings.append(f"Opéron {op.get('id')}: pas de condition promoteur")
        return errors, warnings

    @classmethod
    def auto_repair(cls, data):
        for req in cls.REQUIRED_TOP:
            if req not in data:
                defaults = {"global":{"language":"csharp","state_var":"_cellularState"},
                            "operons":[],"plasmids":[],"global_transposons":[],"proteins":[]}
                data[req] = defaults.get(req, "default")
        if "global" in data:
            for req in cls.REQUIRED_GLOBAL:
                if req not in data["global"]:
                    data["global"][req] = 0.02 if req in ["mutation_rate","indel_rate"] \
                                          else (0 if req == "cell_generation" else "default")
        return data

# =============================================================================
# ANALYSEUR DE MÉTRIQUES ÉTENDU
# =============================================================================
class ProteomeAnalyzer:

    @staticmethod
    def analyze(data):
        stats = {}
        proteins = data.get("proteins", [])
        operons  = data.get("operons", [])

        stats["proteins_count"]   = len(proteins)
        stats["operons_count"]    = len(operons)
        stats["plasmids_count"]   = len(data.get("plasmids", []))
        stats["transposons_count"]= len(data.get("global_transposons", []))

        inheritance = [p.get("extends") for p in proteins if p.get("extends")]
        stats["inheritance_count"] = len(inheritance)
        stats["inheritance_depth"] = max(
            [len(p.get("override", {})) for p in proteins], default=0)

        markers = []
        for p in proteins:
            markers.extend(p.get("epigenetic_markers", []))
        stats["epigenetic_markers_count"] = len(set(markers))
        stats["epigenetic_markers_total"] = len(markers)
        stats["epigenetic_markers_list"]  = markers

        phases = [p.get("meta",{}).get("cell_phase","unknown") for p in proteins]
        stats["phases"] = dict(Counter(phases))

        stats["total_proteins_size"] = sum(
            len(p.get("template", [])) for p in proteins)

        # Expression levels & weights
        stats["expression_levels"] = {
            p["id"]: p.get("meta",{}).get("expression_level", 1.0)
            for p in proteins if "id" in p}
        stats["weights"] = {
            p["id"]: p.get("meta",{}).get("weight", 1.0)
            for p in proteins if "id" in p}

        # Operon gene counts
        stats["operon_gene_counts"] = {
            op["id"]: len(op.get("genes", []))
            for op in operons if "id" in op}

        # Transposon jump probabilities
        stats["transposon_jumps"] = {
            tp["id"]: tp.get("jump_prob", 0)
            for tp in data.get("global_transposons", []) if "id" in tp}

        # Plasmid copy numbers
        stats["plasmid_copies"] = {
            pl["id"]: pl.get("copy_number", 1)
            for pl in data.get("plasmids", []) if "id" in pl}

        # Sub-protein richness
        stats["sub_proteins_count"] = sum(
            len(p.get("sub_proteins", {})) for p in proteins)

        # Template directive analysis
        directive_counts = Counter()
        for p in proteins:
            for line in p.get("template", []):
                for m in re.findall(r'\{\{(\w+)[:\s]', line):
                    directive_counts[m] += 1
        stats["directive_counts"] = dict(directive_counts)

        # Inheritance graph
        inheritance_map = {}
        for p in proteins:
            if p.get("extends") and "id" in p:
                inheritance_map[p["id"]] = p["extends"]
        stats["inheritance_map"] = inheritance_map

        # Operon repressor graph
        repressor_map = {}
        for op in operons:
            if op.get("repressor") and "id" in op:
                repressor_map[op["id"]] = op["repressor"]
        stats["repressor_map"] = repressor_map

        # Mutation rates from templates
        mutation_rates = []
        for p in proteins:
            for line in p.get("template", []):
                m = re.search(r'\{\{mutate:([\d.]+)\}\}', line)
                if m:
                    mutation_rates.append(float(m.group(1)))
        stats["mutation_rates"] = mutation_rates
        stats["avg_mutation_rate"] = np.mean(mutation_rates) if mutation_rates else 0.0

        return stats

# =============================================================================
# ÉDITEUR JSON AVANCÉ (avec recherche)
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
        self._search_indices = []
        self._search_cursor  = 0

    def _setup_tags(self):
        self.tag_config("key",      foreground=BioTheme.ACCENT_PRIMARY)
        self.tag_config("string",   foreground=BioTheme.ACCENT_WARNING)
        self.tag_config("number",   foreground=BioTheme.ACCENT_SECONDARY)
        self.tag_config("boolean",  foreground=BioTheme.ACCENT_PURPLE)
        self.tag_config("null",     foreground=BioTheme.TEXT_MUTED)
        self.tag_config("bracket",  foreground=BioTheme.TEXT_SECONDARY)
        self.tag_config("search",   background=BioTheme.ACCENT_WARNING,
                                    foreground=BioTheme.BG_DARK)
        self.tag_config("search_cur", background=BioTheme.ACCENT_DANGER,
                                      foreground=BioTheme.BG_DARK)

    def _on_key_release(self, event=None):
        self._colorize()

    def _colorize(self):
        for tag in ["key","string","number","boolean","null","bracket"]:
            self.tag_remove(tag, "1.0", END)
        content = self.get("1.0", END)
        for match in re.finditer(r'"([^"]+)"\s*:', content):
            self.tag_add("key", f"1.0+{match.start()}c", f"1.0+{match.end()}c")
        for match in re.finditer(r':\s*"([^"]+)"', content):
            self.tag_add("string", f"1.0+{match.start()}c", f"1.0+{match.end()}c")
        for match in re.finditer(r':\s*(\d+(?:\.\d+)?)', content):
            self.tag_add("number", f"1.0+{match.start()}c", f"1.0+{match.end()}c")
        for match in re.finditer(r':\s*(true|false)', content):
            self.tag_add("boolean", f"1.0+{match.start()}c", f"1.0+{match.end()}c")

    def search(self, term):
        self.tag_remove("search", "1.0", END)
        self.tag_remove("search_cur", "1.0", END)
        self._search_indices = []
        self._search_cursor  = 0
        if not term:
            return 0
        content = self.get("1.0", END)
        for m in re.finditer(re.escape(term), content, re.IGNORECASE):
            start = f"1.0+{m.start()}c"
            end   = f"1.0+{m.end()}c"
            self.tag_add("search", start, end)
            self._search_indices.append((start, end))
        if self._search_indices:
            self._highlight_current()
        return len(self._search_indices)

    def _highlight_current(self):
        self.tag_remove("search_cur", "1.0", END)
        if self._search_indices:
            s, e = self._search_indices[self._search_cursor]
            self.tag_remove("search", s, e)
            self.tag_add("search_cur", s, e)
            self.see(s)

    def search_next(self):
        if self._search_indices:
            s0, e0 = self._search_indices[self._search_cursor]
            self.tag_remove("search_cur", s0, e0)
            self.tag_add("search", s0, e0)
            self._search_cursor = (self._search_cursor + 1) % len(self._search_indices)
            self._highlight_current()

    def search_prev(self):
        if self._search_indices:
            s0, e0 = self._search_indices[self._search_cursor]
            self.tag_remove("search_cur", s0, e0)
            self.tag_add("search", s0, e0)
            self._search_cursor = (self._search_cursor - 1) % len(self._search_indices)
            self._highlight_current()

    def get_json(self):
        try:
            return json.loads(self.get("1.0", END))
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON invalide: {e}")

    def set_json(self, data):
        self.delete("1.0", END)
        self.insert("1.0", json.dumps(data, indent=2, ensure_ascii=False))
        self._colorize()

# =============================================================================
# ARBRE DU PROTÉOME (avec filtre)
# =============================================================================
class ProteomeTree:
    def __init__(self, parent, on_select):
        self.frame = LabelFrame(parent, text="🧬 ARBRE DU PROTÉOME",
                                font=BioTheme.FONT_HEADER,
                                fg=BioTheme.ACCENT_PRIMARY,
                                bg=BioTheme.BG_PANEL,
                                bd=2, relief=SOLID)
        self.frame.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)

        # Filtre
        filter_frame = Frame(self.frame, bg=BioTheme.BG_PANEL)
        filter_frame.pack(fill=X, padx=5, pady=(5,0))
        Label(filter_frame, text="🔍", bg=BioTheme.BG_PANEL,
              fg=BioTheme.ACCENT_SECONDARY, font=("Consolas", 10)).pack(side=LEFT)
        self._filter_var = StringVar()
        self._filter_var.trace("w", self._on_filter_change)
        Entry(filter_frame, textvariable=self._filter_var,
              bg=BioTheme.BG_EDITOR, fg=BioTheme.TEXT_PRIMARY,
              insertbackground=BioTheme.ACCENT_PRIMARY,
              relief=FLAT, font=BioTheme.FONT_MAIN).pack(side=LEFT, fill=X, expand=True)

        self.tree = ttk.Treeview(self.frame, show="tree")
        self.tree.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.tree.config(yscrollcommand=scrollbar.set)

        self.on_select = on_select
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self._data = None
        self._setup_style()

    def _setup_style(self):
        style = ttk.Style()
        style.configure("Treeview", background=BioTheme.BG_TREE,
                        foreground=BioTheme.TEXT_SECONDARY,
                        fieldbackground=BioTheme.BG_TREE,
                        font=BioTheme.FONT_MAIN)
        style.configure("Treeview.Heading", foreground=BioTheme.ACCENT_PRIMARY,
                        background=BioTheme.BG_PANEL, font=BioTheme.FONT_HEADER)

    def load_data(self, data):
        self._data = data
        self._render(data, filter_term="")

    def _render(self, data, filter_term=""):
        self.tree.delete(*self.tree.get_children())
        if not data:
            return
        ft = filter_term.lower()
        root_node = self.tree.insert("", "end", text="🧬 PROTÉOME", open=True)

        def matches(text):
            return (not ft) or (ft in text.lower())

        proteins = [p for p in data.get("proteins", []) if matches(p.get("id",""))]
        pn = self.tree.insert(root_node, "end",
                               text=f"🔬 PROTÉINES ({len(proteins)})", open=True)
        for prot in proteins:
            phase = prot.get("meta",{}).get("cell_phase","?")
            expr  = prot.get("meta",{}).get("expression_level","?")
            label = f"{prot['id']}  [{phase}]  expr={expr}"
            self.tree.insert(pn, "end", text=label, values=(prot["id"],))

        operons = [o for o in data.get("operons",[]) if matches(o.get("id",""))]
        on = self.tree.insert(root_node, "end",
                               text=f"🎛️ OPÉRONS ({len(operons)})", open=True)
        for op in operons:
            genes = ", ".join(op.get("genes",[]))
            self.tree.insert(on, "end", text=f"{op['id']}  → {genes}", values=(op["id"],))

        plasmids = [p for p in data.get("plasmids",[]) if matches(p.get("id",""))]
        ppn = self.tree.insert(root_node, "end",
                                text=f"🧫 PLASMIDES ({len(plasmids)})", open=True)
        for pl in plasmids:
            self.tree.insert(ppn, "end", text=pl["id"], values=(pl["id"],))

        transposons = [t for t in data.get("global_transposons",[])
                       if matches(t.get("id",""))]
        tn = self.tree.insert(root_node, "end",
                               text=f"🦠 TRANSPOSONS ({len(transposons)})", open=True)
        for tp in transposons:
            self.tree.insert(tn, "end",
                             text=f"{tp['id']}  p={tp.get('jump_prob',0):.2f}",
                             values=(tp["id"],))

    def _on_filter_change(self, *args):
        if self._data:
            self._render(self._data, filter_term=self._filter_var.get())

    def _on_select(self, event):
        sel = self.tree.selection()
        if sel:
            item = self.tree.item(sel[0])
            if self.on_select:
                self.on_select(item["text"])

# =============================================================================
# MUTATEUR CONTRÔLÉ
# =============================================================================
class ProteomeMutator:
    MUTATION_TYPES = ["add_protein","remove_protein","rename_protein",
                      "add_operon","modify_promoter","add_epigenetic_marker",
                      "mutate_global_rate","add_plasmid"]

    @classmethod
    def mutate(cls, data, intensity=0.1, seed=None):
        if seed:
            random.seed(seed)
        mutated = copy.deepcopy(data)
        mutations_applied = []
        n_mutations = max(1, int(intensity * 10))

        for _ in range(n_mutations):
            mutation_type = random.choice(cls.MUTATION_TYPES)
            if mutation_type == "add_protein":
                new_id = f"mutant_protein_{random.randint(100, 999)}"
                mutated.setdefault("proteins", []).append({
                    "id": new_id, "filename": f"{new_id}.prot",
                    "extends": None, "description": "Protéine mutante générée",
                    "template": ["{{meta:docstring}}", f"public void {new_id.title()}() {{","}"],
                    "meta": {"weight": round(random.uniform(0.5,2.0),2),
                             "expression_level": round(random.uniform(0.1,1.5),2),
                             "cell_phase": random.choice(["G1","S","G2","M","G0"])},
                    "epigenetic_markers": []})
                mutations_applied.append(f"➕ Protéine créée: {new_id}")
            elif mutation_type == "remove_protein" and len(mutated.get("proteins",[])) > 1:
                removed = random.choice(mutated["proteins"])
                mutated["proteins"].remove(removed)
                mutations_applied.append(f"➖ Protéine supprimée: {removed['id']}")
            elif mutation_type == "modify_promoter" and mutated.get("operons"):
                operon = random.choice(mutated["operons"])
                old_cond = operon.get("promoter_condition","None")
                new_cond = f"state_var {random.choice(['>','<','=='])} {random.randint(0,10)}"
                operon["promoter_condition"] = new_cond
                mutations_applied.append(f"🎛️ Promoteur modifié: {operon['id']}: {old_cond} → {new_cond}")
            elif mutation_type == "add_epigenetic_marker" and mutated.get("proteins"):
                prot = random.choice(mutated["proteins"])
                new_marker = f"mutant_marker_{random.randint(1,99)}"
                prot.setdefault("epigenetic_markers",[]).append(new_marker)
                mutations_applied.append(f"🧬 Marqueur épigénétique ajouté: {prot['id']} → {new_marker}")
            elif mutation_type == "mutate_global_rate":
                mutated.setdefault("global",{})["mutation_rate"] = round(random.uniform(0.01,0.1),3)
                mutations_applied.append(f"🌍 Taux de mutation: {mutated['global']['mutation_rate']:.3f}")

        return mutated, mutations_applied

# =============================================================================
# ██╗   ██╗██╗███████╗██╗   ██╗ █████╗ ██╗     ██╗███████╗ █████╗ ████████╗██╗ ██████╗ ███╗   ██╗
# ╚══╗ ██╔╝██║╚══███╔╝██║   ██║██╔══██╗██║     ██║╚══███╔╝██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║
#    ╚███╔╝ ██║  ███╔╝ ██║   ██║███████║██║     ██║  ███╔╝ ███████║   ██║   ██║██║   ██║██╔██╗ ██║
#    ██╔██╗ ██║ ███╔╝  ██║   ██║██╔══██║██║     ██║ ███╔╝  ██╔══██║   ██║   ██║██║   ██║██║╚██╗██║
#   ██╔╝ ██╗██║███████╗╚██████╔╝██║  ██║███████╗██║███████╗██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║
# =============================================================================

class BioVisualizer:
    """Moteur de visualisation scientifique pour le protéome"""

    @staticmethod
    def _new_figure(nrows=1, ncols=1, title="", figsize=(14,8)):
        apply_bio_style()
        fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
        fig.suptitle(title, color=BioTheme.ACCENT_PRIMARY,
                     fontsize=13, fontweight="bold", fontfamily="monospace")
        fig.patch.set_facecolor(BioTheme.MPL_BG)
        return fig, axes

    # ─── 1. DASHBOARD PRINCIPAL ───────────────────────────────────────────
    @classmethod
    def show_dashboard(cls, data, parent_title=""):
        stats = ProteomeAnalyzer.analyze(data)
        apply_bio_style()
        fig = Figure(figsize=(16, 10))
        fig.patch.set_facecolor(BioTheme.MPL_BG)
        fig.suptitle(f"🔬 PROTÉOME DASHBOARD — {data.get('project','?')}",
                     color=BioTheme.ACCENT_PRIMARY, fontsize=13,
                     fontweight="bold", fontfamily="monospace")

        gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.4)
        ax1 = fig.add_subplot(gs[0, 0])                        # Phases pie
        ax2 = fig.add_subplot(gs[0, 1])                        # Expression levels bar
        ax3 = fig.add_subplot(gs[0, 2], projection="polar")    # Radar métriques globales
        ax4 = fig.add_subplot(gs[1, 0])  # Opéron gene count
        ax5 = fig.add_subplot(gs[1, 1])  # Transposon jump probs
        ax6 = fig.add_subplot(gs[1, 2])  # Directives template

        pal = BioTheme.MPL_PALETTE

        # ── Pie phases cellulaires
        phases = stats["phases"]
        if phases:
            colors_pie = pal[:len(phases)]
            wedges, texts, autotexts = ax1.pie(
                phases.values(), labels=phases.keys(),
                colors=colors_pie, autopct="%1.0f%%",
                startangle=90, textprops={"fontsize":7.5,"color":BioTheme.TEXT_PRIMARY},
                wedgeprops={"edgecolor":BioTheme.BG_DARK,"linewidth":1.2})
            for at in autotexts:
                at.set_color(BioTheme.BG_DARK)
                at.set_fontsize(7)
        ax1.set_title("🔄 Phases cellulaires", color=BioTheme.ACCENT_PRIMARY, fontsize=9)
        ax1.set_facecolor(BioTheme.MPL_AX_BG)

        # ── Bar expression levels
        expr = stats["expression_levels"]
        if expr:
            names = [k[:12] for k in expr.keys()]
            vals  = list(expr.values())
            colors_bar = [pal[i % len(pal)] for i in range(len(vals))]
            bars = ax2.barh(names, vals, color=colors_bar, edgecolor=BioTheme.BG_DARK,
                            linewidth=0.5, height=0.7)
            ax2.axvline(x=np.mean(vals), color=BioTheme.ACCENT_WARNING,
                        linestyle="--", linewidth=1, alpha=0.8, label=f"μ={np.mean(vals):.2f}")
            ax2.legend(fontsize=7)
            ax2.set_xlabel("Expression level", fontsize=8)
        ax2.set_title("📊 Expression levels", color=BioTheme.ACCENT_PRIMARY, fontsize=9)
        ax2.grid(axis="x", alpha=0.4)
        ax2.tick_params(labelsize=7)

        # ── Radar métriques globales
        cls._draw_radar(ax3, stats, fig)

        # ── Opéron gene counts
        op_genes = stats["operon_gene_counts"]
        if op_genes:
            ax4.bar(list(op_genes.keys()), list(op_genes.values()),
                    color=pal[2], edgecolor=BioTheme.BG_DARK, linewidth=0.5)
            ax4.tick_params(labelsize=7, axis="x")
            ax4.set_xticklabels(list(op_genes.keys()), rotation=30, ha="right", fontsize=7)
        ax4.set_title("🎛️ Gènes / Opéron", color=BioTheme.ACCENT_PRIMARY, fontsize=9)
        ax4.set_ylabel("Nb gènes", fontsize=8)
        ax4.grid(axis="y", alpha=0.4)

        # ── Transposon jump probs
        tj = stats["transposon_jumps"]
        if tj:
            ax5.bar(list(tj.keys()), list(tj.values()),
                    color=pal[3], edgecolor=BioTheme.BG_DARK, linewidth=0.5)
            ax5.set_xticklabels(list(tj.keys()), rotation=30, ha="right", fontsize=7)
            ax5.set_ylim(0, max(tj.values()) * 1.3)
        ax5.set_title("🦠 Jump prob (Transposons)", color=BioTheme.ACCENT_PRIMARY, fontsize=9)
        ax5.set_ylabel("Probabilité", fontsize=8)
        ax5.grid(axis="y", alpha=0.4)

        # ── Directives template
        directives = stats.get("directive_counts", {})
        if directives:
            top = dict(sorted(directives.items(), key=lambda x: x[1], reverse=True)[:10])
            ax6.bar(list(top.keys()), list(top.values()),
                    color=pal[4], edgecolor=BioTheme.BG_DARK, linewidth=0.5)
            ax6.set_xticklabels(list(top.keys()), rotation=40, ha="right", fontsize=7)
        ax6.set_title("📝 Directives template (top 10)", color=BioTheme.ACCENT_PRIMARY, fontsize=9)
        ax6.set_ylabel("Occurrences", fontsize=8)
        ax6.grid(axis="y", alpha=0.4)

        cls._open_figure_window(fig, f"📊 Dashboard — {data.get('project','Protéome')}")

    # ─── 2. RADAR MÉTRIQUES ───────────────────────────────────────────────
    @classmethod
    def _draw_radar(cls, ax, stats, fig):
        categories = ["Protéines","Opérons","Plasmides","Transposons","Héritages","Marqueurs ép."]
        raw = [stats["proteins_count"], stats["operons_count"],
               stats["plasmids_count"], stats["transposons_count"],
               stats["inheritance_count"], stats["epigenetic_markers_count"]]
        maxval = max(raw) if max(raw) > 0 else 1
        values = [v / maxval for v in raw]
        values += values[:1]

        N = len(categories)
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]

        ax.set_facecolor(BioTheme.MPL_AX_BG)
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, color=BioTheme.TEXT_SECONDARY, fontsize=7.5)
        ax.set_ylim(0, 1)
        ax.set_yticks([0.25, 0.5, 0.75, 1.0])
        ax.set_yticklabels([], color=BioTheme.TEXT_MUTED, fontsize=6)
        ax.grid(color=BioTheme.MPL_GRID, linestyle="--", linewidth=0.5, alpha=0.6)

        ax.plot(angles, values, color=BioTheme.ACCENT_PRIMARY, linewidth=2)
        ax.fill(angles, values, color=BioTheme.ACCENT_PRIMARY, alpha=0.15)

        for i, (angle, val, raw_val) in enumerate(zip(angles[:-1], values[:-1], raw)):
            ax.annotate(str(raw_val),
                        xy=(angle, val),
                        xytext=(angle, val + 0.08),
                        color=BioTheme.ACCENT_WARNING, fontsize=7.5,
                        ha="center", va="center")
        ax.set_title("🌡️ Métriques globales", color=BioTheme.ACCENT_PRIMARY,
                     fontsize=9, pad=15)

    @classmethod
    def show_radar_standalone(cls, data):
        stats = ProteomeAnalyzer.analyze(data)
        apply_bio_style()
        fig = Figure(figsize=(7, 6))
        fig.patch.set_facecolor(BioTheme.MPL_BG)
        ax = fig.add_subplot(111, polar=True)
        cls._draw_radar(ax, stats, fig)
        cls._open_figure_window(fig, "🌡️ Radar Métriques")

    # ─── 3. HEAT MAP EXPRESSION × WEIGHT ─────────────────────────────────
    @classmethod
    def show_heatmap(cls, data):
        stats = ProteomeAnalyzer.analyze(data)
        proteins = data.get("proteins", [])
        if not proteins:
            messagebox.showinfo("Info", "Aucune protéine à afficher.")
            return

        ids    = [p["id"] for p in proteins]
        expr   = [p.get("meta",{}).get("expression_level", 1.0) for p in proteins]
        weight = [p.get("meta",{}).get("weight", 1.0) for p in proteins]
        phases = [p.get("meta",{}).get("cell_phase","?") for p in proteins]

        apply_bio_style()
        fig = Figure(figsize=(14, 6))
        fig.patch.set_facecolor(BioTheme.MPL_BG)
        gs = gridspec.GridSpec(1, 2, figure=fig, wspace=0.35)
        ax1 = fig.add_subplot(gs[0, 0])
        ax2 = fig.add_subplot(gs[0, 1])
        fig.suptitle("🗺️ Heat Map — Expression × Weight par protéine",
                     color=BioTheme.ACCENT_PRIMARY, fontsize=12, fontweight="bold")

        # Scatter expression vs weight
        phase_colors = {}
        all_phases = list(set(phases))
        for i, ph in enumerate(all_phases):
            phase_colors[ph] = BioTheme.MPL_PALETTE[i % len(BioTheme.MPL_PALETTE)]

        for i, (x, y, pid, ph) in enumerate(zip(expr, weight, ids, phases)):
            ax1.scatter(x, y, color=phase_colors[ph], s=80, zorder=3, alpha=0.9,
                        edgecolors=BioTheme.BG_DARK, linewidths=0.5)
            ax1.annotate(pid[:10], (x, y), textcoords="offset points",
                         xytext=(5, 3), fontsize=6.5, color=BioTheme.TEXT_SECONDARY)

        ax1.set_xlabel("Expression level", fontsize=9)
        ax1.set_ylabel("Weight", fontsize=9)
        ax1.set_title("Scatter Expression vs Weight", color=BioTheme.ACCENT_PRIMARY, fontsize=10)
        ax1.grid(alpha=0.3)
        patches = [mpatches.Patch(color=phase_colors[ph], label=ph) for ph in all_phases]
        ax1.legend(handles=patches, fontsize=7, loc="upper left",
                   facecolor=BioTheme.BG_PANEL, edgecolor=BioTheme.BORDER)

        # Heat map (matrice protéine × métrique)
        matrix = np.array([[e, w] for e, w in zip(expr, weight)])
        im = ax2.imshow(matrix.T, aspect="auto", cmap="plasma",
                        interpolation="nearest", vmin=0)
        ax2.set_yticks([0, 1])
        ax2.set_yticklabels(["Expression", "Weight"], fontsize=8)
        ax2.set_xticks(range(len(ids)))
        ax2.set_xticklabels([i[:10] for i in ids], rotation=60, ha="right", fontsize=6.5)
        ax2.set_title("Heat Map Métriques", color=BioTheme.ACCENT_PRIMARY, fontsize=10)
        fig.colorbar(im, ax=ax2, fraction=0.046, pad=0.04,
                     label="Valeur normalisée").ax.yaxis.label.set_color(BioTheme.TEXT_SECONDARY)

        cls._open_figure_window(fig, "🗺️ Heat Map Expression × Weight")

    # ─── 4. GRAPHE DE DÉPENDANCES (NetworkX) ─────────────────────────────
    @classmethod
    def show_dependency_graph(cls, data):
        G = nx.DiGraph()
        colors_map = {}
        proteins   = data.get("proteins", [])
        operons    = data.get("operons", [])
        transposons= data.get("global_transposons", [])
        plasmids   = data.get("plasmids", [])

        prot_ids = {p["id"] for p in proteins if "id" in p}
        op_ids   = {o["id"] for o in operons   if "id" in o}
        tp_ids   = {t["id"] for t in transposons if "id" in t}
        pl_ids   = {p["id"] for p in plasmids   if "id" in p}

        # Ajouter noeuds
        for pid in prot_ids:
            G.add_node(pid, kind="protein")
            colors_map[pid] = BioTheme.ACCENT_PRIMARY
        for oid in op_ids:
            G.add_node(oid, kind="operon")
            colors_map[oid] = BioTheme.ACCENT_SECONDARY
        for tid in tp_ids:
            G.add_node(tid, kind="transposon")
            colors_map[tid] = BioTheme.ACCENT_DANGER
        for plid in pl_ids:
            G.add_node(plid, kind="plasmid")
            colors_map[plid] = BioTheme.ACCENT_WARNING

        # Arêtes d'héritage protéine
        for p in proteins:
            if p.get("extends") and p["extends"] in prot_ids:
                G.add_edge(p["extends"], p["id"], rel="extends")

        # Arêtes opéron → gènes
        for op in operons:
            for gene in op.get("genes", []):
                if gene in prot_ids:
                    G.add_edge(op["id"], gene, rel="activates")
            if op.get("repressor") and op["repressor"] in op_ids:
                G.add_edge(op["id"], op["repressor"], rel="represses")

        # Arêtes template → references
        for p in proteins:
            if "id" not in p:
                continue
            for line in p.get("template", []):
                for m in re.findall(r'\{\{operon_check:([\w_]+)\}\}', line):
                    if m in op_ids:
                        G.add_edge(p["id"], m, rel="checks_operon")
                for m in re.findall(r'\{\{transposon:([\w_]+)\}\}', line):
                    if m in tp_ids:
                        G.add_edge(p["id"], m, rel="uses_transposon")
                for m in re.findall(r'\{\{plasmid:([\w_]+)\}\}', line):
                    if m in pl_ids:
                        G.add_edge(p["id"], m, rel="injects_plasmid")

        apply_bio_style()
        fig = Figure(figsize=(15, 10))
        fig.patch.set_facecolor(BioTheme.MPL_BG)
        ax = fig.add_subplot(111)
        ax.set_facecolor(BioTheme.MPL_AX_BG)
        ax.set_title(f"🕸️ Graphe de dépendances — {data.get('project','?')}",
                     color=BioTheme.ACCENT_PRIMARY, fontsize=12, fontweight="bold")

        if len(G.nodes) == 0:
            ax.text(0.5, 0.5, "Aucun noeud à afficher", ha="center", va="center",
                    color=BioTheme.TEXT_SECONDARY, fontsize=14, transform=ax.transAxes)
            cls._open_figure_window(fig, "🕸️ Graphe dépendances")
            return

        try:
            pos = nx.spring_layout(G, k=2.5, seed=42, iterations=100)
        except Exception:
            pos = nx.random_layout(G)

        node_colors = [colors_map.get(n, BioTheme.TEXT_MUTED) for n in G.nodes]
        node_sizes  = [500 + G.degree(n) * 80 for n in G.nodes]

        nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors,
                               node_size=node_sizes, alpha=0.9)
        nx.draw_networkx_labels(G, pos, ax=ax,
                                font_size=7, font_color=BioTheme.BG_DARK,
                                font_weight="bold")

        edge_colors_map = {
            "extends":         BioTheme.ACCENT_PRIMARY,
            "activates":       BioTheme.SUCCESS,
            "represses":       BioTheme.ACCENT_DANGER,
            "checks_operon":   BioTheme.ACCENT_SECONDARY,
            "uses_transposon": BioTheme.ACCENT_WARNING,
            "injects_plasmid": BioTheme.ACCENT_PURPLE,
        }
        for rel, color in edge_colors_map.items():
            edges = [(u, v) for u, v, d in G.edges(data=True) if d.get("rel") == rel]
            if edges:
                nx.draw_networkx_edges(G, pos, edgelist=edges, ax=ax,
                                       edge_color=color, arrows=True,
                                       arrowsize=15, width=1.5, alpha=0.7,
                                       connectionstyle="arc3,rad=0.1")

        # Légende
        legend_elements = [
            mpatches.Patch(color=BioTheme.ACCENT_PRIMARY,   label="Protéine"),
            mpatches.Patch(color=BioTheme.ACCENT_SECONDARY, label="Opéron"),
            mpatches.Patch(color=BioTheme.ACCENT_DANGER,    label="Transposon"),
            mpatches.Patch(color=BioTheme.ACCENT_WARNING,   label="Plasmide"),
        ]
        from matplotlib.lines import Line2D
        legend_elements += [
            Line2D([0],[0], color=BioTheme.ACCENT_PRIMARY,   linewidth=2, label="→ extends"),
            Line2D([0],[0], color=BioTheme.SUCCESS,          linewidth=2, label="→ activates"),
            Line2D([0],[0], color=BioTheme.ACCENT_DANGER,    linewidth=2, label="→ represses"),
            Line2D([0],[0], color=BioTheme.ACCENT_SECONDARY, linewidth=2, label="→ checks_operon"),
            Line2D([0],[0], color=BioTheme.ACCENT_WARNING,   linewidth=2, label="→ uses_transposon"),
            Line2D([0],[0], color=BioTheme.ACCENT_PURPLE,    linewidth=2, label="→ injects_plasmid"),
        ]
        ax.legend(handles=legend_elements, loc="upper left", fontsize=7,
                  facecolor=BioTheme.BG_PANEL, edgecolor=BioTheme.BORDER)
        ax.axis("off")

        cls._open_figure_window(fig, "🕸️ Graphe de dépendances",
                                 info=f"{G.number_of_nodes()} noeuds, {G.number_of_edges()} arêtes")

    # ─── 5. SIMULATEUR D'ÉVOLUTION CELLULAIRE ────────────────────────────
    @classmethod
    def show_evolution_simulator(cls, data, parent):
        """Fenêtre de simulation de trajectoire d'état cellulaire"""
        sim_win = Toplevel(parent)
        sim_win.title("📈 Simulateur d'évolution cellulaire")
        sim_win.geometry("1100x750")
        sim_win.configure(bg=BioTheme.BG_DARK)

        # Contrôles
        ctrl = Frame(sim_win, bg=BioTheme.BG_PANEL, pady=8)
        ctrl.pack(fill=X, padx=10, pady=(10,0))

        Label(ctrl, text="⚙️ PARAMÈTRES DE SIMULATION",
              font=BioTheme.FONT_HEADER, fg=BioTheme.ACCENT_PRIMARY,
              bg=BioTheme.BG_PANEL).pack(side=LEFT, padx=10)

        Label(ctrl, text="Générations:", fg=BioTheme.TEXT_SECONDARY,
              bg=BioTheme.BG_PANEL, font=BioTheme.FONT_MAIN).pack(side=LEFT, padx=5)
        gen_var = IntVar(value=50)
        Spinbox(ctrl, from_=10, to=500, textvariable=gen_var, width=6,
                bg=BioTheme.BG_EDITOR, fg=BioTheme.ACCENT_PRIMARY,
                buttonbackground=BioTheme.BG_PANEL, relief=FLAT,
                font=BioTheme.FONT_MAIN).pack(side=LEFT, padx=5)

        Label(ctrl, text="Runs:", fg=BioTheme.TEXT_SECONDARY,
              bg=BioTheme.BG_PANEL, font=BioTheme.FONT_MAIN).pack(side=LEFT, padx=5)
        runs_var = IntVar(value=5)
        Spinbox(ctrl, from_=1, to=20, textvariable=runs_var, width=4,
                bg=BioTheme.BG_EDITOR, fg=BioTheme.ACCENT_PRIMARY,
                buttonbackground=BioTheme.BG_PANEL, relief=FLAT,
                font=BioTheme.FONT_MAIN).pack(side=LEFT, padx=5)

        Label(ctrl, text="État initial:", fg=BioTheme.TEXT_SECONDARY,
              bg=BioTheme.BG_PANEL, font=BioTheme.FONT_MAIN).pack(side=LEFT, padx=5)
        state0_var = IntVar(value=5)
        Spinbox(ctrl, from_=0, to=20, textvariable=state0_var, width=4,
                bg=BioTheme.BG_EDITOR, fg=BioTheme.ACCENT_PRIMARY,
                buttonbackground=BioTheme.BG_PANEL, relief=FLAT,
                font=BioTheme.FONT_MAIN).pack(side=LEFT, padx=5)

        # Figure
        apply_bio_style()
        fig = Figure(figsize=(12, 7))
        fig.patch.set_facecolor(BioTheme.MPL_BG)
        canvas = FigureCanvasTkAgg(fig, master=sim_win)
        canvas.get_tk_widget().pack(fill=BOTH, expand=True, padx=10, pady=5)
        toolbar = NavigationToolbar2Tk(canvas, sim_win)
        toolbar.config(background=BioTheme.BG_PANEL)
        toolbar.update()

        def run_simulation():
            fig.clear()
            gs  = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.35)
            ax1 = fig.add_subplot(gs[0, :])   # trajectoires d'état
            ax2 = fig.add_subplot(gs[1, 0])   # distribution finale
            ax3 = fig.add_subplot(gs[1, 1])   # taux d'apoptose / mitose

            n_gen  = gen_var.get()
            n_runs = runs_var.get()
            s0     = state0_var.get()

            glb     = data.get("global", {})
            mut_rate= glb.get("mutation_rate", 0.03)
            mitosis = glb.get("mitosis_threshold", 12)
            apop    = glb.get("apoptosis_threshold", 0)

            all_trajectories = []
            final_states     = []
            apoptosis_events = []
            mitosis_events   = []

            for run in range(n_runs):
                traj    = [s0]
                apop_g  = []
                mito_g  = []
                state   = s0
                for gen in range(1, n_gen + 1):
                    # Dérive stochastique basée sur les paramètres du protéome
                    delta = np.random.normal(0, 1.5)
                    if np.random.random() < mut_rate:
                        delta += np.random.choice([-3, -2, -1, 1, 2, 3])
                    state = max(0, int(state + delta))
                    if state <= apop:
                        apop_g.append(gen)
                        state = max(1, s0 // 2)  # renaissance
                    if state >= mitosis:
                        mito_g.append(gen)
                        state = state // 2        # mitose
                    traj.append(state)
                all_trajectories.append(traj)
                final_states.append(traj[-1])
                apoptosis_events.append(len(apop_g))
                mitosis_events.append(len(mito_g))

            gens = list(range(n_gen + 1))
            for i, traj in enumerate(all_trajectories):
                color = BioTheme.MPL_PALETTE[i % len(BioTheme.MPL_PALETTE)]
                ax1.plot(gens, traj, color=color, linewidth=1.2, alpha=0.75,
                         label=f"Run {i+1}")

            mean_traj = np.mean(all_trajectories, axis=0)
            ax1.plot(gens, mean_traj, color=BioTheme.ACCENT_WARNING,
                     linewidth=2.5, linestyle="--", label="Moyenne", zorder=5)
            ax1.axhline(y=mitosis, color=BioTheme.SUCCESS, linestyle=":",
                        linewidth=1.5, label=f"Seuil mitose ({mitosis})")
            ax1.axhline(y=apop, color=BioTheme.ACCENT_DANGER, linestyle=":",
                        linewidth=1.5, label=f"Seuil apoptose ({apop})")
            ax1.set_xlabel("Génération", fontsize=9)
            ax1.set_ylabel("État cellulaire", fontsize=9)
            ax1.set_title("📈 Trajectoire d'état cellulaire",
                          color=BioTheme.ACCENT_PRIMARY, fontsize=10)
            ax1.legend(fontsize=7.5, loc="upper right",
                       facecolor=BioTheme.BG_PANEL, edgecolor=BioTheme.BORDER)
            ax1.grid(alpha=0.3)

            ax2.hist(final_states, bins=min(10, n_runs),
                     color=BioTheme.ACCENT_PRIMARY, edgecolor=BioTheme.BG_DARK,
                     linewidth=0.5, alpha=0.85)
            ax2.set_xlabel("État final", fontsize=9)
            ax2.set_ylabel("Fréquence", fontsize=9)
            ax2.set_title("Distribution états finaux",
                          color=BioTheme.ACCENT_PRIMARY, fontsize=9)
            ax2.grid(axis="y", alpha=0.3)

            x = np.arange(n_runs)
            w = 0.35
            ax3.bar(x - w/2, apoptosis_events, w, label="Apoptoses",
                    color=BioTheme.ACCENT_DANGER, edgecolor=BioTheme.BG_DARK, linewidth=0.5)
            ax3.bar(x + w/2, mitosis_events, w, label="Mitoses",
                    color=BioTheme.SUCCESS, edgecolor=BioTheme.BG_DARK, linewidth=0.5)
            ax3.set_xticks(x)
            ax3.set_xticklabels([f"R{i+1}" for i in range(n_runs)], fontsize=8)
            ax3.set_title("Événements cellulaires / Run",
                          color=BioTheme.ACCENT_PRIMARY, fontsize=9)
            ax3.legend(fontsize=7.5, facecolor=BioTheme.BG_PANEL)
            ax3.grid(axis="y", alpha=0.3)

            fig.suptitle(
                f"📈 Simulation évolution cellulaire — {n_runs} runs × {n_gen} générations",
                color=BioTheme.ACCENT_PRIMARY, fontsize=11, fontweight="bold")
            canvas.draw()

        Button(ctrl, text="▶ SIMULER", command=run_simulation,
               bg=BioTheme.ACCENT_PRIMARY, fg=BioTheme.BG_DARK,
               font=("Consolas", 9, "bold"), cursor="hand2",
               relief=FLAT, padx=12, pady=4).pack(side=LEFT, padx=15)

        run_simulation()

    # ─── 6. COMPARATEUR DE CONFIGS (DIFF VISUEL) ─────────────────────────
    @classmethod
    def show_diff(cls, data_a, data_b, name_a="Config A", name_b="Config B", parent=None):
        diff_win = Toplevel(parent)
        diff_win.title(f"⚖️ Comparateur — {name_a} vs {name_b}")
        diff_win.geometry("1200x700")
        diff_win.configure(bg=BioTheme.BG_DARK)

        Label(diff_win,
              text=f"⚖️ DIFF STRUCTUREL : {name_a}  ↔  {name_b}",
              font=BioTheme.FONT_HEADER, fg=BioTheme.ACCENT_PRIMARY,
              bg=BioTheme.BG_DARK).pack(pady=8)

        # Stats comparées
        stats_a = ProteomeAnalyzer.analyze(data_a)
        stats_b = ProteomeAnalyzer.analyze(data_b)

        apply_bio_style()
        fig = Figure(figsize=(13, 4.5))
        fig.patch.set_facecolor(BioTheme.MPL_BG)
        ax = fig.add_subplot(111)
        ax.set_facecolor(BioTheme.MPL_AX_BG)

        metrics = ["proteins_count","operons_count","plasmids_count",
                   "transposons_count","inheritance_count","epigenetic_markers_count"]
        labels  = ["Protéines","Opérons","Plasmides","Transposons","Héritages","Marqueurs ép."]
        vals_a  = [stats_a[m] for m in metrics]
        vals_b  = [stats_b[m] for m in metrics]
        x = np.arange(len(labels))
        w = 0.35
        ax.bar(x - w/2, vals_a, w, label=name_a,
               color=BioTheme.ACCENT_PRIMARY, edgecolor=BioTheme.BG_DARK, linewidth=0.5)
        ax.bar(x + w/2, vals_b, w, label=name_b,
               color=BioTheme.ACCENT_SECONDARY, edgecolor=BioTheme.BG_DARK, linewidth=0.5)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=9)
        ax.set_title("Comparaison des métriques structurelles",
                     color=BioTheme.ACCENT_PRIMARY, fontsize=10)
        ax.legend(fontsize=9, facecolor=BioTheme.BG_PANEL)
        ax.grid(axis="y", alpha=0.4)

        canvas = FigureCanvasTkAgg(fig, master=diff_win)
        canvas.get_tk_widget().pack(fill=X, padx=10)
        canvas.draw()

        # Diff JSON textuel
        text_frame = Frame(diff_win, bg=BioTheme.BG_DARK)
        text_frame.pack(fill=BOTH, expand=True, padx=10, pady=8)

        Label(text_frame, text="📝 Diff JSON (lignes modifiées)",
              font=BioTheme.FONT_HEADER, fg=BioTheme.ACCENT_WARNING,
              bg=BioTheme.BG_DARK).pack()

        diff_text = Text(text_frame, bg=BioTheme.BG_EDITOR, fg=BioTheme.TEXT_PRIMARY,
                         font=BioTheme.FONT_TERMINAL, relief=FLAT, wrap=NONE)
        diff_text.pack(fill=BOTH, expand=True)
        sb = Scrollbar(text_frame, command=diff_text.yview)
        sb.pack(side=RIGHT, fill=Y)
        diff_text.config(yscrollcommand=sb.set)

        str_a = json.dumps(data_a, indent=2, ensure_ascii=False).splitlines(keepends=True)
        str_b = json.dumps(data_b, indent=2, ensure_ascii=False).splitlines(keepends=True)
        diff_lines = list(difflib.unified_diff(str_a, str_b,
                                               fromfile=name_a, tofile=name_b, n=2))

        diff_text.tag_config("add",    foreground=BioTheme.SUCCESS)
        diff_text.tag_config("remove", foreground=BioTheme.ACCENT_DANGER)
        diff_text.tag_config("info",   foreground=BioTheme.ACCENT_SECONDARY)
        diff_text.tag_config("header", foreground=BioTheme.ACCENT_WARNING)

        for line in diff_lines:
            if line.startswith("+++") or line.startswith("---"):
                diff_text.insert(END, line, "header")
            elif line.startswith("+"):
                diff_text.insert(END, line, "add")
            elif line.startswith("-"):
                diff_text.insert(END, line, "remove")
            elif line.startswith("@@"):
                diff_text.insert(END, line, "info")
            else:
                diff_text.insert(END, line)
        diff_text.config(state=DISABLED)

    # ─── 7. ÉPIGÉNÉTIQUE ENRICHI ──────────────────────────────────────────
    @classmethod
    def show_epigenetics(cls, data):
        stats = ProteomeAnalyzer.analyze(data)
        markers = stats["epigenetic_markers_list"]
        if not markers:
            messagebox.showinfo("Info", "Aucun marqueur épigénétique dans ce protéome.")
            return

        mc = Counter(markers)
        apply_bio_style()
        fig = Figure(figsize=(13, 5))
        fig.patch.set_facecolor(BioTheme.MPL_BG)
        gs = gridspec.GridSpec(1, 2, figure=fig, wspace=0.4)
        ax1 = fig.add_subplot(gs[0, 0])
        ax2 = fig.add_subplot(gs[0, 1])
        fig.suptitle("🏷️ Analyse épigénétique",
                     color=BioTheme.ACCENT_PRIMARY, fontsize=12, fontweight="bold")

        top_n = dict(mc.most_common(15))
        colors = BioTheme.MPL_PALETTE[:len(top_n)]
        ax1.barh(list(top_n.keys()), list(top_n.values()),
                 color=colors, edgecolor=BioTheme.BG_DARK, linewidth=0.5)
        ax1.set_xlabel("Occurrences", fontsize=9)
        ax1.set_title("Fréquence des marqueurs (top 15)",
                      color=BioTheme.ACCENT_PRIMARY, fontsize=10)
        ax1.grid(axis="x", alpha=0.4)
        ax1.tick_params(labelsize=7.5)

        # Marqueurs par protéine
        proteins = data.get("proteins", [])
        marker_counts = {p["id"]: len(p.get("epigenetic_markers", []))
                         for p in proteins if "id" in p}
        sorted_mc = dict(sorted(marker_counts.items(), key=lambda x: x[1], reverse=True))
        color_bars = [BioTheme.ACCENT_PURPLE if v > 0 else BioTheme.TEXT_MUTED
                      for v in sorted_mc.values()]
        ax2.bar(list(sorted_mc.keys()), list(sorted_mc.values()),
                color=color_bars, edgecolor=BioTheme.BG_DARK, linewidth=0.5)
        ax2.set_xticklabels(list(sorted_mc.keys()), rotation=45, ha="right", fontsize=7)
        ax2.set_ylabel("Nb marqueurs", fontsize=9)
        ax2.set_title("Marqueurs par protéine",
                      color=BioTheme.ACCENT_PRIMARY, fontsize=10)
        ax2.grid(axis="y", alpha=0.4)

        cls._open_figure_window(fig, "🏷️ Épigénétique")

    # ─── 8. RAPPORT HTML ──────────────────────────────────────────────────
    @classmethod
    def export_html_report(cls, data, filepath):
        stats = ProteomeAnalyzer.analyze(data)
        apply_bio_style()

        # Générer les figures en base64
        def fig_to_b64(fig):
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=96, bbox_inches="tight",
                        facecolor=BioTheme.MPL_BG)
            buf.seek(0)
            return base64.b64encode(buf.read()).decode()

        # Figure 1: Phases + Expression
        fig1, (a1, a2) = plt.subplots(1, 2, figsize=(13, 4))
        fig1.patch.set_facecolor(BioTheme.MPL_BG)
        phases = stats["phases"]
        if phases:
            a1.pie(phases.values(), labels=phases.keys(),
                   colors=BioTheme.MPL_PALETTE[:len(phases)],
                   autopct="%1.0f%%", startangle=90,
                   textprops={"fontsize":8,"color":BioTheme.TEXT_PRIMARY},
                   wedgeprops={"edgecolor":BioTheme.BG_DARK})
            for t in a1.texts:
                t.set_color(BioTheme.TEXT_PRIMARY)
        a1.set_facecolor(BioTheme.MPL_AX_BG)
        a1.set_title("Phases cellulaires", color=BioTheme.ACCENT_PRIMARY, fontsize=10)
        expr = stats["expression_levels"]
        if expr:
            a2.barh(list(expr.keys()), list(expr.values()),
                    color=BioTheme.MPL_PALETTE[:len(expr)], edgecolor=BioTheme.BG_DARK)
        a2.set_title("Expression levels", color=BioTheme.ACCENT_PRIMARY, fontsize=10)
        a2.grid(axis="x", alpha=0.4)
        a2.tick_params(labelsize=7.5)
        b64_1 = fig_to_b64(fig1)
        plt.close(fig1)

        # Figure 2: Heatmap expression × weight
        proteins = data.get("proteins", [])
        if proteins:
            ids = [p["id"] for p in proteins]
            expr_v = [p.get("meta",{}).get("expression_level",1.0) for p in proteins]
            wt_v   = [p.get("meta",{}).get("weight",1.0) for p in proteins]
            matrix = np.array([[e, w] for e, w in zip(expr_v, wt_v)])
            fig2, ax2 = plt.subplots(figsize=(13, 3))
            fig2.patch.set_facecolor(BioTheme.MPL_BG)
            ax2.set_facecolor(BioTheme.MPL_AX_BG)
            im = ax2.imshow(matrix.T, aspect="auto", cmap="plasma",
                            interpolation="nearest")
            ax2.set_yticks([0, 1])
            ax2.set_yticklabels(["Expression", "Weight"], fontsize=9)
            ax2.set_xticks(range(len(ids)))
            ax2.set_xticklabels([i[:12] for i in ids], rotation=60, ha="right", fontsize=7)
            ax2.set_title("Heat Map Expression × Weight", color=BioTheme.ACCENT_PRIMARY, fontsize=10)
            fig2.colorbar(im, ax=ax2, fraction=0.03, pad=0.02)
            b64_2 = fig_to_b64(fig2)
            plt.close(fig2)
        else:
            b64_2 = ""

        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>🧬 Rapport Protéome — {data.get('project','?')}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
  :root {{
    --bg:#0a0f0f; --panel:#0f1515; --editor:#0c1212;
    --green:#00ff9d; --cyan:#00d4ff; --yellow:#ffcc00;
    --red:#ff3366; --purple:#b84dff; --text:#e0f2fe;
    --muted:#8ba3b8; --border:#1a2a2a;
  }}
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ background:var(--bg); color:var(--text); font-family:'Share Tech Mono',monospace; padding:30px; }}
  h1 {{ color:var(--green); font-size:1.6rem; border-bottom:2px solid var(--border); padding-bottom:12px; margin-bottom:24px; }}
  h2 {{ color:var(--cyan); font-size:1.1rem; margin:28px 0 10px; border-left:3px solid var(--cyan); padding-left:10px; }}
  .meta {{ color:var(--muted); font-size:0.85rem; margin-bottom:20px; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:14px; margin:14px 0; }}
  .card {{ background:var(--panel); border:1px solid var(--border); border-radius:6px; padding:16px; text-align:center; }}
  .card .val {{ font-size:2rem; font-weight:bold; }}
  .card .lbl {{ font-size:0.75rem; color:var(--muted); margin-top:4px; }}
  .green {{ color:var(--green); }}
  .cyan  {{ color:var(--cyan);  }}
  .yellow{{ color:var(--yellow);}}
  .red   {{ color:var(--red);   }}
  .purple{{ color:var(--purple);}}
  table {{ width:100%; border-collapse:collapse; font-size:0.85rem; margin:12px 0; }}
  th {{ background:var(--panel); color:var(--green); padding:8px 12px; text-align:left; border-bottom:1px solid var(--border); }}
  td {{ padding:6px 12px; border-bottom:1px solid var(--border); color:var(--text); }}
  tr:hover td {{ background:var(--panel); }}
  img {{ width:100%; border:1px solid var(--border); border-radius:4px; margin:10px 0; }}
  .phase-tag {{ display:inline-block; background:var(--panel); border:1px solid var(--cyan); border-radius:3px; padding:1px 6px; font-size:0.75rem; margin:2px; color:var(--cyan); }}
  footer {{ margin-top:40px; padding-top:16px; border-top:1px solid var(--border); color:var(--muted); font-size:0.8rem; text-align:center; }}
</style>
</head>
<body>
<h1>🧬 RAPPORT PROTÉOME — {data.get('project','?')}</h1>
<div class="meta">Schéma v{data.get('schema_version','?')} · Langage: {data.get('global',{}).get('language','?')} · Généré le {ts}</div>
<p style="color:var(--muted);margin-bottom:20px;">{data.get('description','')}</p>

<h2>📊 Vue d'ensemble</h2>
<div class="grid">
  <div class="card"><div class="val green">{stats['proteins_count']}</div><div class="lbl">🔬 Protéines</div></div>
  <div class="card"><div class="val cyan">{stats['operons_count']}</div><div class="lbl">🎛️ Opérons</div></div>
  <div class="card"><div class="val yellow">{stats['plasmids_count']}</div><div class="lbl">🧫 Plasmides</div></div>
  <div class="card"><div class="val red">{stats['transposons_count']}</div><div class="lbl">🦠 Transposons</div></div>
  <div class="card"><div class="val purple">{stats['epigenetic_markers_count']}</div><div class="lbl">🏷️ Marqueurs ép. uniques</div></div>
  <div class="card"><div class="val cyan">{stats['inheritance_count']}</div><div class="lbl">🧬 Héritages</div></div>
  <div class="card"><div class="val yellow">{stats['sub_proteins_count']}</div><div class="lbl">🔩 Sous-protéines</div></div>
  <div class="card"><div class="val green">{stats['avg_mutation_rate']:.3f}</div><div class="lbl">⚡ Taux mutation moyen</div></div>
</div>

<h2>🧬 Protéines</h2>
<table>
  <tr><th>ID</th><th>Phase</th><th>Expression</th><th>Weight</th><th>Marqueurs ép.</th><th>Hérite de</th></tr>
"""
        for p in data.get("proteins", []):
            meta   = p.get("meta", {})
            phase  = meta.get("cell_phase", "?")
            expr   = meta.get("expression_level", "?")
            wt     = meta.get("weight", "?")
            marks  = ", ".join(p.get("epigenetic_markers", [])) or "—"
            parent = p.get("extends") or "—"
            html += f"  <tr><td class='green'>{p.get('id','?')}</td><td><span class='phase-tag'>{phase}</span></td><td>{expr}</td><td>{wt}</td><td style='font-size:0.78rem;'>{marks}</td><td>{parent}</td></tr>\n"

        html += "</table>\n<h2>🎛️ Opérons</h2>\n<table>\n  <tr><th>ID</th><th>Condition promoteur</th><th>Gènes</th><th>Répresseur</th></tr>\n"
        for op in data.get("operons", []):
            genes = ", ".join(op.get("genes", []))
            rep   = op.get("repressor") or "—"
            html += f"  <tr><td class='cyan'>{op.get('id','?')}</td><td>{op.get('promoter_condition','?')}</td><td>{genes}</td><td>{rep}</td></tr>\n"

        html += "</table>\n<h2>🧫 Plasmides</h2>\n<table>\n  <tr><th>ID</th><th>Circulaire</th><th>Copies</th><th>Description</th></tr>\n"
        for pl in data.get("plasmids", []):
            html += f"  <tr><td class='yellow'>{pl.get('id','?')}</td><td>{'✓' if pl.get('circular') else '✗'}</td><td>{pl.get('copy_number',1)}</td><td>{pl.get('description','')}</td></tr>\n"

        html += "</table>\n<h2>🦠 Transposons</h2>\n<table>\n  <tr><th>ID</th><th>Jump prob</th><th>Description</th></tr>\n"
        for tp in data.get("global_transposons", []):
            html += f"  <tr><td class='red'>{tp.get('id','?')}</td><td>{tp.get('jump_prob',0):.2f}</td><td>{tp.get('description','')}</td></tr>\n"

        html += f"""</table>
<h2>📈 Phases cellulaires</h2>
<div class="grid">
"""
        for ph, cnt in stats["phases"].items():
            html += f"  <div class='card'><div class='val cyan'>{cnt}</div><div class='lbl'>{ph}</div></div>\n"

        html += f"""</div>
<h2>🖼️ Visualisations</h2>
<img src="data:image/png;base64,{b64_1}" alt="Phases & Expression levels">
"""
        if b64_2:
            html += f'<img src="data:image/png;base64,{b64_2}" alt="Heat Map Expression x Weight">\n'

        html += f"""
<footer>
  ProteomEditor v2.0 · Rapport généré le {ts}<br>
  Bio-Hacking Level: ⚡⚡⚡⚡⚡
</footer>
</body>
</html>"""

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        return filepath

    # ─── helper: ouvrir une fenêtre Matplotlib dans Tkinter ──────────────
    @classmethod
    def _open_figure_window(cls, fig, title="Figure", info=""):
        win = Toplevel()
        win.title(title)
        win.configure(bg=BioTheme.BG_DARK)
        win.geometry("1200x750")
        if info:
            Label(win, text=info, bg=BioTheme.BG_DARK,
                  fg=BioTheme.TEXT_MUTED, font=("Consolas", 9)).pack(anchor=W, padx=10)
        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        toolbar = NavigationToolbar2Tk(canvas, win)
        toolbar.config(background=BioTheme.BG_PANEL)
        for child in toolbar.winfo_children():
            try:
                child.config(background=BioTheme.BG_PANEL)
            except Exception:
                pass
        toolbar.update()
        canvas.draw()


# =============================================================================
# BARRE DE RECHERCHE (dock sous la toolbar)
# =============================================================================
class SearchBar:
    def __init__(self, parent, editor: JsonEditor):
        self.editor = editor
        self.frame = Frame(parent, bg=BioTheme.BG_PANEL, height=30)
        self.frame.pack(fill=X, padx=5, pady=(0, 2))
        self.frame.pack_propagate(False)
        self.visible = False

        Label(self.frame, text="🔍 CHERCHER:", fg=BioTheme.ACCENT_SECONDARY,
              bg=BioTheme.BG_PANEL, font=("Consolas", 9)).pack(side=LEFT, padx=6)
        self._var = StringVar()
        self._var.trace("w", self._on_change)
        Entry(self.frame, textvariable=self._var, width=28,
              bg=BioTheme.BG_EDITOR, fg=BioTheme.TEXT_PRIMARY,
              insertbackground=BioTheme.ACCENT_PRIMARY,
              relief=FLAT, font=("Consolas", 9)).pack(side=LEFT, padx=3)
        self._count_lbl = Label(self.frame, text="", fg=BioTheme.TEXT_MUTED,
                                bg=BioTheme.BG_PANEL, font=("Consolas", 9))
        self._count_lbl.pack(side=LEFT, padx=4)
        Button(self.frame, text="▲", command=self.editor.search_prev,
               bg=BioTheme.BG_EDITOR, fg=BioTheme.ACCENT_PRIMARY,
               relief=FLAT, font=("Consolas", 9), cursor="hand2",
               padx=6).pack(side=LEFT, padx=2)
        Button(self.frame, text="▼", command=self.editor.search_next,
               bg=BioTheme.BG_EDITOR, fg=BioTheme.ACCENT_PRIMARY,
               relief=FLAT, font=("Consolas", 9), cursor="hand2",
               padx=6).pack(side=LEFT, padx=2)
        Button(self.frame, text="✕", command=self.hide,
               bg=BioTheme.BG_EDITOR, fg=BioTheme.ACCENT_DANGER,
               relief=FLAT, font=("Consolas", 9), cursor="hand2",
               padx=6).pack(side=LEFT, padx=4)

        self.frame.pack_forget()

    def show(self):
        self.frame.pack(fill=X, padx=5, pady=(0, 2))
        self.visible = True

    def hide(self):
        self.frame.pack_forget()
        self.editor.search("")
        self.visible = False

    def toggle(self):
        if self.visible:
            self.hide()
        else:
            self.show()

    def _on_change(self, *_):
        n = self.editor.search(self._var.get())
        self._count_lbl.config(
            text=f"{n} résultat(s)" if self._var.get() else "",
            fg=BioTheme.SUCCESS if n else BioTheme.ACCENT_DANGER)


# =============================================================================
# INTERFACE PRINCIPALE v2.0
# =============================================================================
class ProteomEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("🧬 PROTEOMEDITOR v2.0 — Bio-Hacking Interface")
        self.root.geometry("1500x900")
        self.root.configure(bg=BioTheme.BG_DARK)

        self.current_file  = None
        self.data          = None
        self._compare_data = None  # Pour le comparateur

        self._setup_ui()
        self.logger = LabLogger(self.console)
        self.logger.info("ProteomEditor v2.0 démarré — Visualisation scientifique activée")
        self.logger.viz("Modules: Dashboard · Graphe · Heatmap · Évolution · Diff · Épigénétique · Export HTML")

    # ──────────────────────────────────────────────────────────────────────
    def _setup_ui(self):
        self._setup_menu()
        self._setup_toolbar()

        main_panel = PanedWindow(self.root, bg=BioTheme.BG_DARK, sashwidth=4, sashrelief=RAISED)
        main_panel.pack(fill=BOTH, expand=True, padx=5, pady=5)

        left_panel = Frame(main_panel, bg=BioTheme.BG_DARK)
        main_panel.add(left_panel, width=370)
        self.tree = ProteomeTree(left_panel, self._on_tree_select)

        right_panel = Frame(main_panel, bg=BioTheme.BG_DARK)
        main_panel.add(right_panel, width=1130)

        editor_frame = LabelFrame(right_panel, text="✏️ ÉDITEUR JSON",
                                  font=BioTheme.FONT_HEADER,
                                  fg=BioTheme.ACCENT_SECONDARY,
                                  bg=BioTheme.BG_PANEL, bd=2, relief=SOLID)
        editor_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        self.editor = JsonEditor(editor_frame, wrap=NONE, height=25)
        self.editor.pack(fill=BOTH, expand=True, padx=5, pady=5)

        # Barre de recherche (dock dynamique)
        self.search_bar = SearchBar(right_panel, self.editor)

        console_frame = LabelFrame(right_panel, text="📟 CONSOLE DE LABORATOIRE",
                                   font=BioTheme.FONT_HEADER,
                                   fg=BioTheme.ACCENT_WARNING,
                                   bg=BioTheme.BG_PANEL, bd=2, relief=SOLID)
        console_frame.pack(fill=BOTH, expand=False, padx=10, pady=(0, 10))

        self.console = Text(console_frame, height=7, bg=BioTheme.BG_EDITOR,
                            fg=BioTheme.TEXT_SECONDARY, font=BioTheme.FONT_TERMINAL,
                            relief=FLAT, wrap=WORD)
        self.console.pack(fill=BOTH, expand=True, padx=5, pady=5)

        self.status_bar = Label(self.root, text="⚡ PRÊT", bg=BioTheme.BG_PANEL,
                                fg=BioTheme.ACCENT_PRIMARY, font=("Consolas", 9),
                                anchor=W, padx=10)
        self.status_bar.pack(fill=X, side=BOTTOM)

    # ──────────────────────────────────────────────────────────────────────
    def _setup_menu(self):
        menubar = Menu(self.root, bg=BioTheme.BG_PANEL, fg=BioTheme.TEXT_PRIMARY,
                       activebackground=BioTheme.ACCENT_SECONDARY,
                       activeforeground=BioTheme.BG_DARK)
        self.root.config(menu=menubar)

        # Fichier
        fm = Menu(menubar, tearoff=0, bg=BioTheme.BG_PANEL, fg=BioTheme.TEXT_PRIMARY)
        fm.add_command(label="📂 Charger",         command=self._load_file,  accelerator="Ctrl+O")
        fm.add_command(label="💾 Sauvegarder",     command=self._save_file,  accelerator="Ctrl+S")
        fm.add_command(label="📎 Sauvegarder sous…", command=self._save_as)
        fm.add_separator()
        fm.add_command(label="🔄 Recharger",       command=self._reload)
        fm.add_separator()
        fm.add_command(label="📄 Exporter rapport HTML", command=self._export_html)
        fm.add_separator()
        fm.add_command(label="❌ Quitter",         command=self.root.quit)
        menubar.add_cascade(label="Fichier", menu=fm)

        # Édition
        em = Menu(menubar, tearoff=0, bg=BioTheme.BG_PANEL, fg=BioTheme.TEXT_PRIMARY)
        em.add_command(label="🔍 Valider",          command=self._validate)
        em.add_command(label="🧹 Nettoyer",         command=self._clean)
        em.add_command(label="📊 Analyser",         command=self._analyze)
        em.add_separator()
        em.add_command(label="🧬 Mutation contrôlée…", command=self._mutate)
        em.add_command(label="🩺 Réparation auto",  command=self._repair)
        em.add_separator()
        em.add_command(label="🔎 Rechercher…",      command=lambda: self.search_bar.toggle(), accelerator="Ctrl+F")
        menubar.add_cascade(label="Édition", menu=em)

        # Visualisation  ←  nouveau menu
        vm = Menu(menubar, tearoff=0, bg=BioTheme.BG_PANEL, fg=BioTheme.TEXT_PRIMARY)
        vm.add_command(label="📊 Dashboard complet",        command=self._show_dashboard)
        vm.add_command(label="🕸️  Graphe de dépendances",  command=self._show_graph)
        vm.add_command(label="🗺️  Heat Map Expression×Weight", command=self._show_heatmap)
        vm.add_command(label="🌡️  Radar métriques",        command=self._show_radar)
        vm.add_command(label="🏷️  Analyse épigénétique",   command=self._show_epigenetics)
        vm.add_separator()
        vm.add_command(label="📈 Simulateur d'évolution",  command=self._show_evolution)
        vm.add_separator()
        vm.add_command(label="⚖️  Comparer deux configs…", command=self._show_diff)
        vm.add_separator()
        vm.add_command(label="📄 Métriques texte",          command=self._show_stats)
        menubar.add_cascade(label="Visualisation", menu=vm)

        # Aide
        hm = Menu(menubar, tearoff=0, bg=BioTheme.BG_PANEL, fg=BioTheme.TEXT_PRIMARY)
        hm.add_command(label="📖 Documentation",   command=self._show_docs)
        hm.add_command(label="ℹ️  À propos",       command=self._show_about)
        menubar.add_cascade(label="Aide", menu=hm)

        self.root.bind("<Control-o>", lambda e: self._load_file())
        self.root.bind("<Control-s>", lambda e: self._save_file())
        self.root.bind("<Control-f>", lambda e: self.search_bar.toggle())

    # ──────────────────────────────────────────────────────────────────────
    def _setup_toolbar(self):
        toolbar = Frame(self.root, bg=BioTheme.BG_PANEL, height=48)
        toolbar.pack(fill=X)
        toolbar.pack_propagate(False)

        buttons = [
            ("🧬 CHARGER",    self._load_file,      BioTheme.ACCENT_PRIMARY),
            ("💾 SAUVEGARDER",self._save_file,      BioTheme.ACCENT_SECONDARY),
            ("🔍 VALIDER",    self._validate,       BioTheme.ACCENT_WARNING),
            ("🧹 NETTOYER",   self._clean,          BioTheme.ACCENT_PURPLE),
            ("📊 ANALYSER",   self._analyze,        BioTheme.SUCCESS),
            ("🧬 MUTATION",   self._mutate,         BioTheme.ACCENT_DANGER),
            # v2 quick-access
            ("📊 DASHBOARD",  self._show_dashboard, BioTheme.ACCENT_PRIMARY),
            ("🕸️ GRAPHE",    self._show_graph,     BioTheme.ACCENT_SECONDARY),
            ("📈 ÉVOLUTION",  self._show_evolution, BioTheme.SUCCESS),
            ("📄 RAPPORT",    self._export_html,    BioTheme.ACCENT_WARNING),
        ]
        sep_before = {"📊 DASHBOARD"}
        for text, cmd, color in buttons:
            if text in sep_before:
                Frame(toolbar, bg=BioTheme.BORDER, width=2,
                      height=30).pack(side=LEFT, padx=4, pady=8)
            btn = Button(toolbar, text=text, command=cmd,
                         bg=BioTheme.BG_EDITOR, fg=color,
                         activebackground=color, activeforeground=BioTheme.BG_DARK,
                         relief=FLAT, font=("Consolas", 8, "bold"),
                         cursor="hand2", padx=10, pady=6)
            btn.pack(side=LEFT, padx=2, pady=6)

    # ──────────────────────────────────────────────────────────────────────
    # I/O
    # ──────────────────────────────────────────────────────────────────────
    def _load_file(self, path=None):
        if not path:
            path = filedialog.askopenfilename(
                title="Charger configuration protéome",
                filetypes=[("JSON","*.json"),("Tous","*.*")])
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
                self.current_file = path
                self.editor.set_json(self.data)
                self.tree.load_data(self.data)
                self.logger.success(f"Chargé: {Path(path).name}")
                self.status_bar.config(text=f"📁 {path}")
                self._analyze(show=False)
            except Exception as e:
                self.logger.error(f"Erreur chargement: {e}")

    def _save_file(self):
        if not self.current_file:
            self._save_as(); return
        try:
            self.data = self.editor.get_json()
            with open(self.current_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            self.logger.success(f"Sauvegardé: {Path(self.current_file).name}")
            self.tree.load_data(self.data)
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde: {e}")

    def _save_as(self):
        path = filedialog.asksaveasfilename(
            title="Sauvegarder sous",
            defaultextension=".json",
            filetypes=[("JSON","*.json")])
        if path:
            self.current_file = path
            self._save_file()

    def _reload(self):
        if self.current_file:
            self._load_file(self.current_file)

    # ──────────────────────────────────────────────────────────────────────
    # OPÉRATIONS v1
    # ──────────────────────────────────────────────────────────────────────
    def _validate(self):
        if not self.data:
            self.logger.warning("Aucune donnée chargée"); return
        errors, warnings = ProteomeValidator.validate(self.data)
        for err in errors:   self.logger.error(err)
        for w in warnings:   self.logger.warning(w)
        if not errors and not warnings:
            self.logger.success("✅ Validation réussie — Structure conforme")
        else:
            self.logger.validation(f"{len(errors)} erreur(s), {len(warnings)} avertissement(s)")

    def _clean(self):
        if not self.data: return
        try:
            cleaned = json.loads(json.dumps(self.data, indent=2))
            if "global" in cleaned:
                cleaned["global"].pop("_comment", None)
            self.data = cleaned
            self.editor.set_json(self.data)
            self.logger.success("Nettoyage effectué")
        except Exception as e:
            self.logger.error(f"Erreur nettoyage: {e}")

    def _analyze(self, show=True):
        if not self.data:
            self.logger.warning("Aucune donnée à analyser"); return
        stats = ProteomeAnalyzer.analyze(self.data)
        msg = (f"🔬 {stats['proteins_count']} protéines | "
               f"🎛️ {stats['operons_count']} opérons | "
               f"🧫 {stats['plasmids_count']} plasmides | "
               f"🦠 {stats['transposons_count']} transposons | "
               f"🧬 {stats['epigenetic_markers_count']} marqueurs ép.")
        self.logger.info(msg)
        if show:
            self._show_stats()

    def _mutate(self):
        if not self.data: return
        dialog = Toplevel(self.root)
        dialog.title("🧬 Mutation contrôlée")
        dialog.geometry("420x220")
        dialog.configure(bg=BioTheme.BG_DARK)
        dialog.transient(self.root); dialog.grab_set()

        Label(dialog, text="🧬 INTENSITÉ DE MUTATION",
              font=BioTheme.FONT_HEADER, fg=BioTheme.ACCENT_PRIMARY,
              bg=BioTheme.BG_DARK).pack(pady=12)
        scale = Scale(dialog, from_=0.1, to=1.0, resolution=0.1, orient=HORIZONTAL,
                      label="Intensité (0.1 = légère, 1.0 = radicale)",
                      bg=BioTheme.BG_PANEL, fg=BioTheme.TEXT_PRIMARY,
                      troughcolor=BioTheme.BG_EDITOR,
                      activebackground=BioTheme.ACCENT_DANGER, length=340)
        scale.set(0.3); scale.pack(pady=10)

        def apply():
            intensity = scale.get()
            mutated, mutations = ProteomeMutator.mutate(
                self.data, intensity, seed=random.randint(1, 9999))
            self.data = mutated
            self.editor.set_json(self.data)
            self.tree.load_data(self.data)
            self.logger.mutation(f"Mutation appliquée (intensité: {intensity}) — {len(mutations)} changement(s)")
            for m in mutations[:5]: self.logger.mutation(f"  • {m}")
            if len(mutations) > 5: self.logger.mutation(f"  ... +{len(mutations)-5}")
            dialog.destroy()

        Button(dialog, text="🧬 APPLIQUER MUTATION", command=apply,
               bg=BioTheme.ACCENT_DANGER, fg=BioTheme.BG_DARK,
               font=("Consolas", 10, "bold"), cursor="hand2",
               relief=FLAT, padx=14, pady=6).pack(pady=10)

    def _repair(self):
        if not self.data: return
        self.data = ProteomeValidator.auto_repair(self.data)
        self.editor.set_json(self.data)
        self.tree.load_data(self.data)
        self.logger.success("Réparation automatique effectuée")

    def _show_stats(self):
        if not self.data: return
        stats = ProteomeAnalyzer.analyze(self.data)
        win = Toplevel(self.root)
        win.title("📊 Métriques du Protéome")
        win.geometry("560x680")
        win.configure(bg=BioTheme.BG_DARK)
        text = Text(win, bg=BioTheme.BG_EDITOR, fg=BioTheme.TEXT_PRIMARY,
                    font=BioTheme.FONT_CODE, wrap=WORD, padx=10, pady=10)
        text.pack(fill=BOTH, expand=True)

        directives = stats.get("directive_counts", {})
        dir_str = "\n".join(f"   • {k}: {v}" for k, v in
                            sorted(directives.items(), key=lambda x: x[1], reverse=True)[:10])
        stats_str = f"""
╔══════════════════════════════════════════════════════════════╗
║                  📊 MÉTRIQUES DU PROTÉOME v2.0               ║
╚══════════════════════════════════════════════════════════════╝

🔬 PROTÉINES
   • Total : {stats['proteins_count']}
   • Héritages : {stats['inheritance_count']}
   • Profondeur max override : {stats['inheritance_depth']}
   • Lignes totales template : {stats['total_proteins_size']}
   • Sous-protéines : {stats['sub_proteins_count']}

🎛️ OPÉRONS : {stats['operons_count']}
🧫 PLASMIDES : {stats['plasmids_count']}
🦠 TRANSPOSONS : {stats['transposons_count']}

🧬 ÉPIGÉNÉTIQUE
   • Marqueurs uniques : {stats['epigenetic_markers_count']}
   • Occurrences totales : {stats['epigenetic_markers_total']}

⚡ MUTATION
   • Taux global (config) : {self.data.get('global',{}).get('mutation_rate','?')}
   • Taux moyen templates : {stats['avg_mutation_rate']:.4f}

📆 PHASES CELLULAIRES
"""
        for ph, cnt in stats["phases"].items():
            stats_str += f"   • {ph}: {cnt}\n"
        stats_str += "\n📝 DIRECTIVES TEMPLATE (top 10)\n" + dir_str + "\n"

        text.insert("1.0", stats_str)
        text.config(state=DISABLED)

    # ──────────────────────────────────────────────────────────────────────
    # VISUALISATION v2 — délégation à BioVisualizer
    # ──────────────────────────────────────────────────────────────────────
    def _guard(self):
        if not self.data:
            self.logger.warning("Aucune donnée chargée"); return False
        return True

    def _show_dashboard(self):
        if not self._guard(): return
        self.logger.viz("Ouverture Dashboard complet…")
        try:
            BioVisualizer.show_dashboard(self.data)
        except Exception as e:
            self.logger.error(f"Dashboard: {e}")

    def _show_graph(self):
        if not self._guard(): return
        self.logger.viz("Construction graphe de dépendances…")
        try:
            BioVisualizer.show_dependency_graph(self.data)
        except Exception as e:
            self.logger.error(f"Graphe: {e}")

    def _show_heatmap(self):
        if not self._guard(): return
        self.logger.viz("Calcul heat map expression × weight…")
        try:
            BioVisualizer.show_heatmap(self.data)
        except Exception as e:
            self.logger.error(f"Heatmap: {e}")

    def _show_radar(self):
        if not self._guard(): return
        self.logger.viz("Tracé radar métriques…")
        try:
            BioVisualizer.show_radar_standalone(self.data)
        except Exception as e:
            self.logger.error(f"Radar: {e}")

    def _show_epigenetics(self):
        if not self._guard(): return
        self.logger.viz("Analyse épigénétique enrichie…")
        try:
            BioVisualizer.show_epigenetics(self.data)
        except Exception as e:
            self.logger.error(f"Épigénétique: {e}")

    def _show_evolution(self):
        if not self._guard(): return
        self.logger.viz("Lancement simulateur d'évolution cellulaire…")
        try:
            BioVisualizer.show_evolution_simulator(self.data, self.root)
        except Exception as e:
            self.logger.error(f"Simulateur: {e}")

    def _show_diff(self):
        """Charger une seconde config et comparer"""
        if not self._guard(): return
        path = filedialog.askopenfilename(
            title="Charger la 2ème configuration à comparer",
            filetypes=[("JSON","*.json"),("Tous","*.*")])
        if not path: return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data_b = json.load(f)
            name_a = Path(self.current_file).name if self.current_file else "Config A"
            name_b = Path(path).name
            self.logger.viz(f"Comparaison: {name_a} ↔ {name_b}")
            BioVisualizer.show_diff(self.data, data_b, name_a, name_b, self.root)
        except Exception as e:
            self.logger.error(f"Diff: {e}")

    def _export_html(self):
        if not self._guard(): return
        path = filedialog.asksaveasfilename(
            title="Exporter rapport HTML",
            defaultextension=".html",
            filetypes=[("HTML","*.html")])
        if not path: return
        try:
            self.logger.viz("Génération rapport HTML avec figures embarquées…")
            BioVisualizer.export_html_report(self.data, path)
            self.logger.success(f"Rapport exporté: {Path(path).name}")
            webbrowser.open(path)
        except Exception as e:
            self.logger.error(f"Export HTML: {e}")

    def _show_docs(self):
        webbrowser.open("https://github.com/bio-compiler/proteome-editor")

    def _show_about(self):
        messagebox.showinfo("À propos", """🧬 PROTEOMEDITOR v2.0 — Bio-Hacking Interface

Gap Upgrade — Visualisation scientifique :
• Dashboard matplotlib (6 graphes)
• Graphe de dépendances NetworkX
• Heat Map expression × weight
• Radar chart métriques globales
• Analyse épigénétique enrichie
• Simulateur d'évolution cellulaire
• Comparateur de configs (diff visuel + stats)
• Recherche/filtre dans l'éditeur et l'arbre
• Export rapport HTML standalone avec figures

Bio-Hacking Level: ⚡⚡⚡⚡⚡
""")

    def _on_tree_select(self, item_text):
        pass

# =============================================================================
# MAIN
# =============================================================================
def main():
    root = Tk()
    app  = ProteomEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
