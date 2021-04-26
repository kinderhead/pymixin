import sys
sys.path.append("..")
import pymixin # noqa
import textwrap # noqa

pymixin.init()

class test(pymixin.BulkMixin):
    @classmethod
    def test(cls):
        print("hi")

m = test(pymixin.Mixin)

pymixin.Mixin = m.add()
pymixin.Mixin.test()
