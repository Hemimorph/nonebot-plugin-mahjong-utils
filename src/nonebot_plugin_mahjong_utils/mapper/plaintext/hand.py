from typing import TextIO, Iterable, Optional, Sequence

from mahjong_utils.models.tile import Tile
from mahjong_utils.models.furo import Kan, Furo
from mahjong_utils.models.tile_type import TileType

_SUITED_TILE_BASE = {
    TileType.M: 0x1F007,
    TileType.S: 0x1F010,
    TileType.P: 0x1F019,
}
_HONOR_TILES = {
    1: 0x1F000,  # East
    2: 0x1F001,  # South
    3: 0x1F002,  # West
    4: 0x1F003,  # North
    5: 0x1F006,  # White dragon
    6: 0x1F005,  # Green dragon
    7: 0x1F004,  # Red dragon
}
_TILE_BACK = chr(0x1F02B)


def tile_unicode(tile: Tile) -> str:
    """Map a Japanese Mahjong tile to its Unicode Mahjong Tile symbol."""
    if tile.tile_type == TileType.Z:
        return chr(_HONOR_TILES[tile.num])

    # The Unicode Mahjong Tiles block has no separate symbols for red fives.
    return chr(_SUITED_TILE_BASE[tile.tile_type] + tile.real_num - 1)


def tiles_unicode(tiles: Iterable[Tile]) -> str:
    return "".join(map(tile_unicode, tiles))


def furo_unicode(furo: Furo) -> str:
    if isinstance(furo, Kan) and furo.ankan:
        return f"{_TILE_BACK}{tile_unicode(furo.tile) * 2}{_TILE_BACK}"
    return tiles_unicode(furo.tiles)


def map_hand(io: TextIO, tiles: Sequence[Tile], furo: Optional[Sequence[Furo]] = None):
    if len(tiles) % 3 == 2:
        got = tiles[-1]
        tiles = [*sorted(tiles[:-1]), got]
    else:
        tiles = sorted(tiles)

    io.write(tiles_unicode(tiles))
    io.write(" ")

    if furo:
        for fr in furo:
            io.write(furo_unicode(fr))
            io.write(" ")
