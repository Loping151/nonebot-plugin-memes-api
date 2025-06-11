from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER, Permission
from nonebot_plugin_alconna import Alconna, Args, on_alconna
from nonebot_plugin_uninfo import Uninfo

from ..manager import MemeMode, meme_manager
from .utils import UserId, find_meme


def _uninfo_role(session: Uninfo) -> bool:
    return session.scene.is_private or bool(
        session.member and session.member.role and session.member.role.level > 1
    )


PERM_EDIT = SUPERUSER | Permission(_uninfo_role)
PERM_GLOBAL = SUPERUSER


block_matcher = on_alconna(
    Alconna("禁用表情", Args["meme_name", str]),
    block=True,
    priority=11,
    use_cmd_start=True,
    permission=PERM_EDIT,
)
unblock_matcher = on_alconna(
    Alconna("启用表情", Args["meme_name", str]),
    block=True,
    priority=11,
    use_cmd_start=True,
    permission=PERM_EDIT,
)
block_gl_matcher = on_alconna(
    Alconna("全局禁用表情", Args["meme_name", str]),
    block=True,
    priority=11,
    use_cmd_start=True,
    permission=PERM_GLOBAL,
)
unblock_gl_matcher = on_alconna(
    Alconna("全局启用表情", Args["meme_name", str]),
    block=True,
    priority=11,
    use_cmd_start=True,
    permission=PERM_GLOBAL,
)
black_list_matcher = on_alconna(
    Alconna("黑名单"),
    aliases= ["禁用列表", "黑名单列表"],
    block=True,
    priority=11,
    use_cmd_start=True,
    permission=PERM_GLOBAL,
)

@block_matcher.handle()
async def _(matcher: Matcher, user_id: UserId, meme_name: str):
    meme = await find_meme(matcher, meme_name)
    if meme_manager.block(user_id, meme.key):
        await matcher.finish(f"表情 {meme.key} 禁用成功")
    else:
        await matcher.finish(f"表情 {meme.key} 已被主人禁用或已在黑名单中")

@unblock_matcher.handle()
async def _(matcher: Matcher, user_id: UserId, meme_name: str):
    meme = await find_meme(matcher, meme_name)
    if meme_manager.unblock(user_id, meme.key):
        await matcher.finish(f"表情 {meme.key} 启用成功")
    else:
        await matcher.finish(f"表情 {meme.key} 已被主人禁用")


@block_gl_matcher.handle()
async def _(matcher: Matcher, meme_name: str):
    meme = await find_meme(matcher, meme_name)
    meme_manager.change_mode(MemeMode.WHITE, meme.key)
    await matcher.finish(f"表情 {meme.key} 已设为白名单模式")


@unblock_gl_matcher.handle()
async def _(matcher: Matcher, meme_name: str):
    meme = await find_meme(matcher, meme_name)
    meme_manager.change_mode(MemeMode.BLACK, meme.key)
    await matcher.finish(f"表情 {meme.key} 已设为黑名单模式")
    
    
@black_list_matcher.handle()
async def _(matcher: Matcher):
    black_list = meme_manager.get_black_list()
    if not black_list:
        await matcher.finish("当前没有禁用的表情")
    else:
        await matcher.finish("当前禁用的表情列表：\n" + "\n".join(black_list))