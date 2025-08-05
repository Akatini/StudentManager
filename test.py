def getDict(outs: str)-> dict:
    #根据格式化输入"key1=word1 key2=word2"得到字典
    gets = input(str)
    lis = gets.split(sep=" ")
    dic = dict()
    for elem in lis:
        key,value = tuple(elem.split("="))
        dic[key] = value
    return dic

print(getDict("输入字典集:"))