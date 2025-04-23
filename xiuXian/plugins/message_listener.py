import nonebot

import xiuXian.plugins.xiuxian_config as config
from xiuXian.plugins.message_handle import handle_message

bot = nonebot.get_bot()


@bot.on_message('group')  # 监听群消息
async def handle_group_message(ctx):
    try:
        # 不是群里的或者不是小小机器人发的
        if config.group_id != ctx.get('group_id') or config.xiaoxiao_qq_number != ctx['sender']['user_id']:
            return
        await etl_message(ctx)

    except Exception as e:
        nonebot.log.logger.error(e)


async def etl_message(ctx):
    if ctx['message_format'] == 'array':
        message_id = ctx['message_id']
        for i in ctx['message']:
            if i['type'] == 'text':
                await handle_message(i['data']['text'], message_id)
                return
