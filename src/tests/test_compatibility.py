from importlib.util import find_spec

import pytest
from nonebug import App
from nonebot.message import handle_event
from nonebot.adapters.onebot.v11 import Message

from tests.utils import create_obv11_bot, mock_obv11_message_event


async def run_text_command(app: App, monkeypatch, message: str) -> str:
    from nonebot_plugin_alconna.uniseg import UniMessage
    from nonebot_plugin_mahjong_utils.config import conf
    from nonebot_plugin_mahjong_utils.mapper import last_sent

    conf.mahjong_utils_send_image = False
    last_sent["text"] = None

    async def fake_send(*args, **kwargs):
        return []

    monkeypatch.setattr(UniMessage, "send", fake_send)

    async with app.test_api() as ctx:
        bot = create_obv11_bot(ctx)
        event = mock_obv11_message_event(Message(message))
        await handle_event(bot=bot, event=event)

    return last_sent["text"]


@pytest.mark.asyncio
async def test_pairi_without_arg_returns_help(app: App, monkeypatch):
    from nonebot_plugin_mahjong_utils.matchers.tiles_analyse import PAIRI_HELP_TEXT

    result = await run_text_command(app, monkeypatch, "/牌理")

    assert result == PAIRI_HELP_TEXT


@pytest.mark.asyncio
async def test_invalid_pairi_command_returns_error(app: App, monkeypatch):
    result = await run_text_command(app, monkeypatch, "/牌理 invalid")

    assert result == "请输入正确的牌型"


@pytest.mark.asyncio
async def test_pairi_alias_and_13_tile_state(app: App, monkeypatch):
    result = await run_text_command(app, monkeypatch, "/牌理 1112345678999p")

    assert "听牌" in result
    assert "进张：123456789p" in result


@pytest.mark.asyncio
async def test_14_tile_last_tile_furo_dora_and_chinese_options(app: App, monkeypatch):
    result = await run_text_command(
        app,
        monkeypatch,
        "/牌理 23445633p777s 0990m 立直 一发 dora3 自风东 场风南",
    )

    assert "dora3" in result
    assert "0990m" in result
    assert "立直" in result


@pytest.mark.asyncio
async def test_invalid_tile_input_is_rejected():
    from nonebot_plugin_mahjong_utils.matchers.pairi import handle_msg_for_pairi

    with pytest.raises(ValueError):
        await handle_msg_for_pairi("0z")


def test_detector_is_optional():
    from nonebot_plugin_mahjong_utils.matchers.tiles_img_analyse import (
        MAHJONG_DETECTOR_AVAILABLE,
    )

    assert MAHJONG_DETECTOR_AVAILABLE is (find_spec("mahjong_detector") is not None)


@pytest.mark.skipif(
    find_spec("mahjong_detector") is None,
    reason="mahjong-detector extra is not installed",
)
def test_detector_extra_with_blank_image():
    from PIL import Image
    from mahjong_detector import detect_tiles

    assert detect_tiles(Image.new("RGB", (640, 480), "white")) == []
