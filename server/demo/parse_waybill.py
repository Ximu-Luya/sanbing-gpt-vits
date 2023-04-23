import re

# s = "好的，跟您确认一遍，您的订单号是华莱士二十五号单，是吗？"
s = "好的，跟您确认一遍，您的订单号是华莱士二十五，是吗？"
# match_obj = re.search(r'订单号是(.+?)号单', s)
match_obj = re.search(r'订单号是(.+?)[,，.。]', s)

print(match_obj)
if match_obj:
    result = match_obj.group(1)
    print(result)