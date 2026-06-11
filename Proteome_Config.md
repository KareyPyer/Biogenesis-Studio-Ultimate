# 🧬 Structure et rôles des attributs dans `proteome_config_949.json`

Ce fichier JSON est le **métamodèle** d’un système cellulaire artificiel.  
Il décrit un protéome complet capable d’évolution, de mémoire épigénétique, de stress, d’apoptose, et d’auto-référence (boucles étranges).  
Il sert d’entrée au `ProtEngine` (dans `prot_generator_multilang.py`).

---

## 1. 📦 Racine du document

| Attribut | Type | Rôle |
|----------|------|------|
| `schema_version` | `string` | Version du format – permet l’évolution du schéma |
| `project` | `string` | Nom du projet (ici `StrangeLoopCellularProteome_UltraExtended`) |
| `description` | `string` | Résumé textuel du contenu fonctionnel |
| `global` | `object` | Paramètres globaux à tout le système (voir ci-dessous) |
| `operons` | `array` | Liste des opérons (régulation transcriptionnelle) |
| `plasmids` | `array` | Plasmides (éléments génétiques circulaires ou linéaires) |
| `global_transposons` | `array` | Transposons globaux (éléments mobiles) |
| `proteins` | `array` | **Cœur du système** – définition de chaque protéine |

---

## 2. 🌍 `global` – Paramètres système

Ces valeurs sont accessibles dans toutes les protéines via `{{global:...}}`.

| Attribut | Rôle |
|----------|------|
| `language` | Langage cible (`csharp` ici) |
| `indent_size`, `comment_prefix` | Formatage du code généré |
| `state_var` | Nom de la variable d’état cellulaire (`_cellularState`) |
| `entropy_var` | Nom du générateur aléatoire (`_entropy`) |
| `max_recursion_depth` | Profondeur maximale d’héritage / inclusion |
| `distillation_blend_prob` | Probabilité de mélange cognitif (analyse récursive) |
| `oscillation_period` | Période par défaut pour `{{oscillate:}}` |
| `quine_depth` | Profondeur d’auto-impression |
| `plasmid_dir`, `operon_prefix` | Chemins et préfixes nommés |
| `epigenetic_memory_slots` | Nombre de marques épigénétiques stockables |
| `mitosis_threshold`, `apoptosis_threshold` | Seuils de cycle cellulaire |
| `base_fitness`, `mutation_rate` | Évolution génétique |
| `cell_generation` | Compteur de génération (démarre à 0) |

---

## 3. 🎛️ `operons` – Régulation transcriptionnelle

Chaque opéron contrôle l’expression d’un ou plusieurs gènes (`genes`).

| Attribut | Rôle |
|----------|------|
| `id` | Identifiant (ex: `OP_STRESS`) |
| `promoter_condition` | Condition d’activation (ex: `state_var > 8`) |
| `description` | Rôle biologique simulé |
| `genes` | Liste des protéines activées |
| `repressor` | Opéron qui inhibe celui-ci (inter-régulation) |

Ces opérons sont évalués dynamiquement pendant l’exécution du code généré.

---

## 4. 🧫 `plasmids` – Éléments génétiques circulaires

Ils injectent des blocs de code dans les protéines via `{{plasmid:ID}}`.

| Attribut | Rôle |
|----------|------|
| `id` | Identifiant (ex: `PLM_LOGGER`) |
| `description` | Rôle fonctionnel |
| `circular` | `true` = circulaire (représentation visuelle) |
| `copy_number` | Nombre de copies simulées |
| `sequence` | Lignes de code à injecter |

Exemples :
- `PLM_LOGGER` : log horodaté structuré
- `PLM_WATCHDOG` : anti-deadlock (reset épigénétique)
- `PLM_TELOMERE` : compteur de sénescence
- `PLM_CHECKPOINT` : validation avant mitose
- `PLM_QUORUM` : détection de densité cellulaire

---

## 5. 🧬 `global_transposons` – Éléments mobiles

Injectés via `{{transposon:ID}}`. Ils **sautent** dans le code généré avec une certaine probabilité `jump_prob`.

| Attribut | Rôle |
|----------|------|
| `id` | Identifiant |
| `description` | Effet biologique simulé |
| `jump_prob` | Probabilité de saut (ex: `0.12`) |
| `effect` | Code exécuté lors du saut |

Exemples :
- `TP_AMPLIFY` : amplifie `_cellularState`
- `TP_SILENCE` : silenciation transitoire
- `TP_RETROTRANSPOSON` : insère une copie de lui-même
- `TP_INVERSION` : inverse la variation d’état

---

## 6. 🧪 `proteins` – Définition des protéines (cœur)

Chaque protéine est un **moule à code** qui peut hériter d’une autre.

### 6.1 Métadonnées principales

| Attribut | Rôle |
|----------|------|
| `id` | Identifiant unique |
| `filename` | Nom du fichier généré (ex: `histone_methylase.prot`) |
| `extends` | Héritage (réutilisation de template) |
| `description` | Rôle biologique simulé |
| `template` | **Liste de lignes** avec directives `{{...}}` |

### 6.2 `override` – Surcharge partielle

Utilisé uniquement si `extends` est défini.  
Permet de surcharger des champs imbriqués (syntaxe pointée).

Exemple :
```json
"override": {
  "meta.cell_phase": "apoptosis_late"
}
```

### 6.3 `variables` – Variables locales accessibles dans le template

Exemple : `"base_state": 5` → utilisable via `{{base_state}}`.

### 6.4 `meta` – Métadonnées descriptives et comportementales

| Attribut | Rôle |
|----------|------|
| `docstring` | Documentation (peut être auto-imprimée via `{{meta:docstring}}`) |
| `philosophy_high` / `philosophy_mid` | Messages philosophiques conditionnels |
| `weight` | Importance (taille du nœud dans le graphe) |
| `expression_level` | Niveau d’expression simulé |
| `cell_phase` | Phase du cycle cellulaire (affecte la couleur dans le graphe) |

### 6.5 `conway_rules` – Règles de jeu de la vie (automate cellulaire)

Déclenché via `{{ca_state:REGLE}}`.  
Exemple : `B3/S23` modifie `_cellularState` et les organelles selon des règles proches du Game of Life.

### 6.6 `sub_proteins` – Fonctions internes injectables

Accessibles via `{{self_ref:NOM}}`.  
Permet de découper une protéine en sous-unités logiques.

### 6.7 `epigenetic_markers` – Marqueurs épigénétiques portés par la protéine

Utilisés dans la heatmap et dans la mémoire cellulaire.  
Exemples : `"h3k4me3_promoter"`, `"h3k9me3_stress_silenced"`.

---

## 7. 🧩 Directives utilisables dans les `template`

Elles sont interprétées par `ProtRenderer` :

| Directive | Rôle |
|-----------|------|
| `{{meta:...}}` | Affiche une entrée du `meta` |
| `{{expr: ...}}` | Évalue une expression (random, maths) |
| `{{comment}}` | Insère le symbole de commentaire du langage |
| `{{state_var}}` | Insère le nom de la variable d’état |
| `{{entropy}}` | Insère le générateur aléatoire |
| `{{repeat:N}} ... {{endrepeat}}` | Déroule un bloc N fois |
| `{{if:cond}} ... {{elif:...}} ... {{else}} ... {{endif}}` | Conditionnel |
| `{{mutate:P}} ... {{endmutate}}` | Exécute avec probabilité P |
| `{{oscillate:P}} ... {{endoscillate}}` | Exécute si `generation % P == 0` |
| `{{quine:}}` | Imprime le template lui-même |
| `{{plasmid:ID}}` | Insère un plasmide |
| `{{transposon:ID}}` | Insère un transposon (saut aléatoire) |
| `{{operon_check:ID}}` | Vérifie l’état d’un opéron |
| `{{self_ref:NOM}}` | Injecte une sous-protéine |
| `{{ca_state:REGLE}}` | Applique une règle de Conway |
| `{{parent:ID}}` | Hérite du template d’une autre protéine |

---

## 8. 🔁 Héritage entre protéines

| Protéine | Hérite de | Surcharge notable |
|----------|-----------|-------------------|
| `heatshock` | `initialize` | `base_state=2`, `cell_phase=G1_arrest` |
| `dna_fragmentation` | `caspase_cascade` | `cell_phase=apoptosis_late` |
| `period_gene` | `clock_gene` | `cell_phase=G1_late` |
| `chromatin_remodeler` | `histone_methylase` | `weight=1.4` |

Cela permet une **réutilisation massive** des templates et une **spécialisation fine**.

---

## 9. 🧠 Résumé fonctionnel par catégorie

| Catégorie | Éléments | Rôle global |
|-----------|----------|-------------|
| **Cycle cellulaire** | `mitosis_threshold`, `apoptosis_threshold`, `cell_phase` | Simulation du vivant |
| **Régulation** | Opérons, plasmides | Contrôle transcriptionnel |
| **Évolution** | Mutation, fitness, niches, coévolution | Adaptation génétique |
| **Épigénétique** | Marqueurs, mémoire, `TP_SILENCE` | Héritage non génétique |
| **Stress / mort** | `heatshock`, `caspase_cascade`, `DNAFragmentation` | Réponse aux agressions |
| **Auto-référence** | `strange_loop`, `quine`, `self_ref` | Boucles réflexives (Hofstadter) |
| **Méta-programmation** | `{{...}}`, héritage, override | Génération dynamique de code |

---

Ce fichier JSON n’est donc **pas une simple configuration**, mais un **véritable langage de description de systèmes cellulaires artificiels**, avec un moteur de génération multi-langages et une sémantique bio-inspirée complète.
