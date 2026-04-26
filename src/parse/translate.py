from pynput import keyboard


def hotkey(key: keyboard.Key, activeMods: set):
    modMap = {
        keyboard.Key.ctrl_l: "<ctrl>",
        keyboard.Key.ctrl_r: "<ctrl>",
        keyboard.Key.alt_l: "<alt>",
        keyboard.Key.alt_r: "<alt>",
        keyboard.Key.shift_l: "<shift>",
        keyboard.Key.shift_r: "<shift>",
    }

    # Check if the key is a modifier key and update activeMods accordingly
    if key in modMap:
        activeMods.add(modMap[key])
        return None

    # Determine the base key representation
    if isinstance(key, keyboard.KeyCode) and key.char:          base = key.char.lower()
    elif hasattr(key, "name") and key.name:                     base = f"<{key.name}>"
    else:                                                       return None

    # Order modifiers in a consistent way
    orderedMods = [mod for mod in ("<ctrl>", "<alt>", "<shift>") if mod in activeMods]

    return "+".join(orderedMods + [base]) if orderedMods else base