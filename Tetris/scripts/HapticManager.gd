extends Node

## HapticManager.gd
## Manages DualSense haptics and vibration feedback.

class_name HapticManager

# Vibration strengths
const STRENGTH_LIGHT = 0.2
const STRENGTH_MEDIUM = 0.5
const STRENGTH_STRONG = 1.0

func _ready():
	print("[HapticManager] Initialized. DualSense haptics ready.")

## Trigger a vibration effect based on the intensity of the event
func trigger_vibration(intensity: float, duration: float = 0.2):
	# In a real Godot project with specialized plugins or native C++ wrappers, 
	# we would call the Joypad API for haptics here.
	# Example: Input.start_joybuzz(device_id, low_freq, high_freq, duration)
	
	print("[Haptic] VIBRATION triggered! Intensity: ", intensity, " Duration: ", duration, "s")

## Specialized effect for Line Clear (The 'Hand-feel' factor)
func play_line_clear_effect(lines_count: int):
	var strength = STRENGTH_MEDIUM
	if lines_count == 4: # TETRIS!
		strength = STRENGTH_STRONG
	elif lines_count == 1:
		strength = STRENGTH_LIGHT
		
	trigger_vibration(strength, 0.3)
