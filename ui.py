from src.constants import DEBUG, HEROES, HERO_IDS, ROLE_TANK, ROLE_DPS, ROLE_SUPPORT, HERO_ROLES, MAX_SLOTS_TANK, MAX_SLOTS_DPS, MAX_SLOTS_SUPPORT, ROLES, ROLE_COUNT, TOTAL_SLOTS_ALL, COUNTERS_FILE
from tkinter import StringVar, Tk, Toplevel, Menu, Frame, Label, Button, PhotoImage, Event, NORMAL, DISABLED, W, E, NE
from src.resources.manager import prefer_local_resource, resource_path, ensure_configurable, IS_LOCAL 
from src.resources import createPhotoImages, portraits
from configparser import ConfigParser
from src.parse import translate
from pynput import keyboard
from os import startfile
import recognize
import threading
import jsonData


class ui:
    class Layout:
        # * Constants
        # Padding
        SMALL_PADDING: int = 2
        ROLE_FRAME_SEPERATOR_PADDING: int = 5
        WINDOW_PADDING: int = 10
        
        # Sizes
        CHARACTER_BUTTON_SIZE: int = 75

        # Character grid
        GRID: dict[str, dict[int, int]] = {                                             # Number of buttons in each row
            # Tank
            ROLE_TANK: {                                                               
                0: 3,                                                                       
                1: 3,
                2: 3,
                3: 3,
                4: 3
            },

            # DPS
            ROLE_DPS: {                                                                  
                0: 5,                                                                       
                1: 5,
                2: 5,
                3: 5,
                4: 4
            },

            # Support
            ROLE_SUPPORT: {
                0: 3,                                                                       
                1: 3,
                2: 3,
                3: 3,
                4: 2
            }
        }

        # * Selected hero & counters layout constexprs
        SELECTED_HERO_HEIGHT: int = 83                                           
        COUNTERS_AREA_HEIGHT: int = 125

        MAX_COUNTERS_PER_ROLE: int = 7                                                  # TODO: Update this so we can support more counters, and
                                                                                        #     : implement a solution which allows for infinite 
                                                                                        #     : counters to show while retaining the quick and clean
                                                                                        #     : overview the current implementation has

        # * Switch- & icon layout constexprs 
        INPUT_FRAME_HEIGHT: int = 35
        ROLE_ICON_FRAME_HEIGHT: int = 35
        
        # * Hero selection layout constexprs
        # Role button rows
        TANK_BUTTON_ROWS: int = len(GRID[ROLE_TANK])
        DPS_BUTTON_ROWS: int = len(GRID[ROLE_DPS])
        SUPPORT_BUTTON_ROWS: int = len(GRID[ROLE_SUPPORT])

        # Role button columns
        TANK_BUTTON_COLUMNS: int = max(GRID[ROLE_TANK].values())
        DPS_BUTTON_COLUMNS: int = max(GRID[ROLE_DPS].values())
        SUPPORT_BUTTON_COLUMNS: int = max(GRID[ROLE_SUPPORT].values())

        # Max button rows
        CHARACTER_BUTTON_ROWS: int = max((
            TANK_BUTTON_ROWS,
            DPS_BUTTON_ROWS,
            SUPPORT_BUTTON_ROWS
        ))

        # Frame dimensions
        TANK_FRAME_WIDTH: int = TANK_BUTTON_COLUMNS * CHARACTER_BUTTON_SIZE             # ? Amount of columns * size of one button
        DPS_FRAME_WIDTH: int = DPS_BUTTON_COLUMNS * CHARACTER_BUTTON_SIZE               # ? Amount of columns * size of one button
        SUPPORT_FRAME_WIDTH: int = SUPPORT_BUTTON_COLUMNS * CHARACTER_BUTTON_SIZE       # ? Amount of columns * size of one button

        ROLE_FRAMES_HEIGHT: int = CHARACTER_BUTTON_ROWS * CHARACTER_BUTTON_SIZE         # ? Amount of rows * size of one button

        # * Globals
        WINDOW_WIDTH: int = 850                                                         # TODO: I think this can be calculated
        WINDOW_HEIGHT: int = sum((
            SELECTED_HERO_HEIGHT, 
            COUNTERS_AREA_HEIGHT, 
            INPUT_FRAME_HEIGHT,
            SMALL_PADDING, 
            ROLE_ICON_FRAME_HEIGHT,
            ROLE_FRAMES_HEIGHT
        ))

        VIEWPORT_WIDTH: int = WINDOW_WIDTH - (2 * WINDOW_PADDING)
        VIEWPORT_HEIGHT: int = WINDOW_HEIGHT - (2 * WINDOW_PADDING)

        # * Positions
        # Role frame positions
        TANK_FRAME_X: int = 0 + WINDOW_PADDING                                                      # 0                     + window_padding
        DPS_FRAME_X: int = (TANK_FRAME_X + TANK_FRAME_WIDTH) + ROLE_FRAME_SEPERATOR_PADDING         # 255 +   role_padding  + window_padding
        SUPPORT_FRAME_X: int = (DPS_FRAME_X + DPS_FRAME_WIDTH) + ROLE_FRAME_SEPERATOR_PADDING       # 600 + 2*role_padding  + window_padding
        
        ROLE_FRAMES_Y: int = WINDOW_HEIGHT - ROLE_FRAMES_HEIGHT

        # Switch- & icon positions
        ROLE_ICON_Y: int = ROLE_FRAMES_Y - ROLE_ICON_FRAME_HEIGHT
        INPUT_FRAME_Y: int = ROLE_ICON_Y - SMALL_PADDING - INPUT_FRAME_HEIGHT                       # ? Bottom-based layout (anchored to bottom)
        # // INPUT_FRAME_Y: int = SELECTED_HERO_HEIGHT + COUNTERS_AREA_HEIGHT                       # ? Top-based layout (anchored to top)



    def __init__(self):
        self.root = Tk()

        self.root.geometry(f"{self.Layout.WINDOW_WIDTH}x{self.Layout.WINDOW_HEIGHT}")
        self.root.title("Overwatch Fucked Me")
        self.root.configure(background="#3C3C3C")
        
        self.characterButtonsDictionary = {}

        self.buttonList: dict[str, list] = {}

        self.selectedHeroes: list[Button | None] = [None for _ in range(TOTAL_SLOTS_ALL)] 
        self.slotsRemaining = {ROLE_TANK: MAX_SLOTS_TANK, ROLE_DPS: MAX_SLOTS_DPS, ROLE_SUPPORT: MAX_SLOTS_SUPPORT}
        self.roleFrameDict = {".tankFrame": ROLE_TANK, ".dpsFrame": ROLE_DPS, ".supportFrame": ROLE_SUPPORT}
        
        self.activeCounters = {}

        self.extendedLimits = False
        self.aiActive = False

        self.initializeWindow()

        self.fullbuttonList = []
        for i in self.buttonList.values():
            self.fullbuttonList.extend(i)

        self.characterHighlighted = ""
        self.characterHighlightedRectList = []

        # Load config
        self.configPath, self.configIsLocal = prefer_local_resource("config.ini")

        self.config = ConfigParser()
        self.config.read(self.configPath)

        threading.Thread(target=self.keyListener, daemon=True, name="listening-Thread").start()

        self.root.protocol("WM_DELETE_WINDOW", self.onClose)

        self.root.mainloop()


    # Setup
    def initializeWindow(self):
        # Images
        createPhotoImages()

        # General UI
        self._menubar()
        self._frames()
        self._labels()
        self._buttons()
        
        self.tank()
        self.dps()
        self.support()


    # Program control
    def onClose(self):
        print('[§] Stopping listener!')
        self.hk.stop()
        print("[$] Stopping root!")
        self.root.destroy()


    def popup(self, title: str = "Alert", geometry: str = "300x200") -> Toplevel:
        # Create popup window
        popup = Toplevel(self.root)

        # Configure popup window
        popup.resizable(False, False)                                                   # Prevent resizing to avoid layout issues
        popup.transient(self.root)                                                      # Make always on top
        popup.grab_set()                                                                # Make the popup modal

        # Set passed parameters
        popup.title(title)
        popup.geometry(geometry)

        return popup

    # UI elements
    def _menubar(self):
        menubar = Menu(self.root)                                                       # Toolbar at the top of the window

        # File 
        fileMenu = Menu(menubar, tearoff=False)                                         # Dropdown menu when clicking on "File" in the toolbar

        fileMenu.add_command(label="Exit", command=self.onClose)

        # Edit 
        editMenu = Menu(menubar, tearoff=False)                                         # Dropdown menu when clicking on "Edit" in the toolbar

        editMenu.add_command(label="Edit counters.json", command=self.editCounters)
        editMenu.add_separator()
        editMenu.add_command(label="Reload counters", command=self.reloadCounters)
        
        # Settings
        settingsMenu = Menu(menubar, tearoff=False)                                     # Dropdown menu when clicking on "Settings" in the toolbar
        
        keybindsMenu = Menu(settingsMenu, tearoff=False)                                # Submenu for keybinds in the settings menu
        keybindsMenu.add_command(label="Capture", command=lambda: self.promptNewKeybind("capture")) 
        keybindsMenu.add_command(label="Trigger debug", command=lambda: self.promptNewKeybind("debug"))          # ? This is really just DEBUG button
        keybindsMenu.add_separator()
        keybindsMenu.add_command(label="Reset to default", command=lambda: self.resetKeybinds())
        
        settingsMenu.add_cascade(label="Change keybinds...", menu=keybindsMenu)
        settingsMenu.add_separator()
        settingsMenu.add_command(label="Reset all settings", command=lambda: self.resetSettings())

        # Add dropdowns to toolbar
        menubar.add_cascade(label="File", menu=fileMenu)
        menubar.add_cascade(label="Edit", menu=editMenu)
        menubar.add_cascade(label="Settings", menu=settingsMenu)
        
        self.root.config(menu=menubar)

    def _frames(self):
        self.recommendedCharacterFrameList = []

        # Character portraits
        for i in range(TOTAL_SLOTS_ALL):
            characterFrame = Frame(
                master=self.root, 
                height=self.Layout.SELECTED_HERO_HEIGHT + self.Layout.COUNTERS_AREA_HEIGHT, 
                width=(self.Layout.VIEWPORT_WIDTH/TOTAL_SLOTS_ALL), 
                background="#3C3C3C", 
                name=f"characterFrame{i}"
            )

            characterFrame.place(
                x=((self.Layout.VIEWPORT_WIDTH/TOTAL_SLOTS_ALL)*i + (TOTAL_SLOTS_ALL*i)), 
                y=0
            )
            self.recommendedCharacterFrameList.append(characterFrame)

        # Character buttons
        self.inputFrame = Frame(master=self.root, height=self.Layout.INPUT_FRAME_HEIGHT, width=self.Layout.WINDOW_WIDTH, background="#3C3C3C", name="inputFrame")
        self.roleInfoFrame = Frame(master=self.root, height=self.Layout.ROLE_ICON_FRAME_HEIGHT, width=self.Layout.WINDOW_WIDTH, background="#3C3C3C", name="roleInfoFrame")

        self.tankFrame = Frame(master=self.root, height=self.Layout.ROLE_FRAMES_HEIGHT, width=self.Layout.TANK_FRAME_WIDTH, background="#3C3C3C", name="tankFrame")
        self.dpsFrame = Frame(master=self.root, height=self.Layout.ROLE_FRAMES_HEIGHT, width=self.Layout.DPS_FRAME_WIDTH, background="#3C3C3C", name="dpsFrame")
        self.supportFrame = Frame(master=self.root, height=self.Layout.ROLE_FRAMES_HEIGHT, width=self.Layout.SUPPORT_FRAME_WIDTH, background="#3C3C3C", name="supportFrame")

        self.inputFrame.place(x=0, y=self.Layout.INPUT_FRAME_Y)
        self.roleInfoFrame.place(x=0 + self.Layout.WINDOW_PADDING, y=self.Layout.ROLE_ICON_Y)

        self.tankFrame.place(   x=self.Layout.TANK_FRAME_X,     y=self.Layout.ROLE_FRAMES_Y)
        self.dpsFrame.place(    x=self.Layout.DPS_FRAME_X,      y=self.Layout.ROLE_FRAMES_Y)
        self.supportFrame.place(x=self.Layout.SUPPORT_FRAME_X,  y=self.Layout.ROLE_FRAMES_Y)    

    def _labels(self):
        self.counterImagePlaceholders: list[dict[str, list[Label]]] = []                # 2D list of labels which get replaced with portraits of the counters (3x7)
        self.characterImagePlaceholders: list[Label] = []                               # List of labels which get replaced with portraits of the selected heroes (5)

        for a, b in enumerate(self.recommendedCharacterFrameList):
            characterPlaceholder = Label(
                b, 
                height=(self.Layout.SELECTED_HERO_HEIGHT), 
                width=(self.Layout.VIEWPORT_WIDTH/10), 
                # image=placeholderPortrait, 
                image=portraits.HERO_3x3["blank"],
                bg="#4C4C4C", 
                name=f"placeholder@{a}characterLabel"
            )

            characterPlaceholder.place(x=0, y=0)

            self.characterImagePlaceholders.append(characterPlaceholder)

            # Counter placeholders
            placeholderDict: dict[str, list[Label]] = {}

            for roleIndex, role in enumerate(ROLES):
                for counterIndex in range(self.Layout.MAX_COUNTERS_PER_ROLE):
                    # Object
                    counterPlaceholder = Label(
                        b, 
                        height=((self.Layout.COUNTERS_AREA_HEIGHT / ROLE_COUNT)), 
                        width=(self.Layout.VIEWPORT_WIDTH / TOTAL_SLOTS_ALL / self.Layout.MAX_COUNTERS_PER_ROLE), 
                        # image=placeholderPortrait, 
                        image=portraits.HERO_3x3["blank"],
                        bg="#444444",
                        name=f"placeholder@{a}-{counterIndex}-{roleIndex}Label"
                    )

                    # Location
                    counterPlaceholder.place(
                        x=(((self.Layout.VIEWPORT_WIDTH / TOTAL_SLOTS_ALL / self.Layout.MAX_COUNTERS_PER_ROLE) * counterIndex)), 
                        y=((self.Layout.COUNTERS_AREA_HEIGHT / ROLE_COUNT) * (roleIndex) + self.Layout.SELECTED_HERO_HEIGHT)
                    )

                    # Data
                    counterPlaceholder.counterData = None
                    counterPlaceholder.counterID = None

                    # Functionality
                    counterPlaceholder.bind("<Enter>", self.showCounterTooltip)
                    counterPlaceholder.bind("<Leave>", self.hideCounterTooltip)

                    # Storage
                    placeholderDict.setdefault(
                        role,                                                           # Get the list of placeholders for the current role (tank/dps/support)
                        []                                                              # If it doesn't exist, create a new empty list
                    ).append(counterPlaceholder)

            self.counterImagePlaceholders.append(placeholderDict)
        self.roleIconList = [PhotoImage(file=resource_path("res", "icons", "role", f"{i}Icon.png")).subsample(4, 4) for i in ROLES]

        for x, i in enumerate(ROLES):
            iconLabel = Label(self.roleInfoFrame, image=self.roleIconList[x], bg="#3C3C3C", name=f"{i}IconLabel")
            iconLabel.place(x=([-5, -5+225+5, -5+600+10][x]), y=-7)

    def _buttons(self):
        self.extendedLimitsButton = Button(master=self.inputFrame, text="Extended Limits", name="extendedLimitsButton")
        self.extendedLimitsButton.place(x=5, y=self.Layout.INPUT_FRAME_HEIGHT / 2, anchor=W)
        self.extendedLimitsButton.bind("<Button>", self.mouseButton)

        self.aiActiveButton = Button(master=self.inputFrame, text="AI Recognition", name="aiActiveButton")
        self.aiActiveButton.place(x=self.Layout.WINDOW_WIDTH - 5, y=self.Layout.INPUT_FRAME_HEIGHT / 2, anchor=E)
        self.aiActiveButton.bind("<Button>", self.mouseButton)


    # Select characters
    def tank(self):
        tankButtonList = []
        self.tankPortraitList = [
            portraits.HERO_4x4[heroID]
            for heroID in HERO_IDS[ROLE_TANK]
        ]

        i = 0
        for y in self.Layout.GRID[ROLE_TANK]:
            for x in range(self.Layout.GRID[ROLE_TANK][y]):
                tankButton: Button = Button(
                    self.tankFrame, 
                    image=self.tankPortraitList[i], 
                    name=HERO_IDS[ROLE_TANK][i]
                )

                tankButton.place(
                    x=(
                        (x * self.Layout.CHARACTER_BUTTON_SIZE) 
                        + ((self.Layout.CHARACTER_BUTTON_SIZE/2) * (self.Layout.TANK_BUTTON_COLUMNS - self.Layout.GRID[ROLE_TANK][y]))
                    ), 
                    y=(y * self.Layout.CHARACTER_BUTTON_SIZE)
                )

                tankButton.bind("<Button>", self.mouseButtonCharacters)
                tankButton.bind("<Enter>", self.animationFocus)
                tankButton.bind("<Leave>", self.animationDefocus)

                self.characterButtonsDictionary[HEROES[ROLE_TANK][i]] = tankButton
                tankButtonList.append(tankButton)
                i += 1

        self.buttonList[ROLE_TANK] = tankButtonList

    def dps(self):
        dpsButtonList = []
        self.dpsPortraitList = [
            portraits.HERO_4x4[heroID]
            for heroID in HERO_IDS[ROLE_DPS]
        ]

        i = 0
        for y in self.Layout.GRID[ROLE_DPS]:
            for x in range(self.Layout.GRID[ROLE_DPS][y]):
                dpsButton = Button(
                    self.dpsFrame, 
                    image=self.dpsPortraitList[i], 
                    name=HERO_IDS[ROLE_DPS][i]
                )

                dpsButton.place(
                    x=(
                        (x * self.Layout.CHARACTER_BUTTON_SIZE) 
                        + ((self.Layout.CHARACTER_BUTTON_SIZE/2) * (self.Layout.DPS_BUTTON_COLUMNS - self.Layout.GRID[ROLE_DPS][y]))
                    ), 
                    y=(y * self.Layout.CHARACTER_BUTTON_SIZE)
                )

                dpsButton.bind("<Button>", self.mouseButtonCharacters)
                dpsButton.bind("<Enter>", self.animationFocus)
                dpsButton.bind("<Leave>", self.animationDefocus)

                self.characterButtonsDictionary[HEROES[ROLE_DPS][i]] = dpsButton
                dpsButtonList.append(dpsButton)
                i += 1
        
        self.buttonList[ROLE_DPS] = dpsButtonList

    def support(self):
        supportButtonList = []
        self.supportPortraitList = [
            portraits.HERO_4x4[heroID]
            for heroID in HERO_IDS[ROLE_SUPPORT]
        ]

        i = 0
        for y in self.Layout.GRID[ROLE_SUPPORT]:
            for x in range(self.Layout.GRID[ROLE_SUPPORT][y]):
                supportButton = Button(
                    self.supportFrame, 
                    image=self.supportPortraitList[i], 
                    name=HERO_IDS[ROLE_SUPPORT][i]
                )
                
                supportButton.place(
                    x=(
                        (x * self.Layout.CHARACTER_BUTTON_SIZE) 
                        + ((self.Layout.CHARACTER_BUTTON_SIZE/2) * (self.Layout.SUPPORT_BUTTON_COLUMNS - self.Layout.GRID[ROLE_SUPPORT][y]))
                    ), 
                    y=(y * self.Layout.CHARACTER_BUTTON_SIZE)
                )
                
                supportButton.bind("<Button>", self.mouseButtonCharacters)
                supportButton.bind("<Enter>", self.animationFocus)
                supportButton.bind("<Leave>", self.animationDefocus)

                self.characterButtonsDictionary[HEROES[ROLE_SUPPORT][i]] = supportButton
                supportButtonList.append(supportButton)
                
                i += 1

        self.buttonList[ROLE_SUPPORT] = supportButtonList


    # Event handlers
    def mouseButtonCharacters(self, event: Event):
        heroButtonRole = self.roleFrameDict[str(event.widget.master)]
        selectedCount = sum(1 for h in self.selectedHeroes if h is not None)

        if event.num == 1:
            canSelect = (
                event.widget["state"] == NORMAL
                and event.widget not in self.selectedHeroes
                and (self.slotsRemaining[heroButtonRole] > 0 if not self.extendedLimits else selectedCount < TOTAL_SLOTS_ALL)
            )
            if not canSelect: return "break"

            slot = self.selectedHeroes.index(None)
            self.selectedHeroes[slot] = event.widget
            event.widget.configure(bg="SystemHighlight")

            if not self.extendedLimits:
                self.slotsRemaining[heroButtonRole] -= 1
                if self.slotsRemaining[heroButtonRole] == 0:
                    for btn in self.buttonList[heroButtonRole]:
                        if btn not in self.selectedHeroes:
                            btn["state"] = DISABLED
            else:
                if selectedCount + 1 >= TOTAL_SLOTS_ALL:
                    for btn in self.fullbuttonList:
                        if btn not in self.selectedHeroes:
                            btn["state"] = DISABLED

            self.root.after(0, self.updateTeamComp)
            return "break"

        elif event.num == 2:
            print(str(event.widget.master))

        elif event.num == 3:
            if event.widget not in self.selectedHeroes: return "break"

            self.selectedHeroes[self.selectedHeroes.index(event.widget)] = None         # TODO: Fix: find by identity, not index
            event.widget.configure(bg="SystemButtonFace")

            if not self.extendedLimits:
                self.slotsRemaining[heroButtonRole] += 1
                for btn in self.buttonList[heroButtonRole]:
                    btn["state"] = NORMAL
            else:
                for btn in self.fullbuttonList:
                    btn["state"] = NORMAL

            self.root.after(0, self.updateTeamComp)
            return "break"


    def mouseButton(self, event: Event):
        if event.widget == self.extendedLimitsButton:
            self.extendedLimits = [True, False][self.extendedLimits]
            self.extendedLimitsButton.configure(bg=["SystemButtonFace", "Green"][self.extendedLimits])

            # self.selectedHeroes.clear()
            self.selectedHeroes = [None for _ in range(TOTAL_SLOTS_ALL)]
            # self.selectedRoles = {ROLE_TANK: [], ROLE_DPS: [], ROLE_SUPPORT: []}
            self.slotsRemaining = {ROLE_TANK: MAX_SLOTS_TANK, ROLE_DPS: MAX_SLOTS_DPS, ROLE_SUPPORT: MAX_SLOTS_SUPPORT}

            self.updateTeamComp()

            if not self.aiActive:
                for button in self.fullbuttonList:
                    button.configure(bg="SystemButtonFace")
                    button["state"] = NORMAL
        if event.widget == self.aiActiveButton:
            self.aiActive = [True, False][self.aiActive]
            self.aiActiveButton.configure(bg=["SystemButtonFace", "Green"][self.aiActive])

            # self.selectedHeroes.clear()
            self.selectedHeroes = [None for _ in range(TOTAL_SLOTS_ALL)]
            # self.selectedRoles = {ROLE_TANK: [], ROLE_DPS: [], ROLE_SUPPORT: []}
            self.slotsRemaining = {ROLE_TANK: MAX_SLOTS_TANK, ROLE_DPS: MAX_SLOTS_DPS, ROLE_SUPPORT: MAX_SLOTS_SUPPORT}

            self.updateTeamComp()

            if self.aiActive:
                for button in self.fullbuttonList:
                    button.configure(bg="SystemButtonFace")
                    button["state"] = DISABLED
            else:
                for button in self.fullbuttonList:
                    button["state"] = NORMAL
        return "break"

    def keyListener(self):
        self.ongoingKeybaordRequest = False

        def captureImage():
            if self.aiActive and not self.ongoingKeybaordRequest:
                print('[§] Starting recognition')

                self.ongoingKeybaordRequest = True
                self.selectedHeroes = []

                recognize.capture_image()
                returnedClasses = recognize.recognize()

                for cls in returnedClasses:
                    classID, className, confidenceScore = cls[0].split(" ", 1) + [cls[1]]

                    # ! NOTE:
                    #   TODO: ADD COUNTERS AND LAYOUT SUPPORT FOR "Doctrine"
                    if className not in ("Waiting for player", "Player not selected", "Doctrine"):
                        try:
                            self.selectedHeroes.append(self.characterButtonsDictionary[className])
                            continue                                                    # ? A bit hacky, but we `continue` to avoid appending 
                                                                                        # ? `None` to selectedHeroes in two separate places
                        except KeyError:
                            print(f"[!] ERROR: Coun't find recognized character \"{className}\" in `self.characterButtonsDictionary`!")

                    # ? This is kinda a bad fix, but for every case where we don't add a character
                    # ? classification, we add `None`. This SHOULD always make the for-loop iterate 
                    # ? 5 times regardless, but it's not programmed explicitly, so there can be some bugs here
                    self.selectedHeroes.append(None)

                # // self.updateTeamComp()
                self.root.after(0, lambda: self.updateTeamComp(forceReload=True))       # ? Tkinter widgets should only be updated on the main thread
                self.ongoingKeybaordRequest = False

        def startRecognition():
            threading.Thread(target=captureImage, name="captureThread").start()

        def triggerDebug():
            if not DEBUG:   return

            print("[¤] Keybinds:")
            for key, value in self.config.items("keybinds", raw=True):
                print(f"[¤]     {key}: {value}")

        def savePortraits():
            # | Debug only function
            # Used when collecting images for portrait dataset
            if not DEBUG:   return 

            recognize.capture_image(persistPortraits=True)


        # Set up hotkeys
        self.hk = keyboard.GlobalHotKeys({
                self.config.get("keybinds", "capture"): startRecognition,
                self.config.get("keybinds", "debug"): triggerDebug,
                # | DISABLE THIS AS THIS IS DEBUG ONLY
                # // "<ctrl>+s": savePortraits
        })


        self.hk.start()

    def updateKeybind(self, action: str, keybind: str):
        # * Config file handling
        # Check whether config is bundled or local
        if not self.configIsLocal:
            # Copy config to writable location
            self.configPath = ensure_configurable("config.ini")

            # And update local/bundled status
            self.configIsLocal = IS_LOCAL

            # Reload loaded config
            self.config.read(self.configPath)

        
        # * Update keybind
        self.config.set("keybinds", action, keybind)


        # * Cleanup
        # Save config
        with open(self.configPath, "w", encoding="utf-8") as configFile:
            self.config.write(configFile)

        # Restart listener
        self.keyListener()

    def editCounters(self):
        # Open counters.json in default editor
        startfile(ensure_configurable(COUNTERS_FILE))

        # Prompt a popup to know when the user is done editing 
        popup = self.popup(title="Editing counters.json", geometry="200x110")

        Label(popup, text="After you are done editing, click \nthe button below to refresh \nthe counters in the app.").pack(pady=(8, 6))
        Button(popup, text="Update counters", command=lambda: [popup.destroy(), self.reloadCounters()]).pack(pady=(0, 8))

    def showCounterTooltip(self, event: Event):
        data = event.widget.counterData

        if not data: return

        self.counterTooltip = Toplevel(self.root)
        self.counterTooltip.wm_overrideredirect(True)
        self.counterTooltip.configure(background="#222222")

        text = (
            f"Rating: {data['rating']}/10\n\n"
            f"{data['description']}"
        )

        Label(
            self.counterTooltip,
            text=text,
            justify="left",
            wraplength=280,
            padx=8,
            pady=6,
            fg="white",
            bg="#222222"
        ).pack()

        x = event.widget.winfo_rootx() + event.widget.winfo_width() + 5
        y = event.widget.winfo_rooty()

        self.counterTooltip.geometry(f"+{x}+{y}")


    def hideCounterTooltip(self, event: Event):
        tooltip = getattr(self, "counterTooltip", None)

        if tooltip is not None:
            tooltip.destroy()
            self.counterTooltip = None


    # Processing
    def updateTeamComp(self, forceReload: bool = False):
        # Update portraits and counters for the selected heroes
        for index, heroButton in enumerate(self.selectedHeroes):                        # ? Enumerate so we can use the index for updating the placeholder label
            if heroButton is None:                                                      # No hero selected in this slot
                # Clear the portrait placeholder for this slot
                self.characterImagePlaceholders[index].configure(image=portraits.HERO_3x3["blank"])
                
                # Clear the counter placeholders' data for this slot
                for role in ROLES:
                    for counterPlaceholder in self.counterImagePlaceholders[index][role]:
                        counterPlaceholder.counterID = None
                        counterPlaceholder.counterData = None
                        counterPlaceholder.configure(image=portraits.HERO_6x6["blank"])

                # ! NOTE:
                # ? The reason as to why i decided to go with this implementation flow, instead
                # ? of just always clearing the counters on update, is so that we keep the GUI
                # ? feeling responsive, and not flickering when adding/removing manually. Yet 
                # ? we still want the GUI to update correctly, so when scanning for heroes, or
                # ? when we update a hero's counters, we need to clear the previous counters, 
                # ? as they never get to be set to None
                continue
                        
            else:  
                # ! NOTE:
                # ? The reason as to why i decided to go with this implementation flow, instead
                # ? of just always clearing the counters on update, is so that we keep the GUI
                # ? feeling responsive, and not flickering when adding/removing manually. Yet 
                # ? we still want the GUI to update correctly, so when scanning for heroes, or
                # ? when we update a hero's counters, we need to clear the previous counters, 
                # ? as they never get to be set to None
                if forceReload:
                    # Clear the counter placeholders' data for this slot
                    for role in ROLES:
                        for counterPlaceholder in self.counterImagePlaceholders[index][role]:
                            counterPlaceholder.counterID = None
                            counterPlaceholder.counterData = None
                            counterPlaceholder.configure(image=portraits.HERO_6x6["blank"])

                # * Character
                # Create the portrait for the selected hero
                characterPortrait = portraits.HERO_3x3[heroButton.winfo_name()]
            
                # and set it on the corresponding placeholder label
                self.characterImagePlaceholders[index].configure(image=characterPortrait)


                # * Counters
                heroCounters = jsonData.counters[heroButton.winfo_name()]
                usedSlots = {ROLE_TANK: 0, ROLE_DPS: 0, ROLE_SUPPORT: 0}                # To keep track of how many counter slots we have used for each role, so we know where to place the next counter portrait

                for counterID, data in heroCounters.items():                            # TODO: Use the `data` for something
                    counterRole = HERO_ROLES[counterID]

                    # TODO: Fix this issue (somehow)
                    # Safety check to prevent index out of range errors 
                    if usedSlots[counterRole] >= self.Layout.MAX_COUNTERS_PER_ROLE: 
                        print(f"[!] Warning: Maximum counters reached for role " +  
                              f"{counterRole}. Counter \"{counterID}\" will be skipped.")

                        continue                                                        # Skip this counter if we've already used all available slots for its role

                    # Update the counters' data and portrait
                    portrait = portraits.HERO_6x6[counterID]
                    # self.counterImagePlaceholders[index][counterRole][usedSlots[counterRole]].configure(image=portrait)

                    counterPlaceholder = (
                        self.counterImagePlaceholders[index][counterRole][usedSlots[counterRole]]
                    )
                                        
                    counterPlaceholder.counterID = counterID
                    counterPlaceholder.counterData = data
                    counterPlaceholder.configure(image=portrait)

                    usedSlots[counterRole] += 1
                    
        
    def animationFocus(self, event: Event):
        if event.widget["state"] == NORMAL:
            self.characterHighlightedRectList.append([event.widget, event.widget.winfo_x(), event.widget.winfo_y()])    
            # print("<Enter>", event.widget.winfo_x() + 3, event.widget.winfo_y() + 3, event.widget.winfo_height(), event.widget.winfo_width())
            event.widget.configure(height=70, width=70)
            event.widget.place(x=event.widget.winfo_x() - 3, y=event.widget.winfo_y() - 3)

    def animationDefocus(self, event: Event):
        if event.widget["state"] == NORMAL:
            # print("<Leave>", event.widget.winfo_x() + 3, event.widget.winfo_y() + 3, event.widget.winfo_height(), event.widget.winfo_width())
            try:
                widget = self.characterHighlightedRectList.pop(0)
                widget[0].configure(height=64, width=64)
                widget[0].place(x=widget[1], y=widget[2])
            except IndexError:
                pass

    def promptNewKeybind(self, action: str):
        # Temporarily stop the listener to prevent triggering of keybinds during keybind editing
        self.hk.stop()

        # Create popup window
        popup = self.popup(title=f"Action: {action}", geometry="200x120")

        # Variables
        status = StringVar(value="Press your new keybind...")
        recorded = {"value": None}
        recorder = {"listener": None}
        
        # * UI elements
        # Labels
        Label(popup, textvariable=status).pack(pady=(8, 4))

        # Buttons
        confirmButton = Button(popup, text="Confirm", state=DISABLED)
        resetButton = Button(popup, text="Reset")
        cancelButton = Button(popup, text="Cancel")

        confirmButton.pack(side="right", padx=(0, 8), pady=(0, 8))
        resetButton.pack(side="right", padx=6, pady=(0, 8))
        cancelButton.pack(side="right", padx=6, pady=(0, 8))

        # * Process
        # Variables
        activeMods = set()

        # Recording functions
        def stopRecorder():
            listener = recorder["listener"]
            if listener is not None:
                listener.stop()
                recorder["listener"] = None

        def startRecording():
            # Just in case, clean up any existing data and listener from a previous run to ensure a clean state
            stopRecorder()
            activeMods.clear()
            recorded["value"] = None
            status.set("Press your new keybind...")
            confirmButton.configure(state=DISABLED)

            def onPress(key):
                # Translate modifiers to a consistent format 
                hotkey = translate.hotkey(key, activeMods)
                if hotkey is None: return                                               # Don't record unsupported keys

                # Update active modifiers set
                recorded["value"] = hotkey
                self.root.after(0, lambda: status.set(f"Recorded: {hotkey}"))           # Update status label with the recorded hotkey
                self.root.after(0, lambda: confirmButton.configure(state=NORMAL))       # Enable confirm button once a valid hotkey is recorded

                return False

            def onRelease(key):
                # Update active modifiers set on key release to ensure accurate recording of modifier combinations
                if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):       activeMods.discard("<ctrl>")
                elif key in (keyboard.Key.alt_l, keyboard.Key.alt_r):       activeMods.discard("<alt>")
                elif key in (keyboard.Key.shift_l, keyboard.Key.shift_r):   activeMods.discard("<shift>")
                # ! elif key in (keyboard.Key.tab):                             activeMods.discard("<tab>")

            recorder["listener"] = keyboard.Listener(on_press=onPress, on_release=onRelease)
            recorder["listener"].start()

        # Button commands
        def cancel():
            stopRecorder()
            popup.destroy()
            self.keyListener()                                                          # Start listener again 

        def confirm():
            # Prevent confirming if no keybind was recorded
            if not recorded["value"]:   return

            # Stop recorder and update keybind
            stopRecorder()
            popup.destroy()
            self.updateKeybind(action, recorded["value"])

        def reset():
            startRecording()

        # Bindings
        popup.protocol("WM_DELETE_WINDOW", cancel)                                      # On close, trigger cancel() to ensure proper listener handling
        cancelButton.configure(command=cancel)                                          # Trigger cancel() when clicking the cancel button
        confirmButton.configure(command=confirm)                                        # Trigger confirm() when clicking the confirm button
        resetButton.configure(command=reset)                                            # Trigger reset() when clicking the reset button

        # Start recording immediately
        startRecording()

    def resetKeybinds(self):
        # No-op if config is loaded from bundled resource
        if not self.configIsLocal:  return

        # Stop listener to prevent triggering of keybinds during reset process
        self.hk.stop()

        # Get default keybinds from bundled config
        tempConfigPath = resource_path("config.ini")
        tempConfig = ConfigParser()
        tempConfig.read(tempConfigPath)

        # Update keybinds
        for action, keybind in tempConfig.items("keybinds", raw=True):
            self.config.set("keybinds", action, keybind)
        
        # Save config
        with open(self.configPath, "w", encoding="utf-8") as configFile: 
            self.config.write(configFile)

        # Restart listener
        self.keyListener()

    def resetSettings(self):
        # No-op if config is loaded from bundled resource
        if not self.configIsLocal:  return

        # Stop listener to prevent triggering of keybinds during reset process
        self.hk.stop()

        # Get default settings from bundled config
        tempConfigPath = resource_path("config.ini")
        tempConfig = ConfigParser()
        tempConfig.read(tempConfigPath)

        # Update settings
        for section in tempConfig.sections():
            for setting, value in tempConfig.items(section, raw=True):
                self.config.set(section, setting, value)
        
        # Save config
        with open(self.configPath, "w", encoding="utf-8") as configFile: 
            self.config.write(configFile)

        # Restart listener
        self.keyListener()
        
    def reloadCounters(self):
        # Reload jsonData to update counters with the new data
        jsonData.load()

        # Update the team comp display to reflect any changes in counters
        self.updateTeamComp(forceReload=True)


if __name__ == "__main__":
    print("[!] This file is not ment to be run!\n\n")
    input("Press \"Enter\" to exit . . .")



