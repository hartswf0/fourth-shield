#!/usr/bin/env python3
"""
Shield of Achilles — Page→Scene Compiler

USAGE:
  python3 build.py

This script:
1. Copies all .png files from current dir to ./dist/pages/
2. Generates scene.json for each page in ./dist/scenes/000X/
3. Creates manifest.json listing all scenes

Requires: Python 3.6+, no external dependencies
"""

import os
import json
import shutil
from pathlib import Path

# Configuration
SOURCE_DIR = Path(".")
DIST_DIR = Path("./dist")
PAGES_DIR = DIST_DIR / "pages"
SCENES_DIR = DIST_DIR / "scenes"

# Scene defaults
SCENE_WIDTH = 1920
SCENE_HEIGHT = 1080
BASE_DEPTH = 0
LAYER_SPACING = 80

def ensure_dirs():
    """Create output directories if they don't exist."""
    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    SCENES_DIR.mkdir(parents=True, exist_ok=True)

def get_page_images():
    """Find all PNG images in source directory (excluding dist)."""
    images = []
    for f in sorted(SOURCE_DIR.glob("*.png")):
        if "dist" not in str(f):
            images.append(f)
    return images

def copy_pages(images):
    """Copy page images to dist/pages with zero-padded names."""
    copied = []
    for i, img in enumerate(images, 1):
        dest_name = f"{i:04d}.png"
        dest_path = PAGES_DIR / dest_name
        shutil.copy(img, dest_path)
        copied.append({
            "index": i,
            "original": img.name,
            "dest": dest_name
        })
        print(f"  Copied: {img.name} → {dest_name}")
    return copied

def generate_cutouts(page_index, num_cutouts=8):
    """Generate heuristic cutout regions for layered depth effect."""
    cutouts = []
    
    # Title bar region (top)
    cutouts.append({
        "id": f"title-bar",
        "x": 0.05, "y": 0.02, "w": 0.9, "h": 0.12,
        "depth": 200,
        "label": "Title Region"
    })
    
    # Main content regions - arranged in grid
    regions = [
        {"x": 0.02, "y": 0.18, "w": 0.28, "h": 0.35, "label": "Left Panel"},
        {"x": 0.32, "y": 0.18, "w": 0.36, "h": 0.35, "label": "Center Panel"},
        {"x": 0.70, "y": 0.18, "w": 0.28, "h": 0.35, "label": "Right Panel"},
        {"x": 0.02, "y": 0.56, "w": 0.45, "h": 0.22, "label": "Bottom Left"},
        {"x": 0.50, "y": 0.56, "w": 0.48, "h": 0.22, "label": "Bottom Right"},
        {"x": 0.35, "y": 0.80, "w": 0.30, "h": 0.15, "label": "Footer"},
    ]
    
    for i, r in enumerate(regions):
        cutouts.append({
            "id": f"region-{i+1}",
            "x": r["x"], "y": r["y"], "w": r["w"], "h": r["h"],
            "depth": 60 + (i * 30),
            "label": r["label"]
        })
    
    # Add some "floating" accent elements
    accents = [
        {"x": 0.15, "y": 0.30, "w": 0.08, "h": 0.08, "depth": 180},
        {"x": 0.48, "y": 0.25, "w": 0.06, "h": 0.10, "depth": 160},
        {"x": 0.80, "y": 0.35, "w": 0.07, "h": 0.07, "depth": 170},
    ]
    
    for i, a in enumerate(accents):
        cutouts.append({
            "id": f"accent-{i+1}",
            "x": a["x"], "y": a["y"], "w": a["w"], "h": a["h"],
            "depth": a["depth"],
            "label": f"Accent {i+1}"
        })
    
    return cutouts

def generate_scene_json(page_info):
    """Generate a complete scene.json for a page."""
    idx = page_info["index"]
    page_file = page_info["dest"]
    
    cutouts = generate_cutouts(idx)
    
    # Build entities list
    entities = []
    
    # Background plane with full page texture
    entities.append({
        "id": "background",
        "type": "plane",
        "texture": "page",
        "size": [SCENE_WIDTH, SCENE_HEIGHT],
        "position": [0, 0, 0],
        "rotation": [0, 0, 0],
        "material": {
            "transparent": False,
            "opacity": 1.0,
            "emissive": 0.02
        }
    })
    
    # Cutout planes at varying depths
    for cutout in cutouts:
        w = int(cutout["w"] * SCENE_WIDTH)
        h = int(cutout["h"] * SCENE_HEIGHT)
        x = int((cutout["x"] + cutout["w"]/2 - 0.5) * SCENE_WIDTH)
        y = int((0.5 - cutout["y"] - cutout["h"]/2) * SCENE_HEIGHT)
        
        entities.append({
            "id": cutout["id"],
            "type": "cutoutPlane",
            "fromImage": "page",
            "cutout": {
                "x": cutout["x"],
                "y": cutout["y"],
                "w": cutout["w"],
                "h": cutout["h"]
            },
            "position": [x, y, cutout["depth"]],
            "size": [w, h],
            "material": {
                "transparent": True,
                "alphaMode": "blend",
                "opacity": 0.95,
                "emissive": 0.08
            },
            "animation": {
                "type": "float",
                "amplitude": 3,
                "speed": 0.5 + (hash(cutout["id"]) % 10) / 20
            }
        })
    
    # Add some primitive shapes for diagram feel
    primitives = [
        {
            "id": "connector-line-1",
            "type": "primitive",
            "shape": "cylinder",
            "position": [0, 0, 100],
            "rotation": [0, 0, 90],
            "scale": [2, 400, 2],
            "material": {"color": "#c9a227", "metalness": 0.6, "roughness": 0.3, "opacity": 0.4}
        },
        {
            "id": "node-sphere-1",
            "type": "primitive",
            "shape": "sphere",
            "position": [-300, 100, 120],
            "rotation": [0, 0, 0],
            "scale": [25, 25, 25],
            "material": {"color": "#cd7f32", "metalness": 0.8, "roughness": 0.2}
        },
        {
            "id": "node-sphere-2",
            "type": "primitive",
            "shape": "sphere",
            "position": [300, 100, 120],
            "rotation": [0, 0, 0],
            "scale": [25, 25, 25],
            "material": {"color": "#cd7f32", "metalness": 0.8, "roughness": 0.2}
        }
    ]
    entities.extend(primitives)
    
    # Build snap points for navigation
    snap_points = [
        {"name": "Front View", "cameraPos": [0, 0, 1200], "target": [0, 0, 0]},
        {"name": "Top Down", "cameraPos": [0, 800, 600], "target": [0, 0, 0]},
        {"name": "Left Angle", "cameraPos": [-600, 200, 1000], "target": [0, 0, 0]},
        {"name": "Right Angle", "cameraPos": [600, 200, 1000], "target": [0, 0, 0]},
        {"name": "Close Up", "cameraPos": [0, 0, 600], "target": [0, 0, 100]},
    ]
    
    scene = {
        "id": f"{idx:04d}",
        "title": f"Page {idx}: {page_info['original'].replace('.png', '')}",
        "sourceImage": f"../pages/{page_file}",
        "units": {
            "system": "pixels",
            "scale": 1
        },
        "camera": {
            "type": "perspective",
            "position": [0, 0, 1200],
            "target": [0, 0, 0],
            "fov": 50
        },
        "environment": {
            "background": "#0a0a0f",
            "fog": {
                "enabled": True,
                "color": "#0a0a0f",
                "near": 800,
                "far": 2000
            }
        },
        "lights": [
            {"type": "hemisphere", "skyColor": "#c9a227", "groundColor": "#0a0a0f", "intensity": 0.4},
            {"type": "directional", "position": [300, 600, 400], "intensity": 1.0, "color": "#ffffff"},
            {"type": "point", "position": [-400, 300, 500], "intensity": 0.6, "color": "#cd7f32"},
            {"type": "point", "position": [400, -200, 500], "intensity": 0.4, "color": "#2dd4bf"}
        ],
        "assets": {
            "textures": [
                {"id": "page", "src": f"../pages/{page_file}"}
            ],
            "ldraw": []
        },
        "entities": entities,
        "navigation": {
            "snapPoints": snap_points,
            "tour": [
                {"snapPoint": "Front View", "seconds": 3},
                {"snapPoint": "Left Angle", "seconds": 2},
                {"snapPoint": "Close Up", "seconds": 3},
                {"snapPoint": "Right Angle", "seconds": 2},
                {"snapPoint": "Top Down", "seconds": 2}
            ]
        }
    }
    
    return scene

def write_scene(page_info, scene):
    """Write scene.json to appropriate directory."""
    scene_dir = SCENES_DIR / f"{page_info['index']:04d}"
    scene_dir.mkdir(parents=True, exist_ok=True)
    
    scene_file = scene_dir / "scene.json"
    with open(scene_file, 'w') as f:
        json.dump(scene, f, indent=2)
    
    print(f"  Generated: {scene_file}")
    return str(scene_file)

def generate_manifest(pages, scenes):
    """Generate manifest.json with all scenes."""
    manifest = {
        "title": "Shield of Achilles Production Pipeline",
        "version": "1.0.0",
        "generated": "2026-01-14",
        "totalPages": len(pages),
        "scenes": []
    }
    
    for page, scene_path in zip(pages, scenes):
        manifest["scenes"].append({
            "id": f"{page['index']:04d}",
            "title": page["original"].replace(".png", ""),
            "page": f"pages/{page['dest']}",
            "scene": f"scenes/{page['index']:04d}/scene.json"
        })
    
    manifest_file = DIST_DIR / "manifest.json"
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n  Manifest: {manifest_file}")
    return manifest

def main():
    print("\n🛡 Shield of Achilles — Page→Scene Compiler\n")
    print("=" * 50)
    
    # Setup
    print("\n[1/4] Creating directories...")
    ensure_dirs()
    
    # Find and copy pages
    print("\n[2/4] Finding page images...")
    images = get_page_images()
    if not images:
        print("  ERROR: No .png files found in current directory!")
        return
    print(f"  Found {len(images)} pages")
    
    print("\n[3/4] Copying pages to dist/pages/...")
    pages = copy_pages(images)
    
    # Generate scenes
    print("\n[4/4] Generating 3D scenes...")
    scene_paths = []
    for page in pages:
        scene = generate_scene_json(page)
        scene_path = write_scene(page, scene)
        scene_paths.append(scene_path)
    
    # Generate manifest
    print("\n[5/5] Writing manifest...")
    manifest = generate_manifest(pages, scene_paths)
    
    print("\n" + "=" * 50)
    print("✓ Build complete!")
    print(f"  Pages: {len(pages)}")
    print(f"  Scenes: {len(scene_paths)}")
    print("\nTo view:")
    print("  python3 -m http.server 8000")
    print("  open http://localhost:8000/dist/index.html")
    print()

if __name__ == "__main__":
    main()
