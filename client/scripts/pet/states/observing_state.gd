class_name ObservingState
extends PetState

## Observing state: The pet looks closely at something (scanning animation).

func enter() -> void:
	# Use "think" as a placeholder if "observe" doesn't exist
	if pet.sprite.sprite_frames.has_animation("observe"):
		pet.sprite.play("observe")
	else:
		pet.sprite.play("think")

func physics_update(_delta: float) -> void:
	pass
