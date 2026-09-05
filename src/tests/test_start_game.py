import pytest


def test_roll_dice_generates_two_independent_dice(monkeypatch):
    from nonebot_plugin_mahjong_utils.matchers import start_game

    values = iter((0, 5))

    def fake_randbelow(upper_bound):
        assert upper_bound == 6
        return next(values)

    monkeypatch.setattr(start_game, "randbelow", fake_randbelow)

    assert start_game.roll_dice() == (1, 6)


@pytest.mark.parametrize(
    ("total", "player"),
    [
        (2, "南家（庄家下家）"),
        (3, "西家（庄家对家）"),
        (4, "北家（庄家上家）"),
        (5, "东家（庄家自己）"),
        (6, "南家（庄家下家）"),
        (7, "西家（庄家对家）"),
        (8, "北家（庄家上家）"),
        (9, "东家（庄家自己）"),
        (10, "南家（庄家下家）"),
        (11, "西家（庄家对家）"),
        (12, "北家（庄家上家）"),
    ],
)
def test_get_opening_player_4p(total: int, player: str):
    from nonebot_plugin_mahjong_utils.matchers.start_game import get_opening_player_4p

    assert get_opening_player_4p(total) == player


@pytest.mark.parametrize(
    ("total", "player"),
    [
        (2, "南家（庄家下家）"),
        (3, "西家（庄家上家）"),
        (4, "东家（庄家自己）"),
        (5, "南家（庄家下家）"),
        (6, "西家（庄家上家）"),
        (7, "东家（庄家自己）"),
        (8, "南家（庄家下家）"),
        (9, "西家（庄家上家）"),
        (10, "东家（庄家自己）"),
        (11, "南家（庄家下家）"),
        (12, "西家（庄家上家）"),
    ],
)
def test_get_opening_player_3p(total: int, player: str):
    from nonebot_plugin_mahjong_utils.matchers.start_game import get_opening_player_3p

    assert get_opening_player_3p(total) == player


@pytest.mark.parametrize(
    ("text", "mode"),
    [
        ("", "yonma"),
        ("四麻", "yonma"),
        ("4", "yonma"),
        ("三麻", "sanma"),
        ("3", "sanma"),
        ("雀魂三麻", "sanma"),
    ],
)
def test_parse_game_mode(text: str, mode: str):
    from nonebot_plugin_mahjong_utils.matchers.start_game import parse_game_mode

    assert parse_game_mode(text) == mode


def test_parse_game_mode_rejects_invalid_text():
    from nonebot_plugin_mahjong_utils.utils.interceptors import BadRequestError
    from nonebot_plugin_mahjong_utils.matchers.start_game import parse_game_mode

    with pytest.raises(BadRequestError, match="请输入“四麻”或“三麻”"):
        parse_game_mode("美式麻将")


def test_format_yonma_instruction():
    from nonebot_plugin_mahjong_utils.matchers.start_game import (
        format_yonma_instruction,
    )

    result = format_yonma_instruction(3, 4)

    assert "🎲 3 + 4 = 7" in result
    assert "西家" in result
    assert "右端" in result
    assert "留在断口右侧" in result
    assert "7 墩" in result
    assert "第 3 墩" in result
    assert "14 张" in result
    assert "宝牌指示牌" in result


def test_format_sanma_instruction():
    from nonebot_plugin_mahjong_utils.matchers.start_game import (
        format_sanma_instruction,
    )

    result = format_sanma_instruction(3, 4)

    assert "🎲 3 + 4 = 7" in result
    assert "东家" in result
    assert "右端" in result
    assert "留在断口右侧" in result
    assert "7 墩" in result
    assert "第 5 墩" in result
    assert "北拔" in result
    assert "14 张" in result
    assert "北拔只补牌，不翻杠宝牌" in result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("command", "expected_mode_text"),
    [
        ("/开局", "四麻：开西家"),
        ("/开局 四麻", "四麻：开西家"),
        ("/开局 三麻", "雀魂式三麻：开东家"),
    ],
)
async def test_start_game_command(monkeypatch, command, expected_mode_text):
    from nonebot_plugin_mahjong_utils.matchers import start_game

    class CommandBody:
        def extract_plain_text(self):
            return command.removeprefix("/开局").strip()

    sent = []

    async def fake_send_text(text):
        sent.append(text)

    monkeypatch.setattr(start_game, "roll_dice", lambda: (3, 4))
    monkeypatch.setattr(start_game, "send_text", fake_send_text)

    await start_game.handle(CommandBody())

    assert "🎲 3 + 4 = 7" in sent[0]
    assert expected_mode_text in sent[0]
