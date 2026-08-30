import asyncio
from contextlib import asynccontextmanager, suppress
from functools import wraps

from nonebot import Bot, logger
from nonebot.adapters import Event
from nonebot.exception import ActionFailed, MatcherException
from nonebot.matcher import current_bot, current_event, current_matcher

from ..config import conf
from ..mapper import send_text


class BadRequestError(Exception):
    def __init__(self, message: str = ""):
        super().__init__(message)
        self.message = message


def handle_error(*, silently: bool = False):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except (MatcherException, ActionFailed):
                raise
            except BadRequestError as e:
                if not silently and e.message:
                    await send_text(e.message)
                await current_matcher.get().finish()
            except BaseException as e:
                if not silently:
                    await send_text(f"内部错误：{type(e)}{e}")
                raise

        return wrapper

    return decorator


async def _send_delayed_loading_prompt(bot: Bot, event: Event):
    try:
        await asyncio.sleep(5)
        await bot.send(event=event, message="努力加载中")
    except asyncio.CancelledError:
        raise
    except BaseException:
        logger.exception("发送加载提示失败")


@asynccontextmanager
async def _handling_reaction(bot: Bot, event: Event):
    task = asyncio.create_task(_send_delayed_loading_prompt(bot, event))
    try:
        yield
    finally:
        if not task.done():
            task.cancel()
        with suppress(asyncio.CancelledError):
            await task


def with_handling_reaction():
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if conf.mahjong_utils_test:
                return await func(*args, **kwargs)

            try:
                bot = current_bot.get()
                event = current_event.get()
            except LookupError:
                return await func(*args, **kwargs)

            async with _handling_reaction(bot, event):
                return await func(*args, **kwargs)

        return wrapper

    return decorator
