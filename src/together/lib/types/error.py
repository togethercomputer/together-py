from typing import Any

from ... import TogetherError


class DownloadError(TogetherError):
    def __init__(
        self,
        message: str,
        **kwargs: Any,
    ) -> None:
        self.message = message
        super().__init__(**kwargs)


class FileTypeError(TogetherError):
    def __init__(
        self,
        message: str,
        **kwargs: Any,
    ) -> None:
        self.message = message
        super().__init__(**kwargs)
