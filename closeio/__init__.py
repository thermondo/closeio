try:
    from .closeio import CloseIO, CloseIOError  # noqa
except ImportError:
    pass

import warnings
warnings.warn('Important: faster_closeio is no longer maintained. Please use the official close.io library instead: https://pypi.org/project/closeio/', DeprecationWarning)
