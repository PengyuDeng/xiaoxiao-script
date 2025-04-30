from datetime import datetime

import nonebot

import xiuXian.plugins.xiuxian_config as config
from xiuXian.plugins.message_sender import send


@nonebot.scheduler.scheduled_job('cron', hour='8', minute='0')
async def stop():
    """
    自动签到
    :return:
    """
    await send("修仙签到")


@nonebot.scheduler.scheduled_job('cron', hour='9', minute='1')
async def receive_herbal_medicine():
    await send("宗门丹药领取")


@nonebot.scheduler.scheduled_job('cron', hour='9', minute='2')
async def auto_reward():
    await send("灵田结算")


@nonebot.scheduler.scheduled_job('cron', hour='9', minute='3')
async def reward_family_task():
    """
    宗门任务接取
    :return:
    """
    await send("宗门任务接取")


# 12:30 停止自动修炼
@nonebot.scheduler.scheduled_job('cron', hour='12', minute='30')
async def stop_practice():
    config.auto_practice = False
    config.auto_practice_has_send = False


# 12:31 探索秘境
@nonebot.scheduler.scheduled_job('cron', hour='12', minute='31')
async def go_secret_area():
    await send("探索秘境")


@nonebot.scheduler.scheduled_job('interval', seconds=31)
async def auto_practice():
    # 计算当前的时间戳一次，避免多次调用
    if config.auto_practice:
        current_timestamp = int(datetime.now().timestamp())
        time_since_last_send = current_timestamp - config.xiulian_send_timestamp

        # 如果还未发送过或距离上一次发送已经超过120秒，则发送消息
        if not config.auto_practice_has_send or time_since_last_send > 90:
            await send('修炼')
            config.auto_practice_has_send = True
            config.xiulian_send_timestamp = current_timestamp  # 更新最后发送的时间戳
