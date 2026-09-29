from ._transform_patch import apply as _apply_transform_patch

# Widens the transformer's scalar fast path to cover unions of scalars, which is
# what protobuf int64 arrays (token ids) become. Inert once upstream covers it.
# See _transform_patch for the measurement and why it cannot live in _utils.
_apply_transform_patch()

from .types import (
    DownloadError,
    FileTypeError,
)
from .utils import (
    check_file,
)
from .resources import (
    UploadManager,
    DownloadManager,
    AsyncUploadManager,
    AsyncDownloadManager,
)

__all__ = [
    "DownloadManager",
    "AsyncDownloadManager",
    "AsyncUploadManager",
    "UploadManager",
    "DownloadError",
    "FileTypeError",
    "check_file",
]
