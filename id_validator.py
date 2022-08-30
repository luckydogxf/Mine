#!/usr/bin/env python
'''

已知身*份*证*号码的数据结构如下：

1、身*份*证*号码的结构
公民身份号码是特征组合码，由十七位数字本体码和一位校验码组成。排列顺序从左至右依次为：六位数字地址码，八位数字出生日期码，三位数字顺序码和一位数字校验码。

2、地址码（6位）（110000-659004）
表示编码对象常住户口所在县(市、旗、区)的行政区划代码，按GB/T2260的规定执行。身*份*证*号码的前两位表示的是省，第三到四位表示的是市，第五到六位表示的是区县。

3、出生日期码（8位）（190101-$(date +%Y%m%d))
表示编码对象出生的年、月、日，按GB/T7408的规定执行，年、月、日代码之间不用分隔符。

4、顺序码（3位）(001-999)
表示在同一地址码所标识的区域范围内，对同年、同月、同日出生的人编定的顺序号，顺序码的奇数分配给男性，偶数分配给女性。

5、校验码（1位）(0-9,X)
（1）十七位数字本体码加权求和公式
     S = Sum(Ai * Wi), i = 0, ... , 16 ，先对前17位数字的权求和
     其中： Ai:表示第i位置上的身*份*证*号码数字值
            Wi:表示第i位置上的加权因子 （Wi: 7 9 10 5 8 4 2 1 6 3 7 9 10 5 8 4 2 ）
（2）计算模
     Y = mod(S, 11)

（3）通过模得到对应的校验码
     Y: 0 1 2 3 4 5 6 7 8 9 10
校验码: 1 0 X 9 8 7 6 5 4 3 2
'''

import time,sys

last_code={"0":"1","1":"0","2":"x","3":"9","4":"8","5":"7","6":"6","7":"5","8":"4","9":"3","10":"2"}
check_sum= [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]

def validator(id_card):

    region=int(id_card[0:6])
    birth=int(id_card[6:14])
    gender=id_card[14:17]
    s18=id_card[17]
    s17=id_card[0:17]

    if region not in [d for d in xrange(110000,659005)] :
              sys.exit("invalid region")
    elif birth not in [d for d in xrange(19000101,int(time.strftime("%Y%m%d", time.localtime()))+1)] :
              sys.exit("invalid birthday")
    elif gender not in ["%03d"%d for d in xrange(1,1000)] :
         # int(gender)%2==0,female,else male
                    sys.exit("invalid gender")

    total = 0
    for i in xrange(17):
       total += int(s17[i]) * check_sum[i]
    result = total%11

    if last_code[str(result)] == s18 :
      print "ok " + id_card
    else :
       print "invalid, checksum is %s"%last_code[str(result)]

validator("342626199412250537")

'''
还可以简化一下，比如比较地区的，110000--659005还有生日的19000101到现在，区间太大了，可以把输入的跟最大和最小的比较，比如region <110000 || region >659005
就直接break了，日期也一样，这样效率高很多。'''
