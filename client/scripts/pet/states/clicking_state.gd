class_name ClickingState
extends PetState

## Clicking state: The pet performs a "click" action (e.g., jumps or stomps).
## Once the "hit" frame is reached, it emits click_ready.

signal click_impact

func enter() -> void:
	# Use "walk" or "idle" if "click" animation doesn't exist
	if pet.sprite.sprite_frames.has_animation("click"):
		pet.sprite.play("click")
	else:
		# Fallback simulation
		_simulate_click()

func _simulate_click() -> void:
	# Basic animation simulation for placeholder sprites
	var tween = get_tree().create_tween()
	tween.tween_property(pet.sprite, "scale", Vector2(1.2, 0.8), 0.1)
	tween.tween_property(pet.sprite, "scale", Vector2(1.0, 1.0), 0.1)
	tween.finished.connect(func(): 
		click_impact.emit()
		state_machine.transition_to("idle")
	)

func exit() -> void:
	pet.sprite.scale = Vector2(1.0, 1.0)
