import inspect
import textwrap

from .mixin import Mixin, MixinLocation
from .logging import log

def patch():
    log("Patching python instance")

    @Mixin.inject(inspect, "getsource", MixinLocation())
    def getsource_patch():
        if hasattr(object, "_mixin_cache"):
            #print("Mixin source")
            return getattr(object, "_mixin_cache")

class Patcher:
    def __init__(self, module):
        """Create a pickle-able mixin patch.

        Parameters
        ----------
        module : string
            The import statment for the module. eg. `import pickle`
        """
        self.module = module
        self.patches = []
    
    def add_inject(self, name, loc=MixinLocation()):
        """Decorator for injection patches.

        Parameters
        ----------
        name : str
            Path to method to inject into.
        loc : MixinLocation, optional
            Location to inject, by default MixinLocation().
        """
        def wrapper(function):
            self.patches.append({"name": name, "function": inspect.getsource(function), "loc": loc, "type": "inject"})
        return wrapper
    
    def add_override(self, name):
        """Decorator for override patches.

        Parameters
        ----------
        name : str
            Path to method to override.
        """
        def wrapper(function):
            self.patches.append({"name": name, "function": inspect.getsource(function), "loc": None, "type": "override"})
        return wrapper
    
    def add_new(self, name):
        """Decorator for new function patches.

        Parameters
        ----------
        name : str
            Path to method to add.
        """
        def wrapper(function):
            self.patches.append({"name": name, "function": inspect.getsource(function), "loc": None, "type": "add"})
        return wrapper
    
    def patch(self):
        """Patch module using patches.
        """
        for i in self.patches:
            l = {}
            lines = self.recursive_dedent(i["function"]).split("\n")
            if lines[0][0] == "@":
                lines = lines[1:]
            #print("\n".join(lines))
            exec("\n".join(lines), {}, l)
            mixin_func = l[list(l.keys())[0]]
            setattr(mixin_func, "_mixin_cache", i["function"])
            if i["type"] == "inject":
                print(self.get_cls(i["name"]))
                Mixin.inject(self.get_cls(i["name"]), self.get_name(i["name"]), i["loc"])(mixin_func)
    
    def recursive_dedent(self, txt):
        if txt == textwrap.dedent(txt):
            return txt
        return self.recursive_dedent(textwrap.dedent(txt))
    
    def execute_module(self):
        l = {}
        exec(self.module, {}, l)
        return l[list(l.keys())[0]]
    
    def get_cls(self, name):
        path = name.split(".")[:-1]
        cls = self.execute_module()
        for i in path:
            cls = getattr(cls, i)
        return cls
    
    def get_name(self, name):
        return name.split(".")[-1]
