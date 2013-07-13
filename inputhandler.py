import libtcodpy as libtcod

UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3
ENTER = 4
REST = 5
HEAL = 6
HURT = 7
TELEPORT = 8
SPAWN = 9
INVISIBILITY = 10
ESCAPE = 11
PICKUP = 12
INVENTORY = 13
EXAMINE = 14
SHIFT = 15

#Dungeon creator
RESET = 16
DRUNKWALK = 17
CELLULAR = 18

KEY_SHIFT = libtcod.KEY_SHIFT

# TODO move to settings.
move_controls = {
    UP: (0, -1),  # up
    DOWN: (0, 1),   # down
    LEFT: (-1, 0),  # left
    RIGHT: (1, 0),   # right
}

controls = {
    't': UP,  # up
    libtcod.KEY_UP: UP,  # up

    'h': DOWN,   # down
    libtcod.KEY_DOWN: DOWN,  # up

    'd': LEFT,  # left
    libtcod.KEY_LEFT: LEFT,  # left

    'n': RIGHT,   # right
    libtcod.KEY_RIGHT: RIGHT,  # right

    libtcod.KEY_ENTER: ENTER,
    libtcod.KEY_ESCAPE: ESCAPE,
    libtcod.KEY_SHIFT: SHIFT,  # shift

    "r": REST,
    "p": PICKUP,
    "i": INVENTORY,
    "x": EXAMINE,
    libtcod.KEY_0: RESET,
    libtcod.KEY_1: HEAL,
    libtcod.KEY_1: DRUNKWALK,
    libtcod.KEY_2: HURT,
    libtcod.KEY_2: CELLULAR,
    libtcod.KEY_3: TELEPORT,
    libtcod.KEY_4: SPAWN,
    libtcod.KEY_5: INVISIBILITY,
}


def wait_for_keypress():
    key = libtcod.Key()
    mouse = libtcod.Mouse()

    libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS,
                               key, mouse, False)
    key_char = get_key_char(key)
    return key_char


def get_keypress():
    key = libtcod.Key()
    mouse = libtcod.Mouse()

    libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS,
                                key, mouse)
    key_char = get_key_char(key)
    if key_char in controls.keys():
        return controls[key_char]
    return None


def get_key_char(key):
    if key.vk == libtcod.KEY_CHAR:
        return chr(key.c).lower()  # Case insensetive
    else:
        return key.vk


def is_special_key_pressed(special_key):
    if special_key in controls.keys():
        return libtcod.console_is_key_pressed(special_key)
    return False
