

class __Portraits:
    """
    A proxy object to lazily load the portraits only when they are needed and ready. 
    """
    _real = None
    
    def __getattr__(self, name):
        return getattr(self._real, name)


portraits = __Portraits()


def createPhotoImages():
    if __Portraits._real is not None:
        return

    try:                                    import _portraits
    except ImportError: from src.resources  import _portraits

    __Portraits._real = _portraits

