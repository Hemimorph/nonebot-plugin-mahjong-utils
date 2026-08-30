from nonebot import get_plugin_config
from pydantic import BaseModel, ConfigDict


class Config(BaseModel):
    model_config = ConfigDict(extra="ignore")

    mahjong_utils_sniff_mode: bool = False
    mahjong_utils_command_mode: bool = True
    mahjong_utils_send_image: bool = False

    mahjong_utils_test: bool = False


conf = get_plugin_config(Config)
