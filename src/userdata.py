import dataclasses
from canvasapi import Canvas

@dataclasses.dataclass
class UserData():
    api_key: str
    base_url: str

    def make_canvas(self) -> Canvas:
        return Canvas(self.base_url, self.api_key)