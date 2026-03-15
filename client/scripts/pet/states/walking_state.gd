class_name WalkingState
extends PetState

## Walking state: Moving from current position to a target.

signal arrived_at_target

var target_position: Vector2
var move_speed: float = 200.0

func enter() -> void:
	pet.sprite.play("walk")

func physics_update(delta: float) -> void:
	if pet.global_position.distance_to(target_position) < 5.0:
		arrived_at_target.emit()
		pet.arrived_at_target.emit()
		state_machine.transition_to("idle")
		return
		
	# Flip sprite based on direction
	pet.sprite.flip_h = (target_position.x < pet.global_position.x)
	
	# Move towards target
	pet.global_position = pet.global_position.move_toward(target_position, move_speed * delta)
