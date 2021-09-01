'''
Author: Village-Secretary
Date: 2021-02-07 16:44:52
LastEditTime: 2021-09-01 15:22:16
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: \DemoPy\.vscode\GetSubjects.py
'''

import re
import requests
import urllib.parse
import os
import threading
import time
from tqdm import tqdm
import Topic

# 链接
url_stuframe = 'http://exam.zjjhy.net/StuFrame.aspx?stuNo='        # 毕业补考url
url_termframe = 'http://exam.zjjhy.net/TermFrame.aspx?stuNo='      # 学年补考url

# 获取HTML中的hidden属性及其值
re_html_hidden_key_value = r'type=\"hidden\" name=\"([^\"]+)\" id=\"\1\" (?:value=\"([^\"]*)\")*'
# 获取HTML中的考试时间序号
re_html_examtime = r'<option (?:selected=\"selected\")*\s*value=\"([^\"]+)\">'
# 获取HTML中的需要提交的表单题目序号
re_html_topic_number = r'GridView1\$ctl([0-9]+)\$ChkSelected'
# 获取模拟考试的考试url
re_url_simulation_test = r'window.open\(\'([^\']+)'
# 获取模拟补考键(查看是否存在这个键来判断是否此科目已经考过)
re_is_tested = r'value="模拟测试"'
# 获取HTML中考试科目的中文名
re_html_chinese_name = r'<span id=\"lblCourseName\">(.*)(?=</span>)'
# 获取url中的题目代码
re_get_topic_code = r'[\d]+(?=\.)'
# 获取HTML中题目的标题
re_get_topic_title = r'<span id=\"lblMainBody\">(.*)(?=</span>)'
# 获取HTML中题目的选项
re_get_topic_options = r'<label for=\"rbItem([A|B|C|D])\">(?:\([A|B|C|D]\))\s+(.*)(?=</label>)'
# 获取HTMl中题目的判断选项是否隐藏(根据此项来判断此题是否为判断题)
re_get_topic_judgment = r'<div id=\"QuestionItemsJudge\" style=\"([^\"]+)\">'
# 获取HTML中题目的答案和解析
re_get_topic_answer_analyze = r'<span id=\"lblAnswer\"><p>([^<]+)<p>(.*)(?=</span>)'
# 获取题目中标题、选项、等文本中的照片文件
re_get_png = r'src=\"([^\"]+)\"'


# 设置Get报文头
headers_get = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36 Edg/88.0.705.63' }

# 设置Post报文头
headers_post = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36 Edg/88.0.705.63', 
                'Content-Type': 'application/x-www-form-urlencoded' }


# 获取HTML中的hidden属性
def Set_Hidden_Key_Value(html):
    hid_list = re.findall(re_html_hidden_key_value, html)
    payload = dict()
    for l in hid_list:
        payload[l[0]] = l[1]
    return payload

# 设置[全部显示]键的表单
def Set_Display_All(html, examtime):
    payload = Set_Hidden_Key_Value(html)
    payload['__EVENTTARGET'] = 'rbNoPaging'
    payload['ddlExamTime'] = str(examtime)
    payload['txtPageSize'] = '10'
    payload['PageControl'] = 'rbNoPaging'
    
    # 返回键值
    return urllib.parse.urlencode(payload)

# 设置[全选]键的表单
def Set_Select_All(html, examtime):
    payload = Set_Hidden_Key_Value(html)
    payload['__EVENTTARGET'] = 'cbSelectAll'
    payload['ddlExamTime'] = str(examtime)
    payload['txtPageSize'] = '10'
    payload['PageControl'] = 'rbNoPaging'
    payload['cbSelectAll'] = 'on'
    
    # 返回键值
    return urllib.parse.urlencode(payload)

# 设置[模拟补考]键的表单
def Set_Simulation_Test(html, examtime):
    payload = Set_Hidden_Key_Value(html)
    payload['ddlExamTime'] = str(examtime)
    payload['txtPageSize'] = '10'
    payload['PageControl'] = 'rbNoPaging'
    payload['cbSelectAll'] = 'on'
    payload['btnSimulationTest'] = '模拟测试'
    topic_number = re.findall(re_html_topic_number, html)
    for num in topic_number:
        payload['GridView1$ctl' + num + '$ChkSelected'] = 'on'
        
    # 返回键值
    return urllib.parse.urlencode(payload)

# 设置[选择考试时间(科目)]键的表单
def Set_Choose_Exam_Time(html, examtime):
    payload = Set_Hidden_Key_Value(html)
    payload['__EVENTTARGET'] = 'ddlExamTime'
    payload['ddlExamTime'] = str(examtime)
    payload['txtPageSize'] = '10'
    payload['PageControl'] = 'rbPaging'
    
    # 返回键值
    return urllib.parse.urlencode(payload)

# 设置[提交结果]键的表单
def Set_Submit_Result(html):
    payload = Set_Hidden_Key_Value(html)
    payload['btnSubmit'] = '提交结果'
    
    # 返回键值
    return urllib.parse.urlencode(payload)

# 设置[选择题目]键的表单
def Set_Choose_Topic(html, topic_code, topic_num):
    payload = Set_Hidden_Key_Value(html)
    payload[str(topic_code)] = '第' + str(topic_num) + '题'
    
    # 返回键值
    return urllib.parse.urlencode(payload)

# GET请求
def My_Get(url, c_str = None, is_output = True):
    r = requests.get(url, headers = headers_get, timeout = 5.0)
    if is_output:
        print(c_str, '[GET]  \tStatus_code: ', r.status_code, '\tContent-Length: ', r.headers['Content-Length'])
    return r

# POST请求
def My_Post(url, payload, c_str = '', is_output = True):
    r = requests.post(url,  data = payload, headers = headers_post, timeout = 5.0)
    if is_output:
        print(c_str, '[POST] \tStatus_code: ', r.status_code, '\tContent-Length: ', r.headers['Content-Length'])
    return r

# 设置网络连接信息（运行时显示此次POST或GET是干啥）
def Ret_Getting_Information(examtime = 'None', c_str = ''):
    inf_str = '[' + str(examtime) + ']'
    inf_str += c_str + '\t\t'
    return inf_str

# 返回获取的模拟考试的题目链接
def Ret_url_simulation_test(connection_url, examtime):
    # 连接获取url页面
    r = My_Get(url = connection_url, c_str = Ret_Getting_Information(c_str = '获取url页面'))
    
    # 设置[选择考试时间(科目)]键的提交表单
    payload = Set_Choose_Exam_Time(html = r.text, examtime = examtime)

    # 提交[选择考试时间(科目)]键
    r = My_Post(url = connection_url, payload = payload, 
                c_str = Ret_Getting_Information(str(examtime), '提交\"选择科目\"键'))
    
    # 设置[全部显示]键的提交表单
    payload = Set_Display_All(html = r.text, examtime = examtime)

    # 提交[显示全部]键
    r = My_Post(url = connection_url, payload = payload, 
            c_str = Ret_Getting_Information(str(examtime), '提交\"显示全部\"键'))

    # 设置[全选]键的提交表单
    payload = Set_Select_All(html = r.text, examtime = examtime)
    # 提交[全选]键
    r = My_Post(url = connection_url, payload = payload, 
            c_str = Ret_Getting_Information(str(examtime), '提交\"全选\"键'))

    # 设置[模拟补考]键的提交表单
    payload = Set_Simulation_Test(html = r.text, examtime = examtime)

    # 提交[模拟补考]键
    r = My_Post(url = connection_url, payload = payload, 
            c_str = Ret_Getting_Information(str(examtime), '提交\"模拟补考\"键'))
    
    # 获取返回的模拟考试页面链接
    url_simulation_test = re.findall(re_url_simulation_test, r.text)
    
    # 返回模拟考试页面链接
    return 'http://exam.zjjhy.net/' + url_simulation_test[0]

# 判断是否有已经考过的科目，且丢掉已经考过的科目序号
def Weed_Out_Tested(connection_url, examtimes):
    # 连接获取url页面
    r = My_Get(url = connection_url, is_output = False)
    
    examtimes_copy = examtimes.copy()       # 拷贝一个新的列表
    chinese_names = dict()
    
    for examtime in examtimes:
        # 设置[[选择考试时间(科目)]键的提交表单
        payload = Set_Choose_Exam_Time(html = r.text, examtime = examtime)
        
        # 提交[[选择考试时间(科目)]键
        r = My_Post(url = connection_url, payload = payload, is_output = False)
        
        # 搜索当前页面是否有模拟补考键
        if re.search(re_is_tested, r.text) == None:
            examtimes_copy.remove(examtime)
        else:
            # 如果有模拟补考键，则获取考试的科目的中文名
            chinese_names[examtime] = re.findall(re_html_chinese_name, r.text)[0]
        
    return [examtimes_copy, chinese_names]

# 检测题目中的照片url，并添加(替换)上域名
def Replace_Image_Url(text):
    # 获取照片url
    img_urls = re.findall(re_get_png, text)
    
    # 用获取到的照片url列表，来寻找替换
    for img_url in img_urls:
        text = re.sub(img_url, 'http://exam.zjjhy.net/' + img_url[1:], text)
    
    return text

# 分析HTML文件以获取需要的题目数据
def Analyze_HTMl_Files_To_Topic(html, topic_num):
    topic_temp = Topic.Topic()
    
    # 获取标题，检查题目中是否有图片
    topic_title = Replace_Image_Url(re.findall(re_get_topic_title, html)[0])
    
    # 获取选项
    topic_options_temp = dict(re.findall(re_get_topic_options, html))
    topic_options = dict()
    
    # 循环检查选项中是否有照片
    for opt_key, opt_value in topic_options_temp.items():
        topic_options[opt_key] = Replace_Image_Url(opt_value)
    
    # 获取判断
    topic_judgment = re.findall(re_get_topic_judgment, html)
    
    # 获取答案和分析
    topic_answer_analyze = re.findall(re_get_topic_answer_analyze, html)[0]
    
    if 'display:none' == topic_judgment[0]:
        topic_temp.read(number = topic_num, title = topic_title, options = topic_options, judgment = False, 
                        answer = topic_answer_analyze[0], analyze = topic_answer_analyze[1])
    else:
        topic_temp.read(number = topic_num, title = topic_title, options = topic_options, judgment = True, 
                        answer = topic_answer_analyze[0], analyze = topic_answer_analyze[1])
    
    return topic_temp

# 循环获取某一科的所有题目
def Get_All_Topics(connection_url, examtime):
    
    # 获取模拟考试页面
    r = My_Get(url = connection_url, 
            c_str = Ret_Getting_Information(str(examtime), c_str = '获取\'考试\'页面'))

    # 设置[提交结果]键的提交表单
    payload = Set_Submit_Result(html = r.text)

    # 提交[提交结果]键
    r = My_Post(url = connection_url, payload = payload, 
                c_str = Ret_Getting_Information(str(examtime), '提交\"提交结果\"键'))

    # 获取url中所有的题目代码
    all_topics_code = re.findall(re_get_topic_code, connection_url)

    topic_num = 1
    topics = []
    
    # 循环获取所有的题目
    # 这里的tqdm是用来显示进度条
    with tqdm(all_topics_code, desc='[' + str(examtime) + ']') as t:
        for topic_code in t:

            # 设置[选择题目]键的提交表单
            payload = Set_Choose_Topic(html = r.text, topic_code = topic_code, topic_num = topic_num)

            # 提交[选择题目]键
            r = My_Post(url = connection_url, payload = payload, is_output = False)
            
            # 分析获取的HTML文件，并返回一个Topic类型的对象
            topics.append(Analyze_HTMl_Files_To_Topic(r.text, topic_num = topic_num))
            
            topic_num += 1
            
            time.sleep(0.01)         # 设置0.01秒的延迟
            
    return [examtime, topics]

# 将topics列表中的题目写入html文件中    
def Write_To_File(topics, filename):
    
    f = open(filename + '.html', "w", encoding='utf-8')
    
    # 写入格式
    f.write('<!DOCTYPE html><html>\n\t<head>\n\t\t<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n\t</head>\n')
    
    for topic in topics:
        f.write(topic.write())
        f.write('\n<br><br>')
    
    f.write('</html>')
    f.close()
    

# 查看科目文件是否存在，如果存在则删除已存在的科目代码
def Is_Subject_File(examtimes, chinese_names):
    # 从examtimes中拷贝一份到examtimes_copy
    examtimes_copy = examtimes.copy()
    for examtime in examtimes:
        if os.path.exists(chinese_names[examtime] + '_' + str(examtime) + '.html'):
            examtimes_copy.remove(examtime)
    
    return examtimes_copy

# 开始运行
if __name__ == '__main__':
    
    print('请输出入你的学号: ', end='')
    stuid = input()
        
    # 设置连接url
    while True:
        print('毕业补考[S]OR学年补考[T]: ', end='')
        c_str = input()
        if c_str == 'S':
            connection_url = url_stuframe + stuid
        elif c_str == 'T':
            connection_url = url_termframe + stuid
        else:
            continue
        break
    
    # 获取科目的所有题目的列表
    list_topics = []
    
    try:
        
        print()
        # 连接获取url页面
        r = My_Get(url = connection_url, c_str = Ret_Getting_Information(c_str = '获取url页面'))

        # 获取HTML中所有的考试时间
        all_examtimes = re.findall(re_html_examtime, r.text)

        # 剔除掉已经考过的科目
        list_temp = Weed_Out_Tested(connection_url = connection_url, examtimes = all_examtimes)
        new_examtimes = list_temp[0]        # 获取新的可获取的考试科目代号
        chinese_names = list_temp[1]        # 获取新的可获取的考试科目中文名

        # 剔除掉已经获取的科目
        new_new_examtimes = Is_Subject_File(new_examtimes, chinese_names)
        
        print('\n' + 
              '总共\t ' + str(len(all_examtimes)) + ' 门科目\n' + 
              '已有\t ' + str(len(all_examtimes) - len(new_examtimes)) + ' 门科目考完\n' + 
              '能获取\t ' + str(len(new_examtimes)) + ' 门科目\n' + 
              '已获取\t ' + str(len(new_examtimes) - len(new_new_examtimes)) + ' 门科目\n' + 
              '需要获取 ' + str(len(new_new_examtimes)) + ' 门科目\n')

        # 获取每科的题目url链接
        urls_simulation_test = dict()              # 题目url列表

        # 获取模拟考试页面链接
        for examtime in new_new_examtimes:
            print('\n' + examtime + ': ')
            urls_simulation_test[examtime] = Ret_url_simulation_test(connection_url, examtime)
            
        print()
        for url_key, url_value in urls_simulation_test.items():
            print(url_key + ': ' + url_value)
        print()
        
        # 循环获取所有科目的所有题目
        for url_key, url_value in urls_simulation_test.items():
            list_topics.append(Get_All_Topics(url_value, url_key))
            
        # 循环将题目写入文件中
        for topics in list_topics:
            Write_To_File(topics = topics[1], filename = chinese_names[topics[0]] + '_' + str(topics[0]))
        
        # Create_Thread_List(urls_simulation_test = urls_simulation_test)
            
        print('获取完成！')
    
    except requests.exceptions.Timeout as e:
        print(e)
        print('[请求超时]')
        
        # 如果发送异常，则循环将已获取的题目写入文件中
        for topics in list_topics:
            Write_To_File(topics = topics[1], filename = chinese_names[topics[0]] + '_' + str(topics[0]))
        
    except requests.exceptions.HTTPError as e:
        print(e)
        print('[不成功的状态码]')
        
        # 如果发送异常，则循环将已获取的题目写入文件中
        for topics in list_topics:
            Write_To_File(topics = topics[1], filename = chinese_names[topics[0]] + '_' + str(topics[0]))
    
    except requests.exceptions.ConnectionError as e:
        print(e)
        print('[网络环境异常]')
        
        # 如果发送异常，则循环将已获取的题目写入文件中
        for topics in list_topics:
            Write_To_File(topics = topics[1], filename = chinese_names[topics[0]] + '_' + str(topics[0]))