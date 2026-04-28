from unicodedata import normalize, combining
from pynput import keyboard
from re import sub


def hotkey(key: keyboard.Key, activeMods: set):
    modMap = {
        keyboard.Key.ctrl_l: "<ctrl>",
        keyboard.Key.ctrl_r: "<ctrl>",
        keyboard.Key.alt_l: "<alt>",
        keyboard.Key.alt_r: "<alt>",
        keyboard.Key.shift_l: "<shift>",
        keyboard.Key.shift_r: "<shift>",
        # ! keyboard.Key.tab: "<tab>",
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
    orderedMods = [mod for mod in ("<ctrl>", "<alt>", "<shift>") if mod in activeMods]  # ! "<tab>"

    return "+".join(orderedMods + [base]) if orderedMods else base


def heroID(name: str) -> str:
    # 1) lowercase + trim
    s = name.strip().lower()

    # 2) remove accents (Lúcio -> Lucio)
    s = normalize("NFKD", s)
    s = "".join(ch for ch in s if not combining(ch))

    # 3) remove dots (D.Va -> DVa)
    s = s.replace(".", "")

    # 4) spaces/underscores -> hyphen
    s = sub(r"[_\s]+", "-", s)

    # 5) keep only a-z, 0-9, hyphen
    s = sub(r"[^a-z0-9-]", "", s)

    # 6) collapse repeated hyphens
    s = sub(r"-{2,}", "-", s).strip("-")

    # 7) special cases
    match s:
        case "freja":                                                                   # ! This will not just impact scraping, but also the eveywhere else where heroID is used
            s = "freya"                                                                 # ? https://counterpickgg.com uses "freya" instead of "freja" :shrug:

    return s