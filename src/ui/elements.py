from tkinter import Button


class HeroButton(Button):
    def __init__(self, master, heroId: str, **kwargs):
        # Inherit from Button class
        super().__init__(master, name=heroId, **kwargs)

        # * Constants
        self.__HERO_ID = heroId

        # * State
        self.__isInteractable = True


    # * Getters
    @property
    def HERO_ID(self): return self.__HERO_ID
    @property
    def isInteractable(self): return self.__isInteractable

    # * Setters
    def disable(self): self.__isInteractable = False
    def enable(self): self.__isInteractable = True