import warnings

try:
    from .closeio import CloseIO, CloseIOError  # noqa
except ImportError:
    pass

warnings.warn('Important: faster_closeio is no longer maintained. Please use the official close.io library instead: https://pypi.org/project/closeio/', DeprecationWarning)
