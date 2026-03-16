class_name IdleState
extends PetState

## Idle state: Basic breathing or slight motion animation.

func enter() -> void:
	pet.sprite.play("idle")

func physics_update(_delta: float) -> void:
	# Idle state does nothing but stay put, or maybe random small jitter
	pass
