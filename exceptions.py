class MixinError(Exception):
    def __init__(self):
        self.message = "An exception has occured in a mixin"
        super().__init__(self.message)
