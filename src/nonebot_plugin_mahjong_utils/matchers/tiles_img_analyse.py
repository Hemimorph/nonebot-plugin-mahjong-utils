from io import BytesIO

from nonebot import logger
from mahjong_utils.models.tile import Tile

from nonebot_plugin_mahjong_utils.utils.executor import run_in_my_executor

from .pairi import handle_pairi
from ..utils.interceptors import BadRequestError

try:
    from mahjong_detector import detect_tiles

    MAHJONG_DETECTOR_AVAILABLE = True
except ImportError:
    MAHJONG_DETECTOR_AVAILABLE = False

character_tile_mapping = {
    "tou": "1z",
    "nan": "2z",
    "sha": "3z",
    "pe": "4z",
    "haku": "5z",
    "hatsu": "6z",
    "chun": "7z",
}


async def handle_image_for_pairi(image: bytes | None):
    if not MAHJONG_DETECTOR_AVAILABLE:
        raise BadRequestError("图片牌理需要安装 nonebot-plugin-mahjong-utils[detect]")
    if not image:
        raise BadRequestError("无法获取图片内容")

    tiles = await run_in_my_executor(detect_tiles, BytesIO(image))
    tiles = [character_tile_mapping.get(t, t) for t in tiles]
    tiles = [Tile.by_text(t) for t in tiles]

    logger.debug(f"tiles detect result: {tiles}")

    if not tiles:
        raise BadRequestError("未识别到麻将牌")

    try:
        await handle_pairi(tiles, [])
    except BadRequestError as e:
        raise BadRequestError(f"{e.message}，从图片检测到的手牌为{tiles}") from e
