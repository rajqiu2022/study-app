import json
import random
import asyncio
import os
import hashlib
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import PracticeSession, WrongQuestion, LearningRecord, LLMConfig, User
from ..schemas import PracticeSessionCreate, PracticeSessionOut
from ..llm_service import call_llm, build_practice_prompt, parse_llm_questions, get_llm_config_with_iflow

router = APIRouter()

# TTS 音频缓存目录
TTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "tts")
os.makedirs(TTS_DIR, exist_ok=True)

# ==================== 数学题库 ====================
MATH_TEMPLATES = {
    "加减法": [
        {"q": "{a} + {b} = ?", "type": "填空题"},
        {"q": "{a} - {b} = ?", "type": "填空题"},
        {"q": "小明有{a}个苹果，又买了{b}个，一共有几个？", "type": "应用题"},
    ],
    "乘法": [
        {"q": "{a} × {b} = ?", "type": "填空题"},
        {"q": "每排{a}个座位，共{b}排，一共有多少个座位？", "type": "应用题"},
    ],
    "除法": [
        {"q": "{a} ÷ {b} = ?", "type": "填空题"},
        {"q": "{a}个苹果平均分给{b}个人，每人几个？", "type": "应用题"},
    ],
    "分数": [
        {"q": "1/2 + 1/4 = ?", "type": "填空题"},
        {"q": "3/4 - 1/2 = ?", "type": "填空题"},
    ],
    "default": [
        {"q": "{a} + {b} = ?", "type": "填空题"},
        {"q": "{a} × {b} = ?", "type": "填空题"},
    ],
}

# ==================== 英语题库 ====================
ENGLISH_WORD_BANK = [
    {"word": "apple", "meaning": "苹果", "category": "水果"},
    {"word": "banana", "meaning": "香蕉", "category": "水果"},
    {"word": "orange", "meaning": "橘子", "category": "水果"},
    {"word": "grape", "meaning": "葡萄", "category": "水果"},
    {"word": "watermelon", "meaning": "西瓜", "category": "水果"},
    {"word": "strawberry", "meaning": "草莓", "category": "水果"},
    {"word": "cat", "meaning": "猫", "category": "动物"},
    {"word": "dog", "meaning": "狗", "category": "动物"},
    {"word": "bird", "meaning": "鸟", "category": "动物"},
    {"word": "fish", "meaning": "鱼", "category": "动物"},
    {"word": "rabbit", "meaning": "兔子", "category": "动物"},
    {"word": "elephant", "meaning": "大象", "category": "动物"},
    {"word": "monkey", "meaning": "猴子", "category": "动物"},
    {"word": "panda", "meaning": "熊猫", "category": "动物"},
    {"word": "red", "meaning": "红色", "category": "颜色"},
    {"word": "blue", "meaning": "蓝色", "category": "颜色"},
    {"word": "green", "meaning": "绿色", "category": "颜色"},
    {"word": "yellow", "meaning": "黄色", "category": "颜色"},
    {"word": "white", "meaning": "白色", "category": "颜色"},
    {"word": "black", "meaning": "黑色", "category": "颜色"},
    {"word": "one", "meaning": "一", "category": "数字"},
    {"word": "two", "meaning": "二", "category": "数字"},
    {"word": "three", "meaning": "三", "category": "数字"},
    {"word": "four", "meaning": "四", "category": "数字"},
    {"word": "five", "meaning": "五", "category": "数字"},
    {"word": "six", "meaning": "六", "category": "数字"},
    {"word": "seven", "meaning": "七", "category": "数字"},
    {"word": "eight", "meaning": "八", "category": "数字"},
    {"word": "nine", "meaning": "九", "category": "数字"},
    {"word": "ten", "meaning": "十", "category": "数字"},
    {"word": "book", "meaning": "书", "category": "学习"},
    {"word": "pen", "meaning": "钢笔", "category": "学习"},
    {"word": "pencil", "meaning": "铅笔", "category": "学习"},
    {"word": "ruler", "meaning": "尺子", "category": "学习"},
    {"word": "school", "meaning": "学校", "category": "学习"},
    {"word": "teacher", "meaning": "老师", "category": "学习"},
    {"word": "student", "meaning": "学生", "category": "学习"},
    {"word": "father", "meaning": "爸爸", "category": "家庭"},
    {"word": "mother", "meaning": "妈妈", "category": "家庭"},
    {"word": "brother", "meaning": "哥哥/弟弟", "category": "家庭"},
    {"word": "sister", "meaning": "姐姐/妹妹", "category": "家庭"},
    {"word": "hand", "meaning": "手", "category": "身体"},
    {"word": "head", "meaning": "头", "category": "身体"},
    {"word": "eye", "meaning": "眼睛", "category": "身体"},
    {"word": "ear", "meaning": "耳朵", "category": "身体"},
    {"word": "nose", "meaning": "鼻子", "category": "身体"},
    {"word": "mouth", "meaning": "嘴巴", "category": "身体"},
    {"word": "Monday", "meaning": "星期一", "category": "星期"},
    {"word": "Tuesday", "meaning": "星期二", "category": "星期"},
    {"word": "Wednesday", "meaning": "星期三", "category": "星期"},
    {"word": "Thursday", "meaning": "星期四", "category": "星期"},
    {"word": "Friday", "meaning": "星期五", "category": "星期"},
    {"word": "Saturday", "meaning": "星期六", "category": "星期"},
    {"word": "Sunday", "meaning": "星期日", "category": "星期"},
    {"word": "spring", "meaning": "春天", "category": "季节"},
    {"word": "summer", "meaning": "夏天", "category": "季节"},
    {"word": "autumn", "meaning": "秋天", "category": "季节"},
    {"word": "winter", "meaning": "冬天", "category": "季节"},
    {"word": "rice", "meaning": "米饭", "category": "食物"},
    {"word": "bread", "meaning": "面包", "category": "食物"},
    {"word": "milk", "meaning": "牛奶", "category": "食物"},
    {"word": "egg", "meaning": "鸡蛋", "category": "食物"},
    {"word": "water", "meaning": "水", "category": "食物"},
    {"word": "cake", "meaning": "蛋糕", "category": "食物"},
    {"word": "big", "meaning": "大的", "category": "形容词"},
    {"word": "small", "meaning": "小的", "category": "形容词"},
    {"word": "long", "meaning": "长的", "category": "形容词"},
    {"word": "short", "meaning": "短的/矮的", "category": "形容词"},
    {"word": "happy", "meaning": "快乐的", "category": "形容词"},
    {"word": "sad", "meaning": "伤心的", "category": "形容词"},
    {"word": "hot", "meaning": "热的", "category": "形容词"},
    {"word": "cold", "meaning": "冷的", "category": "形容词"},
    {"word": "run", "meaning": "跑", "category": "动作"},
    {"word": "jump", "meaning": "跳", "category": "动作"},
    {"word": "swim", "meaning": "游泳", "category": "动作"},
    {"word": "sing", "meaning": "唱歌", "category": "动作"},
    {"word": "dance", "meaning": "跳舞", "category": "动作"},
    {"word": "read", "meaning": "阅读", "category": "动作"},
    {"word": "write", "meaning": "写", "category": "动作"},
    {"word": "eat", "meaning": "吃", "category": "动作"},
    {"word": "drink", "meaning": "喝", "category": "动作"},
    {"word": "sleep", "meaning": "睡觉", "category": "动作"},
]

ENGLISH_SENTENCE_BANK = [
    {"q": "How are you?", "answer": "你好吗？", "type": "翻译"},
    {"q": "What is your name?", "answer": "你叫什么名字？", "type": "翻译"},
    {"q": "I like apples.", "answer": "我喜欢苹果。", "type": "翻译"},
    {"q": "She is a teacher.", "answer": "她是一个老师。", "type": "翻译"},
    {"q": "He can swim.", "answer": "他会游泳。", "type": "翻译"},
    {"q": "This is my book.", "answer": "这是我的书。", "type": "翻译"},
    {"q": "I have two cats.", "answer": "我有两只猫。", "type": "翻译"},
    {"q": "The dog is big.", "answer": "这只狗很大。", "type": "翻译"},
    {"q": "Today is Monday.", "answer": "今天是星期一。", "type": "翻译"},
    {"q": "I go to school by bus.", "answer": "我坐公共汽车去上学。", "type": "翻译"},
    {"q": "Good morning!", "answer": "早上好！", "type": "翻译"},
    {"q": "Thank you.", "answer": "谢谢你。", "type": "翻译"},
    {"q": "What time is it?", "answer": "现在几点了？", "type": "翻译"},
    {"q": "I am a student.", "answer": "我是一个学生。", "type": "翻译"},
    {"q": "Let's play together.", "answer": "我们一起玩吧。", "type": "翻译"},
]

ENGLISH_GRAMMAR_BANK = [
    {"q": "I ___ a student. (am/is/are)", "answer": "am", "type": "语法填空"},
    {"q": "She ___ a cat. (have/has)", "answer": "has", "type": "语法填空"},
    {"q": "There ___ three books on the desk. (is/are)", "answer": "are", "type": "语法填空"},
    {"q": "He ___ to school every day. (go/goes)", "answer": "goes", "type": "语法填空"},
    {"q": "This is ___ apple. (a/an)", "answer": "an", "type": "语法填空"},
    {"q": "I can ___ English. (speak/speaks)", "answer": "speak", "type": "语法填空"},
    {"q": "They ___ playing football. (is/are)", "answer": "are", "type": "语法填空"},
    {"q": "My mother ___ cooking. (is/are)", "answer": "is", "type": "语法填空"},
    {"q": "We ___ happy today. (am/is/are)", "answer": "are", "type": "语法填空"},
    {"q": "He ___ like milk. (don't/doesn't)", "answer": "doesn't", "type": "语法填空"},
    {"q": "___ you like bananas? (Do/Does)", "answer": "Do", "type": "语法填空"},
    {"q": "She ___ reading a book now. (is/are)", "answer": "is", "type": "语法填空"},
    {"q": "Look! The birds ___ flying. (is/are)", "answer": "are", "type": "语法填空"},
    {"q": "How ___ apples do you have? (much/many)", "answer": "many", "type": "语法填空"},
    {"q": "The cat is ___ the box. (in/on/at)", "answer": "in", "type": "语法填空"},
]

# ==================== 语文题库 ====================
CHINESE_PINYIN_BANK = [
    {"char": "学", "pinyin": "xué", "type": "拼音"},
    {"char": "校", "pinyin": "xiào", "type": "拼音"},
    {"char": "老", "pinyin": "lǎo", "type": "拼音"},
    {"char": "师", "pinyin": "shī", "type": "拼音"},
    {"char": "读", "pinyin": "dú", "type": "拼音"},
    {"char": "书", "pinyin": "shū", "type": "拼音"},
    {"char": "花", "pinyin": "huā", "type": "拼音"},
    {"char": "草", "pinyin": "cǎo", "type": "拼音"},
    {"char": "朋", "pinyin": "péng", "type": "拼音"},
    {"char": "友", "pinyin": "yǒu", "type": "拼音"},
    {"char": "快", "pinyin": "kuài", "type": "拼音"},
    {"char": "乐", "pinyin": "lè", "type": "拼音"},
    {"char": "祖", "pinyin": "zǔ", "type": "拼音"},
    {"char": "国", "pinyin": "guó", "type": "拼音"},
    {"char": "春", "pinyin": "chūn", "type": "拼音"},
    {"char": "天", "pinyin": "tiān", "type": "拼音"},
    {"char": "秋", "pinyin": "qiū", "type": "拼音"},
    {"char": "风", "pinyin": "fēng", "type": "拼音"},
    {"char": "雨", "pinyin": "yǔ", "type": "拼音"},
    {"char": "雪", "pinyin": "xuě", "type": "拼音"},
]

CHINESE_IDIOM_BANK = [
    {"q": "一心一___", "answer": "意", "hint": "形容专心致志", "type": "填字"},
    {"q": "三心二___", "answer": "意", "hint": "形容犹豫不决或不专心", "type": "填字"},
    {"q": "画蛇添___", "answer": "足", "hint": "比喻做多余的事", "type": "填字"},
    {"q": "守株待___", "answer": "兔", "hint": "比喻不劳而获", "type": "填字"},
    {"q": "掩耳盗___", "answer": "铃", "hint": "比喻自己欺骗自己", "type": "填字"},
    {"q": "亡羊补___", "answer": "牢", "hint": "比喻出了问题后及时补救", "type": "填字"},
    {"q": "刻舟求___", "answer": "剑", "hint": "比喻不知变通", "type": "填字"},
    {"q": "狐假虎___", "answer": "威", "hint": "比喻借别人的威势吓人", "type": "填字"},
    {"q": "对牛弹___", "answer": "琴", "hint": "比喻对不懂道理的人讲道理", "type": "填字"},
    {"q": "叶公好___", "answer": "龙", "hint": "比喻表面爱好而非真正喜欢", "type": "填字"},
    {"q": "拔苗助___", "answer": "长", "hint": "比喻违反事物发展规律", "type": "填字"},
    {"q": "井底之___", "answer": "蛙", "hint": "比喻见识短浅", "type": "填字"},
]

CHINESE_ANCIENT_POEM_BANK = [
    {"q": "床前明月光，___。", "answer": "疑是地上霜", "author": "李白《静夜思》", "type": "诗句填空"},
    {"q": "___，低头思故乡。", "answer": "举头望明月", "author": "李白《静夜思》", "type": "诗句填空"},
    {"q": "春眠不觉晓，___。", "answer": "处处闻啼鸟", "author": "孟浩然《春晓》", "type": "诗句填空"},
    {"q": "___，春风吹又生。", "answer": "野火烧不尽", "author": "白居易《赋得古原草送别》", "type": "诗句填空"},
    {"q": "锄禾日当午，___。", "answer": "汗滴禾下土", "author": "李绅《悯农》", "type": "诗句填空"},
    {"q": "白日依山尽，___。", "answer": "黄河入海流", "author": "王之涣《登鹳雀楼》", "type": "诗句填空"},
    {"q": "___，更上一层楼。", "answer": "欲穷千里目", "author": "王之涣《登鹳雀楼》", "type": "诗句填空"},
    {"q": "鹅鹅鹅，___。", "answer": "曲项向天歌", "author": "骆宾王《咏鹅》", "type": "诗句填空"},
    {"q": "两个黄鹂鸣翠柳，___。", "answer": "一行白鹭上青天", "author": "杜甫《绝句》", "type": "诗句填空"},
    {"q": "日照香炉生紫烟，___。", "answer": "遥看瀑布挂前川", "author": "李白《望庐山瀑布》", "type": "诗句填空"},
    {"q": "离离原上草，___。", "answer": "一岁一枯荣", "author": "白居易《赋得古原草送别》", "type": "诗句填空"},
    {"q": "小荷才露尖尖角，___。", "answer": "早有蜻蜓立上头", "author": "杨万里《小池》", "type": "诗句填空"},
]

# ==================== 科学题库 ====================
SCIENCE_BANK = [
    {"q": "水在什么温度会结冰？", "answer": "0°C", "options": ["-10°C", "0°C", "50°C", "100°C"], "category": "物质", "type": "选择题"},
    {"q": "水烧开（沸腾）的温度是多少？", "answer": "100°C", "options": ["0°C", "50°C", "80°C", "100°C"], "category": "物质", "type": "选择题"},
    {"q": "地球绕着什么转？", "answer": "太阳", "options": ["月亮", "太阳", "火星", "北极星"], "category": "天文", "type": "选择题"},
    {"q": "月亮绕着什么转？", "answer": "地球", "options": ["太阳", "地球", "火星", "木星"], "category": "天文", "type": "选择题"},
    {"q": "一年有多少个季节？", "answer": "4", "options": ["2", "3", "4", "5"], "category": "常识", "type": "选择题"},
    {"q": "植物通过什么来制造食物？", "answer": "光合作用", "options": ["呼吸作用", "光合作用", "蒸腾作用", "消化作用"], "category": "生物", "type": "选择题"},
    {"q": "人体最大的器官是什么？", "answer": "皮肤", "options": ["心脏", "肝脏", "皮肤", "大脑"], "category": "人体", "type": "选择题"},
    {"q": "声音是通过什么传播的？", "answer": "振动", "options": ["光线", "振动", "温度", "颜色"], "category": "物理", "type": "选择题"},
    {"q": "彩虹有几种颜色？", "answer": "7", "options": ["3", "5", "7", "9"], "category": "自然", "type": "选择题"},
    {"q": "蝌蚪长大后会变成什么？", "answer": "青蛙", "options": ["鱼", "蛇", "青蛙", "乌龟"], "category": "生物", "type": "选择题"},
    {"q": "太阳系中最大的行星是什么？", "answer": "木星", "options": ["地球", "火星", "木星", "土星"], "category": "天文", "type": "选择题"},
    {"q": "含羞草被碰触后会怎样？", "answer": "叶子合拢", "options": ["开花", "叶子合拢", "变色", "长高"], "category": "生物", "type": "选择题"},
    {"q": "铁在潮湿环境中容易发生什么？", "answer": "生锈", "options": ["融化", "生锈", "膨胀", "变硬"], "category": "物质", "type": "选择题"},
    {"q": "人类呼吸需要什么气体？", "answer": "氧气", "options": ["氮气", "氧气", "二氧化碳", "氢气"], "category": "人体", "type": "选择题"},
    {"q": "磁铁能吸引什么材料？", "answer": "铁", "options": ["木头", "塑料", "铁", "玻璃"], "category": "物理", "type": "选择题"},
    {"q": "世界上最大的动物是什么？", "answer": "蓝鲸", "options": ["大象", "长颈鹿", "蓝鲸", "鲨鱼"], "category": "生物", "type": "选择题"},
    {"q": "电池的能量来自什么转化？", "answer": "化学能", "options": ["光能", "热能", "化学能", "风能"], "category": "物理", "type": "选择题"},
    {"q": "植物的根主要作用是什么？", "answer": "吸收水分和养分", "options": ["进行光合作用", "吸收水分和养分", "传播种子", "释放氧气"], "category": "生物", "type": "选择题"},
    {"q": "地球表面大部分被什么覆盖？", "answer": "海洋", "options": ["森林", "沙漠", "海洋", "草原"], "category": "地理", "type": "选择题"},
    {"q": "恐龙生活在什么时代？", "answer": "中生代", "options": ["古生代", "中生代", "新生代", "现代"], "category": "自然", "type": "选择题"},
]


# ==================== 出题函数 ====================

def generate_math_questions(knowledge_point: str, count: int, difficulty: int = 2):
    """生成数学题"""
    questions = []
    templates = MATH_TEMPLATES.get(knowledge_point, MATH_TEMPLATES["default"])

    for i in range(count):
        tpl = random.choice(templates)
        max_num = difficulty * 20 + 10
        a = random.randint(1, max_num)
        b = random.randint(1, max(1, a))
        q_text = tpl["q"].format(a=a, b=b)

        answer = ""
        if "+" in tpl["q"]:
            answer = str(a + b)
        elif "-" in tpl["q"]:
            answer = str(a - b)
        elif "×" in tpl["q"]:
            answer = str(a * b)
        elif "÷" in tpl["q"] and b != 0:
            a = b * random.randint(1, 10)
            q_text = tpl["q"].format(a=a, b=b)
            answer = str(a // b)

        options = None
        if tpl["type"] == "选择题" or random.random() < 0.3:
            correct = int(answer) if answer.isdigit() else 0
            opts = sorted(set([correct, correct + random.randint(1, 5), correct - random.randint(1, 5), correct + random.randint(2, 8)]))
            options = [str(o) for o in opts[:4]]
            if answer not in options:
                options[-1] = answer

        questions.append({
            "index": i + 1,
            "question": q_text,
            "type": "选择题" if options else tpl["type"],
            "options": options,
            "answer": answer,
            "user_answer": "",
            "is_correct": None,
        })
    return questions


def generate_english_questions(knowledge_point: str, count: int, difficulty: int = 2):
    """生成英语题"""
    questions = []
    kp = knowledge_point.lower()

    # 根据知识点选择题型
    if any(k in kp for k in ["单词", "词汇", "word", "水果", "动物", "颜色", "数字", "食物", "身体", "家庭", "学习", "星期", "季节", "形容词", "动作"]):
        # 按类别过滤
        category_map = {
            "水果": "水果", "动物": "动物", "颜色": "颜色", "数字": "数字",
            "食物": "食物", "身体": "身体", "家庭": "家庭", "学习": "学习",
            "星期": "星期", "季节": "季节", "形容词": "形容词", "动作": "动作",
        }
        category = None
        for k, v in category_map.items():
            if k in kp:
                category = v
                break
        pool = [w for w in ENGLISH_WORD_BANK if (category is None or w["category"] == category)]
        if not pool:
            pool = ENGLISH_WORD_BANK
        questions = _gen_word_questions(pool, count)

    elif any(k in kp for k in ["语法", "grammar", "填空"]):
        questions = _gen_from_bank(ENGLISH_GRAMMAR_BANK, count)

    elif any(k in kp for k in ["句子", "翻译", "sentence"]):
        questions = _gen_from_bank(ENGLISH_SENTENCE_BANK, count)

    else:
        # 混合出题：单词 + 语法 + 句子
        word_count = max(1, count // 3)
        grammar_count = max(1, count // 3)
        sentence_count = count - word_count - grammar_count

        pool = random.sample(ENGLISH_WORD_BANK, min(len(ENGLISH_WORD_BANK), word_count * 4))
        questions.extend(_gen_word_questions(pool, word_count))
        questions.extend(_gen_from_bank(ENGLISH_GRAMMAR_BANK, grammar_count))
        questions.extend(_gen_from_bank(ENGLISH_SENTENCE_BANK, sentence_count))
        random.shuffle(questions)

    # 重新编号
    for i, q in enumerate(questions):
        q["index"] = i + 1
    return questions[:count]


def _gen_word_questions(pool, count):
    """从单词库生成题目（英译中或中译英）"""
    questions = []
    selected = random.sample(pool, min(len(pool), count))
    all_meanings = [w["meaning"] for w in ENGLISH_WORD_BANK]
    all_words = [w["word"] for w in ENGLISH_WORD_BANK]

    for i, item in enumerate(selected):
        if random.random() < 0.5:
            # 英译中：看英文选中文
            wrong_opts = random.sample([m for m in all_meanings if m != item["meaning"]], 3)
            opts = wrong_opts + [item["meaning"]]
            random.shuffle(opts)
            questions.append({
                "index": i + 1,
                "question": f"\"{item['word']}\" 的中文意思是什么？",
                "type": "选择题",
                "options": opts,
                "answer": item["meaning"],
                "user_answer": "",
                "is_correct": None,
            })
        else:
            # 中译英：看中文选英文
            wrong_opts = random.sample([w for w in all_words if w != item["word"]], 3)
            opts = wrong_opts + [item["word"]]
            random.shuffle(opts)
            questions.append({
                "index": i + 1,
                "question": f"\"{item['meaning']}\" 用英语怎么说？",
                "type": "选择题",
                "options": opts,
                "answer": item["word"],
                "user_answer": "",
                "is_correct": None,
            })
    return questions


def _gen_from_bank(bank, count):
    """从题库随机抽题"""
    questions = []
    selected = random.sample(bank, min(len(bank), count))
    for i, item in enumerate(selected):
        q = {
            "index": i + 1,
            "question": item["q"],
            "type": item.get("type", "填空题"),
            "options": None,
            "answer": item["answer"],
            "user_answer": "",
            "is_correct": None,
        }
        # 如果有提示信息
        if "hint" in item:
            q["question"] += f"（提示：{item['hint']}）"
        if "author" in item:
            q["question"] += f"（{item['author']}）"
        questions.append(q)
    return questions


def generate_chinese_questions(knowledge_point: str, count: int, difficulty: int = 2):
    """生成语文题"""
    questions = []
    kp = knowledge_point

    if any(k in kp for k in ["拼音", "注音"]):
        questions = _gen_pinyin_questions(count)
    elif any(k in kp for k in ["成语", "词语"]):
        questions = _gen_from_bank([{"q": f"{item['q']}", "answer": item["answer"], "type": item["type"], "hint": item["hint"]} for item in CHINESE_IDIOM_BANK], count)
    elif any(k in kp for k in ["古诗", "诗词", "诗句"]):
        questions = _gen_from_bank([{"q": item["q"], "answer": item["answer"], "type": item["type"], "author": item["author"]} for item in CHINESE_ANCIENT_POEM_BANK], count)
    else:
        # 混合：拼音 + 成语 + 古诗
        pinyin_count = max(1, count // 3)
        idiom_count = max(1, count // 3)
        poem_count = count - pinyin_count - idiom_count
        questions.extend(_gen_pinyin_questions(pinyin_count))
        questions.extend(_gen_from_bank([{"q": f"{item['q']}", "answer": item["answer"], "type": item["type"], "hint": item["hint"]} for item in CHINESE_IDIOM_BANK], idiom_count))
        questions.extend(_gen_from_bank([{"q": item["q"], "answer": item["answer"], "type": item["type"], "author": item["author"]} for item in CHINESE_ANCIENT_POEM_BANK], poem_count))
        random.shuffle(questions)

    for i, q in enumerate(questions):
        q["index"] = i + 1
    return questions[:count]


def _gen_pinyin_questions(count):
    """生成拼音题（看字选拼音）"""
    questions = []
    selected = random.sample(CHINESE_PINYIN_BANK, min(len(CHINESE_PINYIN_BANK), count))
    all_pinyins = [p["pinyin"] for p in CHINESE_PINYIN_BANK]

    for i, item in enumerate(selected):
        wrong_opts = random.sample([p for p in all_pinyins if p != item["pinyin"]], min(3, len(all_pinyins) - 1))
        opts = wrong_opts + [item["pinyin"]]
        random.shuffle(opts)
        questions.append({
            "index": i + 1,
            "question": f"「{item['char']}」的正确拼音是什么？",
            "type": "选择题",
            "options": opts,
            "answer": item["pinyin"],
            "user_answer": "",
            "is_correct": None,
        })
    return questions


def generate_science_questions(knowledge_point: str, count: int, difficulty: int = 2):
    """生成科学题"""
    kp = knowledge_point
    # 按类别过滤
    category_map = {
        "天文": "天文", "生物": "生物", "物理": "物理", "物质": "物质",
        "人体": "人体", "自然": "自然", "地理": "地理", "常识": "常识",
    }
    category = None
    for k, v in category_map.items():
        if k in kp:
            category = v
            break
    pool = [q for q in SCIENCE_BANK if (category is None or q["category"] == category)]
    if not pool:
        pool = SCIENCE_BANK

    selected = random.sample(pool, min(len(pool), count))
    questions = []
    for i, item in enumerate(selected):
        questions.append({
            "index": i + 1,
            "question": item["q"],
            "type": item.get("type", "选择题"),
            "options": item.get("options"),
            "answer": item["answer"],
            "user_answer": "",
            "is_correct": None,
        })
    return questions


def generate_questions(subject_id: str, knowledge_point: str, count: int, difficulty: int = 2):
    """根据学科分发到对应的出题函数"""
    if subject_id == "english":
        return generate_english_questions(knowledge_point, count, difficulty)
    elif subject_id == "chinese":
        return generate_chinese_questions(knowledge_point, count, difficulty)
    elif subject_id == "science":
        return generate_science_questions(knowledge_point, count, difficulty)
    else:
        return generate_math_questions(knowledge_point, count, difficulty)


@router.post("/generate", response_model=PracticeSessionOut)
async def generate_practice(data: PracticeSessionCreate, db: Session = Depends(get_db)):
    use_ai = False
    questions = None
    practice_mode = data.practice_mode or "custom"

    # 检查是否启用了全局大模型配置（自动同步iFlow）
    llm_config = get_llm_config_with_iflow(db)

    # 根据练习模式准备知识点和上下文
    extra_context_for_prompt = ""
    auto_knowledge_point = data.knowledge_point or ""

    if practice_mode == "wrong_review":
        # 错题练习：从错题本中提取题目作为出题依据
        wrong_qs_raw = (
            db.query(WrongQuestion)
            .filter(WrongQuestion.user_id == data.user_id, WrongQuestion.is_resolved == False)
            .order_by(WrongQuestion.mistake_date.desc())
            .limit(20)
            .all()
        )
        if data.subject_id:
            wrong_qs_raw = [wq for wq in wrong_qs_raw if wq.subject_id == data.subject_id]
        if wrong_qs_raw:
            wrong_points = list(set(wq.knowledge_point for wq in wrong_qs_raw if wq.knowledge_point))
            auto_knowledge_point = auto_knowledge_point or "、".join(wrong_points[:5])
            wrong_details = []
            for wq in wrong_qs_raw[:10]:
                wrong_details.append(f"- 知识点：{wq.knowledge_point}，题目：{wq.question_content[:60]}，正确答案：{wq.correct_answer or '未知'}")
            extra_context_for_prompt = f"\n\n【错题练习模式】请根据以下学生做错的题目，出相似的变式题来帮助巩固：\n" + "\n".join(wrong_details)

    elif practice_mode == "important_review":
        # 重点知识练习：从学习记录中提取重点/薄弱知识点
        records = (
            db.query(LearningRecord)
            .filter(LearningRecord.user_id == data.user_id)
            .order_by(LearningRecord.study_date.desc())
            .limit(30)
            .all()
        )
        if data.subject_id:
            records = [r for r in records if r.subject_id == data.subject_id]
        # 优先选重要+薄弱的
        important = [r for r in records if r.is_important or r.mastery_level <= 2]
        if not important:
            important = records[:10]
        if important:
            kp_list = list(set(r.knowledge_point for r in important if r.knowledge_point))
            auto_knowledge_point = auto_knowledge_point or "、".join(kp_list[:5])
            kp_details = []
            for r in important[:10]:
                mastery_text = {1: "未掌握", 2: "需加强", 3: "一般", 4: "熟练", 5: "精通"}
                kp_details.append(f"- {r.knowledge_point}（掌握度：{mastery_text.get(r.mastery_level, '一般')}，{'⭐重点' if r.is_important else ''}）")
            extra_context_for_prompt = f"\n\n【重点知识练习模式】请根据以下学生的重点/薄弱知识点出题来巩固复习：\n" + "\n".join(kp_details)

    if llm_config and llm_config.api_url and llm_config.model_name:
        # 获取用户年级
        user = db.query(User).filter(User.id == data.user_id).first()
        grade = user.grade if user else "三年级"

        # 查询用户知识库：薄弱知识点 + 错题
        weak_records = (
            db.query(LearningRecord)
            .filter(LearningRecord.user_id == data.user_id, LearningRecord.mastery_level <= 2)
            .all()
        )
        weak_points = list(set(r.knowledge_point for r in weak_records if r.knowledge_point))

        wrong_qs_raw_all = (
            db.query(WrongQuestion)
            .filter(WrongQuestion.user_id == data.user_id, WrongQuestion.is_resolved == False)
            .order_by(WrongQuestion.mistake_date.desc())
            .limit(10)
            .all()
        )
        wrong_qs = [
            {"knowledge_point": wq.knowledge_point, "question": wq.question_content[:80],
             "correct_answer": wq.correct_answer or ""}
            for wq in wrong_qs_raw_all if wq.knowledge_point
        ]

        # 如果有学科过滤
        if data.subject_id:
            weak_points_filtered = list(set(
                r.knowledge_point for r in weak_records
                if r.knowledge_point and r.subject_id == data.subject_id
            ))
            wrong_qs_filtered = [
                {"knowledge_point": wq.knowledge_point, "question": wq.question_content[:80],
                 "correct_answer": wq.correct_answer or ""}
                for wq in wrong_qs_raw_all
                if wq.knowledge_point and wq.subject_id == data.subject_id
            ]
            if weak_points_filtered or wrong_qs_filtered:
                weak_points = weak_points_filtered
                wrong_qs = wrong_qs_filtered

        # 综合练习模式：题目数量由系统决定（约25题）
        exam_count = 30 if practice_mode == "exam" else (data.total_questions or 5)

        prompt = build_practice_prompt(
            subject_id=data.subject_id or "math",
            knowledge_point=auto_knowledge_point,
            count=exam_count,
            grade=grade,
            weak_points=weak_points,
            wrong_questions=wrong_qs,
            practice_mode=practice_mode,
        )
        # 追加练习模式的额外上下文
        if extra_context_for_prompt:
            prompt += extra_context_for_prompt

        try:
            llm_response = await call_llm(
                provider=llm_config.provider,
                api_url=llm_config.api_url,
                api_key=llm_config.api_key,
                model_name=llm_config.model_name,
                prompt=prompt,
                deep_thinking=llm_config.deep_thinking,
            )
            questions = parse_llm_questions(llm_response, exam_count)
            if questions:
                use_ai = True
        except Exception as e:
            import traceback
            print(f"[LLM ERROR] 大模型出题失败: {e}")
            traceback.print_exc()

    # 回退到本地题库
    if not questions:
        questions = generate_questions(
            subject_id=data.subject_id or "math",
            knowledge_point=auto_knowledge_point,
            count=data.total_questions or 5,
        )
    session = PracticeSession(
        user_id=data.user_id,
        subject_id=data.subject_id,
        knowledge_point=auto_knowledge_point,
        question_type=("AI出题" if use_ai else "本地题库"),
        practice_mode=practice_mode,
        total_questions=len(questions),
        status="practicing",
        questions_json=json.dumps(questions, ensure_ascii=False),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/", response_model=List[PracticeSessionOut])
def list_sessions(user_id: str = Query(...), db: Session = Depends(get_db)):
    return (
        db.query(PracticeSession)
        .filter(PracticeSession.user_id == user_id)
        .order_by(PracticeSession.created_at.desc())
        .limit(20)
        .all()
    )


@router.post("/tts/generate")
async def generate_tts(data: dict):
    """生成英语听力语音（Edge TTS）"""
    text = data.get("text", "").strip()
    if not text:
        raise HTTPException(400, "缺少文本内容")

    # 用文本 hash 做文件名缓存
    text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
    filename = f"{text_hash}.mp3"
    filepath = os.path.join(TTS_DIR, filename)

    # 如果缓存存在直接返回
    if os.path.exists(filepath):
        return {"url": f"/api/practice/tts/audio/{filename}"}

    try:
        import edge_tts
        voice = data.get("voice", "en-US-JennyNeural")
        rate = data.get("rate", "-10%")
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        await communicate.save(filepath)
        return {"url": f"/api/practice/tts/audio/{filename}"}
    except Exception as e:
        print(f"[TTS ERROR] {e}")
        raise HTTPException(500, f"语音生成失败: {str(e)}")


@router.get("/tts/audio/{filename}")
def get_tts_audio(filename: str):
    """获取 TTS 音频文件"""
    filepath = os.path.join(TTS_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(404, "音频文件不存在")
    return FileResponse(filepath, media_type="audio/mpeg")


@router.post("/{session_id}/submit")
def submit_answers(session_id: str, answers: dict, db: Session = Depends(get_db)):
    """提交答案: answers = {"answers": {"1": "42", "2": "10", ...}}"""
    session = db.query(PracticeSession).filter(PracticeSession.id == session_id).first()
    if not session:
        raise HTTPException(404, "练习不存在")

    questions = json.loads(session.questions_json)
    user_answers = answers.get("answers", {})
    correct = 0
    wrong_list = []
    total_score = 0
    earned_score = 0

    for q in questions:
        idx = str(q["index"])
        q_score = q.get("score", 0)
        total_score += q_score
        if idx in user_answers:
            q["user_answer"] = user_answers[idx]
            q["is_correct"] = user_answers[idx].strip() == q["answer"].strip()
            if q["is_correct"]:
                correct += 1
                earned_score += q_score
            else:
                wrong_list.append(q)

    session.correct_count = correct
    session.status = "completed"
    session.questions_json = json.dumps(questions, ensure_ascii=False)

    # 将做错的题目自动记录到错题本
    for wq in wrong_list:
        wrong_record = WrongQuestion(
            user_id=session.user_id,
            subject_id=session.subject_id,
            knowledge_point=session.knowledge_point or "",
            question_content=wq.get("question", ""),
            my_answer=wq.get("user_answer", ""),
            correct_answer=wq.get("answer", ""),
            error_type="练习错题",
        )
        db.add(wrong_record)

    db.commit()

    # 如果有分值信息，用分值计算；否则回退到比例计算
    if total_score > 0:
        score = earned_score
    else:
        score = round(correct / len(questions) * 100) if questions else 0

    return {
        "total": len(questions),
        "correct": correct,
        "score": score,
        "total_score": total_score if total_score > 0 else 100,
        "earned_score": earned_score,
        "details": questions,
        "wrong_added": len(wrong_list),
    }


@router.post("/{session_id}/abandon")
def abandon_session(session_id: str, db: Session = Depends(get_db)):
    """废弃练习"""
    session = db.query(PracticeSession).filter(PracticeSession.id == session_id).first()
    if not session:
        raise HTTPException(404, "练习不存在")
    session.status = "abandoned"
    db.commit()
    return {"success": True}


@router.get("/{session_id}", response_model=PracticeSessionOut)
def get_session(session_id: str, db: Session = Depends(get_db)):
    """获取单个练习详情"""
    session = db.query(PracticeSession).filter(PracticeSession.id == session_id).first()
    if not session:
        raise HTTPException(404, "练习不存在")
    return session
