import datetime
from datetime import datetime, timedelta

import nonebot
from aiocqhttp import MessageSegment
from apscheduler.triggers.date import DateTrigger

import xiuXian.plugins.xiuxian_config as config

bot = nonebot.get_bot()

# 通知 在{YYYY-MM-DD HH:MM:SS}进行{message}


async def notification(message, seconds):
    """
    :param seconds: 多少秒
    :param message: 发送的消息
    :return: 无
    """

    future_time = datetime.now() + timedelta(seconds=seconds)

    # 打印格式化后的新时间点
    formatted_future_time = future_time.strftime('%Y-%m-%d %H:%M:%S')

    message = '将在' + formatted_future_time + '进行' + message

    await bot.send_group_msg(group_id=config.group_id,
                             message=message)


async def delete(message_id):
    await bot.delete_msg(message_id=message_id)


async def send(message):
    """
    :param message: 发送消息
    :return: 无
    """
    res = await bot.send_group_msg(group_id=config.group_id,
                                   message=MessageSegment.at(3889001741) + " " + message)
    await delete(res['message_id'])


async def job(message, delay):
    nonebot.scheduler.add_job(
        func=send,
        trigger=DateTrigger(
            run_date=datetime.now() + timedelta(seconds=delay)
        ),
        args=(message,),
        misfire_grace_time=60,
    )
