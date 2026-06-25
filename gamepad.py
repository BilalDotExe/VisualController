import vgamepad as vg

gamepad = vg.VX360Gamepad()

def steeringControl (steering: float):
    gamepad.left_joystick(x_value=int(steering * 32767), y_value=0)
    gamepad.update()

def throttleControl(throttle: float):
    gamepad.right_trigger(value=int(throttle * 255))
    gamepad.update()

def press_a():
    gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    gamepad.update()

def release_a():
    gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    gamepad.update()