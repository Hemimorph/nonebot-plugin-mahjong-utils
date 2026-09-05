import re

from mahjong_utils.point_by_han_hu import (
    get_child_point_by_han_hu,
    get_parent_point_by_han_hu,
)
from nonebot_plugin_alconna import (
    Args,
    Match,
    Alconna,
    MultiVar,
    AlcMatches,
    CommandMeta,
    AlconnaMatch,
    on_alconna,
)

from ..config import conf
from ..mapper import send_point_by_han_hu
from ..ac import command_service, sniffer_service
from ..utils.interceptors import BadRequestError, handle_error

han_hu_pattern = r"^([1-9][0-9]*)番([1-9][0-9]*)符$"


async def handle_msg_for_han_hu(han: int, hu: int):
    try:
        parent_point = get_parent_point_by_han_hu(han, hu)
        child_point = get_child_point_by_han_hu(han, hu)
    except ValueError:
        raise BadRequestError("请输入正确的番符数目")

    await send_point_by_han_hu(han, hu, parent_point, child_point)


if conf.mahjong_utils_sniff_mode:
    han_hu_sniffer_matcher = on_alconna(
        Alconna(
            re.compile(han_hu_pattern),
            meta=CommandMeta(hide=True),
            namespace="nonebot_plugin_mahjong_utils.han_hu_sniffer",
            separators="\0",
        )
    )
    sniffer_service.patch_matcher(han_hu_sniffer_matcher)

    @han_hu_sniffer_matcher.handle()
    @handle_error()
    async def handle(result: AlcMatches):
        matched = result.header_match.result
        await handle_msg_for_han_hu(int(matched.group(1)), int(matched.group(2)))


if conf.mahjong_utils_command_mode:
    han_hu_command_matcher = on_alconna(
        Alconna(
            "日麻番符算点",
            Args["parts", MultiVar(str, "*")],
            meta=CommandMeta(
                description="查询日麻番符点数",
                usage="/日麻番符算点 <x>番<y>符",
                example="/番符 3番40符",
            ),
        ),
        aliases={"番符"},
        use_cmd_start=True,
        block=True,
    )
    command_service.patch_matcher(han_hu_command_matcher)

    @han_hu_command_matcher.handle()
    @handle_error()
    async def handle(
        parts: Match[tuple[str, ...]] = AlconnaMatch("parts"),
    ):
        matched = re.fullmatch(han_hu_pattern, " ".join(parts.result))
        if matched is None:
            raise BadRequestError("请输入正确的番符数目")

        await handle_msg_for_han_hu(int(matched.group(1)), int(matched.group(2)))
