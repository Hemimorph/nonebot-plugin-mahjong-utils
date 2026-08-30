from typing import List, TextIO

from mahjong_utils.models.furo import Furo
from mahjong_utils.models.tile import Tile
from mahjong_utils.hora import Hora, RegularHoraHandPattern

from .point_by_han_hu import get_ron_text, get_tsumo_text
from .general import num_mapping, yaku_mapping
from .hand import furo_unicode, tile_unicode, tiles_unicode


def map_yakuman_text(io: TextIO, yakuman: int):
    io.write(f"{num_mapping[yakuman]}倍役满")


def map_regular_hora_hand_pattern(io: TextIO, pattern: RegularHoraHandPattern):
    io.write("手牌拆解：\n")
    io.write(f"  雀头：{tile_unicode(pattern.jyantou) * 2}\n")
    if pattern.menzen_mentsu:
        io.write(
            f"  面子：{' '.join(tiles_unicode(x.tiles) for x in sorted(pattern.menzen_mentsu, key=str))}\n"
        )
    if pattern.furo:
        io.write(
            f"  副露：{' '.join(furo_unicode(x) for x in sorted(pattern.furo, key=str))}\n"
        )


def map_han_hu(io: TextIO, hora: Hora):
    if hora.has_yakuman:
        io.write(f"  番数：{sum(x.han for x in hora.yaku) // 13}倍役满\n")
    else:
        io.write(f"  番数：{hora.han}番\n")
    io.write(f"  符数：{hora.hu}\n")


def map_hora(
    io: TextIO,
    hora_ron: Hora,
    hora_tsumo: Hora,
    tiles: List[Tile],
    furo: List[Furo],
    *,
    allow_ron: bool = True,
    allow_tsumo: bool = True,
):
    hora = hora_ron
    show_ron = allow_ron and hora_ron.han > 0
    show_tsumo = allow_tsumo and hora_tsumo.han > 0

    if isinstance(hora.pattern, RegularHoraHandPattern):
        map_regular_hora_hand_pattern(io, hora.pattern)

    if show_tsumo:
        io.write("\n自摸时：\n")
        io.write(
            f"  役种：{' '.join(sorted(yaku_mapping[x] for x in hora_tsumo.yaku))}\n"
        )
        map_han_hu(io, hora_tsumo)
        io.write(
            f"  亲家和牌：{get_tsumo_text(0, hora_tsumo.parent_point.tsumo, True)}\n"
        )
        io.write(
            f"  子家和牌：{get_tsumo_text(hora_tsumo.child_point.tsumo_parent, hora_tsumo.child_point.tsumo_child, False)}\n"
        )

    if show_ron:
        io.write("\n荣和时：\n")
        io.write(
            f"  役种：{' '.join(sorted(yaku_mapping[x] for x in hora_ron.yaku))}\n"
        )
        map_han_hu(io, hora_ron)
        io.write(f"  亲家和牌：{get_ron_text(hora_ron.parent_point.ron, True)}\n")
        io.write(f"  子家和牌：{get_ron_text(hora_ron.child_point.ron, False)}\n")

    if not show_tsumo and not show_ron:
        io.write("\n和牌，但是无役\n")
