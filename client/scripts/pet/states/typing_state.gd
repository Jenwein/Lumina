class_name TypingState
extends PetState

## Typing state: Typing animation.

func enter() -> void:
	pet.sprite.play("type")
