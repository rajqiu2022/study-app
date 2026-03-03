"""
课本知识大纲数据 - 小学1-6年级 + 初中7-9年级
按照人教版/部编版课程标准整理
结构: { "年级": { "学科id": { "上册": [...单元], "下册": [...单元] } } }
每个单元: { "unit": "单元名称", "topics": ["知识点1", "知识点2", ...] }
"""

CURRICULUM = {
    "一年级": {
        "math": {
            "上册": [
                {"unit": "第一单元 准备课", "topics": ["数一数", "比多少"]},
                {"unit": "第二单元 位置", "topics": ["上下前后", "左右"]},
                {"unit": "第三单元 1~5的认识和加减法", "topics": ["1~5的认识", "比大小", "第几", "分与合", "加法", "减法", "0的认识和加减法"]},
                {"unit": "第四单元 认识图形（一）", "topics": ["长方体、正方体、圆柱、球的认识"]},
                {"unit": "第五单元 6~10的认识和加减法", "topics": ["6和7的认识", "8和9的认识", "10的认识", "连加连减", "加减混合"]},
                {"unit": "第六单元 11~20各数的认识", "topics": ["数数、读数", "写数", "10加几和相应的减法"]},
                {"unit": "第七单元 认识钟表", "topics": ["认识整时"]},
                {"unit": "第八单元 20以内的进位加法", "topics": ["9加几", "8、7、6加几", "5、4、3、2加几"]},
            ],
            "下册": [
                {"unit": "第一单元 认识图形（二）", "topics": ["认识长方形、正方形、三角形、圆", "拼一拼"]},
                {"unit": "第二单元 20以内的退位减法", "topics": ["十几减9", "十几减8、7、6", "十几减5、4、3、2"]},
                {"unit": "第三单元 分类与整理", "topics": ["按单一标准分类", "按不同标准分类"]},
                {"unit": "第四单元 100以内数的认识", "topics": ["数数、数的组成", "读数、写数", "数的顺序", "比较大小", "整十数加一位数及减法"]},
                {"unit": "第五单元 认识人民币", "topics": ["认识人民币", "简单的计算"]},
                {"unit": "第六单元 100以内的加法和减法（一）", "topics": ["整十数加减整十数", "两位数加一位数和整十数", "两位数减一位数和整十数"]},
                {"unit": "第七单元 找规律", "topics": ["图形和数字的变化规律"]},
            ],
        },
        "chinese": {
            "上册": [
                {"unit": "第一单元 识字", "topics": ["天地人", "金木水火土", "口耳目", "日月水火", "对韵歌"]},
                {"unit": "第二单元 汉语拼音", "topics": ["声母", "韵母", "整体认读音节", "拼读"]},
                {"unit": "第三单元 课文", "topics": ["秋天", "小小的船", "江南", "四季"]},
                {"unit": "第四单元 识字", "topics": ["画", "大小多少", "小书包", "日月明", "升国旗"]},
                {"unit": "第五单元 课文", "topics": ["影子", "比尾巴", "青蛙写诗", "雨点儿"]},
                {"unit": "第六单元 课文", "topics": ["明天要远足", "大还是小", "项链"]},
                {"unit": "第七单元 课文", "topics": ["雪地里的小画家", "乌鸦喝水", "小蜗牛"]},
            ],
            "下册": [
                {"unit": "第一单元 识字", "topics": ["春夏秋冬", "姓氏歌", "小青蛙", "猜字谜"]},
                {"unit": "第二单元 课文", "topics": ["吃水不忘挖井人", "我多想去看看", "一个接一个", "四个太阳"]},
                {"unit": "第三单元 识字", "topics": ["小公鸡和小鸭子", "树和喜鹊", "怎么都快乐"]},
                {"unit": "第四单元 课文", "topics": ["静夜思", "夜色", "端午粽", "彩虹"]},
                {"unit": "第五单元 识字", "topics": ["动物儿歌", "古对今", "操场上", "人之初"]},
                {"unit": "第六单元 课文", "topics": ["古诗二首", "荷叶圆圆", "要下雨了"]},
                {"unit": "第七单元 课文", "topics": ["文具的家", "一分钟", "动物王国开大会", "小猴子下山"]},
            ],
        },
        "english": {
            "上册": [
                {"unit": "Unit 1 Hello!", "topics": ["Hello/Hi打招呼", "I'm...自我介绍", "文具单词：pencil, pen, ruler, eraser, crayon"]},
                {"unit": "Unit 2 Colours", "topics": ["颜色单词：red, yellow, green, blue, black, white, orange, brown", "What colour is it?"]},
                {"unit": "Unit 3 Look at me!", "topics": ["身体部位：head, eye, ear, nose, mouth, face, arm, hand, leg, foot", "Look at me!"]},
            ],
            "下册": [
                {"unit": "Unit 1 My classroom", "topics": ["教室物品：window, door, desk, chair, blackboard", "What's in the classroom?"]},
                {"unit": "Unit 2 My schoolbag", "topics": ["书本文具：schoolbag, book, pen, pencil box", "What's in your schoolbag?"]},
                {"unit": "Unit 3 My friends", "topics": ["描述朋友外貌", "He/She is..."]},
            ],
        },
        "science": {
            "上册": [
                {"unit": "第一单元 植物", "topics": ["我们知道的植物", "观察一棵植物", "植物的叶"]},
                {"unit": "第二单元 比较与测量", "topics": ["在观察中比较", "起点和终点", "用手来测量"]},
            ],
            "下册": [
                {"unit": "第一单元 我们周围的物体", "topics": ["发现物体的特征", "谁轻谁重", "认识物体的形状"]},
                {"unit": "第二单元 动物", "topics": ["我们知道的动物", "校园里的动物", "观察一种动物"]},
            ],
        },
    },
    "二年级": {
        "math": {
            "上册": [
                {"unit": "第一单元 长度单位", "topics": ["厘米和米的认识", "线段的认识"]},
                {"unit": "第二单元 100以内的加法和减法（二）", "topics": ["两位数加两位数", "两位数减两位数", "连加连减和加减混合", "解决问题"]},
                {"unit": "第三单元 角的初步认识", "topics": ["认识角", "画角", "直角的认识"]},
                {"unit": "第四单元 表内乘法（一）", "topics": ["乘法的初步认识", "2~6的乘法口诀"]},
                {"unit": "第五单元 观察物体（一）", "topics": ["从不同位置观察物体"]},
                {"unit": "第六单元 表内乘法（二）", "topics": ["7的乘法口诀", "8的乘法口诀", "9的乘法口诀"]},
            ],
            "下册": [
                {"unit": "第一单元 数据收集整理", "topics": ["收集数据", "记录数据", "简单统计表"]},
                {"unit": "第二单元 表内除法（一）", "topics": ["除法的初步认识", "用2~6的乘法口诀求商"]},
                {"unit": "第三单元 图形的运动（一）", "topics": ["对称", "平移和旋转"]},
                {"unit": "第四单元 表内除法（二）", "topics": ["用7、8、9的乘法口诀求商", "解决问题"]},
                {"unit": "第五单元 混合运算", "topics": ["混合运算的顺序", "有小括号的混合运算"]},
                {"unit": "第六单元 有余数的除法", "topics": ["余数的认识", "有余数的除法计算", "解决问题"]},
                {"unit": "第七单元 万以内数的认识", "topics": ["1000以内数的认识", "10000以内数的认识", "近似数"]},
                {"unit": "第八单元 克和千克", "topics": ["认识克", "认识千克"]},
            ],
        },
        "chinese": {
            "上册": [
                {"unit": "第一单元 课文", "topics": ["小蝌蚪找妈妈", "我是什么", "植物妈妈有办法"]},
                {"unit": "第二单元 识字", "topics": ["场景歌", "树之歌", "拍手歌", "田家四季歌"]},
                {"unit": "第三单元 课文", "topics": ["曹冲称象", "玲玲的画", "一封信", "妈妈睡了"]},
                {"unit": "第四单元 课文", "topics": ["古诗二首（登鹳雀楼、望庐山瀑布）", "黄山奇石", "日月潭", "葡萄沟"]},
                {"unit": "第五单元 课文", "topics": ["坐井观天", "寒号鸟", "我要的是葫芦"]},
                {"unit": "第六单元 课文", "topics": ["大禹治水", "朱德的扁担", "难忘的泼水节"]},
                {"unit": "第七单元 课文", "topics": ["古诗二首（夜宿山寺、敕勒歌）", "雾在哪里", "雪孩子"]},
            ],
            "下册": [
                {"unit": "第一单元 课文", "topics": ["古诗二首（村居、咏柳）", "找春天", "开满鲜花的小路", "邓小平爷爷植树"]},
                {"unit": "第二单元 课文", "topics": ["雷锋叔叔你在哪里", "千人糕", "一匹出色的马"]},
                {"unit": "第三单元 识字", "topics": ["神州谣", "传统节日", "贝的故事", "中国美食"]},
                {"unit": "第四单元 课文", "topics": ["彩色的梦", "枫树上的喜鹊", "沙滩上的童话", "我是一只小虫子"]},
                {"unit": "第五单元 课文", "topics": ["寓言二则（亡羊补牢、揠苗助长）", "画杨桃", "小马过河"]},
                {"unit": "第六单元 课文", "topics": ["古诗二首（晓出净慈寺送林子方、绝句）", "雷雨", "要是你在野外迷了路", "太空生活趣事多"]},
                {"unit": "第七单元 课文", "topics": ["大象的耳朵", "蜘蛛开店", "青蛙卖泥塘", "小毛虫"]},
            ],
        },
        "english": {
            "上册": [
                {"unit": "Unit 1 My family", "topics": ["家庭成员：father, mother, brother, sister, grandpa, grandma", "This is my..."]},
                {"unit": "Unit 2 My body", "topics": ["身体部位复习与拓展", "Touch your..."]},
                {"unit": "Unit 3 Animals", "topics": ["动物单词：cat, dog, bird, fish, monkey, panda, tiger, elephant", "I like..."]},
            ],
            "下册": [
                {"unit": "Unit 1 My day", "topics": ["日常活动：get up, go to school, have lunch, go home", "What time is it?"]},
                {"unit": "Unit 2 Weather", "topics": ["天气单词：sunny, rainy, cloudy, windy, snowy", "How's the weather?"]},
                {"unit": "Unit 3 Seasons", "topics": ["四季：spring, summer, autumn/fall, winter", "What season do you like?"]},
            ],
        },
        "science": {
            "上册": [
                {"unit": "第一单元 我们的地球家园", "topics": ["地球家园中有什么", "土壤——动植物的乐园", "太阳的位置和方向"]},
                {"unit": "第二单元 材料", "topics": ["我们生活中的物品", "各种各样的材料", "纸的特性"]},
            ],
            "下册": [
                {"unit": "第一单元 磁铁", "topics": ["磁铁能吸引什么", "磁铁怎样吸引物体", "磁铁的两极"]},
                {"unit": "第二单元 声音", "topics": ["听听声音", "声音是怎样产生的", "声音的高低变化"]},
            ],
        },
    },
    "三年级": {
        "math": {
            "上册": [
                {"unit": "第一单元 时、分、秒", "topics": ["秒的认识", "时间的计算"]},
                {"unit": "第二单元 万以内的加法和减法（一）", "topics": ["两位数加减两位数", "几百几十加减几百几十"]},
                {"unit": "第三单元 测量", "topics": ["毫米、分米的认识", "千米的认识", "吨的认识"]},
                {"unit": "第四单元 万以内的加法和减法（二）", "topics": ["三位数加三位数", "三位数减三位数", "解决问题"]},
                {"unit": "第五单元 倍的认识", "topics": ["倍的认识", "求一个数是另一个数的几倍", "求一个数的几倍是多少"]},
                {"unit": "第六单元 多位数乘一位数", "topics": ["口算乘法", "笔算乘法", "解决问题"]},
                {"unit": "第七单元 长方形和正方形", "topics": ["四边形的认识", "周长的认识", "长方形和正方形的周长"]},
                {"unit": "第八单元 分数的初步认识", "topics": ["认识几分之一", "认识几分之几", "分数的简单计算"]},
            ],
            "下册": [
                {"unit": "第一单元 位置与方向（一）", "topics": ["认识东南西北", "认识东南、东北、西南、西北"]},
                {"unit": "第二单元 除数是一位数的除法", "topics": ["口算除法", "笔算除法"]},
                {"unit": "第三单元 复式统计表", "topics": ["认识复式统计表", "运用复式统计表"]},
                {"unit": "第四单元 两位数乘两位数", "topics": ["口算乘法", "笔算乘法", "解决问题"]},
                {"unit": "第五单元 面积", "topics": ["面积和面积单位", "长方形正方形的面积计算", "面积单位间的进率"]},
                {"unit": "第六单元 年、月、日", "topics": ["年月日的认识", "平年和闰年", "24时计时法"]},
                {"unit": "第七单元 小数的初步认识", "topics": ["认识小数", "小数的大小比较", "简单的小数加减法"]},
            ],
        },
        "chinese": {
            "上册": [
                {"unit": "第一单元", "topics": ["大青树下的小学", "花的学校", "不懂就要问"]},
                {"unit": "第二单元", "topics": ["古诗三首（山行、赠刘景文、夜书所见）", "铺满金色巴掌的水泥道", "秋天的雨", "听听秋的声音"]},
                {"unit": "第三单元", "topics": ["去年的树", "那一定会很好", "在牛肚子里旅行", "一块奶酪"]},
                {"unit": "第四单元", "topics": ["总也倒不了的老屋", "胡萝卜先生的长胡子", "小狗学叫"]},
                {"unit": "第五单元", "topics": ["搭船的鸟", "金色的草地"]},
                {"unit": "第六单元", "topics": ["古诗三首（望天门山、饮湖上初晴后雨、望洞庭）", "富饶的西沙群岛", "海滨小城", "美丽的小兴安岭"]},
                {"unit": "第七单元", "topics": ["大自然的声音", "父亲树林和鸟", "带刺的朋友"]},
                {"unit": "第八单元", "topics": ["司马光", "掌声", "灰雀", "手术台就是阵地"]},
            ],
            "下册": [
                {"unit": "第一单元", "topics": ["古诗三首（绝句、惠崇春江晚景、三衢道中）", "燕子", "荷花", "昆虫备忘录"]},
                {"unit": "第二单元", "topics": ["守株待兔", "陶罐和铁罐", "鹿角和鹿腿", "池子与河流"]},
                {"unit": "第三单元", "topics": ["纸的发明", "赵州桥", "一幅名扬中外的画"]},
                {"unit": "第四单元", "topics": ["花钟", "蜜蜂", "小虾"]},
                {"unit": "第五单元", "topics": ["小真的长头发", "我变成了一棵树"]},
                {"unit": "第六单元", "topics": ["童年的水墨画", "剃头大师", "肥皂泡", "我不能失信"]},
                {"unit": "第七单元", "topics": ["我们奇妙的世界", "海底世界", "火烧云"]},
                {"unit": "第八单元", "topics": ["慢性子裁缝和急性子顾客", "方帽子店", "漏", "枣核"]},
            ],
        },
        "english": {
            "上册": [
                {"unit": "Unit 1 Hello!", "topics": ["Hello/Hi/Goodbye打招呼告别", "What's your name? My name is...", "文具：ruler, pencil, eraser, crayon, pen, pencil box, book, bag"]},
                {"unit": "Unit 2 Colours", "topics": ["颜色：red, green, yellow, blue, white, black, orange, brown", "I see... Show me..."]},
                {"unit": "Unit 3 Look at me!", "topics": ["五官身体：head, face, ear, eye, nose, mouth, arm, hand, finger, leg, foot, body"]},
                {"unit": "Unit 4 We love animals", "topics": ["动物：cat, dog, monkey, duck, panda, pig, bird, bear, elephant, tiger", "What's this? It's a..."]},
                {"unit": "Unit 5 Let's eat!", "topics": ["食物饮料：bread, juice, egg, milk, water, cake, fish, rice", "I'd like some... Have some..."]},
                {"unit": "Unit 6 Happy birthday!", "topics": ["数字1-10", "How old are you? I'm... Happy birthday!"]},
            ],
            "下册": [
                {"unit": "Unit 1 Welcome back to school!", "topics": ["国家：UK, Canada, USA, China", "I'm from... Where are you from?", "boy, girl, teacher, student"]},
                {"unit": "Unit 2 My family", "topics": ["家庭成员：father, mother, man, woman, sister, brother, grandmother, grandfather", "Who's that...? He's/She's my..."]},
                {"unit": "Unit 3 At the zoo", "topics": ["动物特征：big, small, long, short, tall, thin, fat", "It's so... It has..."]},
                {"unit": "Unit 4 Where is my car?", "topics": ["位置介词：in, on, under", "Where is...? It's in/on/under the..."]},
                {"unit": "Unit 5 Do you like pears?", "topics": ["水果：apple, pear, orange, banana, watermelon, strawberry, grape", "Do you like...? Yes, I do. / No, I don't."]},
                {"unit": "Unit 6 How many?", "topics": ["数字11-20", "How many...do you see/have? I see/have..."]},
            ],
        },
        "science": {
            "上册": [
                {"unit": "第一单元 水", "topics": ["水到哪里去了", "水沸腾了", "水结冰了", "冰融化了", "水的三态变化"]},
                {"unit": "第二单元 空气", "topics": ["感受空气", "空气能占据空间吗", "压缩空气", "空气有质量吗"]},
                {"unit": "第三单元 天气", "topics": ["我们关心天气", "认识气温计", "测量降水量", "观察风"]},
            ],
            "下册": [
                {"unit": "第一单元 植物的生长变化", "topics": ["种子里孕育着新生命", "种植凤仙花", "我们的凤仙花出苗了"]},
                {"unit": "第二单元 动物的一生", "topics": ["迎接蚕宝宝", "蚕长大了", "蚕变了新模样"]},
                {"unit": "第三单元 太阳地球和月球", "topics": ["仰望天空", "阳光下物体的影子", "影子的秘密"]},
            ],
        },
    },
    "四年级": {
        "math": {
            "上册": [
                {"unit": "第一单元 大数的认识", "topics": ["亿以内数的认识", "亿以内数的读写", "数的大小比较", "近似数", "亿以上数的认识"]},
                {"unit": "第二单元 公顷和平方千米", "topics": ["公顷的认识", "平方千米的认识"]},
                {"unit": "第三单元 角的度量", "topics": ["线段、直线和射线", "角的度量", "角的分类", "画角"]},
                {"unit": "第四单元 三位数乘两位数", "topics": ["口算乘法", "笔算乘法", "常见的数量关系"]},
                {"unit": "第五单元 平行四边形和梯形", "topics": ["垂直与平行", "平行四边形的认识", "梯形的认识"]},
                {"unit": "第六单元 除数是两位数的除法", "topics": ["口算除法", "笔算除法", "商的变化规律"]},
                {"unit": "第七单元 条形统计图", "topics": ["认识条形统计图"]},
            ],
            "下册": [
                {"unit": "第一单元 四则运算", "topics": ["加减法的意义和各部分关系", "乘除法的意义和各部分关系", "括号"]},
                {"unit": "第二单元 观察物体（二）", "topics": ["从不同位置观察立体图形"]},
                {"unit": "第三单元 运算定律", "topics": ["加法交换律和结合律", "乘法交换律和结合律", "乘法分配律"]},
                {"unit": "第四单元 小数的意义和性质", "topics": ["小数的意义", "小数的性质", "小数的大小比较", "小数点移动引起小数大小变化", "小数与单位换算", "近似数"]},
                {"unit": "第五单元 三角形", "topics": ["三角形的认识", "三角形的分类", "三角形的内角和"]},
                {"unit": "第六单元 小数的加法和减法", "topics": ["小数加减法", "小数加减混合运算"]},
                {"unit": "第七单元 图形的运动（二）", "topics": ["轴对称", "平移"]},
                {"unit": "第八单元 平均数与条形统计图", "topics": ["平均数", "复式条形统计图"]},
            ],
        },
        "chinese": {
            "上册": [
                {"unit": "第一单元", "topics": ["观潮", "走月亮", "现代诗二首", "繁星"]},
                {"unit": "第二单元", "topics": ["一个豆荚里的五粒豆", "蝙蝠和雷达", "呼风唤雨的世纪", "蝴蝶的家"]},
                {"unit": "第三单元", "topics": ["古诗三首（暮江吟、题西林壁、雪梅）", "爬山虎的脚", "蟋蟀的住宅"]},
                {"unit": "第四单元", "topics": ["盘古开天地", "精卫填海", "普罗米修斯", "女娲补天"]},
                {"unit": "第五单元", "topics": ["麻雀", "爬天都峰"]},
                {"unit": "第六单元", "topics": ["牛和鹅", "一只窝囊的大老虎", "陀螺"]},
                {"unit": "第七单元", "topics": ["古诗三首（出塞、凉州词、夏日绝句）", "为中华之崛起而读书", "梅兰芳蓄须"]},
                {"unit": "第八单元", "topics": ["王戎不取道旁李", "西门豹治邺", "故事二则"]},
            ],
            "下册": [
                {"unit": "第一单元", "topics": ["古诗词三首（四时田园杂兴、宿新市徐公店、清平乐·村居）", "乡下人家", "天窗", "三月桃花水"]},
                {"unit": "第二单元", "topics": ["琥珀", "飞向蓝天的恐龙", "纳米技术就在我们身边", "千年梦圆在今朝"]},
                {"unit": "第三单元", "topics": ["短诗三首", "绿", "白桦", "在天晴了的时候"]},
                {"unit": "第四单元", "topics": ["猫", "母鸡", "白鹅"]},
                {"unit": "第五单元", "topics": ["海上日出", "记金华的双龙洞"]},
                {"unit": "第六单元", "topics": ["小英雄雨来", "我们家的男子汉", "芦花鞋"]},
                {"unit": "第七单元", "topics": ["古诗三首（芙蓉楼送辛渐、塞下曲、墨梅）", "文言文二则（囊萤夜读、铁杵成针）", "黄继光"]},
                {"unit": "第八单元", "topics": ["宝葫芦的秘密", "巨人的花园", "海的女儿"]},
            ],
        },
        "english": {
            "上册": [
                {"unit": "Unit 1 My classroom", "topics": ["教室物品：classroom, window, door, picture, blackboard, light, floor, wall", "What's in the classroom? Let me/us clean..."]},
                {"unit": "Unit 2 My schoolbag", "topics": ["科目书本：schoolbag, maths book, English book, Chinese book, storybook, notebook", "What's in your schoolbag? An English book..."]},
                {"unit": "Unit 3 My friends", "topics": ["外貌描述：strong, thin, tall, short, quiet, friendly", "My friend is... He/She has..."]},
                {"unit": "Unit 4 My home", "topics": ["房间：bedroom, living room, study, kitchen, bathroom", "Where is/are...? Is he/she in the...?"]},
                {"unit": "Unit 5 Dinner's ready", "topics": ["食物餐具：beef, chicken, noodles, vegetables, soup, knife, fork, spoon, chopsticks", "What would you like? I'd like some..."]},
                {"unit": "Unit 6 Meet my family!", "topics": ["家庭与职业：family, parents, uncle, aunt, baby, doctor, driver, nurse, farmer, cook", "How many people are there in your family?"]},
            ],
            "下册": [
                {"unit": "Unit 1 My school", "topics": ["学校设施：playground, library, art room, music room, first floor, second floor", "Where is the...? It's on the... floor."]},
                {"unit": "Unit 2 What time is it?", "topics": ["时间表达：o'clock, time for...", "What time is it? It's... o'clock. Time for/to..."]},
                {"unit": "Unit 3 Weather", "topics": ["天气：warm, cold, cool, hot, sunny, rainy, cloudy, windy, snowy", "What's the weather like? It's... Can I go outside?"]},
                {"unit": "Unit 4 At the farm", "topics": ["农场动物蔬菜：horse, cow, sheep, hen, tomato, potato, carrot, green beans", "What are these/those? They're... Are these...?"]},
                {"unit": "Unit 5 My clothes", "topics": ["衣物：clothes, hat, dress, skirt, pants, shirt, jacket, shoes, socks", "Whose...is this/are these? It's/They're..."]},
                {"unit": "Unit 6 Shopping", "topics": ["购物：how much, pretty, expensive, cheap, nice, try on, size", "Can I help you? How much is/are...?"]},
            ],
        },
        "science": {
            "上册": [
                {"unit": "第一单元 声音", "topics": ["听听声音", "声音是怎样产生的", "声音是怎样传播的", "我们是怎样听到声音的"]},
                {"unit": "第二单元 呼吸与消化", "topics": ["感受我们的呼吸", "呼吸与健康生活", "食物在体内的旅行"]},
                {"unit": "第三单元 运动和力", "topics": ["让小车运动起来", "用气球驱动小车", "弹簧测力计", "运动与摩擦力"]},
            ],
            "下册": [
                {"unit": "第一单元 植物的生长变化", "topics": ["种子里孕育着新生命", "种植凤仙花", "种子长出了根"]},
                {"unit": "第二单元 电路", "topics": ["电和我们的生活", "点亮小灯泡", "简易电路", "电路出故障了"]},
                {"unit": "第三单元 岩石与土壤", "topics": ["岩石与矿物", "制作岩石和矿物标本", "认识几种常见的岩石"]},
            ],
        },
    },
    "五年级": {
        "math": {
            "上册": [
                {"unit": "第一单元 小数乘法", "topics": ["小数乘整数", "小数乘小数", "积的近似数", "整数乘法运算定律推广到小数"]},
                {"unit": "第二单元 位置", "topics": ["用数对确定位置"]},
                {"unit": "第三单元 小数除法", "topics": ["小数除以整数", "一个数除以小数", "商的近似数", "循环小数", "用计算器探索规律"]},
                {"unit": "第四单元 可能性", "topics": ["可能性", "掷一掷"]},
                {"unit": "第五单元 简易方程", "topics": ["用字母表示数", "方程的意义", "解方程", "用方程解决问题"]},
                {"unit": "第六单元 多边形的面积", "topics": ["平行四边形的面积", "三角形的面积", "梯形的面积", "组合图形的面积"]},
                {"unit": "第七单元 植树问题", "topics": ["植树问题的三种情况"]},
            ],
            "下册": [
                {"unit": "第一单元 观察物体（三）", "topics": ["从不同方向观察物体"]},
                {"unit": "第二单元 因数与倍数", "topics": ["因数和倍数的认识", "2、5、3的倍数的特征", "质数和合数"]},
                {"unit": "第三单元 长方体和正方体", "topics": ["长方体和正方体的认识", "表面积", "体积和体积单位", "容积和容积单位"]},
                {"unit": "第四单元 分数的意义和性质", "topics": ["分数的意义", "真分数和假分数", "分数的基本性质", "约分", "通分", "分数和小数的互化"]},
                {"unit": "第五单元 图形的运动（三）", "topics": ["旋转"]},
                {"unit": "第六单元 分数的加法和减法", "topics": ["同分母分数加减法", "异分母分数加减法", "分数加减混合运算"]},
                {"unit": "第七单元 折线统计图", "topics": ["单式折线统计图", "复式折线统计图"]},
            ],
        },
        "chinese": {
            "上册": [
                {"unit": "第一单元", "topics": ["白鹭", "落花生", "桂花雨", "珍珠鸟"]},
                {"unit": "第二单元", "topics": ["搭石", "将相和", "什么比猎豹的速度更快"]},
                {"unit": "第三单元", "topics": ["猎人海力布", "牛郎织女"]},
                {"unit": "第四单元", "topics": ["古诗三首（示儿、题临安邸、己亥杂诗）", "少年中国说", "圆明园的毁灭", "小岛"]},
                {"unit": "第五单元", "topics": ["太阳", "松鼠"]},
                {"unit": "第六单元", "topics": ["慈母情深", "父爱之舟", "精彩极了和糟糕透了"]},
                {"unit": "第七单元", "topics": ["古诗词三首（山居秋暝、枫桥夜泊、长相思）", "四季之美", "鸟的天堂", "月迹"]},
                {"unit": "第八单元", "topics": ["古人谈读书", "忆读书", "我的长生果"]},
            ],
            "下册": [
                {"unit": "第一单元", "topics": ["古诗三首（四时田园杂兴、稚子弄冰、村晚）", "祖父的园子", "月是故乡明", "梅花魂"]},
                {"unit": "第二单元", "topics": ["草船借箭", "景阳冈", "猴王出世", "红楼春趣"]},
                {"unit": "第三单元", "topics": ["综合性学习：遨游汉字王国"]},
                {"unit": "第四单元", "topics": ["他像一棵挺脱的树", "两茎灯草", "刷子李"]},
                {"unit": "第五单元", "topics": ["人物描写一组", "自相矛盾", "田忌赛马"]},
                {"unit": "第六单元", "topics": ["神奇的探险之旅"]},
                {"unit": "第七单元", "topics": ["威尼斯的小艇", "牧场之国", "金字塔"]},
                {"unit": "第八单元", "topics": ["杨氏之子", "手指", "童年的发现"]},
            ],
        },
        "english": {
            "上册": [
                {"unit": "Unit 1 What's he like?", "topics": ["描述人物：old, young, funny, kind, strict, polite, clever, hard-working, helpful, shy", "Who's your...? He/She is... Is he/she...?"]},
                {"unit": "Unit 2 My week", "topics": ["星期：Monday~Sunday", "科目：Chinese, English, maths, PE, music, art, science", "What do you have on...? I have..."]},
                {"unit": "Unit 3 What would you like?", "topics": ["食物饮料：ice cream, tea, hamburger, sandwich, salad", "What would you like to eat/drink? I'd like... My/Her/His favourite food is..."]},
                {"unit": "Unit 4 What can you do?", "topics": ["才艺活动：sing, dance, draw cartoons, do kung fu, play the pipa/basketball/ping-pong", "What can you do? I can... Can you...?"]},
                {"unit": "Unit 5 There is a big bed", "topics": ["家具物品：clock, plant, bottle, photo, bike, water bottle, in front of, beside, behind, between", "There is/are... Where is...?"]},
                {"unit": "Unit 6 In a nature park", "topics": ["自然景物：forest, river, lake, mountain, hill, tree, bridge, building, village, house", "Is there a...? Yes, there is./No, there isn't. Are there any...?"]},
            ],
            "下册": [
                {"unit": "Unit 1 My day", "topics": ["日常活动：eat breakfast/lunch/dinner, do morning exercises, have...class, play sports, clean my room", "When do you...? I usually... at..."]},
                {"unit": "Unit 2 My favourite season", "topics": ["四季活动：go swimming, make a snowman, pick apples, fly kites, plant trees", "Which season do you like best? I like... best. Why? Because I can..."]},
                {"unit": "Unit 3 My school calendar", "topics": ["月份：January~December", "节日活动：New Year's Day, Christmas, Easter, Mother's Day, Children's Day", "When is...? It's in..."]},
                {"unit": "Unit 4 When is Easter?", "topics": ["序数词：first~twelfth", "When is your birthday? It's on... My birthday is on..."]},
                {"unit": "Unit 5 Whose dog is it?", "topics": ["名词性物主代词：mine, yours, his, hers, theirs, ours", "Whose...is it? It's... The...is..."]},
                {"unit": "Unit 6 Work quietly!", "topics": ["现在进行时：eating, playing, jumping, drinking, sleeping, reading, listening, talking, singing", "What is/are...doing? He/She/They is/are...ing"]},
            ],
        },
        "science": {
            "上册": [
                {"unit": "第一单元 光", "topics": ["有关光的思考", "光是怎样传播的", "光的反射", "光与热"]},
                {"unit": "第二单元 地球表面的变化", "topics": ["地球的表面", "地球的结构", "地震的成因及作用"]},
                {"unit": "第三单元 计量时间", "topics": ["时间的测量", "用水测量时间", "我的水钟"]},
            ],
            "下册": [
                {"unit": "第一单元 生物与环境", "topics": ["种子发芽实验", "绿豆苗的生长", "蚯蚓的选择"]},
                {"unit": "第二单元 船的研究", "topics": ["船的历史", "用浮的材料造船", "增加船的载重量"]},
                {"unit": "第三单元 环境与我们", "topics": ["地球——宇宙的奇迹", "我们面临的环境问题", "珍惜水资源"]},
            ],
        },
    },
    "六年级": {
        "math": {
            "上册": [
                {"unit": "第一单元 分数乘法", "topics": ["分数乘整数", "分数乘分数", "分数混合运算", "解决问题"]},
                {"unit": "第二单元 位置与方向（二）", "topics": ["用方向和距离确定位置"]},
                {"unit": "第三单元 分数除法", "topics": ["分数除法的意义", "分数除法计算", "解决问题"]},
                {"unit": "第四单元 比", "topics": ["比的意义", "比的基本性质", "比的应用"]},
                {"unit": "第五单元 圆", "topics": ["圆的认识", "圆的周长", "圆的面积", "扇形"]},
                {"unit": "第六单元 百分数（一）", "topics": ["百分数的意义和写法", "百分数和分数小数的互化", "用百分数解决问题"]},
                {"unit": "第七单元 扇形统计图", "topics": ["认识扇形统计图", "选择合适的统计图"]},
            ],
            "下册": [
                {"unit": "第一单元 负数", "topics": ["负数的认识", "负数在生活中的应用"]},
                {"unit": "第二单元 百分数（二）", "topics": ["折扣", "成数", "税率", "利率"]},
                {"unit": "第三单元 圆柱与圆锥", "topics": ["圆柱的认识和表面积", "圆柱的体积", "圆锥的认识和体积"]},
                {"unit": "第四单元 比例", "topics": ["比例的意义和基本性质", "正比例和反比例", "比例的应用", "比例尺"]},
                {"unit": "第五单元 数学广角——鸽巢问题", "topics": ["鸽巢原理"]},
                {"unit": "第六单元 整理和复习", "topics": ["数与代数整理", "图形与几何整理", "统计与概率整理"]},
            ],
        },
        "chinese": {
            "上册": [
                {"unit": "第一单元", "topics": ["草原", "丁香结", "古诗词三首（宿建德江、六月二十七日望湖楼醉书、西江月·夜行黄沙道中）", "花之歌"]},
                {"unit": "第二单元", "topics": ["七律·长征", "狼牙山五壮士", "开国大典", "灯光"]},
                {"unit": "第三单元", "topics": ["竹节人", "宇宙生命之谜", "故宫博物院"]},
                {"unit": "第四单元", "topics": ["桥", "穷人", "在柏林"]},
                {"unit": "第五单元", "topics": ["夏天里的成长", "盼"]},
                {"unit": "第六单元", "topics": ["古诗三首（浪淘沙、江南春、书湖阴先生壁）", "只有一个地球", "三黑和土地", "青山不老"]},
                {"unit": "第七单元", "topics": ["文言文二则（伯牙鼓琴、书戴嵩画牛）", "月光曲", "京剧趣谈"]},
                {"unit": "第八单元", "topics": ["少年闰土", "好的故事", "我的伯父鲁迅先生", "有的人"]},
            ],
            "下册": [
                {"unit": "第一单元", "topics": ["北京的春节", "腊八粥", "古诗三首（寒食、迢迢牵牛星、十五夜望月）", "藏戏"]},
                {"unit": "第二单元", "topics": ["鲁滨逊漂流记", "骑鹅旅行记", "汤姆·索亚历险记"]},
                {"unit": "第三单元", "topics": ["匆匆", "那个星期天"]},
                {"unit": "第四单元", "topics": ["古诗三首（马诗、石灰吟、竹石）", "十六年前的回忆", "为人民服务", "金色的鱼钩"]},
                {"unit": "第五单元", "topics": ["学弈", "两小儿辩日", "真理诞生于一百个问号之后", "表里的生物"]},
                {"unit": "第六单元", "topics": ["综合复习"]},
            ],
        },
        "english": {
            "上册": [
                {"unit": "Unit 1 How can I get there?", "topics": ["地点场所：science museum, post office, bookstore, cinema, hospital, crossing, turn left/right, go straight", "Where is the...? It's near/next to/behind... How can I get there?"]},
                {"unit": "Unit 2 Ways to go to school", "topics": ["交通方式：on foot, by bus, by plane, by taxi, by ship, by subway, by train, by bike", "How do you come to school? I usually come by... Don't go at the red light."]},
                {"unit": "Unit 3 My weekend plan", "topics": ["周末计划：visit grandparents, see a film, take a trip, go to the supermarket, this morning/afternoon/evening, tonight, tomorrow, next week", "What are you going to do? I'm going to..."]},
                {"unit": "Unit 4 I have a pen pal", "topics": ["爱好活动：dancing, singing, reading stories, playing football/basketball, doing kung fu, studying Chinese/English", "What are your/his/her hobbies? I/He/She likes..."]},
                {"unit": "Unit 5 What does he do?", "topics": ["职业：factory worker, postman, businessman, police officer, fisherman, scientist, pilot, coach", "What does your father/mother do? He/She is a/an..."]},
                {"unit": "Unit 6 How do you feel?", "topics": ["情感感受：angry, afraid, sad, worried, happy, ill, wear warm clothes, see a doctor, count to ten, do more exercise, take a deep breath", "How do you feel? I'm... He/She should..."]},
            ],
            "下册": [
                {"unit": "Unit 1 How tall are you?", "topics": ["比较级：taller, shorter, longer, older, younger, bigger, smaller, thinner, heavier", "How tall/heavy/old are you? I'm... You're...than me."]},
                {"unit": "Unit 2 Last weekend", "topics": ["一般过去时：watched TV, washed clothes, cleaned the room, stayed at home, read a book, saw a film", "What did you do last weekend? I..."]},
                {"unit": "Unit 3 Where did you go?", "topics": ["过去式不规则：went, rode, hurt, ate, took, bought, fell off, could", "Where did you go over the holiday? How did you go there? What did you do?"]},
                {"unit": "Unit 4 Then and now", "topics": ["过去与现在对比：before/now, there was/were, could/couldn't, years ago", "There was/were no... Years ago... Now..."]},
            ],
        },
        "science": {
            "上册": [
                {"unit": "第一单元 微小世界", "topics": ["放大镜", "放大镜下的昆虫世界", "微小世界和我们"]},
                {"unit": "第二单元 地球的运动", "topics": ["地球的自转与公转", "昼夜交替现象", "四季变化"]},
                {"unit": "第三单元 工具和机械", "topics": ["使用工具", "杠杆的科学", "滑轮的研究", "斜面的作用"]},
            ],
            "下册": [
                {"unit": "第一单元 生物的多样性", "topics": ["校园生物大搜索", "制作校园生物分布图"]},
                {"unit": "第二单元 宇宙", "topics": ["太阳系", "在星空中", "探索宇宙"]},
                {"unit": "第三单元 物质的变化", "topics": ["我们身边的物质", "物质发生了什么变化", "米饭淀粉和碘酒的变化"]},
            ],
        },
    },
    "七年级": {
        "math": {
            "上册": [
                {"unit": "第一章 有理数", "topics": ["正数和负数", "有理数", "有理数的加减法", "有理数的乘除法", "有理数的乘方"]},
                {"unit": "第二章 整式的加减", "topics": ["整式", "合并同类项与去括号", "整式的加减"]},
                {"unit": "第三章 一元一次方程", "topics": ["一元一次方程", "解一元一次方程（合并同类项）", "解一元一次方程（去括号）", "实际问题与一元一次方程"]},
                {"unit": "第四章 几何图形初步", "topics": ["几何图形", "直线、射线、线段", "角"]},
            ],
            "下册": [
                {"unit": "第五章 相交线与平行线", "topics": ["相交线", "垂线", "同位角、内错角、同旁内角", "平行线的判定和性质"]},
                {"unit": "第六章 实数", "topics": ["平方根", "立方根", "实数"]},
                {"unit": "第七章 平面直角坐标系", "topics": ["有序数对", "平面直角坐标系"]},
                {"unit": "第八章 二元一次方程组", "topics": ["二元一次方程组", "消元——解方程组", "实际问题与二元一次方程组"]},
                {"unit": "第九章 不等式与不等式组", "topics": ["不等式", "一元一次不等式", "一元一次不等式组"]},
                {"unit": "第十章 数据的收集、整理与描述", "topics": ["统计调查", "直方图"]},
            ],
        },
        "chinese": {
            "上册": [
                {"unit": "第一单元", "topics": ["春", "济南的冬天", "雨的四季", "古代诗歌四首（观沧海、闻王昌龄左迁龙标遥有此寄、次北固山下、天净沙·秋思）"]},
                {"unit": "第二单元", "topics": ["秋天的怀念", "散步", "散文诗二首（金色花、荷叶·母亲）", "世说新语二则（咏雪、陈太丘与友期行）"]},
                {"unit": "第三单元", "topics": ["从百草园到三味书屋", "再塑生命的人", "窃读记"]},
                {"unit": "第四单元", "topics": ["纪念白求恩", "植树的牧羊人", "走一步再走一步", "诫子书"]},
                {"unit": "第五单元", "topics": ["猫", "动物笑谈", "狼"]},
                {"unit": "第六单元", "topics": ["皇帝的新装", "诗二首（天上的街市、太阳船）", "女娲造人", "寓言四则"]},
            ],
            "下册": [
                {"unit": "第一单元", "topics": ["邓稼先", "说和做", "回忆鲁迅先生", "孙权劝学"]},
                {"unit": "第二单元", "topics": ["黄河颂", "老山界", "谁是最可爱的人", "土地的誓言", "木兰诗"]},
                {"unit": "第三单元", "topics": ["阿长与《山海经》", "台阶", "卖油翁"]},
                {"unit": "第四单元", "topics": ["叶圣陶先生二三事", "驿路梨花", "最苦与最乐", "陋室铭", "爱莲说"]},
                {"unit": "第五单元", "topics": ["紫藤萝瀑布", "一棵小桃树", "外国诗二首（假如生活欺骗了你、未选择的路）"]},
                {"unit": "第六单元", "topics": ["伟大的悲剧", "太空一日", "带上她的眼睛", "河中石兽"]},
            ],
        },
        "english": {
            "上册": [
                {"unit": "Starter Units 1-3", "topics": ["26个英文字母", "Good morning! What's this in English?", "What color is it? 基础问候与颜色"]},
                {"unit": "Unit 1 My name's Gina.", "topics": ["自我介绍与问候", "What's your/his/her name?", "My/His/Her name is...", "Nice to meet you."]},
                {"unit": "Unit 2 This is my sister.", "topics": ["介绍家人朋友", "This/That is... These/Those are...", "family members词汇"]},
                {"unit": "Unit 3 Is this your pencil?", "topics": ["辨认物品所属", "Is this/that...? Yes, it is./No, it isn't.", "物品名词"]},
                {"unit": "Unit 4 Where's my schoolbag?", "topics": ["方位介词：in, on, under, behind, next to", "Where is/are...? It's/They're..."]},
                {"unit": "Unit 5 Do you have a soccer ball?", "topics": ["have/has的用法", "Do you have...? Does he/she have...?", "球类运动词汇"]},
                {"unit": "Unit 6 Do you like bananas?", "topics": ["食物词汇", "Do you like...? Yes, I do./No, I don't.", "healthy food"]},
                {"unit": "Unit 7 How much are these socks?", "topics": ["服装词汇", "How much is/are...? 数字与价格"]},
                {"unit": "Unit 8 When is your birthday?", "topics": ["月份与序数词", "When is...? My birthday is on..."]},
                {"unit": "Unit 9 My favorite subject is science.", "topics": ["学科名称", "What's your favorite subject? Why do you like...? Because it's..."]},
            ],
            "下册": [
                {"unit": "Unit 1 Can you play the guitar?", "topics": ["can表示能力", "Can you...? I can/can't...", "乐器和活动词汇"]},
                {"unit": "Unit 2 What time do you go to school?", "topics": ["时间表达", "What time do you...? I usually... at...", "daily routines日常活动"]},
                {"unit": "Unit 3 How do you get to school?", "topics": ["交通方式", "How do/does...get to school? take the bus/subway, ride a bike, walk"]},
                {"unit": "Unit 4 Don't eat in class.", "topics": ["祈使句和规则", "Don't... You must/mustn't...", "school rules"]},
                {"unit": "Unit 5 Why do you like pandas?", "topics": ["描述动物", "Why...? Because... What animals do you like?", "形容词描述"]},
                {"unit": "Unit 6 I'm watching TV.", "topics": ["现在进行时", "What are you doing? I'm...ing. Is he/she...ing?"]},
                {"unit": "Unit 7 It's raining!", "topics": ["天气描述", "How's the weather? It's sunny/cloudy/raining/snowing/windy"]},
                {"unit": "Unit 8 Is there a post office near here?", "topics": ["问路与指路", "Is there a...? Where is...? Go along... Turn left/right."]},
                {"unit": "Unit 9 What does he look like?", "topics": ["描述外貌", "What does...look like? He/She is tall/short/thin. He/She has long/short/curly/straight hair."]},
                {"unit": "Unit 10 I'd like some noodles.", "topics": ["点餐用语", "What would you like? I'd like... What kind/size of...?"]},
                {"unit": "Unit 11 How was your school trip?", "topics": ["一般过去时", "How was...? It was great/terrible. Did you...? Yes, I did./No, I didn't."]},
                {"unit": "Unit 12 What did you do last weekend?", "topics": ["过去时态运用", "What did you do...? I went/visited/played/studied..."]},
            ],
        },
        "science": {
            "上册": [
                {"unit": "第一章 科学入门", "topics": ["科学并不神秘", "走进科学实验室", "科学观察", "科学测量"]},
                {"unit": "第二章 观察生物", "topics": ["生物与非生物", "细胞", "生物体的结构层次"]},
                {"unit": "第三章 人类的家园——地球", "topics": ["地球的形状和内部结构", "地球仪和地图", "组成地壳的岩石"]},
                {"unit": "第四章 物质的特性", "topics": ["物质的构成", "质量的测量", "物质的密度", "物质的比热"]},
            ],
            "下册": [
                {"unit": "第一章 代代相传的生命", "topics": ["新生命的诞生", "走向成熟", "动物的生长时期", "植物的一生"]},
                {"unit": "第二章 对环境的察觉", "topics": ["感觉世界", "声音的发生和传播", "耳和听觉", "光和颜色", "光的反射和折射"]},
                {"unit": "第三章 运动和力", "topics": ["机械运动", "力的存在", "重力", "弹力和摩擦力", "牛顿第一定律"]},
                {"unit": "第四章 地球与宇宙", "topics": ["太阳和月球", "地球的自转", "地球的公转", "月相"]},
            ],
        },
    },
    "八年级": {
        "math": {
            "上册": [
                {"unit": "第十一章 三角形", "topics": ["与三角形有关的线段", "与三角形有关的角", "多边形及其内角和"]},
                {"unit": "第十二章 全等三角形", "topics": ["全等三角形", "三角形全等的判定（SSS、SAS、ASA、AAS、HL）", "角的平分线的性质"]},
                {"unit": "第十三章 轴对称", "topics": ["轴对称", "等腰三角形", "线段的垂直平分线的性质"]},
                {"unit": "第十四章 整式的乘法与因式分解", "topics": ["整式的乘法", "乘法公式", "因式分解"]},
                {"unit": "第十五章 分式", "topics": ["分式", "分式的运算", "分式方程"]},
            ],
            "下册": [
                {"unit": "第十六章 二次根式", "topics": ["二次根式", "二次根式的乘除", "二次根式的加减"]},
                {"unit": "第十七章 勾股定理", "topics": ["勾股定理", "勾股定理的逆定理"]},
                {"unit": "第十八章 平行四边形", "topics": ["平行四边形", "特殊的平行四边形（矩形、菱形、正方形）"]},
                {"unit": "第十九章 一次函数", "topics": ["函数", "正比例函数", "一次函数", "课题学习"]},
                {"unit": "第二十章 数据的分析", "topics": ["数据的集中趋势", "数据的波动程度"]},
            ],
        },
        "chinese": {
            "上册": [
                {"unit": "第一单元", "topics": ["消息二则（我三十万大军胜利南渡长江、人民解放军百万大军横渡长江）", "首届诺贝尔奖颁发", "一着惊海天", "藏戏", "新闻写作"]},
                {"unit": "第二单元", "topics": ["藤野先生", "回忆我的母亲", "列夫·托尔斯泰", "美丽的颜色"]},
                {"unit": "第三单元", "topics": ["三峡", "短文二篇（答谢中书书、记承天寺夜游）", "与朱元思书", "唐诗五首"]},
                {"unit": "第四单元", "topics": ["背影", "白杨礼赞", "昆明的雨", "散文二篇"]},
                {"unit": "第五单元", "topics": ["中国石拱桥", "苏州园林", "蝉", "梦回繁华"]},
                {"unit": "第六单元", "topics": ["《孟子》二章", "愚公移山", "周亚夫军细柳", "诗词五首"]},
            ],
            "下册": [
                {"unit": "第一单元", "topics": ["社戏", "回延安", "安塞腰鼓", "灯笼"]},
                {"unit": "第二单元", "topics": ["大自然的语言", "阿西莫夫短文两篇", "大雁归来", "时间的脚印"]},
                {"unit": "第三单元", "topics": ["桃花源记", "小石潭记", "核舟记", "诗经二首"]},
                {"unit": "第四单元", "topics": ["最后一次讲演", "应有格物致知精神", "我一生中的重要抉择", "庆祝奥林匹克运动复兴25周年"]},
                {"unit": "第五单元", "topics": ["壶口瀑布", "在长江源头各拉丹冬", "登勃朗峰", "一滴水经过丽江"]},
                {"unit": "第六单元", "topics": ["北冥有鱼", "虽有嘉肴", "马说", "唐诗三首（石壕吏、茅屋为秋风所破歌、卖炭翁）"]},
            ],
        },
        "english": {
            "上册": [
                {"unit": "Unit 1 Where did you go on vacation?", "topics": ["过去时态复习", "复合不定代词：anyone, anything, something, everything, nothing", "假期活动描述"]},
                {"unit": "Unit 2 How often do you exercise?", "topics": ["频率副词：always, usually, often, sometimes, hardly ever, never", "How often...? 日常活动频率"]},
                {"unit": "Unit 3 I'm more outgoing than my sister.", "topics": ["比较级：more, -er, better, worse", "Who is more/...er...? 人物比较"]},
                {"unit": "Unit 4 What's the best movie theater?", "topics": ["最高级：most, -est, best, worst", "What's the best/most...? 场所和事物比较"]},
                {"unit": "Unit 5 Do you want to watch a game show?", "topics": ["影视节目类型：game show, talk show, news, sitcom, cartoon, documentary", "What do you think of...? I love/like/don't mind/can't stand..."]},
                {"unit": "Unit 6 I'm going to study computer science.", "topics": ["be going to表将来", "What are you going to be? I'm going to... How are you going to do that?"]},
                {"unit": "Unit 7 Will people have robots?", "topics": ["will表将来预测", "There will be... Will people...? Yes, they will./No, they won't."]},
                {"unit": "Unit 8 How do you make a banana milk shake?", "topics": ["祈使句步骤描述", "How do you make...? First... Then... Next... Finally..."]},
                {"unit": "Unit 9 Can you come to my party?", "topics": ["邀请与拒绝", "Can you come to...? Sure, I'd love to./Sorry, I can't. I have to..."]},
                {"unit": "Unit 10 If you go to the party, you'll have a great time!", "topics": ["if条件句", "If you..., you will/won't... What will happen if...?"]},
            ],
            "下册": [
                {"unit": "Unit 1 What's the matter?", "topics": ["健康问题：headache, stomachache, toothache, fever, sore throat, cough", "What's the matter? You should/shouldn't..."]},
                {"unit": "Unit 2 I'll help to clean up the city parks.", "topics": ["志愿活动", "I'd like to... I could... 动词不定式"]},
                {"unit": "Unit 3 Could you please clean your room?", "topics": ["请求与许可", "Could you please...? Could I...? chores家务词汇"]},
                {"unit": "Unit 4 Why don't you talk to your parents?", "topics": ["建议与意见", "Why don't you...? You could/should... What should I do?"]},
                {"unit": "Unit 5 What were you doing when the rainstorm came?", "topics": ["过去进行时", "What were you doing when...? I was...ing when/while..."]},
                {"unit": "Unit 6 An old man tried to move the mountains.", "topics": ["故事复述", "Once upon a time... 过去时态在故事中的运用"]},
                {"unit": "Unit 7 What's the highest mountain in the world?", "topics": ["数据与比较", "How high/deep/long is...? 地理知识与最高级"]},
                {"unit": "Unit 8 Have you read Treasure Island yet?", "topics": ["现在完成时", "Have you...yet? I have already/just/never... 读书与经历"]},
                {"unit": "Unit 9 Have you ever been to a museum?", "topics": ["现在完成时与经历", "Have you ever been to...? I've been to.../I've never been to..."]},
                {"unit": "Unit 10 I've had this bike for three years.", "topics": ["现在完成时与持续", "How long have you had/been...? I've had/been...for/since..."]},
            ],
        },
        "science": {
            "上册": [
                {"unit": "第一章 水和水的溶液", "topics": ["地球上的水", "水的组成", "水的浮力", "物质在水中的溶解"]},
                {"unit": "第二章 天气与气候", "topics": ["大气层", "气温", "大气的压强", "风和降水", "天气预报", "气候和影响气候的因素"]},
                {"unit": "第三章 生命活动的调节", "topics": ["植物生命活动的调节", "人体的激素调节", "神经调节"]},
                {"unit": "第四章 电路探秘", "topics": ["电荷与电流", "电流的测量", "物质的导电性与电阻", "变阻器", "电压的测量"]},
            ],
            "下册": [
                {"unit": "第一章 电与磁", "topics": ["指南针为什么能指方向", "电生磁", "电动机", "电磁感应"]},
                {"unit": "第二章 微粒的模型与符号", "topics": ["模型、符号的建立与作用", "物质的微观粒子模型", "原子结构的模型", "组成物质的元素"]},
                {"unit": "第三章 空气与生命", "topics": ["空气与氧气", "氧化和燃烧", "化学方程式", "光合作用"]},
                {"unit": "第四章 植物与土壤", "topics": ["土壤的成分", "各种各样的土壤", "植物的根与物质吸收", "植物的茎与物质运输"]},
            ],
        },
    },
    "九年级": {
        "math": {
            "上册": [
                {"unit": "第二十一章 一元二次方程", "topics": ["一元二次方程", "解一元二次方程（直接开平方法、配方法、公式法、因式分解法）", "实际问题与一元二次方程"]},
                {"unit": "第二十二章 二次函数", "topics": ["二次函数的图象和性质", "二次函数与一元二次方程", "实际问题与二次函数"]},
                {"unit": "第二十三章 旋转", "topics": ["图形的旋转", "中心对称", "课题学习 图案设计"]},
                {"unit": "第二十四章 圆", "topics": ["圆的有关性质", "点和圆、直线和圆的位置关系", "正多边形和圆", "弧长和扇形面积"]},
            ],
            "下册": [
                {"unit": "第二十五章 概率初步", "topics": ["随机事件与概率", "用列举法求概率", "用频率估计概率"]},
                {"unit": "第二十六章 反比例函数", "topics": ["反比例函数", "实际问题与反比例函数"]},
                {"unit": "第二十七章 相似", "topics": ["图形的相似", "相似三角形", "位似"]},
                {"unit": "第二十八章 锐角三角函数", "topics": ["锐角三角函数", "解直角三角形及其应用"]},
                {"unit": "第二十九章 投影与视图", "topics": ["投影", "三视图"]},
            ],
        },
        "chinese": {
            "上册": [
                {"unit": "第一单元", "topics": ["沁园春·雪", "周总理你在哪里", "我爱这土地", "乡愁", "你是人间的四月天"]},
                {"unit": "第二单元", "topics": ["敬业与乐业", "就英法联军远征中国致巴特勒上尉的信", "论教养", "精神的三间小屋"]},
                {"unit": "第三单元", "topics": ["岳阳楼记", "醉翁亭记", "湖心亭看雪", "诗词三首（行路难、酬乐天扬州初逢席上见赠、水调歌头）"]},
                {"unit": "第四单元", "topics": ["故乡", "我的叔叔于勒", "孤独之旅"]},
                {"unit": "第五单元", "topics": ["中国人失掉自信力了吗", "怀疑与学问", "谈创造性思维"]},
                {"unit": "第六单元", "topics": ["智取生辰纲", "范进中举", "三顾茅庐", "刘姥姥进大观园"]},
            ],
            "下册": [
                {"unit": "第一单元", "topics": ["祖国啊我亲爱的祖国", "梅岭三章", "短诗五首", "海燕"]},
                {"unit": "第二单元", "topics": ["孔乙己", "变色龙", "溜索", "蒲柳人家"]},
                {"unit": "第三单元", "topics": ["鱼我所欲也", "唐雎不辱使命", "送东阳马生序", "词四首（渔家傲·秋思、江城子·密州出猎、破阵子、满江红）"]},
                {"unit": "第四单元", "topics": ["短文两篇（谈读书、不求甚解）", "山水画的意境", "无言之美", "驱遣我们的想象"]},
                {"unit": "第五单元", "topics": ["屈原", "天下第一楼"]},
                {"unit": "第六单元", "topics": ["曹刿论战", "邹忌讽齐王纳谏", "出师表", "诗词曲五首"]},
            ],
        },
        "english": {
            "上册": [
                {"unit": "Unit 1 How can we become good learners?", "topics": ["学习方法", "by doing sth. 方式方法表达", "How do you study for...?"]},
                {"unit": "Unit 2 I think that mooncakes are delicious!", "topics": ["节日文化", "宾语从句 that/whether/if", "传统节日词汇"]},
                {"unit": "Unit 3 Could you please tell me where the restrooms are?", "topics": ["间接疑问句（宾语从句）", "礼貌询问", "Could you tell me where/how/when...?"]},
                {"unit": "Unit 4 I used to be afraid of the dark.", "topics": ["used to do表过去习惯", "I used to... but now I...", "人物变化描述"]},
                {"unit": "Unit 5 What are the shirts made of?", "topics": ["被动语态", "be made of/from/in/by", "What is/are...made of?"]},
                {"unit": "Unit 6 When was it invented?", "topics": ["被动语态（过去时）", "When was...invented? It was invented in/by..."]},
                {"unit": "Unit 7 Teenagers should be allowed to choose their own clothes.", "topics": ["含情态动词的被动语态", "should be allowed to... agree/disagree"]},
                {"unit": "Unit 8 It must belong to Carla.", "topics": ["情态动词表推测", "must/might/could/can't + be", "Whose...is this? It must/might/could belong to..."]},
                {"unit": "Unit 9 I like music that I can dance to.", "topics": ["定语从句（that/which/who）", "I like/prefer...that/who...", "What kind of...do you like?"]},
                {"unit": "Unit 10 You're supposed to shake hands.", "topics": ["be supposed to/be expected to", "文化差异与礼仪", "You're supposed/not supposed to..."]},
            ],
            "下册": [
                {"unit": "Unit 1 People who are important to me.", "topics": ["定语从句深化", "关系代词who/that/which", "描述重要人物"]},
                {"unit": "Unit 2 It's important that we save the earth.", "topics": ["环保话题", "主语从句 It's important/necessary that...", "环境问题词汇"]},
                {"unit": "Unit 3 To be honest, I think it's ugly.", "topics": ["表达观点", "I think/believe/agree that... In my opinion..."]},
                {"unit": "Unit 4 I've learned a lot about Chinese culture.", "topics": ["现在完成时综合运用", "中国传统文化话题", "I've learned/known/been..."]},
            ],
        },
        "science": {
            "上册": [
                {"unit": "第一章 物质及其变化", "topics": ["物质的变化", "物质的酸碱性", "常见的酸", "常见的碱", "酸和碱之间发生的反应"]},
                {"unit": "第二章 物质转化与材料利用", "topics": ["金属材料", "金属的化学性质", "非金属材料", "有机合成材料"]},
                {"unit": "第三章 能量的转化与守恒", "topics": ["能量及其形式", "机械能", "能量转化的量度", "电能的利用", "核能"]},
                {"unit": "第四章 代谢与平衡", "topics": ["食物与摄食", "食物的消化与吸收", "体内物质的运输", "能量的获得", "体内物质的动态平衡"]},
            ],
            "下册": [
                {"unit": "第一章 演化的自然", "topics": ["宇宙的起源", "太阳系的形成与地球的诞生", "恒星的一生", "地球的演变和生命的起源"]},
                {"unit": "第二章 生物与环境", "topics": ["种群和生物群落", "生态系统", "生态系统的稳定性"]},
                {"unit": "第三章 人的健康与环境", "topics": ["健康", "来自微生物的威胁", "身体的防卫", "非传染性疾病", "人的运动系统"]},
                {"unit": "第四章 可持续发展", "topics": ["人类发展与环境问题", "能源及其利用", "实现可持续发展"]},
            ],
        },
    },
}


# 所有年级列表
ALL_GRADES = [
    "一年级", "二年级", "三年级", "四年级", "五年级", "六年级",
    "七年级", "八年级", "九年级",
]

# 所有学科列表
ALL_SUBJECTS = ["math", "chinese", "english", "science"]

SUBJECT_NAMES = {"math": "数学", "chinese": "语文", "english": "英语", "science": "科学"}


def get_curriculum(grade: str, subject_id: str, semester: str = None):
    """获取指定年级学科的课本大纲"""
    grade_data = CURRICULUM.get(grade, {})
    subject_data = grade_data.get(subject_id, {})
    if semester:
        return {semester: subject_data.get(semester, [])}
    return subject_data


def get_unit_topics(grade: str, subject_id: str, semester: str, unit_name: str):
    """获取指定单元的知识点列表"""
    grade_data = CURRICULUM.get(grade, {})
    subject_data = grade_data.get(subject_id, {})
    semester_data = subject_data.get(semester, [])
    for unit in semester_data:
        if unit["unit"] == unit_name:
            return unit["topics"]
    return []


def get_semester_all_topics(grade: str, subject_id: str, semester: str):
    """获取一个学期所有知识点（平铺）"""
    grade_data = CURRICULUM.get(grade, {})
    subject_data = grade_data.get(subject_id, {})
    semester_data = subject_data.get(semester, [])
    all_topics = []
    for unit in semester_data:
        all_topics.extend(unit["topics"])
    return all_topics
