WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

BLOCK_MAP = [
	'666666666666',
	'444557755444',
	'333333333333',
	'222222222222',
	'111111111111',
	'            ',
	'            ',
	'            ',
	'            ']

COLOR_LEGEND = {
	'1': 'blue',
	'2': 'green',
	'3': 'red',
	'4': 'orange',
	'5': 'purple',
	'6': 'bronce',
	'7': 'grey',
}

GAP_SIZE = 2
BLOCK_HEIGHT = WINDOW_HEIGHT / len(BLOCK_MAP) - GAP_SIZE
BLOCK_WIDTH = WINDOW_WIDTH / len(BLOCK_MAP[0]) - GAP_SIZE
TOP_OFFSET = WINDOW_HEIGHT // 30

UPGRADES = ['speed','laser','heart','size']

# Controller button mapping shared with the rest of the arcade so the same
# physical buttons keep the same meaning across every game.
A_BUTTON = 0
SELECT_BUTTON = 6
START_BUTTON = 7
L1_BUTTON = 4
R1_BUTTON = 5
QUIT_COMBO_BUTTONS = (START_BUTTON, SELECT_BUTTON, L1_BUTTON, R1_BUTTON)

# Left analog stick horizontal axis used for paddle movement, with a deadzone
# wide enough to ignore resting drift on cheap controllers.
LEFT_STICK_X_AXIS = 0
CONTROLLER_DEADZONE = 0.15