import pydantic

from prana_rc.entity import Speed, Mode


class SetStateDTO(pydantic.BaseModel):
    speed: Speed = None
    mode: Mode = None
    winter_mode: bool = None
    heating: bool = None
