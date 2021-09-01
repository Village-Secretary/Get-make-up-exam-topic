'''
Author: Village-Secretary
Date: 2021-02-01 21:40:10
LastEditTime: 2021-09-01 15:20:42
LastEditors: Please set LastEditors
Description: 单个题目类
FilePath: \DemoPy\.vscode\Topic.py
'''

# 题目文本格式为：
#
# 1.  直流电机的电枢绕组的电势是（ ）。
# [A] 交流电势
# [B] 直流电势
# [C] 励磁电势
# [D] 换向电势
# 参考答案：A
# 试题解析：直流电机的电枢绕组的电势是交流电势。
#


import re

# 获取答案文本中所显示的选项正则表达式
re_options_answer = r'参考答案：([A|B|C|D])'


# 题目类
class Topic:
    def __init__(self):
        self.__number = 0                                         # 题号
        self.__title = ''                                         # 标题
        self.__options = { 'A':'', 'B':'', 'C':'', 'D':'' }       # 选项
        self.__judgment = False                                   # 判断
        self.__answer = ''                                        # 答案
        self.__analyze = ''                                       # 解析
    
    
    '''
    description: 解析答案文本中所显示的选项(单字符)，返回A、B、C、D中的一个
    param {*} self
    return {str}
    '''    
    def __ret_options_answer(self):
        re_list = re.findall(re_options_answer, self.__answer)
        c_answer = re_list[0]       # 获取匹配的答案字符
        return c_answer
    
    
    '''
    description: 返回汇总4个选项的所有文本
    param {*} self
    return {str}
    '''
    def __ret_options_txt(self):
        c_answer = self.__ret_options_answer()             # 获取答案选项
        options_txt = ''
        for option_key, option_value in self.__options.items():
            # 判断是否为答案选项，如果是，则html红色背景代码
            if c_answer == option_key:
                options_txt += '<p style=\"background-color:Red;\">'
            else:
                options_txt += '<p>'
            options_txt += '[' + option_key + '] ' + option_value + '</p>\r\n'
        return options_txt
    
    
    '''
    description: 输出一个完整的题目文本，包含题号、标题、选项、答案、解析文本
    param {*} self
    return {*}
    '''    
    def write(self):
        # 填充标题文本
        topic_txt = '<p>' + str(self.__number) + '.\t' + self.__title + "</p>\r\n"
        
        # 填充选项文本
        # 根据此题是否为判断题来选择是否用选项文本填充topic_txt
        if False == self.__judgment:
            topic_txt += self.__ret_options_txt()
            # 填充答案
            topic_txt += '<p>' + self.__answer + "</p>\r\n"
        else:
            # 填充答案
            topic_txt += '<p  style=\"background-color:Red;\">' + self.__answer + "</p>\r\n"
        
        # 填充解析
        topic_txt += '<p>' + self.__analyze + "</p>\r\n"
        
        return topic_txt
    
    
    '''
    description: 读取填充标题、选项、判断、答案成员变量
    param {*} self
    param {str} title
    param {dict} options
    param {bool} judgment
    param {str} answer
    return {*}
    '''
    def read(self, number, title, options, judgment, answer, analyze):
        self.__number = number
        self.__title = title
        self.__options = options
        self.__judgment = judgment
        self.__answer = answer
        self.__analyze = analyze
        
    

    
# # 测试输出

# number = 1
# title = '直流电机的电枢绕组的电势是（ ）。'
# options = { 'A':'<img src=\"C:\\Users\\22485\\Desktop\\头像.jpg\" style=\"height:25px\" />', 'B':'直流电势', 'C':'励磁电势', 'D':'换向电势' }
# judgment = False
# answer = '参考答案：A'
# analyze = '试题解析：直流电机的电枢绕组的电势是交流电势。'

# f = open('text.html', "w")

# text = Topic()
# text.read(number, title, options, judgment, answer, analyze)

# f.write(text.write())

# f.close()