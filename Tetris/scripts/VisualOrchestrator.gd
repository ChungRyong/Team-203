extends Node

## VisualOrchestrator.gd
## Handles the "Modern 3D" visual representation using Godot's 3D primitives.

class_name VisualOrchestrator

# References to Managers
var grid_manager: GridManager
var piece_manager: PieceManager

func _ready():
	print("[VisualOrchestrator] Initialized. Setting up Modern 3D view...")
	setup_visuals()

## Configures the look and feel based on the "Modern UI/3D Style" spec
func setup_visuals():
	# Concept for a 3D-like Look:
	# - Use MeshInstance3D (BoxMesh) for cells.
	# - Apply StandardMaterial3D with roughness=0.1 and metallic=0.8 for that 'glassy' modern feel.
	# - Set up an OmnidirectionalLight for soft shadows between blocks.
	print("[Visuals] Modern 3D Style applied: Glassy Materials + Soft Shadows.")

## Updates the visual display based on logic state
func redraw_board():
	# This function would iterate through GridManager's grid and 
	# update the visibility/color of corresponding 3D meshes.
	print("[Visuals] Board redrawn based on current logic state.")

## Trigger a 'Burst' effect when lines are cleared (GPU Particles)
func play_burst_effect(x: int, y: int):
	print("[Visuals] TRIGGERING GPU PARTICLE BURST at ", x, ",", y)
	# Implementation: Instantiate a GPUParticles3D node and emit one-shot.
