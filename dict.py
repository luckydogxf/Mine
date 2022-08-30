'''
统计 node开头的行里面3个范围（53,102),(103,122),(223,376)里面有多少个active和down的，注意53-102，103-122,223-376这3个范围里可能有没出现在文本里，比如node-245.xxxx-yy.com。 注意某些主机名字是node-xxx,有的是node-NNN.xxx-yy.com。

同时要统计   renderG开头的行的'1-202','167-181（注意这里的167-181是需要排除掉的，其实就是1-166,182-202这2个当做一个整体'这个范围里active/down的个数， 还有 '167-204','181-202'（同理排除181-202，然后当做一个整体（ 这个里的active/down的个数。范围里的主机未必在文本出现。

这个问题用python处理非常容易理解。就把文本$1,$4放字典里面，然后把既定范围放list, 判断list是否在dict的key里面，再就放一个新的dict，最后统计新的dict的active/down的数量，最后清空dict.
'''
#!/usr/bin/env python

import subprocess

spec ={'node': ((53,102),(103,122),(223,376)),

        'renderG' : (('1-166','181-202'),('167-180','203-204'))
}

cmd ="qbhosts | awk '/node/||/renderG/'"

output = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).communicate()[0]

d ={}

for i in output.splitlines():

    items = i.split()
    if not items[0].endswith("xxx.com"):
        items[0]=items[0]+".xxx.com"
    d[items[0]] = items[3]

for k,v in spec.items() :

                for  i in v:
                        # set default value for m1,m2.
                        m1=m2=None

                        if type(i[0]) == str or type(i[1]) == str :

                                begin = i[0].split("-")[0]
                                m1 = i[0].split("-")[1]
                                m2 = i[1].split("-")[0]
                                end = i[1].split("-")[1]
                                host = [ "%s-%03d.xxx.com" %(k,m ) for m in xrange(int(begin),int(end)+1) if m not in xrange(int(m1)+1,int(m2))]

                        else :
                                begin,end = i[0],i[1]
                                host = [ "%s-%03d.xxx.com" %(k,m) for m in xrange(begin,end+1) ]
                        #print "--------\n",host,"\n----------------"

                        temp = {}

                        for h in host :

                                if h in d.keys():
                                        temp[h] = d[h]

                                #else : print "%s doesn't exist."%h

                        act = len([k1 for k1,v1 in temp.items() if v1 =="active" ])
                        down = len([k1 for k1,v1 in temp.items() if v1 =="down" ])
                        # duplicate hostname node-347 and node-238

                        if m1 and m2 :

                                print "\n%s[%03d-%03d,%03d-%03d].xxx.com have %d active node(s), %d down node(s)\n" % (k,int(begin),int(m1),int(m2),int(end),act,down)

                        else:
                                print "\n%s[%03d-%03d].xxx.com have %d active node(s), %d down node(s)\n" % (k,int(begin),int(end),act,down)

                        temp.clear()
renderG-001.xxxx-yy.com     00:22:19:AE:97:90  10.7.16.1      active  1/1   /efx     G96
renderG-002.xxxx-yy.com     00:22:19:AE:97:9D  10.7.16.2      active  1/1   /efx     G96
renderG-003.xxxx-yy.com     00:22:19:AE:97:AA  10.7.16.3      active  1/1   /efx     G96
renderG-004.xxxx-yy.com     00:22:19:AE:97:B7  10.7.16.4      active  1/1   /efx     G96
renderG-005.xxxx-yy.com     00:22:19:AE:97:C4  10.7.16.5      active  1/1   /efx     G96
renderG-006.xxxx-yy.com     00:22:19:AE:971  10.7.16.6      active  1/1   /efx     G96
renderG-007.xxxx-yy.com     00:22:19:AE:97E  10.7.16.7      active  1/1   /efx     G96
renderG-008.xxxx-yy.com     00:22:19:AE:97:EB  10.7.16.8      active  1/1   /efx     G96
renderG-009.xxxx-yy.com     00:26:B9:28:47E  172.16.5.144   down    0/0   /efx     G96
renderG-009.xxxx-yy.com     00:22:19:C1:B9:0D  10.7.16.9      active  1/1   /efx     G96
renderG-009.xxxx-yy.com     00:26:B9:28:471  10.7.16.9      down    0/1   /efx     G96
renderG-010.xxxx-yy.com     00:22:19:AE:98:05  10.7.16.10     active  1/1   /efx     G96
renderG-011.xxxx-yy.com     00:22:19:AE:98:12  10.7.16.11     active  1/1   /efx     G96
renderG-012.xxxx-yy.com     00:22:19:AE:98:1F  10.7.16.12     active  1/1   /efx     G96
renderG-013.xxxx-yy.com     00:22:19:AE:98:2C  10.7.16.13     active  1/1   /efx     G96
renderG-014.xxxx-yy.com     00:22:19:AE:98:39  10.7.16.14     active  1/1   /efx     G96
renderG-015.xxxx-yy.com     00:22:19:AE:98:46  10.7.16.15     active  1/1   /efx     G96
renderG-016.xxxx-yy.com     00:22:19:AE:98:53  10.7.16.16     active  1/1   /efx     G96
renderG-017.xxxx-yy.com     00:26:B9:28:8F2  10.7.16.21     active  1/1   /efx     G96
renderG-018.xxxx-yy.com     00:26:B9:28:8FF  10.7.16.22     down    0/1   /efx     G96
renderG-019.xxxx-yy.com     00:26:B9:28:8F:C5  10.7.16.20     active  1/1   /efx     G96
renderG-020.xxxx-yy.com     00:26:B9:28:8F:B8  10.7.16.19     active  1/1   /efx     G96
renderG-021.xxxx-yy.com     00:26:B9:28:8F:AB  10.7.16.18     active  1/1   /efx     G96
renderG-022.xxxx-yy.com     00:26:B9:28:90:3A  10.7.16.29     active  1/1   /efx     G96
renderG-023.xxxx-yy.com     00:26:B9:28:90:2D  10.7.16.28     active  1/1   /efx     G96
renderG-024.xxxx-yy.com     00:26:B9:28:0F:73  10.7.16.24     active  1/1   /efx     G96
renderG-025.xxxx-yy.com     00:26:B9:28:90:47  10.7.16.30     active  1/1   /efx     G96
renderG-026.xxxx-yy.com     00:26:B9:28:90:20  10.7.16.27     active  1/1   /efx     G96
renderG-027.xxxx-yy.com     00:26:B9:28:90:13  10.7.16.26     active  1/1   /efx     G96
renderG-028.xxxx-yy.com     00:26:B9:28:90:54  10.7.16.31     active  1/1   /efx     G96
renderG-029.xxxx-yy.com     00:26:B9:28:90:06  10.7.16.25     active  1/1   /efx     G96
renderG-030.xxxx-yy.com     00:26:B9:28:90:61  10.7.16.32     active  1/1   /efx     G96
renderG-031.xxxx-yy.com     00:26:B9:28:8F:9E  10.7.16.17     active  1/1   /efx     G96
renderG-032.xxxx-yy.com     00:26:B9:28:8F:EC  10.7.16.23     active  1/1   /efx     G96
renderG-033.xxxx-yy.com     00:26:B9:28:54:FD  10.7.16.33     down    0/1   /efx     G96
renderG-034.xxxx-yy.com     00:26:B9:28:55:0A  10.7.16.34     active  1/1   /efx     G96
renderG-035.xxxx-yy.com     00:26:B9:28:55:17  10.7.16.35     active  1/1   /efx     G96
renderG-036.xxxx-yy.com     00:26:B9:28:55:24  10.7.16.36     active  1/1   /efx     G96
renderG-037.xxxx-yy.com     00:26:B9:28:55:31  10.7.16.37     active  1/1   /efx     G96
renderG-038.xxxx-yy.com     00:26:B9:28:55:3E  10.7.16.38     active  1/1   /efx     G96
renderG-039.xxxx-yy.com     00:26:B9:28:55:4B  10.7.16.39     active  1/1   /efx     G96
renderG-040.xxxx-yy.com     00:26:B9:28:55:58  10.7.16.40     active  1/1   /efx     G96
renderG-041.xxxx-yy.com     00:26:B9:28:55:65  10.7.16.41     active  1/1   /efx     G96
renderG-042.xxxx-yy.com     00:26:B9:28:55:72  10.7.16.42     active  1/1   /efx     G96
renderG-043.xxxx-yy.com     00:26:B9:28:55:7F  10.7.16.43     active  1/1   /efx     G96
renderG-044.xxxx-yy.com     00:26:B9:28:55:8C  10.7.16.44     active  1/1   /efx     G96
renderG-045.xxxx-yy.com     00:26:B9:28:55:99  10.7.16.45     active  1/1   /efx     G96
renderG-046.xxxx-yy.com     00:26:B9:28:55:A6  10.7.16.46     active  1/1   /efx     G96
renderG-047.xxxx-yy.com     00:26:B9:28:55:B3  10.7.16.47     active  1/1   /efx     G96
renderG-048.xxxx-yy.com     00:26:B9:28:55:C0  10.7.16.48     active  1/1   /efx     G96
renderG-049.xxxx-yy.com     00:26:B9:28:0E:BD  10.7.16.49     active  1/1   /efx     G96
renderG-050.xxxx-yy.com     00:26:B9:28:0E:CA  10.7.16.50     active  1/1   /efx     G96
renderG-051.xxxx-yy.com     00:26:B9:28:0E7  10.7.16.51     active  1/1   /efx     G96
renderG-052.xxxx-yy.com     00:26:B9:28:0E:E4  10.7.16.52     active  1/1   /efx     G96
renderG-054.xxxx-yy.com     00:26:B9:28:0E:FE  10.7.16.54     active  1/1   /efx     G96
renderG-055.xxxx-yy.com     00:26:B9:28:0F:0B  10.7.16.55     active  1/1   /efx     G96
renderG-056.xxxx-yy.com     00:26:B9:28:0F:18  10.7.16.56     active  1/1   /efx     G96
renderG-057.xxxx-yy.com     00:26:B9:28:0F:25  10.7.16.57     active  1/1   /efx     G96
renderG-058.xxxx-yy.com     00:26:B9:28:0F:32  10.7.16.58     active  1/1   /efx     G96
renderG-059.xxxx-yy.com     00:26:B9:28:0F:3F  10.7.16.59     active  1/1   /efx     G96
renderG-060.xxxx-yy.com     00:26:B9:28:0F:4C  10.7.16.60     active  1/1   /efx     G96
renderG-061.xxxx-yy.com     00:26:B9:28:0F:59  10.7.16.61     active  1/1   /efx     G96
renderG-062.xxxx-yy.com     00:26:B9:28:0F:66  10.7.16.62     active  1/1   /efx     G96
renderG-063.xxxx-yy.com     00:22:19:C1:B9:00  172.16.10.50   down    0/0   /efx     G96
renderG-063.xxxx-yy.com     00:22:19:C1:B9:41  172.16.5.83    active  1/1   /efx     G96
renderG-063.xxxx-yy.com     00:26:B9:28:47:C4  10.7.16.63     down    0/0   /efx     G96
renderG-064.xxxx-yy.com     00:26:B9:28:0F:80  10.7.16.64     active  1/1   /efx     G96
renderG-065.xxxx-yy.com     00:26:B9:28:C8:9C  10.7.16.65     active  1/1   /efx     G96
renderG-066.xxxx-yy.com     00:26:B9:28:C8:A9  10.7.16.66     active  1/1   /efx     G96
renderG-067.xxxx-yy.com     00:26:B9:28:C8:B6  10.7.16.67     active  1/1   /efx     G96
renderG-068.xxxx-yy.com     00:26:B9:28:C8:C3  10.7.16.68     active  1/1   /efx     G96
renderG-069.xxxx-yy.com     00:26:B9:28:C80  10.7.16.69     active  1/1   /efx     G96
renderG-070.xxxx-yy.com     00:26:B9:28:C8D  10.7.16.70     active  1/1   /efx     G96
renderG-071.xxxx-yy.com     00:26:B9:28:C8:EA  10.7.16.71     active  1/1   /efx     G96
renderG-072.xxxx-yy.com     00:26:B9:28:C8:F7  10.7.16.72     active  1/1   /efx     G96
renderG-073.xxxx-yy.com     00:26:B9:28:C9:04  10.7.16.73     active  1/1   /efx     G96
renderG-074.xxxx-yy.com     00:26:B9:28:C9:11  10.7.16.74     active  1/1   /efx     G96
renderG-075.xxxx-yy.com     00:26:B9:28:C9:1E  10.7.16.75     active  1/1   /efx     G96
renderG-076.xxxx-yy.com     00:26:B9:28:C9:2B  10.7.16.76     active  1/1   /efx     G96
renderG-077.xxxx-yy.com     00:26:B9:28:C9:38  10.7.16.77     active  1/1   /efx     G96
renderG-078.xxxx-yy.com     00:26:B9:28:C9:45  10.7.16.78     active  1/1   /efx     G96
renderG-079.xxxx-yy.com     00:26:B9:28:C9:52  10.7.16.79     active  1/1   /efx     G96
renderG-080.xxxx-yy.com     00:26:B9:28:C9:5F  10.7.16.80     active  1/1   /efx     G96
