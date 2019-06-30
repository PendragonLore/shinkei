class Version:
    __slots__ = ("api", "singyeong")

    def __init__(self, data):
        self.api = data["api"]
        self.singyeong = data["singyeong"]
