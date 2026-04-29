from resourceManager import prefer_local_resource, resource_path, ensure_configurable, IS_BUNDLED, IS_LOCAL 
from tkinter import StringVar, Tk, Toplevel, Menu, Frame, Label, Button, PhotoImage, NORMAL, DISABLED, NE
from src.constants import DEBUG, HEROES, ROLE_TANK, ROLE_DPS, ROLE_SUPPORT
from configparser import ConfigParser
from src.parse import translate
from pynput import keyboard
from os import startfile
import recognize
import threading
import jsonData


class ui:
    class Layout:
        # * Consts
        # Padding
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
                4: 2
            },

            # DPS
            ROLE_DPS: {                                                                  
                0: 5,                                                                       
                1: 5,
                2: 5,
                3: 5,
                4: 3
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

        # * Constexprs
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

        # Frame positions
        TANK_FRAME_X: int = 0 + WINDOW_PADDING                                                      # 0                     + window_padding
        DPS_FRAME_X: int = (TANK_FRAME_X + TANK_FRAME_WIDTH) + ROLE_FRAME_SEPERATOR_PADDING         # 255 +   role_padding  + window_padding
        SUPPORT_FRAME_X: int = (DPS_FRAME_X + DPS_FRAME_WIDTH) + ROLE_FRAME_SEPERATOR_PADDING       # 600 + 2*role_padding  + window_padding

        ROLE_FRAMES_Y: int = 250                                                        # Kinda arbitrary, but it works


    def __init__(self):
        self.root = Tk()

        self.root.geometry("850x625")
        self.root.title("Overwatch Fucked Me")
        self.root.configure(background="#3C3C3C")
        
        self.characterButtonsDictionary = {}

        self.buttonList: dict[str, list] = {}

        self.selectedCharacters = []
        self.selectedRoles = {ROLE_TANK: [], ROLE_DPS: [], ROLE_SUPPORT: []}
        self.roleFrameDict = {".tankFrame": ROLE_TANK, ".dpsFrame": ROLE_DPS, ".supportFrame": ROLE_SUPPORT}
        
        self.activeCounters = {}

        self.extendedLimits = False
        self.aiActive = False

        self.initializeWindow()

        self.fullbuttonList = []
        for i in self.buttonList.values():
            self.fullbuttonList.extend(i)

        # // print(self.buttonList)
        # // print(self.fullbuttonList)

        self.characterHighlighted = ""
        self.characterHighlightedRectList = []

        # Load config
        self.configPath, self.configIsLocal = prefer_local_resource("config.ini")

        self.config = ConfigParser()
        self.config.read(self.configPath)

        # self.initateStop = False

        # self.root.bind("<Control-i>", captureImage)
        threading.Thread(target=self.keyListener, daemon=True, name="listening-Thread").start()

        self.root.protocol("WM_DELETE_WINDOW", self.onClose)

        self.root.mainloop()


    # Setup
    def initializeWindow(self):
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
        for i in range(5):
            characterFrame = Frame(master=self.root, height=125+50, width=(830/5), background="#3C3C3C", name=f"characterFrame{i}")
            characterFrame.place(x=((830/5)*i + (5*i)), y=0)
            self.recommendedCharacterFrameList.append(characterFrame)

        # Character buttons
        self.inputFrame = Frame(master=self.root, height=35, width=850, background="#3C3C3C", name="inputFrame")
        self.roleInfoFrame = Frame(master=self.root, height=35, width=850, background="#3C3C3C", name="roleInfoFrame")

        self.tankFrame = Frame(master=self.root, height=self.Layout.ROLE_FRAMES_HEIGHT, width=self.Layout.TANK_FRAME_WIDTH, background="#3C3C3C", name="tankFrame")
        self.dpsFrame = Frame(master=self.root, height=self.Layout.ROLE_FRAMES_HEIGHT, width=self.Layout.DPS_FRAME_WIDTH, background="#3C3C3C", name="dpsFrame")
        self.supportFrame = Frame(master=self.root, height=self.Layout.ROLE_FRAMES_HEIGHT, width=self.Layout.SUPPORT_FRAME_WIDTH, background="#3C3C3C", name="supportFrame")

        self.inputFrame.place(x=0, y=178)
        self.roleInfoFrame.place(x=0 + self.Layout.WINDOW_PADDING, y=215)

        self.tankFrame.place(   x=self.Layout.TANK_FRAME_X,     y=self.Layout.ROLE_FRAMES_Y)
        self.dpsFrame.place(    x=self.Layout.DPS_FRAME_X,      y=self.Layout.ROLE_FRAMES_Y)
        self.supportFrame.place(x=self.Layout.SUPPORT_FRAME_X,  y=self.Layout.ROLE_FRAMES_Y)    

    def _labels(self):
        self.placeholderMatrix = []
        self.characterPlaceholderList = []

        placeholderPortrait = PhotoImage(file=resource_path("res", "portraits", "blank.png")).subsample(3, 3)

        for a, b in enumerate(self.recommendedCharacterFrameList):
            placeholderList = []

            characterPlaceholder = Label(b, height=((125/3) + 50), width=(830/10), image=placeholderPortrait, bg="#4C4C4C", name=f"placeholder@{a}characterLabel")
            characterPlaceholder.place(x=0, y=0)

            self.characterPlaceholderList.append(characterPlaceholder)

            for y in range(2):
                for x in range(7):
                    counterPlaceholder = Label(b, height=(125/3), width=(830/5/7), image=placeholderPortrait, bg="#444444", name=f"placeholder@{a}-{x}-{y}Label")
                    counterPlaceholder.place(x=(((830/5/7) * x)), y=((125 / 3) * (y + 1) + 50))
                    placeholderList.append(counterPlaceholder)
            self.placeholderMatrix.append(placeholderList)

        self.roleIconList = [PhotoImage(file=resource_path("res", "icons", "role", f"{i}Icon.png")).subsample(4, 4) for i in ['tank', 'dps', 'support']]

        for x, i in enumerate(['tank', 'dps', 'support']):
            iconLabel = Label(self.roleInfoFrame, image=self.roleIconList[x], bg="#3C3C3C", name=f"{i}IconLabel")
            iconLabel.place(x=([-5, -5+225+5, -5+600+10][x]), y=-7)

    def _buttons(self):
        # global self.extendedLimitsButton

        self.extendedLimitsButton = Button(master=self.inputFrame, text="Extended Limits", name="extendedLimitsButton")
        self.extendedLimitsButton.place(x=5, y=0)
        self.extendedLimitsButton.bind("<Button>", self.mouseButton)

        self.aiActiveButton = Button(master=self.inputFrame, text="AI Recognition", name="aiActiveButton")
        self.aiActiveButton.place(x=845, y=0, anchor=NE)
        self.aiActiveButton.bind("<Button>", self.mouseButton)


    # Select characters
    def tank(self):
        tankButtonList = []
        self.tankPortraitList = [PhotoImage(file=resource_path("res", "portraits", "tank", f"{HEROES[ROLE_TANK][i]}.png")).subsample(4, 4) for i, _ in enumerate(HEROES[ROLE_TANK])]

        i = 0
        for y in self.Layout.GRID[ROLE_TANK]:
            for x in range(self.Layout.GRID[ROLE_TANK][y]):
                tankButton = Button(self.tankFrame, image=self.tankPortraitList[i], name=f"tankButton{i}")
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

                self.characterButtonsDictionary[HEROES[ROLE_TANK][i]] = [tankButton, 0]
                tankButtonList.append(tankButton)
                i += 1

        self.buttonList[ROLE_TANK] = tankButtonList

    def dps(self):
        dpsButtonList = []
        self.dpsPortraitList = [PhotoImage(file=resource_path("res", "portraits", "dps", f"{HEROES[ROLE_DPS][i]}.png")).subsample(4, 4) for i, _ in enumerate(HEROES[ROLE_DPS])]

        i = 0
        for y in self.Layout.GRID[ROLE_DPS]:
            for x in range(self.Layout.GRID[ROLE_DPS][y]):
                dpsButton = Button(self.dpsFrame, image=self.dpsPortraitList[i], name=f"dpsButton{i}")
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

                self.characterButtonsDictionary[HEROES[ROLE_DPS][i]] = [dpsButton, 1]
                dpsButtonList.append(dpsButton)
                i += 1
        
        self.buttonList[ROLE_DPS] = dpsButtonList

    def support(self):
        supportButtonList = []
        self.supportPortraitList = [PhotoImage(file=resource_path("res", "portraits", "support", f"{HEROES[ROLE_SUPPORT][i]}.png")).subsample(4, 4) for i, _ in enumerate(HEROES[ROLE_SUPPORT])]

        i = 0
        for y in self.Layout.GRID[ROLE_SUPPORT]:
            for x in range(self.Layout.GRID[ROLE_SUPPORT][y]):
                supportButton = Button(self.supportFrame, image=self.supportPortraitList[i], name=f"supportButton{i}")
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

                self.characterButtonsDictionary[HEROES[ROLE_SUPPORT][i]] = [supportButton, 2]
                supportButtonList.append(supportButton)
                
                i += 1

        self.buttonList[ROLE_SUPPORT] = supportButtonList


    # Event handlers
    def mouseButtonCharacters(self, event):
        if event.num == 1:
            if (event.widget["state"] == NORMAL 
                and not self.extendedLimits 
                and len(self.selectedRoles[self.roleFrameDict[str(event.widget.master)]]) < (2 - (ROLE_TANK == self.roleFrameDict[str(event.widget.master)]))
                and event.widget not in self.selectedRoles[self.roleFrameDict[str(event.widget.master)]]):
                

                event.widget.configure(bg="SystemHighlight")
                self.selectedRoles[self.roleFrameDict[str(event.widget.master)]].append(event.widget)
                
                # * [1]
                if len(self.selectedRoles[self.roleFrameDict[str(event.widget.master)]]) == (2 - (ROLE_TANK == self.roleFrameDict[str(event.widget.master)])):
                    # * [2]
                    for i in self.buttonList[self.roleFrameDict[str(event.widget.master)]]:
                        # * [3]
                        if i not in self.selectedRoles[self.roleFrameDict[str(event.widget.master)]]:
                            # * [4]
                            i["state"] = DISABLED

            elif event.widget["state"] == NORMAL and self.extendedLimits and len(self.selectedCharacters) < 5 and event.widget not in self.selectedCharacters:
                event.widget.configure(bg="SystemHighlight")
                self.selectedCharacters.append(event.widget)

                if len(self.selectedCharacters) == 5:
                    for i in self.fullbuttonList:
                        if i not in self.selectedCharacters:
                            i["state"] = DISABLED

            threading.Thread(target=self.updateTeamComp, name="updateTeamComp-Thread").start()
            return "break"
        
        elif event.num == 2:
            print(str(event.widget.master))
            # event.widget.configure(height=event.widget.winfo_height()-6, width=event.widget.winfo_width()-6)

        elif event.num == 3:
            if not self.extendedLimits and event.widget in self.selectedRoles[self.roleFrameDict[str(event.widget.master)]]:
                event.widget.configure(bg="SystemButtonFace")
                self.selectedRoles[self.roleFrameDict[str(event.widget.master)]].remove(event.widget)

                for i in self.buttonList[self.roleFrameDict[str(event.widget.master)]]:
                    i["state"] = NORMAL

            elif self.extendedLimits and event.widget in self.selectedCharacters:
                event.widget.configure(bg="SystemButtonFace")
                self.selectedCharacters.remove(event.widget)

                for i in self.fullbuttonList:
                    i["state"] = NORMAL

            threading.Thread(target=self.updateTeamComp, name="updateTeamComp-Thread").start()
            return "break"

    def mouseButton(self, event):
        if event.widget == self.extendedLimitsButton:
            self.extendedLimits = [True, False][self.extendedLimits]
            self.extendedLimitsButton.configure(bg=["SystemButtonFace", "Green"][self.extendedLimits])
            self.selectedCharacters.clear()
            self.selectedRoles = {ROLE_TANK: [], ROLE_DPS: [], ROLE_SUPPORT: []}
            self.updateTeamComp()
            if not self.aiActive:
                for button in self.fullbuttonList:
                    button.configure(bg="SystemButtonFace")
                    button["state"] = NORMAL
        if event.widget == self.aiActiveButton:
            self.aiActive = [True, False][self.aiActive]
            self.aiActiveButton.configure(bg=["SystemButtonFace", "Green"][self.aiActive])
            self.selectedCharacters.clear()
            self.selectedRoles = {ROLE_TANK: [], ROLE_DPS: [], ROLE_SUPPORT: []}
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

                self.selectedCharacters.clear()
                self.selectedRoles = [[], [], []]

                recognize.capture_image()
                returnedClasses = recognize.recognize()

                for i in returnedClasses:
                    if not i[0][i[0].find(' ') + 1:-1] == "Waiting" and not i[0][i[0].find(' ') + 1:-1] == "Not selected":
                        self.selectedCharacters.append(self.characterButtonsDictionary[i[0][i[0].find(' ') + 1:-1]][0])
                    print(f"\"{i[0][i[0].find(' ') + 1:-1]}\"")

                self.updateTeamComp(aiRequest=True)
                
                self.ongoingKeybaordRequest = False

        def startRecognition():
            threading.Thread(target=captureImage, name="captureThread").start()

        def triggerDebug():
            if not DEBUG:   return

            print("[¤] Keybinds:")
            for key, value in self.config.items("keybinds", raw=True):
                print(f"[¤]     {key}: {value}")

        # Set up hotkeys
        self.hk = keyboard.GlobalHotKeys({
                self.config.get("keybinds", "capture"): startRecognition,
                self.config.get("keybinds", "debug"): triggerDebug
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
        startfile(ensure_configurable("counters.json"))

        # Prompt a popup to know when the user is done editing 
        popup = self.popup(title="Editing counters.json", geometry="200x110")

        Label(popup, text="After you are done editing, click \nthe button below to refresh \nthe counters in the app.").pack(pady=(8, 6))
        Button(popup, text="Update counters", command=lambda: [popup.destroy(), self.reloadCounters()]).pack(pady=(0, 8))



    # Processing
    def updateTeamComp(self, aiRequest=False):
        global counterPortraitList, characterPortraitList
        
        counterPortraitList = []
        characterPortraitList = []
        
        if not self.extendedLimits and not aiRequest:
            for a, (role, characters) in enumerate(self.selectedRoles.items()):
                for b, character in enumerate(characters):
                    characterPortrait = PhotoImage(file=resource_path("res", "portraits", ['tank', 'dps', 'support'][a], f"{HEROES[self.roleFrameDict[str(character.master)]][int(''.join([o for o in list(str(character)) if o.isnumeric()]))]}.png")).subsample(3, 3)
                    self.characterPlaceholderList[(a + b + max(a, 1)) - 1].configure(image=characterPortrait)
                    characterPortraitList.append(characterPortrait)

                    counterLists = []
                    
                    for counterRole in ["Tank", "DPS", "Support"]:
                        counterLists.extend(jsonData.counters[HEROES[self.roleFrameDict[str(character.master)]][int("".join([o for o in list(str(character)) if o.isnumeric()]))]][counterRole].values())
                    
                    for i, counter in enumerate(counterLists):
                        portrait = PhotoImage(file=resource_path("res", "portraits", "all", f"{counter}.png")).subsample(6, 6)
                        self.placeholderMatrix[(a + b + max(a, 1)) - 1][i].configure(image=portrait)
                        counterPortraitList.append(portrait)
        else:
            for c, character in enumerate(self.selectedCharacters):
                characterPortrait = PhotoImage(file=resource_path("res", "portraits", "all", f"{HEROES[self.roleFrameDict[str(character.master)]][int(''.join([o for o in list(str(character)) if o.isnumeric()]))]}.png")).subsample(3, 3)
                self.characterPlaceholderList[c].configure(image=characterPortrait)
                characterPortraitList.append(characterPortrait)

                counterLists = []
                
                for counterRole in ["Tank", "DPS", "Support"]:
                    counterLists.extend(jsonData.counters[HEROES[self.roleFrameDict[str(character.master)]][int("".join([o for o in list(str(character)) if o.isnumeric()]))]][counterRole].values())
                
                for i, counter in enumerate(counterLists):
                    portrait = PhotoImage(file=resource_path("res", "portraits", "all", f"{counter}.png")).subsample(6, 6)
                    self.placeholderMatrix[c][i].configure(image=portrait)
                    counterPortraitList.append(portrait)
            
        print(counterLists) # E.g: ['Roadhog', 'Zarya', 'Winston', 'Symmetra', 'Reaper', 'Junkrat', 'Pharah', 'Moira']
        
    def animationFocus(self, event):
        if event.widget["state"] == NORMAL:
            self.characterHighlightedRectList.append([event.widget, event.widget.winfo_x(), event.widget.winfo_y()])    
            # print("<Enter>", event.widget.winfo_x() + 3, event.widget.winfo_y() + 3, event.widget.winfo_height(), event.widget.winfo_width())
            event.widget.configure(height=70, width=70)
            event.widget.place(x=event.widget.winfo_x() - 3, y=event.widget.winfo_y() - 3)

    def animationDefocus(self, event):
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
        # // Label(popup, text=f"Action: {action}").pack(pady=(12, 4))
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
        self.updateTeamComp()


if __name__ == "__main__":
    print("[!] This file is not ment to be run!\n\n")
    input("Press \"Enter\" to exit . . .")



