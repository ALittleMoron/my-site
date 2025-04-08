import os
import sys

from settings.config import config

sys.path.insert(0, config.dir.src_path.as_posix())

from settings.base import *  # noqa
from settings.sub_storages import *  # noqa
from settings.sub_martor import *  # noqa
from settings.sub_unfold import *  # noqa
from settings.sub_anydi import *  # noqa

if DEBUG:  # noqa: F405
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405
