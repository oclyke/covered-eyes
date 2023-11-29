import time
import pysicgl
from semver import SemanticVersion
from .timewarp import TimeWarp
from .audio.manager import AudioManager
from .globals import GlobalsManager
from .artnet import ArtnetProvider
from .layer import Layer


class TimeBase:
    def seconds(self):
        return time.time()


timebase = TimeBase()
