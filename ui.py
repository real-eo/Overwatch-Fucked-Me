from src.constants import ROLE, DEBUG, HERO_IDS, HERO_ROLE_MAP, HERO_COUNTS, MAX_SLOTS_TANK, MAX_SLOTS_DPS, MAX_SLOTS_SUPPORT, HERO_ROLES, ROLE_COUNT, TOTAL_SLOTS_ALL, COUNTERS_FILE
from tkinter import StringVar, Tk, Toplevel, Menu, Frame, Label, PhotoImage, Event, NORMAL, DISABLED, W, E
from src.resources.manager import prefer_local_resource, resource_path, ensure_configurable, IS_LOCAL 
from src.ui import HeroButton, Button, Layout, Resolution
from src.resources import createPhotoImages, portraits
from src.constants.model import SPECIAL_CLASSES
from PIL import Image, ImageTk, ImageOps
from configparser import ConfigParser
from src.constants import ui as UI
from src.parse import translate
from colorsys import hls_to_rgb
from pynput import keyboard
from os import startfile
import recognize
import threading
import jsonData


class ui:
    def __init__(self):
        self.root = Tk()
        self.root.withdraw()                                                            # ? Hide the window while we set it up

        self.root.title("Overwatch Fucked Me")
        self.root.configure(background=UI.STYLE.BACKGROUND)

        self.layout = Layout(screen=Resolution(self.root.winfo_screenwidth(), self.root.winfo_screenheight()))
        self.root.geometry(str(self.layout.geometry))
        
        self.heroButtonsDictionary = {}

        self.buttonList: dict[str, list[HeroButton]] = {}

        self.selectedHeroes: list[HeroButton | None] = [None for _ in range(TOTAL_SLOTS_ALL)] 
        self.slotsRemaining = {ROLE.TANK: MAX_SLOTS_TANK, ROLE.DPS: MAX_SLOTS_DPS, ROLE.SUPPORT: MAX_SLOTS_SUPPORT}
        self.roleFrameDict = {".tankFrame": ROLE.TANK, ".dpsFrame": ROLE.DPS, ".supportFrame": ROLE.SUPPORT}
        
        self.activeCounters = {}
        self.heroImageCache = {}

        self.extendedLimits = False
        self.aiActive = False

        self.initializeWindow()

        self.fullbuttonList: list[HeroButton] = []
        for i in self.buttonList.values():
            self.fullbuttonList.extend(i)

        self.characterHighlighted = ""
        self.characterHighlightedRectList = []

        # Load config
        self.configPath, self.configIsLocal = prefer_local_resource("config.ini")

        self.config = ConfigParser()
        self.config.read(self.configPath)

        threading.Thread(target=self.keyListener, daemon=True, name="listening-Thread").start()

        # Bind events
        self.root.protocol("WM_DELETE_WINDOW", self.onClose)
        self.root.bind("<Configure>", self.configureLayout)

        self.root.deiconify()                                                           # ? Show the window after setup is complete
        self.root.mainloop()                                                            # ? Start the main loop for the window

    def initializeWindow(self):
        # * Creation
        # Images
        createPhotoImages()

        # General UI
        self.createMenubar()
        self.createFrames()
        self.createLabels()
        self.createNonHeroButtons()
        
        # ! self.createTankButtons()
        # ! self.createDpsButtons()
        # ! self.createSupportButtons()
        for role, frame in zip(HERO_ROLES, self.__roleFrames):
            self.createHeroButtons(role, frame)

        # * Placement
        self.reorganizeInterface()
        


    # * Program control
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

    def resizeWindow(self, width: int, height: int):
        """
        Steps:
         1.  Recalculate the layout
         2.  Resize the window to the new layout dimensions
        (3.) Relayout the hero grid based on the new layout
        (4.) Re-flex the UI elements to fit the new layout
        """
        # ? Prevent recursive calls to this function when resizing the window
        if self.layout.isWindowResizing:         return

        # Recalculate the layout
        self.layout.recalculate(width, height)

        # Resize the window to the new layout dimensions
        self.layout.isWindowResizing = True
        try:        
            self.root.geometry(str(self.layout.geometry))
            self.reorganizeInterface()
        finally:    
            self.layout.isWindowResizing = False

        # ? Now done in `reorganizeInterface()` 
        # Relayout the hero grid based on the new layout
        # // for role in HERO_ROLES:  self.placeHeroButtons(role, centerIncompleteRows=True)

        # Re-flex the UI elements to fit the new layout
        # TODO: Implement a method to re-flex the UI elements to fit the new layout


    # * UI elements
    # Creation
    def createMenubar(self):
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

    def createFrames(self):
        # Portraits
        # // self.recommendedHeroFrameList = []
        # // for i in range(TOTAL_SLOTS_ALL):
        # //     characterFrame = Frame(
        # //         master=self.root, 
        # //         height=UI.LAYOUT.SELECTED_HERO_HEIGHT + UI.LAYOUT.COUNTERS_AREA_HEIGHT, 
        # //         width=(UI.LAYOUT.VIEWPORT_WIDTH/TOTAL_SLOTS_ALL), 
        # //         background=UI.STYLE.BACKGROUND, 
        # //         name=f"characterFrame{i}"
        # //     )

        # //     characterFrame.place(
        # //         x=((UI.LAYOUT.VIEWPORT_WIDTH/TOTAL_SLOTS_ALL)*i + (TOTAL_SLOTS_ALL*i)), 
        # //         y=0
        # //     )
        # //     self.recommendedHeroFrameList.append(characterFrame)
        self.recommendedHeroFrameList = [
            Frame(
                self.root,
                name=f"characterFrame{i}",
                background=UI.STYLE.BACKGROUND,
            )
            for i in range(TOTAL_SLOTS_ALL)
        ]


        # Buttons
        # // self.inputFrame = Frame(master=self.root, height=UI.LAYOUT.INPUT_FRAME_HEIGHT, width=UI.LAYOUT.WINDOW_WIDTH, background=UI.STYLE.BACKGROUND, name="inputFrame")
        # // self.roleInfoFrame = Frame(master=self.root, height=UI.LAYOUT.ROLE_ICON_FRAME_HEIGHT, width=UI.LAYOUT.WINDOW_WIDTH, background=UI.STYLE.BACKGROUND, name="roleInfoFrame")
        self.inputFrame = Frame(self.root, name="inputFrame", background=UI.STYLE.BACKGROUND)
        self.roleInfoFrame = Frame(self.root, name="roleInfoFrame", background=UI.STYLE.BACKGROUND)

        # // self.tankFrame = Frame(master=self.root, height=UI.LAYOUT.ROLE_FRAMES_HEIGHT, width=UI.LAYOUT.TANK_FRAME_WIDTH, background=UI.STYLE.BACKGROUND, name="tankFrame")
        # // self.dpsFrame = Frame(master=self.root, height=UI.LAYOUT.ROLE_FRAMES_HEIGHT, width=UI.LAYOUT.DPS_FRAME_WIDTH, background=UI.STYLE.BACKGROUND, name="dpsFrame")
        # // self.supportFrame = Frame(master=self.root, height=UI.LAYOUT.ROLE_FRAMES_HEIGHT, width=UI.LAYOUT.SUPPORT_FRAME_WIDTH, background=UI.STYLE.BACKGROUND, name="supportFrame")

        self.tankFrame = Frame(self.root, name="tankFrame")
        self.dpsFrame = Frame(self.root, name="dpsFrame")
        self.supportFrame = Frame(self.root, name="supportFrame")

        self.__roleFrames = (self.tankFrame, self.dpsFrame, self.supportFrame)

        # // self.inputFrame.place(x=0, y=UI.LAYOUT.INPUT_FRAME_Y)
        # // self.roleInfoFrame.place(x=0 + UI.LAYOUT.WINDOW_PADDING, y=UI.LAYOUT.ROLE_ICON_Y)

        # // self.tankFrame.place(   x=UI.LAYOUT.TANK_FRAME_X,     y=UI.LAYOUT.ROLE_FRAMES_Y)
        # // self.dpsFrame.place(    x=UI.LAYOUT.DPS_FRAME_X,      y=UI.LAYOUT.ROLE_FRAMES_Y)
        # // self.supportFrame.place(x=UI.LAYOUT.SUPPORT_FRAME_X,  y=UI.LAYOUT.ROLE_FRAMES_Y)    

    def createLabels(self):
        self.counterImagePlaceholders: list[dict[ROLE, list[Label]]] = []               # 2D list of labels which get replaced with portraits of the counters (3x7)
        self.characterImagePlaceholders: list[Label] = []                               # List of labels which get replaced with portraits of the selected heroes (5)

        for slotIndex, slotFrame in enumerate(self.recommendedHeroFrameList):
            # * Selected hero
            # Configure slot frame
            slotFrame.grid_rowconfigure(0, weight=0, minsize=UI.LAYOUT.SELECTED_HERO_HEIGHT)
            slotFrame.grid_rowconfigure(1, weight=1)
            slotFrame.grid_columnconfigure(0, weight=1)

            # Selected hero label
            # // characterPlaceholder = Label(
            # //     b, 
            # //     height=(UI.LAYOUT.SELECTED_HERO_HEIGHT), 
            # //     width=(UI.LAYOUT.VIEWPORT_WIDTH/10), 
            # //     image=portraits.HERO_3x3["blank"],
            # //     bg=UI.STYLE.Label.SelectedHero.BACKGROUND, 
            # //     name=f"placeholder@{a}characterLabel"
            # // )
            selectedHeroPlaceholder = Label(
                slotFrame,
                image=portraits.HERO_3x3["blank"],
                bg=UI.STYLE.Label.SelectedHero.BACKGROUND,
                name=f"placeholder@{slotIndex}characterLabel",
            )

            # // characterPlaceholder.place(x=0, y=0)
            selectedHeroPlaceholder.grid(row=0, column=0, sticky="nsew")

            # // self.characterImagePlaceholders.append(characterPlaceholder)
            self.characterImagePlaceholders.append(selectedHeroPlaceholder)

            # * Hero's counters
            # Counters slots frame
            countersFrame = Frame(slotFrame, bg=UI.STYLE.BACKGROUND, name=f"countersFrame{slotIndex}")
            countersFrame.grid(row=1, column=0, sticky="nsew")
 
            # Hero's counters labels
            placeholderDict: dict[ROLE, list[Label]] = {}

            # // for roleIndex, role in enumerate(HERO_ROLES):
            for roleIndex, role in enumerate(HERO_ROLES):
                countersFrame.grid_rowconfigure(roleIndex, weight=1)
                placeholderDict[role] = []

                for counterIndex in range(UI.LAYOUT.MAX_COUNTERS_PER_ROLE):
                    # Configure counters frame
                    countersFrame.grid_columnconfigure(counterIndex, weight=1, uniform=f"counters{slotIndex}")

                    # Object
                    # // counterPlaceholder = Label(
                    # //     b, 
                    # //     height=((UI.LAYOUT.COUNTERS_AREA_HEIGHT / ROLE_COUNT)), 
                    # //     width=(UI.LAYOUT.VIEWPORT_WIDTH / TOTAL_SLOTS_ALL / UI.LAYOUT.MAX_COUNTERS_PER_ROLE), 
                    # //     image=portraits.HERO_3x3["blank"],
                    # //     bg=UI.STYLE.Label.Counter.BACKGROUND,
                    # //     name=f"placeholder@{a}-{counterIndex}-{roleIndex}Label"
                    # // )
                    counterPlaceholder = Label(
                        countersFrame,
                        image=portraits.HERO_3x3["blank"],
                        bg=UI.STYLE.Label.Counter.BACKGROUND,
                        name=(
                            f"placeholder@{slotIndex}-"
                            f"{counterIndex}-{roleIndex}Label"
                        ),
                    )

                    # Location
                    # // counterPlaceholder.place(
                    # //     x=(((UI.LAYOUT.VIEWPORT_WIDTH / TOTAL_SLOTS_ALL / UI.LAYOUT.MAX_COUNTERS_PER_ROLE) * counterIndex)), 
                    # //     y=((UI.LAYOUT.COUNTERS_AREA_HEIGHT / ROLE_COUNT) * (roleIndex) + UI.LAYOUT.SELECTED_HERO_HEIGHT)
                    # // )
                    counterPlaceholder.grid(row=roleIndex, column=counterIndex, sticky="nsew")

                    # Data
                    counterPlaceholder.counterData = None
                    counterPlaceholder.counterID = None

                    # Functionality
                    counterPlaceholder.bind("<Enter>", self.showCounterTooltip)
                    counterPlaceholder.bind("<Leave>", self.hideCounterTooltip)

                    # Storage
                    # // placeholderDict.setdefault(
                    # //     role,                                                           # Get the list of placeholders for the current role (tank/dps/support)
                    # //     []                                                              # If it doesn't exist, create a new empty list
                    # // ).append(counterPlaceholder)
                    placeholderDict[role].append(counterPlaceholder)
            self.counterImagePlaceholders.append(placeholderDict)

        # Role icons
        self.roleIconList = [PhotoImage(file=resource_path("res", "icons", "role", f"{i}Icon.png")).subsample(4, 4) for i in HERO_ROLES]

        for column, role in enumerate(HERO_ROLES):
            self.roleInfoFrame.grid_columnconfigure(column, weight=1)
            
            iconLabel = Label(self.roleInfoFrame, image=self.roleIconList[column], bg=UI.STYLE.BACKGROUND, name=f"{role}IconLabel")
            
            # // iconLabel.place(x=([-5, -5+225+5, -5+600+10][column]), y=-7)
            iconLabel.grid(row=0, column=column, sticky="nsew")

    def createNonHeroButtons(self):
        self.extendedLimitsButton = Button(master=self.inputFrame, text="Extended Limits", name="extendedLimitsButton")
        # // self.extendedLimitsButton.place(x=5, y=UI.LAYOUT.INPUT_FRAME_HEIGHT / 2, anchor=W)
        self.extendedLimitsButton.pack(side="left", padx=5)
        self.extendedLimitsButton.bind("<Button>", self.mouseButton)

        self.aiActiveButton = Button(master=self.inputFrame, text="AI Recognition", name="aiActiveButton")
        # // self.aiActiveButton.place(x=UI.LAYOUT.WINDOW_WIDTH - 5, y=UI.LAYOUT.INPUT_FRAME_HEIGHT / 2, anchor=E)
        self.aiActiveButton.pack(side="right", padx=5)
        self.aiActiveButton.bind("<Button>", self.mouseButton)

    def createHeroButtons(self, role: ROLE, parentFrame: Frame):
        buttons = []
        # self.tankPortraitList = [
            # portraits.HERO_4x4[heroId]
            # for heroId in HERO_IDS[ROLE.TANK]
        # ]

        for heroId in HERO_IDS[role]:
            button = HeroButton(
                parentFrame,
                heroId=heroId,

                image=portraits.HERO_4x4[heroId],
                bg=UI.STYLE.HeroButton.COLOR,
                borderwidth=UI.STYLE.HeroButton.BORDERWIDTH,
                height=UI.STYLE.HeroButton.HEIGHT, 
                width=UI.STYLE.HeroButton.WIDTH
            )

            button.bind("<Button>", self.mouseButtonCharacters)
            button.bind("<Enter>", self.animationFocus)
            button.bind("<Leave>", self.animationDefocus)

            self.heroButtonsDictionary[heroId] = button
            buttons.append(button)

        self.buttonList[role] = buttons

            
    # Placement
    def reorganizeInterface(self) -> None:
        # Role frames
        for frame, rect in zip(self.__roleFrames, self.layout.roleFrameRects):          # ? `roleFrames` is defined in `createFrames()` 
            frame.place_configure(
                x=rect.x,
                y=rect.y,
                width=rect.width,
                height=rect.height,
            )

        # Switch-input frame
        self.inputFrame.place_configure(
            x=0,
            y=self.layout.inputFrameY,
            width=self.layout.geometry.width,
            height=UI.LAYOUT.INPUT_FRAME_HEIGHT,
        )

        # Role info frame
        self.roleInfoFrame.place_configure(
            x=UI.LAYOUT.WINDOW_PADDING,
            y=self.layout.roleIconY,
            width=self.layout.geometry.width - 2 * UI.LAYOUT.WINDOW_PADDING,
            height=UI.LAYOUT.ROLE_ICON_FRAME_HEIGHT,
        )

        # Recommended hero frames
        for index, frame in enumerate(self.recommendedHeroFrameList):
            frame.place_configure(
                x=0,
                y=0,
                width=self.layout.geometry.width/10,
                height=UI.LAYOUT.SELECTED_HERO_HEIGHT,
            )

        # Hero buttons
        for role in HERO_ROLES: self.placeHeroButtons(role)

    def placeHeroButtons(self, role: ROLE, centerIncompleteRows: bool = True) -> None:
        columns = self.layout.heroLayout.widths[role]
    
        for index, button in enumerate(self.buttonList[role]):
            row, column = divmod(index, self.layout.heroLayout.widths[role])            # ? Get the row and column of the button based on the index and number of columns
            buttonsInRow = min(columns, HERO_COUNTS[role] - (row * columns))            # ? Number of buttons in the current row (last row may have less buttons than the others)
            offset = (                                                                  
                (columns - buttonsInRow) / 2                                            # ? Offset to center the buttons 
                if centerIncompleteRows                                                 # ? in the row if there are
                else 0                                                                  # ? less buttons than columns 
            )

            button.place_configure(
                x=int((column + offset) * UI.LAYOUT.HERO_BUTTON_SIZE),
                y=row * UI.LAYOUT.HERO_BUTTON_SIZE,
            )
  

    # ! ----- OLD CODE ----- !
    def createTankButtons(self):
        tankButtonList = []
        self.tankPortraitList = [
            portraits.HERO_4x4[heroID]
            for heroID in HERO_IDS[ROLE.TANK]
        ]

        i = 0
        for y in UI.LAYOUT.GRID[ROLE.TANK]:
            for x in range(UI.LAYOUT.GRID[ROLE.TANK][y]):
                tankButton: HeroButton = HeroButton(
                    self.tankFrame, 
                    heroId=HERO_IDS[ROLE.TANK][i],
                                        
                    image=self.tankPortraitList[i], 
                    bg=UI.STYLE.HeroButton.COLOR,
                    borderwidth=UI.STYLE.HeroButton.BORDERWIDTH,
                    height=UI.STYLE.HeroButton.HEIGHT, 
                    width=UI.STYLE.HeroButton.WIDTH
                )

                tankButton.place(
                    x=(
                        (x * UI.LAYOUT.HERO_BUTTON_SIZE) 
                        + ((UI.LAYOUT.HERO_BUTTON_SIZE/2) * (UI.LAYOUT.TANK_BUTTON_COLUMNS - UI.LAYOUT.GRID[ROLE.TANK][y]))
                    ), 
                    y=(y * UI.LAYOUT.HERO_BUTTON_SIZE)
                )

                tankButton.bind("<Button>", self.mouseButtonCharacters)
                tankButton.bind("<Enter>", self.animationFocus)
                tankButton.bind("<Leave>", self.animationDefocus)

                self.heroButtonsDictionary[HERO_IDS[ROLE.TANK][i]] = tankButton
                tankButtonList.append(tankButton)
                i += 1

        self.buttonList[ROLE.TANK] = tankButtonList

    def createDpsButtons(self):
        dpsButtonList = []
        self.dpsPortraitList = [
            portraits.HERO_4x4[heroID]
            for heroID in HERO_IDS[ROLE.DPS]
        ]

        i = 0
        for y in UI.LAYOUT.GRID[ROLE.DPS]:
            for x in range(UI.LAYOUT.GRID[ROLE.DPS][y]):
                dpsButton: HeroButton = HeroButton(
                    self.dpsFrame, 
                    heroId=HERO_IDS[ROLE.DPS][i],

                    image=self.dpsPortraitList[i], 
                    bg=UI.STYLE.HeroButton.COLOR,
                    borderwidth=UI.STYLE.HeroButton.BORDERWIDTH,
                    height=UI.STYLE.HeroButton.HEIGHT, 
                    width=UI.STYLE.HeroButton.WIDTH
                )

                dpsButton.place(
                    x=(
                        (x * UI.LAYOUT.HERO_BUTTON_SIZE) 
                        + ((UI.LAYOUT.HERO_BUTTON_SIZE/2) * (UI.LAYOUT.DPS_BUTTON_COLUMNS - UI.LAYOUT.GRID[ROLE.DPS][y]))
                    ), 
                    y=(y * UI.LAYOUT.HERO_BUTTON_SIZE)
                )

                dpsButton.bind("<Button>", self.mouseButtonCharacters)
                dpsButton.bind("<Enter>", self.animationFocus)
                dpsButton.bind("<Leave>", self.animationDefocus)

                self.heroButtonsDictionary[HERO_IDS[ROLE.DPS][i]] = dpsButton
                dpsButtonList.append(dpsButton)
                i += 1
        
        self.buttonList[ROLE.DPS] = dpsButtonList

    def createSupportButtons(self):
        supportButtonList = []
        self.supportPortraitList = [
            portraits.HERO_4x4[heroID]
            for heroID in HERO_IDS[ROLE.SUPPORT]
        ]

        i = 0
        for y in UI.LAYOUT.GRID[ROLE.SUPPORT]:
            for x in range(UI.LAYOUT.GRID[ROLE.SUPPORT][y]):
                supportButton: HeroButton = HeroButton(
                    self.supportFrame, 
                    heroId=HERO_IDS[ROLE.SUPPORT][i],
                                        
                    image=self.supportPortraitList[i], 
                    bg=UI.STYLE.HeroButton.COLOR,
                    borderwidth=UI.STYLE.HeroButton.BORDERWIDTH,
                    height=UI.STYLE.HeroButton.HEIGHT, 
                    width=UI.STYLE.HeroButton.WIDTH
                )
                
                supportButton.place(
                    x=(
                        (x * UI.LAYOUT.HERO_BUTTON_SIZE) 
                        + ((UI.LAYOUT.HERO_BUTTON_SIZE/2) * (UI.LAYOUT.SUPPORT_BUTTON_COLUMNS - UI.LAYOUT.GRID[ROLE.SUPPORT][y]))
                    ), 
                    y=(y * UI.LAYOUT.HERO_BUTTON_SIZE)
                )
                
                supportButton.bind("<Button>", self.mouseButtonCharacters)
                supportButton.bind("<Enter>", self.animationFocus)
                supportButton.bind("<Leave>", self.animationDefocus)

                self.heroButtonsDictionary[HERO_IDS[ROLE.SUPPORT][i]] = supportButton
                supportButtonList.append(supportButton)
                
                i += 1

        self.buttonList[ROLE.SUPPORT] = supportButtonList
    # ! -------------------- !

    # * Event handlers
    def mouseButtonCharacters(self, event: Event):
        heroButtonRole = self.roleFrameDict[str(event.widget.master)]
        selectedCount = sum(1 for h in self.selectedHeroes if h is not None)

        if event.num == 1:
            canSelect = (
                event.widget.isInteractable
                and event.widget not in self.selectedHeroes
                and (self.slotsRemaining[heroButtonRole] > 0 if not self.extendedLimits else selectedCount < TOTAL_SLOTS_ALL)
            )
            if not canSelect: return "break"

            slot = self.selectedHeroes.index(None)
            self.selectedHeroes[slot] = event.widget

            if not self.extendedLimits:
                self.slotsRemaining[heroButtonRole] -= 1
                if self.slotsRemaining[heroButtonRole] == 0:
                    for btn in self.buttonList[heroButtonRole]:
                        if btn not in self.selectedHeroes:
                            btn.disable()
            else:
                if selectedCount + 1 >= TOTAL_SLOTS_ALL:
                    for btn in self.fullbuttonList:
                        if btn not in self.selectedHeroes:
                            btn.disable()

            self.root.after(0, self.updateTeamComp)
            self.root.after(0, self.updateHeroButtonHighlights)
            return "break"

        elif event.num == 3:
            if event.widget not in self.selectedHeroes: return "break"

            self.selectedHeroes[self.selectedHeroes.index(event.widget)] = None         # TODO: Fix: find by identity, not index

            if not self.extendedLimits:
                self.slotsRemaining[heroButtonRole] += 1
                for btn in self.buttonList[heroButtonRole]:
                    btn.enable()
            else:
                for btn in self.fullbuttonList:
                    btn.enable()

            self.root.after(0, self.updateTeamComp)
            self.root.after(0, self.updateHeroButtonHighlights)
            return "break"

        # | DEBUG
        elif event.num == 2 and DEBUG:
            button: HeroButton = event.widget

            print(f"\n[D] Hero button: \"{button.HERO_ID}\"")

            # Tkinter configuration options and current values
            for option, details in button.configure().items():
                print(f"[-]   {option}: {details[-1]}")

            # Widget geometry and Tk metadata
            print(f"[-]   winfo_class: {button.winfo_class()}")
            print(f"[-]   winfo_geometry: {button.winfo_geometry()}")
            print(f"[-]   winfo_x: {button.winfo_x()}")
            print(f"[-]   winfo_y: {button.winfo_y()}")
            print(f"[-]   winfo_width: {button.winfo_width()}")
            print(f"[-]   winfo_height: {button.winfo_height()}")
            print(f"[-]   bindtags: {button.bindtags()}")
            print(f"[-]   isInteractable: {button.isInteractable}")

    def mouseButton(self, event: Event):
        if event.widget == self.extendedLimitsButton:
            self.extendedLimits = [True, False][self.extendedLimits]
            self.extendedLimitsButton.configure(bg=[UI.STYLE.ControlButton.COLOR, UI.STYLE.ControlButton.Active.COLOR][self.extendedLimits])

            self.selectedHeroes = [None for _ in range(TOTAL_SLOTS_ALL)]
            self.slotsRemaining = {ROLE.TANK: MAX_SLOTS_TANK, ROLE.DPS: MAX_SLOTS_DPS, ROLE.SUPPORT: MAX_SLOTS_SUPPORT}

            if not self.aiActive:
                for button in self.fullbuttonList:
                    button.configure(bg=UI.STYLE.HeroButton.COLOR)
                    button.enable()

            self.updateTeamComp()
            self.updateHeroButtonHighlights()
        
        if event.widget == self.aiActiveButton:
            self.aiActive = [True, False][self.aiActive]
            self.aiActiveButton.configure(bg=[UI.STYLE.ControlButton.COLOR, UI.STYLE.ControlButton.Active.COLOR][self.aiActive])

            self.selectedHeroes = [None for _ in range(TOTAL_SLOTS_ALL)]
            self.slotsRemaining = {ROLE.TANK: MAX_SLOTS_TANK, ROLE.DPS: MAX_SLOTS_DPS, ROLE.SUPPORT: MAX_SLOTS_SUPPORT}

            if self.aiActive:
                for button in self.fullbuttonList:
                    button.configure(bg=UI.STYLE.HeroButton.COLOR)
                    button.disable()
            else:
                for button in self.fullbuttonList:
                    button.enable()

            self.updateTeamComp()
            self.updateHeroButtonHighlights()

        return "break"

    def keyListener(self):
        self.ongoingKeybaordRequest = False

        def captureImage():
            if self.aiActive and not self.ongoingKeybaordRequest:
                print('[§] Starting recognition')

                self.ongoingKeybaordRequest = True
                self.selectedHeroes = []

                recognize.capture_image()
                returnedClasses = recognize.recognize(extendedLimits=self.extendedLimits)

                for cls in returnedClasses:
                    recognizedHeroId, confidenceScore = cls

                    # Incase one of the enemies got classified as not a hero 
                    if recognizedHeroId in SPECIAL_CLASSES:
                        self.selectedHeroes.append(None)
                        continue                                                        # ? Skip to next iteration

                    # Sanity check - shouldn't happen
                    if recognizedHeroId not in self.heroButtonsDictionary:
                        print(f"[!] ERROR: Coun't find recognized character \"{recognizedHeroId}\" in `self.heroButtonsDictionary`!")
                        self.selectedHeroes.append(None)
                        continue

                    self.selectedHeroes.append(self.heroButtonsDictionary[recognizedHeroId])
              

                self.root.after(0, lambda: self.updateTeamComp(forceReload=True))       # ? Tkinter widgets should only be updated on the main thread
                self.root.after(0, self.updateHeroButtonHighlights)                     # ? Tkinter widgets should only be updated on the main thread
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

    def configureLayout(self, event: Event):
        # ? Additional sanity check if needed
        # if event.widget is not self.root:
        #     print(f"[!] Warning: Received <Configure> event from unexpected widget: {event.widget}. Ignoring.")
        #     return

        # ? If the window moved to a screen with a different resolution
        if (self.root.winfo_screenwidth(), self.root.winfo_screenheight()) != (self.layout.screen.width, self.layout.screen.height):
            requiresResizing = self.layout.monitorResolutionChanged(
                Resolution(
                    self.root.winfo_screenwidth(), 
                    self.root.winfo_screenheight()
                )
            )

            if requiresResizing:                                                        # If the layout is too large for the new screen resolution,
                self.scheduleResizeJob(                                                 # schedule a resize job to adjust the window size. 
                    self.layout.geometry.width,                                         # NOTE: This is fine because the window will be squashed by  
                    self.layout.geometry.height                                         #       `calculateOptimalHeroLayout()` to fit the new screen size 
                )
        
        # ? If the window size changed
        elif (event.width, event.height) != (self.layout.geometry.width, self.layout.geometry.height):
            self.scheduleResizeJob(event.width,event.height)


    # * Processing
    def updateTeamComp(self, forceReload: bool = False):
        # Update portraits and counters for the selected heroes
        for index, heroButton in enumerate(self.selectedHeroes):                        # ? Enumerate so we can use the index for updating the placeholder label
            if heroButton is None:                                                      # No hero selected in this slot
                # Clear the portrait placeholder for this slot
                self.characterImagePlaceholders[index].configure(image=portraits.HERO_3x3["blank"])
                
                # Clear the counter placeholders' data for this slot
                for role in HERO_ROLES:
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
                    for role in HERO_ROLES:
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
                usedSlots = {ROLE.TANK: 0, ROLE.DPS: 0, ROLE.SUPPORT: 0}                # To keep track of how many counter slots we have used for each role, so we know where to place the next counter portrait

                for counterID, data in heroCounters.items():                            # TODO: Use the `data` for something
                    counterRole = HERO_ROLE_MAP[counterID]

                    # TODO: Fix this issue (somehow)
                    # Safety check to prevent index out of range errors 
                    if usedSlots[counterRole] >= UI.LAYOUT.MAX_COUNTERS_PER_ROLE: 
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

    def updateHeroButtonHighlights(self):
        selectedIds = {
            heroButton.winfo_name()
            for heroButton in self.selectedHeroes
            if heroButton is not None
        }

        for button in self.fullbuttonList:
            heroId = button.winfo_name()
            isSelected = button in self.selectedHeroes

            counterScore = sum(
                selectedId in jsonData.counters.get(heroId, {})
                for selectedId in selectedIds
            )

            intensity = min(counterScore / TOTAL_SLOTS_ALL, 1.0)

            # HLS values:
            # 0.0 -> 60 degrees, 100% saturation, 100% lightness
            # 1.0 -> 0 degrees, 100% saturation, 50% lightness
            hue = (60 * (1 - intensity)) / 360
            lightness = 1.0 - (0.5 * intensity)
            saturation = 1.0

            red, green, blue = hls_to_rgb(
                hue,
                lightness,
                saturation
            )

            color = (
                f"#{round(red * 255):02X}"
                f"{round(green * 255):02X}"
                f"{round(blue * 255):02X}"
            )
            
            buttonImage = self.getHeroImage(
                heroId, 
                (
                    color
                    if not isSelected 
                    or self.aiActive
                    or (isSelected and counterScore > 0)
                    else UI.STYLE.HeroButton.Selected.COLOR
                ),
                inactive=not button.isInteractable
            )

            button.configure(
                image=buttonImage,
                bg=UI.STYLE.HeroButton.Selected.COLOR if (isSelected and not self.aiActive) else color,
                activebackground=UI.STYLE.HeroButton.Selected.COLOR if (isSelected and not self.aiActive) else color
            )
                    
    def animationFocus(self, event: Event):
        if event.widget.isInteractable:
            self.characterHighlightedRectList.append([event.widget, event.widget.winfo_x(), event.widget.winfo_y()])    
            event.widget.configure(width=UI.STYLE.HeroButton.Hovered.WIDTH, height=UI.STYLE.HeroButton.Hovered.HEIGHT)
            event.widget.place(x=event.widget.winfo_x() - 2, y=event.widget.winfo_y() - 2)

    def animationDefocus(self, event: Event):
        if event.widget.isInteractable:
            try:
                widget = self.characterHighlightedRectList.pop(0)
                widget[0].configure(width=UI.STYLE.HeroButton.WIDTH, height=UI.STYLE.HeroButton.HEIGHT)
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

    def scheduleResizeJob(self, width: int, height: int):
        # Stop previous resize jobs if it exists
        if self.layout.activeResizeJob is not None:
            self.root.after_cancel(self.layout.activeResizeJob)

        # Schedule a new resize job
        self.layout.activeResizeJob = self.root.after(
            100, 
            lambda: self.resizeWindow(width, height)
        )


    # * Getters
    def getHeroImage(self, heroId, backgroundColor, inactive):
        cacheKey = (heroId, backgroundColor, inactive)

        if cacheKey not in self.heroImageCache:
            sourceImage = ImageTk.getimage(
                portraits.HERO_4x4[heroId]
            ).convert("RGBA")

            if inactive:
                alpha = sourceImage.getchannel("A")

                grayImage = ImageOps.grayscale(
                    sourceImage.convert("RGB")
                ).convert("RGBA")

                # 50% original color + 50% grayscale
                sourceImage = Image.blend(sourceImage, grayImage, UI.STYLE.HeroButton.Disabled.GRAYSCALE_AMOUNT/100)

                # 75% opacity
                sourceImage.putalpha(alpha.point(lambda value: value * UI.STYLE.HeroButton.Disabled.PORTRAIT_OPACITY // 100))


            backgroundImage = Image.new(
                "RGBA",
                sourceImage.size,
                backgroundColor
            )
            backgroundImage.alpha_composite(sourceImage)

            self.heroImageCache[cacheKey] = ImageTk.PhotoImage(backgroundImage)

        return self.heroImageCache[cacheKey]

if __name__ == "__main__":
    print("[!] This file is not ment to be run!\n\n")
    input("Press \"Enter\" to exit . . .")



