from contextlib import asynccontextmanager

import pytest
import nonebot
from nonebot.adapters.onebot.v11 import Adapter


@asynccontextmanager
async def fake_handling_reaction(*args, **kwargs):
    # 避免发送”努力加载中“使单测失败
    yield


@pytest.fixture(scope="session", autouse=True)
def load_bot():
    # 加载适配器
    driver = nonebot.get_driver()
    driver.register_adapter(Adapter)

    # Mock
    nonebot.load_plugin("ssttkkl_nonebot_utils")

    from ssttkkl_nonebot_utils.platform import platform_func

    platform_func.register(
        Adapter.get_name(), "handling_reaction", fake_handling_reaction
    )

    # 加载插件
    nonebot.load_plugin("nonebot_plugin_mahjong_utils")

    from nonebot_plugin_mahjong_utils.config import conf

    conf.mahjong_utils_test = True

    # Access control is an optional runtime implementation. If it happens to be
    # installed in the test environment, keep these tests focused on Mahjong
    # behavior instead of requiring its database migrations.
    try:
        from nonebot_plugin_access_control.service._impl.patcher import (
            ServicePatcherImpl,
        )

        ServicePatcherImpl._matcher_service_mapping.clear()
    except ImportError:
        pass
