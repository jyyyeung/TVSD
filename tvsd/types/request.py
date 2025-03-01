from pydantic import BaseModel

from tvsd.sources.base import Source
from tvsd.types.season import Season


class Request:
    """A download request"""

    season: Season
    source: Source
