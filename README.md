# Shield of Achilles: Production Pipeline

**["Sing, Goddess, of the anger of Peleus’ son Achilles..."]**

This repository contains the digital production pipeline for the *Shield of Achilles* project. It orchestrates the collaboration between three production tribes (Humanists, Techs, Designers) using a "LEGOS" (Logic, Entities, Goals, Obstacles, Shifts) framework.

## 🚀 Quick Start

**Presentation Studio (Interactive Deck)**
> The primary deliverable. A "Total Media Machine" that combines narrative slides, YAML logic, and a live 3D LDraw viewer.
```bash
open "dist/presentation.html"
```

**3D Scene Pipeline (Three.js Viewer)**
> The spatial "Stagecraft Volume" viewer for the full shield geometry.
```bash
open "dist/index.html"
```

---

## 🛠️ Components

### 1. Presentation Studio
*   **File**: `dist/presentation.html`
*   **Source**: `build_presentation.py` + `dist/legos/*.legos`
*   **Function**:
    *   **2D Mode**: Displays narrative slides and YAML logic.
    *   **3D Mode**: Interactive "Grecian Urn" Studio viewer for identifying LDraw parts.
    *   **Compare Mode**: Side-by-side view of the conceptual slide vs. the 3D reality.
    *   **Hot-Swap**: Seamlessly toggle modes without reloading the 3D context.

### 2. LEGOS Framework
*   **Location**: `dist/legos/`
*   **Format**: `.legos` (Composite file containing YAML frontmatter + LDraw MPD code)
*   **Purpose**: The "Source of Truth" for each scene. Defines the entities, goals, and geometric representation of the production stage.

### 3. 3D Scene Pipeline
*   **File**: `dist/index.html`
*   **Source**: `build.py`
*   **Function**: A specialized Three.js viewer for the "Stagecraft Volume". Features orbit controls, camera snapping, and annotation tools.

---

## 🏗️ Build Instructions

**Rebuild the Presentation Studio**
(Run this after editing `.legos` files)
```bash
python3 build_presentation.py
```

**Rebuild the 3D Scene Index**
(Run this if modifying the core Three.js logic or adding raw assets)
```bash
python3 build.py
```

---

## 🏛️ The Tribes

| Tribe | Color | Role | Output |
|-------|-------|------|--------|
| **Humanists** | Gold | Ontology Engineers | Schema & Logic |
| **Techs** | Teal | Pipeline Builders | Material Substrate (LoRA) |
| **Designers** | Bronze | World Builders | Spatial Interface |

*"The Shield is not just an object, but a process."*
