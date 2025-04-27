import logging
from datetime import datetime, timedelta
import re

import nonebot
from apscheduler.triggers.date import DateTrigger

import xiuXian.plugins.xiuxian_config as config
from xiuXian.plugins.message_sender import job, send, delete, notification

mission_task_cache = {}

# 用于存储消息类型和对应处理函数的字典
message_handlers = {}


# 处理消息的异步函数
async def handle_message(message, message_id):
    # 遍历所有的消息类型和处理函数
    for key, handler in message_handlers.items():
        # 检查 message 是否是 key 的子字符串
        if key in message:
            await handler(message, message_id)
            break


# 定义一个装饰器，来标记每个处理函数
def text_in_message(*messages):
    def decorator(func):
        # 将函数和消息类型存储到全局的处理字典中
        for message in messages:
            message_handlers[message] = func
        return func

    return decorator


# 处理任务完成并接取新任务的消息
@text_in_message(
    '传言山外村庄有邪修抢夺灵石，请道友下山为民除害',
    '已刷新，道友当前接取的任务：狩猎邪修\n传言山外村庄有邪修抢夺灵石，请道友下山为民除害',
    '有少量弟子私下消费，私自架设小型窝点，请道友前去查抄',
    '山门将开，宗门急缺一批药草熬制九转丹，请道友下山购买',
    '在宗门外见到师弟欠了别人灵石被追打催债，请道友帮助其还清',
    '山下一月一度的市场又开张了，其中虽凡物较多，但是请道友慷慨解囊，为宗门购买一些蒙尘奇宝'
)
async def handle_task_completion(message, message_id):
    await send('宗门任务完成')


@text_in_message(
    '道友大战一番，气血减少',
    '道友为了完成任务购买宝物消耗灵石'
)
async def handle_task_completion(message, message_id):
    await send('宗门任务接取')


# 处理任务失败的消息
@text_in_message(
    '道友兴高采烈的出门做任务，结果状态欠佳，没过两招就力不从心，坚持不住了，道友只好原路返回，浪费了一次出门机会，看你这么可怜，就不扣你任务次数了！'
)
async def handle_task_failure(message, message_id):
    await job('宗门任务完成', 5 * 60)


# 处理悬赏令相关消息
@text_in_message('道友的个人悬赏令')
async def handle_reward_task(message, message_id):
    reward_task_to_cache(message)


# 处理悬赏令接取任务的消息
@text_in_message(
    '接取任务'
)
async def handle_reward_accept(message, message_id):
    name = find_name(message)
    second = mission_task_cache[name] * 60 + 5

    await notification('悬赏令结算', second)
    # 结束时间+5s后执行 悬赏令结算
    await job('悬赏令结算', second)


# 处理悬赏令结算后的刷新操作
@text_in_message(
    '悬赏令结算，'
)
async def handle_reward_refresh(message, message_id):
    await send('悬赏令刷新')


# 处理宗门任务次数已用尽的消息
@text_in_message(
    '今日无法再获取宗门任务了！'
)
async def handle_task_limit(message, message_id):
    config.auto_practice = False
    config.auto_practice_has_send = False
    await job('悬赏令刷新', 60)


# 处理悬赏令刷新次数已用尽的消息
@text_in_message(
    '道友今日的悬赏令刷新次数已用尽'
)
async def handle_refresh_limit(message, message_id):
    config.auto_practice = True
    config.auto_practice_has_send = False


# 处理宗门贡献度不足的消息
@text_in_message(
    '道友的宗门贡献度不满足'
)
async def handle_contribution_limit(message, message_id):
    await send('宗门捐献 10000000')
    await job('宗门丹药领取', 2)


# 处理秘境任务的消息
@text_in_message(
    '道友进入秘境：'
)
async def handle_exploration(message, message_id):
    minutes = extract_exploration_time(message)
    await job('秘境结算', minutes * 60 + 1)
    await notification('秘境结算', minutes * 60 + 1)
    nonebot.scheduler.add_job(
        func=auto_practice_set_true,
        trigger=DateTrigger(
            run_date=datetime.now() + timedelta(minutes=minutes, seconds=2)
        ),
        misfire_grace_time=60,
    )


def auto_practice_set_true():
    config.auto_practice = True


# 处理药材信息的消息
@text_in_message(
    '本次修炼增加'
)
async def handle_medicine_info(message, message_id):
    await delete(message_id)
    # 开启了自动修炼
    if config.auto_practice:
        await send('修炼')
        config.xiulian_send_timestamp = int(datetime.now().timestamp())
    else:
        # 发送过修炼消息标志符清零
        config.auto_practice_has_send = False


# 处理药材信息的消息
@text_in_message(
    '开始🙏修炼...'
)
async def handle_medicine_info(message, message_id):
    await delete(message_id)


# 悬赏令任务、时间写入缓存
def reward_task_to_cache(text):
    global mission_task_cache
    pattern = r'^\d+、([^\d,]+?),.*?预计需(\d+)分钟'
    matches = re.findall(pattern, text, re.MULTILINE)
    mission_task_cache = {item[0].strip(): int(item[1]) for item in matches}


def extract_exploration_time(text):
    pattern = r'探索需要花费时间：(\d+(\.\d+)?)分钟'
    match = re.search(pattern, text)
    if match:
        return int(float(match.group(1)))
    return None


def find_name(text):
    pattern = r"【(.*?)】"
    return re.findall(pattern, text)[0]
