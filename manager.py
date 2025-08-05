import pymysql
from beautifultable import BeautifulTable

def addStudent(cursor: pymysql.cursors.DictCursor):
    #姓名
    curstr = input("请输入姓名：")
    while any([char.isdigit() for char in curstr]):
        print("姓名中不可以有数字")
        curstr = input("请输入姓名：")
    name = curstr
    #年龄
    curstr = input("请输入年龄：")
    while not curstr.isdigit():
        print("年龄必须全为数字！")
        curstr = input("请输入年龄：")
    age = int(curstr)
    #性别
    curstr = input("请输入性别：")
    while curstr not in ("男","女"):
        print("性别仅可以是男女！")
        curstr = input("请输入性别：")
    sex = "M" if curstr == "男" else "F"
    #放入数据库
    sql = "insert into student(name,age,sex) values(%s,%s,%s)"
    cursor.execute(sql,(name,age,sex))

def getDict(outs: str)-> dict:
    """
    根据格式化输入"key1=word1 key2=word2"得到字典\n
    Args:
        要询问的内容
    Returns:
        根据询问内容提取出的包含了字段的字典
    """
    
    gets = input(outs)
    if not gets:
        return dict()
    lis = gets.split(sep=" ")
    dic = dict()
    for elem in lis:
        key,value = tuple(elem.split("="))
        dic[key] = value
    return dic

def whereStudent(info_dict: dict)-> tuple:
    """
    根据已获得的字段信息得到符合mysql格式的筛选条件\n
    Args:
        包含字段信息的字典
    Returns:
        筛选条件mysql在where语句之后条件，以及包含mysql对应参数元组
    """
    where = ""
    not_first = False
    param = []
    if "name" in info_dict:
        name = info_dict["name"]
        if any([char.isdigit() for char in name]):
            raise ValueError("名字中不可以有数字！")
        where += "and " if not_first else ""
        not_first = True #设置下一个参数并不是where之后的第一个
        where += "name=%s "
        param.append(name) #搜集参数
    if "age" in info_dict:
        age = info_dict["age"]
        if not age.isdigit():
            raise ValueError("年龄必须由全数字构成！")
        where += "and " if not_first else ""
        not_first = True
        where += "age=%s "
        param.append(age)
    if "sex" in info_dict:
        sex = info_dict["sex"]
        if sex not in ("男","女"):
            raise TypeError("性别仅能是男女！")
        sex = 'M' if sex=="男" else 'F'
        where += "and " if not_first else ""
        not_first = True
        where += "sex=%s "
        param.append(sex) #搜集参数
    return (where,tuple(param))

def findStudent(cursor: pymysql.cursors.DictCursor):
    info_dict = getDict("请根据学生字段查找学生：")
    where,param = whereStudent(info_dict)
    sql = "select * from student "
    if where:
        sql += "where " + where
    sql += ";"
    param = tuple(param)
    cursor.execute(sql,param)
    b = BeautifulTable()
    b.columns.header = ["uid","name","age","sex"]
    rows = cursor.fetchall()
    for row in rows:
        b.rows.append(row.values())
    print(b)
def delStudent(cursor: pymysql.cursors.DictCursor):
    info_dict = getDict("请根据学生字段找到要删除的学生信息：")
    where,param = whereStudent(info_dict)
    if not where:
        print("没有搜集到有效字段！")
        return
    sql = "delete from student where "
    sql += where
    cursor.execute(sql,param)
def modifyStudent(cursor: pymysql.cursors.DictCursor):
    info_dict = getDict("请根据学生字段找到要修改的学生信息：")
    where,where_param = whereStudent(info_dict)
    if not where:
        print("没有搜集到有效字段！")
        return
    set_dict = getDict("请为要修改的字段赋值：")
    set_parts = [] #set部分的语句
    set_params = [] #set部分需要传入的参数
    if "name" in set_dict:
        # if any([char.isdigit() for char in set_dict["name"]]):
        #     print("姓名中不可以有数字")
        set_parts.append("name=%s")
        set_params.append(set_dict["name"])
    if "age" in set_dict:
        set_parts.append("age=%s")
        set_params.append(set_dict["age"])
    if "sex" in set_dict:
        set_parts.append("sex=%s")
        if set_dict["sex"] in ("男","女"):
            sex_value = "M" if set_dict["sex"] == "男" else "F"
        set_params.append(sex_value)

    if not set_parts:
        print("没有提供有效的修改字段！")
        return
    
    sql = f"update student set {','.join(set_parts)} where {where}"
    params = tuple(set_params + list(where_param))
    
    try:
        cursor.execute(sql,params)
        print("已修改！")
    except pymysql.Error as e:
        print("修改失败！:",e)
def addScore(cursor:pymysql.cursors.Cursor):
    info_dict = getDict("请根据字段查询要添加分数信息的学生：")
    where,where_params = whereStudent(info_dict)
    #<找到学生uid/>
    findu_sql = "select uid from student where " + where
    cursor.execute(findu_sql,where_params)
    uids = cursor.fetchall()
    if (len(uids) == 0):
        print("没有查询这位学生！")
        return
    if (len(uids) > 1):
        print("一次仅能为一名学生添加考试信息！")
        return
    uid = uids[0]["uid"]
    #</找到学生uid>
    # <指定科目找到cid\>
    course_name = input("请指定科目：")
    findc_sql = "select cid from course where cname=%s"
    cursor.execute(findc_sql,course_name)
    cid = cursor.fetchone()["cid"]
    #</指定科目找到cid>
    #<考试情况/>
    time = input("请输入考试时间：")
    score = input("请输入分数：")
    #</考试情况>
    #<实现加入考试信息\>
    params = (uid,cid,time,score)
    sql = """
        insert into exame(uid,cid,time,score) 
        values(%s,%s,%s,%s)
    """
    cursor.execute(sql,params)
    #</实现加入考试信息>
def findScore(cursor:pymysql.cursors.Cursor):
    info_dict = getDict("请根据字段找到要查询考试信息的学生：")
    where,where_params = whereStudent(info_dict)
    #<查询学生uid/>
    findu_sql = "select uid,name from student where " + where
    cursor.execute(findu_sql,where_params)
    uids = cursor.fetchall()
    if (len(uids) == 0):
        print("没有查询这位学生！")
        return
    if (len(uids) > 1):
        print("一次仅能查询一名学生的考试信息！")
        return
    uid = uids[0]["uid"]
    sname = uids[0]["name"]
    #</查询学生uid>
    #<获得cid/>
    course_name = input("请指定科目：")
    findc_sql = "select cid from course where cname=%s"
    cursor.execute(findc_sql,course_name)
    cid = cursor.fetchone()["cid"]
    #</获得cid>
    #<实现查询成绩功能/>
    sql = """
        select s.uid,s.name,s.sex,c.cname,c.credit,e.score
        from exame e
        inner join student s on s.uid = e.uid
        inner join course c on c.cid = e.cid
        where 
    """
    sql += where
    sql += "and " + "cname=%s "
    params = list(where_params)
    params.append(course_name)
    params = tuple(params)
    cursor.execute(sql,params)
    # print(cursor.fetchall())
    rows = cursor.fetchall()
    table = BeautifulTable()
    table.columns.header = ["uid","name","sex","cname","credit","score"]
    for row in rows:
        table.rows.append(row.values())
    print(table)
    # </实现查询成绩功能>


def showInterface():
    print("    --------------------------------------------")
    print("           学生管理系统 v1.0        ")
    print()
    print("           1:添加学生信息")
    print("           2:查询学生信息")
    print("           3:删除学生信息")
    print("           4:修改学生信息")
    print("           5:添加学生成绩信息")
    print("           6:查询学生成绩信息")
    print("           7:删除学生成绩信息")
    print("           8:修改学生成绩信息")
    print("           9:根据总成绩信息排名")
    print("           10:根据单科成绩信息排名")
    print("           11:查询单科成绩的最高分/最低分/平均分")
    print("           0:退出系统")
    print("    --------------------------------------------")
#课程表course:
# C++基础课程  C++高级课程  C++项目开发  C++算法课程
if __name__ == "__main__":
    connect = pymysql.connect(
        host = "localhost",
        user = "root",
        password = "123456",
        database = "test",
        charset = "utf8",
        cursorclass = pymysql.cursors.DictCursor
    )
    #---得到connect----
    with connect.cursor() as cursor:
        #---得到cursor----

        showInterface()
        time = 0 #当次数超过5，再次显示界面
        while True:
            choice = input("请选择项目：")
            if len(choice) == 0:
                continue
            choice = int(choice)
            time += 1
            if not time % 5:
                showInterface()
            match choice:
                case 1:#添加学生信息
                    addStudent(cursor)
                    connect.commit()
                    print("已成功添加学生！")
                    pass
                case 2:#查询学生信息
                    findStudent(cursor)
                    print("查询成功！")
                    pass
                case 3:
                    delStudent(cursor)
                    connect.commit()
                    print("删除成功！")
                    pass
                case 4:
                    modifyStudent(cursor)
                    connect.commit()
                    pass
                case 5:#添加学生成绩信息
                    addScore(cursor)
                    connect.commit()
                    pass
                case 6:
                    findScore(cursor)
                    
                    pass
                case 7:
                    pass
                case 8:
                    pass
                case 9:
                    pass
                case 10:
                    pass
                case 11:
                    pass
                case 0:#退出系统
                    print("安全退出，欢迎下次使用！")
                    break  
                case _:
                    print("无效输入！")
        