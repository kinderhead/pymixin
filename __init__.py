import logging
from .mixin import Mixin, MixinLocation
from .logging import log
from .patch import patch
from .bulk import BulkMixin

def init(verbose=False):
    logging.islogging = verbose
    log("Initializing mixins")
    patch()
    log("Done")
