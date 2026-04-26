from tkinter import StringVar, Tk, Toplevel, Menu, Frame, Label, Button, PhotoImage, NORMAL, DISABLED, NE
from resourceManager import prefer_local_resource, resource_path, ensure_configurable, IS_BUNDLED, IS_LOCAL 
from configparser import ConfigParser
from src.parse import translate
from pynput import keyboard
from os import startfile
import recognize
import threading
import jsonData


class ui:
    def __init__(self):
        self.root = Tk()

        self.root.geometry("850x550")
        self.root.title("Overwatch Fucked Me")
        self.root.configure(background="#3C3C3C")

        self.characters = [
            ["Dva", "Doomfist", "Junker Queen", "Orisa", "Ramattra", "Reinhardt", "Roadhog", "Sigma", "Winston", "Wrecking Ball", "Zarya"],
            ["Ashe", "Bastion", "Cassidy", "Echo", "Genji", "Hanzo", "Junkrat", "Mei", "Pharah", "Reaper", "Sojourn", "Soldier 76", "Sombra", "Symmetra", "Torbjorn", "Tracer", "Widowmaker"],
            ["Ana", "Baptiste", "Brigitte", "Kiriko", "Lucio", "Mercy", "Moira", "Zenyatta"]
        ]
        
        self.characterButtonsDictionary = {}

        self.buttonList = []

        self.selectedCharacters = []
        self.selectedRoles = [[], [], []]
        self.roleFrameDict = {".tankFrame": 0, ".dpsFrame": 1, ".supportFrame": 2}
        
        self.activeCounters = {}

        self.extendedLimits = False
        self.aiActive = False

        self.initializeWindow()

        self.fullbuttonList = []
        for i in self.buttonList:
            self.fullbuttonList.extend(i)

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

    # // def stopListener(self):
    # //     # If the listener is running, stop it
    # //     if hasattr(self, "hk"):
    # //         self.hk.stop()

    def popup(self, title: str = "Alert", geometry: str = "400x200") -> Toplevel:
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

        editMenu.add_command(label="Edit counters.json", command=lambda: startfile(ensure_configurable("counters.json")))
        
        # Settings
        settingsMenu = Menu(menubar, tearoff=False)                                     # Dropdown menu when clicking on "Settings" in the toolbar
        
        keybindsMenu = Menu(settingsMenu, tearoff=False)                                # Submenu for keybinds in the settings menu
        keybindsMenu.add_command(label="Capture", command=lambda: self.promptNewKeybind("capture")) 
        keybindsMenu.add_command(label="Stop Listener", command=lambda: self.promptNewKeybind("stop"))          # ? This is really just DEBUG button
        keybindsMenu.add_command(label="Reset to default", command=lambda: self.resetKeybinds())
        settingsMenu.add_cascade(label="Keybinds", menu=keybindsMenu)

        # Add dropdowns to toolbar
        menubar.add_cascade(label="File", menu=fileMenu)
        menubar.add_cascade(label="Edit", menu=editMenu)
        menubar.add_cascade(label="Settings", menu=settingsMenu)
        
        self.root.config(menu=menubar)

    def _frames(self):
        # global recommendedCharacterFrameList, inputFrame, roleInfoFrame, tankFrame, dpsFrame, supportFrame

        self.recommendedCharacterFrameList = []

        for i in range(5):
            characterFrame = Frame(master=self.root, height=125+50, width=(830/5), background="#3C3C3C", name=f"characterFrame{i}")
            characterFrame.place(x=((830/5)*i + (5*i)), y=0)
            self.recommendedCharacterFrameList.append(characterFrame)


        self.inputFrame = Frame(master=self.root, height=35, width=850, background="#3C3C3C", name="inputFrame")
        self.roleInfoFrame = Frame(master=self.root, height=35, width=850, background="#3C3C3C", name="roleInfoFrame")

        self.tankFrame = Frame(master=self.root, height=300, width=225, background="#3C3C3C", name="tankFrame")
        self.dpsFrame = Frame(master=self.root, height=300, width=375 + 5, background="#3C3C3C", name="dpsFrame")
        self.supportFrame = Frame(master=self.root, height=300, width=225, background="#3C3C3C", name="supportFrame")

        self.inputFrame.place(x=0, y=178)
        self.roleInfoFrame.place(x=0+10, y=215)

        self.tankFrame.place(x=0+10, y=250)
        self.dpsFrame.place(x=225+10, y=250)
        self.supportFrame.place(x=600+5+10, y=250)    

    def _labels(self):
        # global self.roleIconList, self.placeholderMatrix, self.characterPlaceholderList, self.placeholderPortrait
        # global placeholderPortrait

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
                    # f"#{str(hex(int('101010', 16) * max(x+y+a, 1)))[2:]}"
                    # f"#{str(hex(int('24', 16) * (x + 1)))[2:]}{str(hex(int('7F', 16) * (y + 1)))[2:]}{str(hex(int('33', 16) * (a + 1)))[2:]}"
                    counterPlaceholder = Label(b, height=(125/3), width=(830/5/7), image=placeholderPortrait, bg="#444444", name=f"placeholder@{a}-{x}-{y}Label")
                    counterPlaceholder.place(x=(((830/5/7) * x)), y=((125 / 3) * (y + 1) + 50))
                    placeholderList.append(counterPlaceholder)
            self.placeholderMatrix.append(placeholderList)

        # selectedCharacterPlaceholder = Label(b, height=(125/3) + 50, width=(830/10), image=self.placeholderPortrait, bg=f'#3C3C3C', name=f"placeholderLabel{a}")
        # selectedCharacterPlaceholder.place(x=(0), y=(0))

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
        # global self.buttonList, tankPortraitList

        tankButtonList = []

        self.tankPortraitList = [PhotoImage(file=resource_path("res", "portraits", "tank", f"{self.characters[0][x]}.png")).subsample(4, 4) for x, i in enumerate(self.characters[0])]

        i = 0
        for y in range(4):
            for x in range(3 - int((y+1) / 4)):
                tankButton = Button(self.tankFrame, image=self.tankPortraitList[i], name=f"tankButton{i}")
                tankButton.place(x=((x * 75) + ((75/2) * int((y+1) / 4))), y=(y * 75))

                tankButton.bind("<Button>", self.mouseButtonCharacters)
                tankButton.bind("<Enter>", self.animationFocus)
                tankButton.bind("<Leave>", self.animationDefocus)

                self.characterButtonsDictionary[self.characters[0][i]] = [tankButton, 0]
                tankButtonList.append(tankButton)
                i += 1

        self.buttonList.append(tankButtonList)

    def dps(self):
        # global self.buttonList, dpsPortraitList

        dpsButtonList = []

        self.dpsPortraitList = [PhotoImage(file=resource_path("res", "portraits", "dps", f"{self.characters[1][x]}.png")).subsample(4, 4) for x, i in enumerate(self.characters[1])]

        i = 0
        for y in range(4):
            for x in range(5 - (int((y+1) / 4) * 3)):
                dpsButton = Button(self.dpsFrame, image=self.dpsPortraitList[i], name=f"dpsButton{i}")
                dpsButton.place(x=((x * 75) + ((75 + (75/2)) * int((y+1) / 4)) + 5), y=(y * 75))

                dpsButton.bind("<Button>", self.mouseButtonCharacters)
                dpsButton.bind("<Enter>", self.animationFocus)
                dpsButton.bind("<Leave>", self.animationDefocus)

                self.characterButtonsDictionary[self.characters[1][i]] = [dpsButton, 1]
                dpsButtonList.append(dpsButton)
                i += 1
        
        self.buttonList.append(dpsButtonList)

    def support(self):
        supportButtonList = []

        self.supportPortraitList = [PhotoImage(file=resource_path("res", "portraits", "support", f"{self.characters[2][x]}.png")).subsample(4, 4) for x, i in enumerate(self.characters[2])]

        i = 0
        for y in range(3):
            for x in range(3 - int((y+1) / 3)):
                supportButton = Button(self.supportFrame, image=self.supportPortraitList[i], name=f"supportButton{i}")
                supportButton.place(x=((x * 75) + ((75/2) * int((y+1) / 3)) + 5), y=(y * 75))
                
                supportButton.bind("<Button>", self.mouseButtonCharacters)
                supportButton.bind("<Enter>", self.animationFocus)
                supportButton.bind("<Leave>", self.animationDefocus)

                self.characterButtonsDictionary[self.characters[2][i]] = [supportButton, 2]
                supportButtonList.append(supportButton)
                
                i += 1

        self.buttonList.append(supportButtonList)


    # Event handlers
    def mouseButtonCharacters(self, event):
        if event.num == 1:
            if event.widget["state"] == NORMAL and not self.extendedLimits and len(self.selectedRoles[self.roleFrameDict[str(event.widget.master)]]) < min(2, (self.roleFrameDict[str(event.widget.master)] + 0.5) * 2) and event.widget not in self.selectedRoles[self.roleFrameDict[str(event.widget.master)]]:
                event.widget.configure(bg="SystemHighlight")
                self.selectedRoles[self.roleFrameDict[str(event.widget.master)]].append(event.widget)
                
                # * [1]
                if len(self.selectedRoles[self.roleFrameDict[str(event.widget.master)]]) == min(2, (self.roleFrameDict[str(event.widget.master)] + 0.5) * 2):
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
            self.selectedRoles = [[], [], []]
            self.updateTeamComp()
            if not self.aiActive:
                for button in self.fullbuttonList:
                    button.configure(bg="SystemButtonFace")
                    button["state"] = NORMAL
        if event.widget == self.aiActiveButton:
            self.aiActive = [True, False][self.aiActive]
            self.aiActiveButton.configure(bg=["SystemButtonFace", "Green"][self.aiActive])
            self.selectedCharacters.clear()
            self.selectedRoles = [[], [], []]
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
                        # print(f"Button: {self.characterButtonsDictionary[i[0][i[0].find(' ') + 1:-1]][0]}", f"Role: {self.characterButtonsDictionary[i[0][i[0].find(' ') + 1:-1]][1]}")
                        # self.selectedRoles[self.characterButtonsDictionary[i[0][i[0].find(' ') + 1:-1]][1]].append(self.characterButtonsDictionary[i[0][i[0].find(' ') + 1:-1]][0])
                        self.selectedCharacters.append(self.characterButtonsDictionary[i[0][i[0].find(' ') + 1:-1]][0])
                    print(f"\"{i[0][i[0].find(' ') + 1:-1]}\"")

                self.updateTeamComp(aiRequest=True)
                # threading.Thread(target=self.updateTeamComp, name="updateTeamComp-Thread").start()

                self.ongoingKeybaordRequest = False

        def startRecognition():
            threading.Thread(target=captureImage, name="captureThread").start()

        def stopListener():
            # print('[§] Stopping listener!')
            # self.hk.stop()
            print("[¤] Debug only!")

        # Set up hotkeys
        self.hk = keyboard.GlobalHotKeys({
                self.config.get("keybinds", "stop"): stopListener,
                self.config.get("keybinds", "capture"): startRecognition})
        
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
            # // self.config = ConfigParser()                                              # Unsure if needed
            self.config.read(self.configPath)

        
        # * Update keybind
        self.config.set("keybinds", action, keybind)


        # * Cleanup
        # Save config
        with open(self.configPath, "w", encoding="utf-8") as configFile:
            self.config.write(configFile)

        # Restart listener
        self.keyListener()


    # Processing
    def updateTeamComp(self, aiRequest=False):
        global counterPortraitList, characterPortraitList
        
        counterPortraitList = []
        characterPortraitList = []
        
        if not self.extendedLimits and not aiRequest:
            for a, role in enumerate(self.selectedRoles):
                for b, character in enumerate(role):
                    characterPortrait = PhotoImage(file=resource_path("res", "portraits", ['tank', 'dps', 'support'][a], f"{self.characters[self.roleFrameDict[str(character.master)]][int(''.join([o for o in list(str(character)) if o.isnumeric()]))]}.png")).subsample(3, 3)
                    self.characterPlaceholderList[(a + b + max(a, 1)) - 1].configure(image=characterPortrait)
                    characterPortraitList.append(characterPortrait)

                    counterLists = []
                    
                    for counterRole in ["Tank", "DPS", "Support"]:
                        counterLists.extend(jsonData.counters[self.characters[self.roleFrameDict[str(character.master)]][int("".join([o for o in list(str(character)) if o.isnumeric()]))]][counterRole].values())
                    
                    for i, counter in enumerate(counterLists):
                        portrait = PhotoImage(file=resource_path("res", "portraits", "all", f"{counter}.png")).subsample(6, 6)
                        self.placeholderMatrix[(a + b + max(a, 1)) - 1][i].configure(image=portrait)
                        counterPortraitList.append(portrait)
        else:
            for c, character in enumerate(self.selectedCharacters):
                characterPortrait = PhotoImage(file=resource_path("res", "portraits", "all", f"{self.characters[self.roleFrameDict[str(character.master)]][int(''.join([o for o in list(str(character)) if o.isnumeric()]))]}.png")).subsample(3, 3)
                self.characterPlaceholderList[c].configure(image=characterPortrait)
                characterPortraitList.append(characterPortrait)

                counterLists = []
                
                for counterRole in ["Tank", "DPS", "Support"]:
                    counterLists.extend(jsonData.counters[self.characters[self.roleFrameDict[str(character.master)]][int("".join([o for o in list(str(character)) if o.isnumeric()]))]][counterRole].values())
                
                for i, counter in enumerate(counterLists):
                    portrait = PhotoImage(file=resource_path("res", "portraits", "all", f"{counter}.png")).subsample(6, 6)
                    self.placeholderMatrix[c][i].configure(image=portrait)
                    counterPortraitList.append(portrait)
        
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
        self.hk.stop()()

        # Create popup window
        popup = self.popup(title="Press new keybind", geometry="420x170")

        # Variables
        status = StringVar(value="Press your new keybind...")
        recorded = {"value": None}
        recorder = {"listener": None}
        
        # * UI elements
        # Labels
        Label(popup, text=f"Action: {action}").pack(pady=(12, 4))
        Label(popup, textvariable=status).pack(pady=(0, 12))

        # Buttons
        confirmButton = Button(popup, text="Confirm", state=DISABLED)
        resetButton = Button(popup, text="Reset")
        cancelButton = Button(popup, text="Cancel")

        confirmButton.pack(side="right", padx=(0, 12), pady=(0, 12))
        resetButton.pack(side="right", padx=6, pady=(0, 12))
        cancelButton.pack(side="right", padx=6, pady=(0, 12))

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
        # No-Op if config is loaded from bundled resource
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
        

if __name__ == "__main__":
    print("[!] This file is not ment to be run!\n\n")
    input("Press \"Enter\" to exit . . .")



