import sys
sys.path.append("..")
import pymixin # noqa
import textwrap # noqa

pymixin.init(True)

class test():
    def test_func(self):
        print("hi")

@pymixin.Mixin.override(test, "test_func")
def mixin(self):
    print("before")
    _mixin_overridden_func(self)
    print("after")

obj = test()
obj.test_func()
