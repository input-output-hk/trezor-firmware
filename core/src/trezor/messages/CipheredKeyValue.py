# Automatically generated by pb2py
# fmt: off
import protobuf as p

if __debug__:
    try:
        from typing import Dict, List  # noqa: F401
        from typing_extensions import Literal  # noqa: F401
    except ImportError:
        pass


class CipheredKeyValue(p.MessageType):
    MESSAGE_WIRE_TYPE = 48

    def __init__(
        self,
        *,
        value: bytes = None,
    ) -> None:
        self.value = value

    @classmethod
    def get_fields(cls) -> Dict:
        return {
            1: ('value', p.BytesType, None),
        }
