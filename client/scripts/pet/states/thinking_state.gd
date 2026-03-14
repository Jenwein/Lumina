class_name ThinkingState
extends PetState

## Thinking state: Thinking animation (bubble).

func enter() -> void:
	pet.sprite.play("think")
