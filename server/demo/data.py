import os
import json
import openai
import pandas as pd

os.environ['http_proxy'] = 'http://127.0.0.1:7890'
os.environ['https_proxy'] = 'http://127.0.0.1:7890'


def request_openai(prompt, temperature = 0):
    test_key = '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'
    prod_key = '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'

    messages = [
        {
            'role': 'system',
            'content': prompt,
        }
    ]

    openai.api_key = test_key
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=messages,
        temperature=temperature
    )

    return (response.usage.total_tokens, response.choices[0].message.content)




def get_scenarios(data, query):
    scenarios = [i['name'] for i in data['scenario']]
    category_num = len(scenarios)
    prefix = f'你是一个分类器，有以下{category_num}个类别，按换行符分割\n\n'
    category = '\n'.join(scenarios)
    postfix = '\n\n骑手最可能的2个类别是'

    query = prefix + category + '\n\n骑手：' + query + postfix
    usage, res = request_openai(query)
    print(f'get_scenario_token_usage: {usage}')
    
    output = []
    for scenario in scenarios:
        if scenario in res:
            output.append(scenario)
    return output[:2]


def get_rules(data, query, scenarios):
    questions = {}
    for scenario in data['scenario']:
        if scenario['name'] in scenarios and 'qa' in scenario.keys():
            for question in scenario['qa']:
                if 'zhongbao' in question.keys():
                    questions[question['question']] = question['zhongbao']
    category_num = len(questions.keys())
    
    prefix = f'你是一个分类器，有以下{category_num}个类别，按换行符分割\n\n'
    category = '\n'.join(questions.keys())
    postfix = '\n\n骑手最可能的2个类别是'

    query = prefix + category + '\n\n骑手：' + query + postfix
    usage, res = request_openai(query, 0)
    print(f'get_rule_token_usage: {usage}')

    output = []
    for question, role in questions.items():
        if question in res:
            output.append(question + '\n' + role)
    return output


def get_answer(query, rules, status):
    query = '假设你是美团客服\n\n' \
        + f'骑手状态：{status}\n\n' \
        + '处理规则如下\n' \
        + '\n'.join(rules) + '\n\n' \
        + f'骑手：{query}\n' \
        + '客服：'
    usage, res = request_openai(query, 0)
    print(f'get_answer_token_usage: {usage}')
    
    return res


if __name__ == '__main__':
    query = '哎你好我想问一下我手上有一单草本汤美团五号的，这边那个顾客我给他送过去他不要了怎么办'
    status = '已接单,已取餐,未到达顾客位置,未上报'

    with open('test.json', 'r') as f:
        data = json.load(f)
    
    scenarios = get_scenarios(data, query)
    print(scenarios)

    rules = get_rules(data, query, scenarios)
    print(rules)

    answer = get_answer(query, rules, status)
    print(status)