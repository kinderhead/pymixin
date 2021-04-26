import functools
import inspect
import textwrap

from .exceptions import MixinError
from .logging import log

class MixinLocation:
    def __init__(self):
        self.line = 0
    
    def beginning(self):
        self.line = 0

    def end(self):
        self.line = -1

class Mixin:
    def __init__(self, type, func, cls, name, loc=MixinLocation()):
        functools.update_wrapper(self, func)
        self._func = func
        self._cls = cls
        self._name = name
        self._loc = loc
        if type == "inject":
            self._inject()
        elif type == "override":
            self._override()
    
    @staticmethod
    def override(cls, name):
        """Override decorator

        Parameters
        ----------
        cls : object
            The object to override code in.
        name : str
            Name of function to override.

        Returns
        -------
        function
            The finished function.
        """

        def wrapper(func):
            return Mixin("override", func, cls, name)
        return wrapper
    
    @staticmethod
    def inject(cls, name, loc=MixinLocation()):
        """Injection decorator

        Parameters
        ----------
        cls : object
            The object to inject code into.
        name : str
            Name of the method to inject code into.
        loc : MixinLocation, optional
            Location in the method to inject code. Defaults to beginning.
        
        Returns
        -------
        function
            The finished function.
        """

        def wrapper(func):
            return Mixin("inject", func, cls, name, loc)
        return wrapper
    
    @staticmethod
    def non_invasive(cls, name):
        """Non invasive override decorator
        Doesn't go into the source code to apply mixins
        Does not require a pre-patched environment

        Parameters
        ----------
        cls : object
            The object with the method to override.
        name : str
            Name of the method to override.
        
        Returns
        -------
        function
            The finished function.
        """
        def wrapper(func):
            setattr(cls, name, func)
        return wrapper
    
    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)
    
    def _getsource(self, cls, name):
        source = textwrap.dedent(inspect.getsource(getattr(cls, name)))
        lines = source.split("\n")
        return lines
    
    def _parse_func(self, func, keep_func=False):
        newcode = textwrap.indent(inspect.getsource(func), "    ").split("\n")
        if not keep_func:
            if newcode[0].strip(" ")[0] == "@":
                newcode = newcode[2:]
            else:
                newcode = newcode[1:]
            newcode.insert(0, "    try:\n")
            newcode.append("    except Exception as e:\n        raise _MixinError() from e")
        else:
            if newcode[0].strip(" ")[0] == "@":
                newcode = newcode[1:]
            
            newcode[0] = textwrap.dedent(newcode[0])
            newcode.insert(1, "    try:\n")
            newcode.append("    except Exception as e:\n        raise _MixinError() from e")
        return newcode

    def _finish(self, cls, name, lines, funcname=None):
        l = {}
        g = getattr(cls, name).__globals__
        g["_MixinError"] = MixinError
        #print("\n".join(lines))
        exec("\n".join(lines), getattr(cls, name).__globals__, l)
        if funcname is None:
            setattr(cls, name, l[name])
        else:
            old_name = getattr(getattr(cls, name), "__name__")
            setattr(cls, name, l[funcname])
            setattr(getattr(cls, name), "__name__", old_name)
        setattr(getattr(cls, name), "_mixin_cache", "\n".join(lines))
    
    def _inject(self):
        log(f"Injecting code into {self._cls.__name__}.{self._name}")
        lines = self._getsource(self._cls, self._name)
        newcode = self._parse_func(self._func)

        lines.insert(self._loc.line + 1, "\n".join(newcode))

        self._finish(self._cls, self._name, lines)
    
    def _override(self):
        log(f"Overriding function {self._cls.__name__}.{self._name}")
        newcode = self._parse_func(self._func, True)
        self._finish(self._cls, self._name, newcode, self._func.__name__)
#x = inspect.getsource
#test().f()
