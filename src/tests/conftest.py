import pytest
import nonebot
from nonebot.adapters.onebot.v11 import Adapter


@pytest.fixture(scope="session", autouse=True)
def load_bot():
    # 加载适配器
    driver = nonebot.get_driver()
    driver.register_adapter(Adapter)

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
