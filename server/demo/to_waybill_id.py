import re



def convertNumFromStr(numS):
    numDict = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6,'七': 7, '八': 8, '九': 9, "零" : 0}
    num = 0
    if "百" in numS:
        indexB = numS.index("百")
        value = numS[0:indexB]
        num = numDict[value] * 100
        if "十" in numS:
            indexS = numS.index("十")
            value = numS[indexB+1:indexS]
            if len(value) == 0:
                value = "一"
            num = num + 10 * numDict[value]
            value = numS[indexS+1:]
            if len(value) > 0:
                num = num + numDict[value]
        else:
            if "零" in numS:
                indexB = indexB + 1
            value = numS[indexB+1:]
            if len(value) > 0:
                num = num + numDict[value]
    else:
        if "十" in numS:
            indexS = numS.index("十")
            value = numS[0:indexS]
            if len(value) == 0:
                value = "一"
            num = num + 10 * numDict[value]
            value = numS[indexS+1:]
            if len(value) > 0:
                num = num + numDict[value]
        else:
            num = numDict[numS]
    print("convertNumFromStr %s" %num)
    return num


def parse(pickup_number):
    match_obj = re.match(r'(\D+)(\d+)', pickup_number)
    if match_obj:
        # 商家名
        store_name = match_obj.group(1)
        # 号码
        num = int(match_obj.group(2))
        return store_name, num
    

    match_obj = re.match(r'(\D+?)([零一二三四五六七八九十百千]+)', s)
    
    if match_obj:
        # 商家名
        store_name = match_obj.group(1)
        # 号码
        num_str = match_obj.group(2)
        num = convertNumFromStr(num_str)
        return store_name, num

s = "华莱士122"
print(parse(s))
s = "华莱士一百零三"
print(parse(s))

