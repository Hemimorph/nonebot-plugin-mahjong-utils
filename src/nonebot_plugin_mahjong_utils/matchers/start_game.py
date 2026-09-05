from typing import Literal
from secrets import randbelow

from nonebot import on_command
from nonebot.params import CommandArg

from ..config import conf
from ..mapper import send_text
from ..ac import command_service
from ..utils.interceptors import BadRequestError, handle_error

GameMode = Literal["yonma", "sanma"]

YONMA_PLAYERS = (
    "东家（庄家自己）",
    "南家（庄家下家）",
    "西家（庄家对家）",
    "北家（庄家上家）",
)
SANMA_PLAYERS = (
    "东家（庄家自己）",
    "南家（庄家下家）",
    "西家（庄家上家）",
)

INVALID_MODE_MESSAGE = "请输入“四麻”或“三麻”，例如：\n/开局\n/开局 三麻"


def roll_dice() -> tuple[int, int]:
    """分别掷两枚六面骰子。"""
    return randbelow(6) + 1, randbelow(6) + 1


def get_opening_player_4p(total: int) -> str:
    """按东、南、西、北的顺序计算四麻开门家。"""
    return YONMA_PLAYERS[(total - 1) % len(YONMA_PLAYERS)]


def get_opening_player_3p(total: int) -> str:
    """按东、南、西的顺序计算雀魂三麻开门家。"""
    return SANMA_PLAYERS[(total - 1) % len(SANMA_PLAYERS)]


def parse_game_mode(text: str) -> GameMode:
    text = text.strip()
    if text in {"", "四麻", "4"}:
        return "yonma"
    if text in {"三麻", "3", "雀魂三麻"}:
        return "sanma"
    raise BadRequestError(INVALID_MODE_MESSAGE)


def format_yonma_instruction(d1: int, d2: int) -> str:
    total = d1 + d2
    player = get_opening_player_4p(total)

    return (
        f"🎲 {d1} + {d2} = {total}\n\n"
        f"四麻：开{player}的牌山。\n\n"
        f"请{player}从自己视角的牌山右端开始数 {total} 墩，"
        f"数出 {total} 墩后断开。\n"
        f"把这 {total} 墩留在断口右侧，从断口左侧紧邻的一墩开始配牌。\n\n"
        "按 东 → 南 → 西 → 北 的顺序，每人每次取 2 墩（4 张），共进行 3 轮。"
        "随后庄家跳牌取得上层相隔一墩的两张牌，南、西、北依次各取 1 张；"
        "最终庄家 14 张，三家闲家各 13 张。\n\n"
        f"断口右侧（刚才数出 {total} 墩的方向）是牌尾，沿此方向保留 7 墩（14 张）作为王牌；"
        "靠断口的前 2 墩（4 张）是岭上牌。\n"
        "从开门断口一侧向王牌内部数第 3 墩，翻开上层牌作为初始宝牌指示牌；"
        "该墩下层是初始里宝牌指示牌。"
    )


def format_sanma_instruction(d1: int, d2: int) -> str:
    total = d1 + d2
    player = get_opening_player_3p(total)

    return (
        f"🎲 {d1} + {d2} = {total}\n\n"
        f"雀魂式三麻：开{player}的牌山。\n\n"
        f"请{player}从自己视角的牌山右端开始数 {total} 墩，"
        f"数出 {total} 墩后断开。\n"
        f"把这 {total} 墩留在断口右侧，从断口左侧紧邻的一墩开始配牌。\n\n"
        "按 东 → 南 → 西 的顺序，每人每次取 2 墩（4 张），共进行 3 轮。"
        "随后庄家取得 2 张，南家、西家依次各取 1 张；"
        "最终庄家 14 张，两个闲家各 13 张。\n\n"
        f"断口右侧（刚才数出 {total} 墩的方向）是王牌方向。"
        "从开门断口的王牌一侧向内数第 5 墩，翻开上层牌作为初始宝牌指示牌。\n"
        "靠开门断口一侧的前 4 墩用于北拔和开杠时依次补牌。"
        "每次补牌都要让普通牌山少摸 1 张，确保终局仍留下 14 张王牌。\n"
        "北拔只补牌，不翻杠宝牌；只有开杠才追加翻杠宝牌指示牌。"
        "拔出的北按宝牌计算。"
    )


if conf.mahjong_utils_command_mode:
    start_game_matcher = on_command(
        "日麻开局",
        aliases={"开局", "摇骰开局"},
    )
    command_service.patch_matcher(start_game_matcher)

    @start_game_matcher.handle()
    @handle_error()
    async def handle(cmd_body=CommandArg()):
        mode = parse_game_mode(cmd_body.extract_plain_text())
        d1, d2 = roll_dice()
        if mode == "yonma":
            result = format_yonma_instruction(d1, d2)
        else:
            result = format_sanma_instruction(d1, d2)
        await send_text(result)
