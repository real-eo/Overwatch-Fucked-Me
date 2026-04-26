from pynput import keyboard


def hotkey(key: keyboard.Key, activeMods: set):
    modMap = {
        keyboard.Key.ctrl_l: "<ctrl>",
        keyboard.Key.ctrl_r: "<ctrl>",
        keyboard.Key.alt_l: "<alt>",
        keyboard.Key.alt_r: "<alt>",
        keyboard.Key.shift_l: "<shift>",
        keyboard.Key.shift_r: "<shift>",
        keyboard.Key.tab: "<tab>",
    }

    # Check if the key is a modifier key and update activeMods accordingly
    if key in modMap:
        activeMods.add(modMap[key])
        return None

    base = None

    # Determine the base key representation
    if isinstance(key, keyboard.KeyCode):
        vk = getattr(key, "vk", None)

        # Letters A-Z (stable even with Ctrl held)
        if vk is not None and 65 <= vk <= 90:                   base = chr(vk).lower()

        # Digits 0-9
        elif vk is not None and 48 <= vk <= 57:                 base = chr(vk)
        elif key.char:
            ch = key.char
            
            # Ctrl+letter sometimes arrives as ASCII control char
            if ord(ch) < 32 and "<ctrl>" in activeMods:         base = chr(ord(ch) + 96)
            else:                                               base = ch.lower()
                
    elif hasattr(key, "name") and key.name:                     base = f"<{key.name}>"
    else:                                                       return None



    # Order modifiers in a consistent way
    orderedMods = [mod for mod in ("<ctrl>", "<alt>", "<shift>", "<tab>") if mod in activeMods]

    return "+".join(orderedMods + [base]) if orderedMods else base