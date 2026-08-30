import pytest
from nonebug import App
from nonebot.message import handle_event
from nonebot.adapters.onebot.v11 import Message

from tests.utils import create_obv11_bot, mock_obv11_message_event


async def do_test_text_result(app: App, monkeypatch, message: str, expect: str):
    from nonebot_plugin_alconna.uniseg import UniMessage

    from nonebot_plugin_mahjong_utils.config import conf

    conf.mahjong_utils_send_image = False

    async def fake_send(*args, **kwargs):
        return []

    monkeypatch.setattr(UniMessage, "send", fake_send)

    async with app.test_api() as ctx:
        from nonebot_plugin_mahjong_utils.mapper import last_sent

        bot = create_obv11_bot(ctx)
        event = mock_obv11_message_event(Message(message))
        await handle_event(bot=bot, event=event)
    assert last_sent["text"] == expect


def test_unicode_tile_mapping():
    from mahjong_utils.models.furo import Furo
    from mahjong_utils.models.tile import parse_tiles

    from nonebot_plugin_mahjong_utils.mapper.plaintext.hand import (
        furo_unicode,
        tiles_unicode,
    )

    all_tiles = tiles_unicode(parse_tiles("123456789m123456789p123456789s1234567z"))
    assert all_tiles == ("🀇🀈🀉🀊🀋🀌🀍🀎🀏" "🀙🀚🀛🀜🀝🀞🀟🀠🀡" "🀐🀑🀒🀓🀔🀕🀖🀗🀘" "🀀🀁🀂🀃🀆🀅🀄")
    assert all(0x1F000 <= ord(symbol) <= 0x1F02B for symbol in all_tiles)
    assert tiles_unicode(parse_tiles("0m0p0s")) == "🀋🀝🀔"
    assert furo_unicode(Furo.parse("0990m")) == "🀫🀏🀏🀫"


@pytest.mark.asyncio
async def test_hora_text(app: App, monkeypatch):
    await do_test_text_result(
        app,
        monkeypatch,
        "11123456789999s 天和 自风东 场风东 dora1234",
        "手牌拆解：\n"
        "  雀头：🀐🀐\n"
        "  面子：🀐🀑🀒 🀓🀔🀕 🀖🀗🀘 🀘🀘🀘\n"
        "\n"
        "自摸时：\n"
        "  役种：天和 纯正九莲宝灯\n"
        "  番数：3倍役满\n"
        "  符数：30\n"
        "  亲家和牌：子家48000点（3倍役满，共144000点）\n"
        "  子家和牌：子家24000点，亲家48000点（3倍役满，共96000点）\n",
    )


@pytest.mark.asyncio
async def test_shanten_with_got_text(app: App, monkeypatch):
    await do_test_text_result(
        app,
        monkeypatch,
        "234567s12334p",
        "听牌：\n[打🀛]  进张：🀙🀜 (6张)\n好型改良：🀐（打🀙/🀜，听9张）\n🀑（打🀙/🀜，听9张）\n🀓（打🀙/🀜，听9张）\n🀔（打🀙/🀜，听9张）\n🀖（打🀙/🀜，听9张）\n🀗（打🀙/🀜，听9张）\n[打🀜]  进张：🀛 (2张)\n好型改良：🀙（打🀛，听5张）\n🀜（打🀛，听5张）\n🀐（打🀛，听9张）\n🀑（打🀛，听9张）\n🀓（打🀛，听9张）\n🀔（打🀛，听9张）\n🀖（打🀛，听9张）\n🀗（打🀛，听9张）\n[打🀙]  进张：🀛 (2张)\n好型改良：🀙（打🀛，听5张）\n🀚（打🀛，听6张）\n🀜（打🀛，听5张）\n🀝（打🀚/🀛，听6张）\n🀐（打🀛，听9张）\n🀑（打🀛，听9张）\n🀓（打🀛，听9张）\n🀔（打🀛，听9张）\n🀖（打🀛，听9张）\n🀗（打🀛，听9张）\n\n1向听（退向）：\n[打🀑]  进张：🀙🀚🀛🀜🀝🀑🀒🀓🀔🀕🀖🀗 (37张，好型37张)\n[打🀖]  进张：🀙🀚🀛🀜🀝🀐🀑🀒🀓🀔🀕🀖 (37张，好型37张)\n[打🀓]  进张：🀙🀚🀛🀜🀝🀐🀑🀒🀓 (28张，好型21张)\n[打🀔]  进张：🀙🀚🀛🀜🀝🀔🀕🀖🀗 (28张，好型21张)\n[打🀒]  进张：🀙🀚🀛🀜🀝🀑🀒🀓🀖 (27张，好型19张)\n[打🀕]  进张：🀙🀚🀛🀜🀝🀑🀔🀕🀖 (27张，好型19张)\n[打🀚]  进张：🀙🀚🀛🀜🀝🀞 (19张，好型12张)\n\n",
    )


@pytest.mark.asyncio
async def test_shanten_without_got_text(app: App, monkeypatch):
    await do_test_text_result(
        app,
        monkeypatch,
        "234567s1234p",
        "听牌：\n进张：🀙🀜 (6张)\n好型改良：🀐（打🀙/🀜，听9张）\n🀑（打🀙/🀜，听9张）\n🀓（打🀙/🀜，听9张）\n🀔（打🀙/🀜，听9张）\n🀖（打🀙/🀜，听9张）\n🀗（打🀙/🀜，听9张）",
    )


@pytest.mark.asyncio
async def test_han_hu_text(app: App, monkeypatch):
    await do_test_text_result(
        app,
        monkeypatch,
        "3番40符",
        "3番40符\n亲家和牌时：\n荣和：7700点\n自摸：子家2600点（共7800点）\n\n子家和牌时：\n荣和：5200点\n自摸：子家1300点，亲家2600点（共5200点）",
    )
