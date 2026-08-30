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

    assert result.startswith("听牌：")
    assert "听牌" in result
    assert "进张：🀙🀚🀛🀜🀝🀞🀟🀠🀡" in result


@pytest.mark.asyncio
async def test_14_tile_last_tile_furo_dora_and_chinese_options(app: App, monkeypatch):
    result = await run_text_command(
        app,
        monkeypatch,
        "/牌理 23445633p777s 0990m 立直 一发 dora3 自风东 场风南",
    )

    assert result.startswith("手牌拆解：")
    assert "🀫🀏🀏🀫" in result
    assert "立直" in result


@pytest.mark.asyncio
async def test_hora_only_outputs_available_win_method(app: App, monkeypatch):
    both_yaku_result = await run_text_command(
        app, monkeypatch, "/牌理 11123456789999s"
    )
    assert "自摸时：" in both_yaku_result
    assert "荣和时：" in both_yaku_result

    no_yaku_result = await run_text_command(
        app, monkeypatch, "/牌理 123456m789p22p 789s"
    )
    assert no_yaku_result.startswith("手牌拆解：")
    assert no_yaku_result.endswith("\n和牌，但是无役\n")
    assert "自摸时：" not in no_yaku_result
    assert "荣和时：" not in no_yaku_result
    assert "点" not in no_yaku_result

    natural_tsumo_result = await run_text_command(
        app, monkeypatch, "/牌理 123456m789p456s22p"
    )
    assert "自摸时：" in natural_tsumo_result
    assert "荣和时：" not in natural_tsumo_result

    tsumo_result = await run_text_command(
        app, monkeypatch, "/牌理 11123456789999s 天和"
    )
    assert "自摸时：" in tsumo_result
    assert "荣和时：" not in tsumo_result

    ron_result = await run_text_command(
        app, monkeypatch, "/牌理 11123456789999s 河底"
    )
    assert "荣和时：" in ron_result
    assert "自摸时：" not in ron_result


@pytest.mark.asyncio
async def test_furo_chance_uses_unicode_tiles(app: App, monkeypatch):
    result = await run_text_command(app, monkeypatch, "/牌理 335678m3457p<7m")

    assert result.startswith("上家打🀍\n\n")
    assert "吃打" in result
    assert "7m" not in result


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
