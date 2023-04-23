import re
import json

from tools import *
from collections import OrderedDict

system_prompts = {
    "0": open('stage0.txt','r').read(),
    "1": open('stage1.txt','r').read(),
    "21": open('stage2-用户拒收.txt','r').read(),
    "22": open('stage2-地址不符.txt','r').read()
}

rider_waybills = json.load(open('wb_list-20230331.json','r'), object_pairs_hook=OrderedDict)
waybill_status = json.load(open('status.json','r'), object_pairs_hook=OrderedDict)
rider_waybills_all = {dc['rider_id']:dc for dc in rider_waybills}
tmp_waybill_dc = {dc["waybill_id"]:dc for dc in waybill_status}
for rider_id in rider_waybills_all:
    for wb in rider_waybills_all[rider_id]['wb_list']:
        wb_status = tmp_waybill_dc[wb['waybill_id']]
        wb.update(wb_status)


# stage切换逻辑
def stage_transform(text,stage_id):
    next_stage = stage_id
    senarios = ['用户拒收外卖','用户实际位置与地图定位不符']

    if stage_id == 0:
        if '跟您确认一遍，您的订单号是' in text:
            next_stage = 1
    if stage_id == 1:
        for i,senario in enumerate(senarios):
            if senario in text.replace('顾客','用户'):
                next_stage = 21 + i

    return next_stage


# 前端是否展示运单逻辑
def whether_show_waybill_list(text,stage):
    key_phases = [
        '请问您的订单号是什么',
        '能提供一下这个订单的订单号吗',
        '能提供一下订单号吗',
        '订单号是什么呢',
    ]
    if stage==1 and any([p in text for p in key_phases]):
        return 1
    return 0


# 判断状态是否需要提供骑手的订单状态
def where_provide_waybill_status(stage, next_stage):
    if stage==1 and next_stage>1:
        return 1
    return 0


def to_waybill(pickup_number):
    store_name = None
    num = None

    match_obj = re.match(r'(\D+)(\d+)', pickup_number)
    if match_obj:
        # 商家名
        store_name = match_obj.group(1)
        # 号码
        num = int(match_obj.group(2))

    else:
        match_obj = re.match(r'(\D+?)([零一二三四五六七八九十百千]+)', pickup_number)
        
        if match_obj:
            # 商家名
            store_name = match_obj.group(1)
            # 号码
            num_str = match_obj.group(2)
            num = convertNumFromStr(num_str)

    if store_name is not None and num is not None:
        for rider_id in rider_waybills_all:
            for wb in rider_waybills_all[rider_id]['wb_list']:
                if store_name in wb['sender_name'] and num==wb['fetch_id']:
                    return wb['waybill_id']
    return None


# 从gpt的回答中解析订单号
def parse_waybill(request_data, stage, text):
    parsed_waybill = request_data['options'].get('waybill', None)
    if parsed_waybill is not None:
        return parsed_waybill
    pickup_number = None
    if stage == 0 and '确认一遍' in text:
        key_phases = [
            r'订单号是(.+?)号',
            r'订单号是(.+?)[,，.。]',
        ]
        
        for p in key_phases:
            match_obj = re.search(p, text)
            if match_obj:
                pickup_number = match_obj.group(1)
                break
    if pickup_number is not None:
        return to_waybill(pickup_number)
    return None


def find_waybill_by_id(waybill_id):
    for rider_id in rider_waybills_all:
        for wb in rider_waybills_all[rider_id]['wb_list']:
            if waybill_id == wb['waybill_id']:
                return wb


def get_status(wb, key):
    dialects = {
        '是否到客':'是否到达用户位置'
    }
    status_name = dialects[key] if key in dialects else key
    val = '是' if wb[key]==1 else '否'
    return f'{status_name}:{val}'            


def wrap_prompt(prompt, waybill_id):
    wb = find_waybill_by_id(waybill_id)
    status_keys = [
        '是否到客',
        '是否送达',
        '是否申诉',
        '是否已报备',
        '是否有违规罚单'
    ]

    status_phase = '我当前的状态是'+'\n' \
        +'\n'.join([get_status(wb,k) for k in status_keys])

    wrapped_prompt = prompt + '\n\n' + status_phase
    return wrapped_prompt