from tkinter import Button, Label


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


class CounterLabel(Label):
    def __init__(self, master, **kwargs):
        # Inherit from Label class
        super().__init__(master, **kwargs)

        # * State
        self.__counterId: str = None
        self.__counterData: str = None

    # * Getters
    @property
    def counterId(self): return self.__counterId
    @property
    def counterData(self): return self.__counterData

    # * Setters
    @counterId.setter
    def counterId(self, id: str): self.__counterId = id
    @counterData.setter
    def counterData(self, data: str): self.__counterData = data