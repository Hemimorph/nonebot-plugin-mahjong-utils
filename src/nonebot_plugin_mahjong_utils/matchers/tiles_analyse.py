import re

from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot_plugin_alconna import (
    Args,
    Image,
    Match,
    Alconna,
    MultiVar,
    CommandMeta,
    AlconnaMatch,
    on_alconna,
    image_fetch,
)

from ..config import conf
from ..mapper import send_text
from ..ac import command_service
from .tiles_img_analyse import handle_image_for_pairi
from .pairi import pairi_pattern, handle_msg_for_pairi
from .furo_pairi import furo_pairi_pattern, handle_msg_for_furo_pairi
from ..utils.interceptors import BadRequestError, handle_error, with_handling_reaction

PAIRI_HELP_TEXT = """使用 /牌理 手牌 可以查询日麻牌理和和牌点数。万、筒、索分别用 m、p、s 表示，字牌用 z 表示，例如 123m456p789s；字牌 1z～7z 依次为东、南、西、北、白、发、中，赤五写成 0m、0p、0s。

有副露时，将副露用空格写在手牌后面，例如 123p66z 234m 111z。三张顺子表示吃，三张相同表示碰，四张相同表示明杠；暗杠使用 0XX0，例如 0990p 表示暗杠九筒。

和牌时请把和牌张放在手牌最后一张。还可以在后面继续填写自风、场风和宝牌数量，例如 自风南、场风东、dora3。dora3 表示这副牌实际有 3 枚普通宝牌、杠宝牌或里宝牌，不是宝牌指示牌的数量；赤宝牌仍直接用 0m、0p、0s 表示。

一些无法从最终牌型判断的役需要手动注明，包括 立直、一发、两立直、岭上、枪杠、海底、河底、天和、地和。例如：/牌理 123m456m789m11122z 自风东 场风东 立直 一发 dora2。天和可以直接在最后加 天和，地和同理。其他能够从牌型本身判断的役不需要手动填写。

输入未摸牌状态时，Bot 会计算向听数和进张；输入摸牌后的状态时，会分析切牌；如果已经和牌，则会计算役、番、符和点数。"""

if conf.mahjong_utils_command_mode:
    tiles_analyse_command_matcher = on_alconna(
        Alconna(
            "日麻手牌分析",
            Args["inputs", MultiVar(Image | str, "*")],
            meta=CommandMeta(
                description="分析日麻手牌、进张、和牌点数或麻将牌截图",
                usage="/日麻手牌分析 <手牌代码> [...附加选项]",
                example="/牌理 23445633p777s 0990m 立直 一发 dora3",
            ),
        ),
        aliases={"牌理"},
        use_cmd_start=True,
        priority=10,
        block=True,
    )
    command_service.patch_matcher(tiles_analyse_command_matcher)

    @tiles_analyse_command_matcher.handle()
    @handle_error()
    @with_handling_reaction()
    async def handle(
        event: Event,
        bot: Bot,
        state: T_State,
        inputs: Match[tuple[Image | str, ...]] = AlconnaMatch("inputs"),
    ):
        parts = inputs.result
        images = [part for part in parts if isinstance(part, Image)]
        if images:
            if len(images) != 1 or len(parts) != 1:
                raise BadRequestError("图片牌理仅支持输入一张图片")
            await handle_image_for_pairi(
                await image_fetch(event, bot, state, images[0])
            )
            return

        cmd_body = " ".join(parts).strip()

        if not cmd_body:
            await send_text(PAIRI_HELP_TEXT)
            return

        furo_pairi_match = re.match(furo_pairi_pattern, cmd_body)
        if furo_pairi_match is not None:
            await handle_msg_for_furo_pairi(cmd_body)
            return

        pairi_match = re.match(pairi_pattern, cmd_body)
        if pairi_match is not None:
            await handle_msg_for_pairi(cmd_body)
            return

        raise BadRequestError("请输入正确的牌型")
