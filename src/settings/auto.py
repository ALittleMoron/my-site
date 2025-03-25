import sys

from settings.config import config

sys.path.insert(0, config.dir.src_path.as_posix())

from settings.base import *  # noqa
from settings.sub_storages import *  # noqa
from settings.sub_martor import *  # noqa
from settings.sub_unfold import *  # noqa
from settings.sub_anydi import *  # noqa
