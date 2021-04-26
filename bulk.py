from .logging import log
from .mixin import Mixin, MixinLocation

class BulkMixin(Mixin):
    def __init__(self, cls):
        self.cls = cls
        self.bulk_data = {}
        for i in dir(self):
            if "inject_" in i:
                self.inject(getattr(self, i))
            elif "override_" in i:
                self.override(getattr(self, i))
            else:
                self.non_invasive(getattr(self, i), i)
    
    def inject(self, func, loc=MixinLocation()):
        return super().inject(self.cls, func.__name__.split("inject_")[-1], loc)(func)
    
    def override(self, func):
        return super().override(self.cls, func.__name__.split("override_")[-1])(func)
    
    def non_invasive(self, func, name):
        if name[0] == "_":
            return
        elif name in ["inject", "override", "non_invasive", "add"]:
            return
        elif not isinstance(func, type(self.non_invasive)):
            return
        
        self.bulk_data[name] = func

    def add(self):
        if self.bulk_data != {}:
            return self.cls.__class__(self.cls.__name__, (self.__class__, self.cls), {})
