"""jd-matcher v0.2
最小闭环：一段简历 + 一段 JD -> 一个匹配分。
纯关键词匹配，不接 API。

v0.2 改动：
  1. 支持中文术语（大模型 / 智能体 / 提示词 ...）—— 中文 JD 不再拿 0 分
  2. 加置信度提示 —— 识别到的技能词太少时，明说这个分数不可信
"""

import os
import re
import sys

# ↓↓↓ 这是「词典」不是「技能表」：目标岗位常见的词都要留着，用于识别 JD 要求的是啥 ↓↓↓
SKILLS = [
    # 语言
    "python", "java", "c", "c++", "sql",
    # Java 后端
    "spring", "springboot", "mybatis", "maven", "mysql", "redis",
    # Python / 数据
    "pandas", "numpy", "requests", "flask", "fastapi", "streamlit",
    # AI / Agent
    "llm", "prompt", "rag", "agent", "mcp", "embedding",
    "langchain", "openai", "deepseek", "ollama", "transformer",
    # 工程工具
    "git", "github", "linux", "docker", "api", "json",
]

# ↓↓↓ 中文术语 -> 标准词。国内外企用英文，国内公司用中文，两边都得认 ↓↓↓
ALIASES = {
    "大模型": "llm",
    "语言模型": "llm",
    "机器学习": "ml",
    "深度学习": "dl",
    "智能体": "agent",
    "代理": "agent",
    "提示词": "prompt",
    "提示工程": "prompt",
    "检索增强": "rag",
    "知识库": "rag",
    "向量": "embedding",
    "微调": "finetune",
    "数据库": "sql",
    "接口": "api",
    "后端": "backend",
    "爬虫": "spider",
    "数据分析": "pandas",
}

# ↓↓↓ 简历：只写真做过的。判断标准是「不靠 AI 也能写出 20 行能跑的代码」↓↓↓
DEFAULT_RESUME = """
计算机科学与技术大二在读。
熟悉 Java 基础语法，能写面向对象的小程序，这学期在上 Java 课程。
Python 能写基础脚本，做过课程的数据处理作业。
会用 Git 提交代码，了解 GitHub 基本操作。
"""

# ↓↓↓ JD：贴一段真实的岗位描述，别自己编 ↓↓↓
DEFAULT_JD = """
岗位职责：参与 AI 应用开发，负责智能体产品的功能实现。
任职要求：
1. 熟悉 Python，掌握 Pandas / Numpy 数据处理；
2. 了解 LLM、Prompt 工程与 RAG 检索增强；
3. 熟悉 Git 协作流程；
4. 有 Agent 项目经验者优先。
"""


def load_text(filename, fallback):
    """有同名 txt 就读文件，没有就用写死的示例。"""
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    return fallback


def normalize(text):
    """把中文术语补上对应的英文标准词，让后面的扫描两边都能认。"""
    t = text.lower()
    extra = []
    for cn, std in ALIASES.items():
        if cn in t:
            extra.append(std)
    if extra:
        t = t + " " + " ".join(extra)
    return t


def find_skills(text):
    """从一段文字里找出出现过的技能词。用词边界，避免 react 里的 c 被当成 C 语言。"""
    low = normalize(text)
    found = set()
    for s in SKILLS:
        pattern = r"(?<![a-z0-9])" + re.escape(s) + r"(?![a-z0-9+#])"
        if re.search(pattern, low):
            found.add(s)
    return found


def match(resume, jd):
    jd_skills = find_skills(jd)
    resume_skills = find_skills(resume)

    if not jd_skills:
        return 0, [], []

    hit = jd_skills & resume_skills
    miss = jd_skills - resume_skills
    score = round(len(hit) / len(jd_skills) * 100)
    return score, sorted(hit), sorted(miss)


def report(resume, jd):
    score, hit, miss = match(resume, jd)
    total = len(hit) + len(miss)

    print("=" * 46)
    print(f"  匹配分：{score} / 100")
    print("=" * 46)
    print(f"命中 {len(hit)} 项：" + ("、".join(hit) if hit else "无"))
    print(f"差距 {len(miss)} 项：" + ("、".join(miss) if miss else "无"))
    print(f"识别到 {total} 个技能词")

    # 样本太小的时候，分数没有意义。这一点必须让使用者看到。
    if total < 3:
        print()
        print(f"[不可信] 只识别到 {total} 个技能词。")
        print("         这个分数只说明「我认得的词里你占了几个」，不代表你真的匹配。")
        print("         JD 太笼统，或者词表还缺词。这类岗位要人工判断，别信这个数。")
        print()
        return

    if miss:
        print()
        print("建议：下面这些词 JD 里有、简历里没有，优先补前三个 ——")
        for s in miss[:3]:
            print(f"  - {s}")

    if score < 50:
        print()
        print("结论：差距偏大。要么补技能，要么换一个更贴合的岗位。")
    elif score < 75:
        print()
        print("结论：可以投。补齐差距项后成功率明显上升。")
    else:
        print()
        print("结论：够格了，直接投。别再刷教程了。")
    print()


if __name__ == "__main__":
    # 用法：python jd_matcher.py jd1.txt
    jd_file = sys.argv[1] if len(sys.argv) > 1 else "jd.txt"

    if not os.path.exists(jd_file):
        print(f"[提示] 没找到 {jd_file}，先用内置示例跑。")
    print(f"[简历] resume.txt    [岗位] {jd_file}")
    print()

    resume = load_text("resume.txt", DEFAULT_RESUME)
    jd = load_text(jd_file, DEFAULT_JD)
    report(resume, jd)
