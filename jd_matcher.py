"""jd-matcher v0.1
最小闭环：一段简历 + 一段 JD -> 一个匹配分。
第一版不接 API，纯关键词匹配。跑通比先进重要。
"""

import re

# ↓↓↓ 这一块你必须自己改一次：把你简历里真实有的技术，和你目标岗位常要的技术，全加进来 ↓↓↓
SKILLS = [
]


def find_skills(text):
    """从一段文字里找出出现过的技能词。用词边界，避免 react 里的 c 被当成 C 语言。"""
    low = text.lower()
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

    print("=" * 46)
    print(f"  匹配分：{score} / 100")
    print("=" * 46)
    print(f"命中 {len(hit)} 项：" + ("、".join(hit) if hit else "无"))
    print(f"差距 {len(miss)} 项：" + ("、".join(miss) if miss else "无"))

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
    RESUME = """
    计算机科学与技术大二在读。
    JD = """
    岗位职责：参与 AI 应用开发，负责智能体产品的功能实现。
    任职要求：
    1. 熟悉 Python，掌握 Pandas / Numpy 数据处理；
    2. 了解 LLM、Prompt 工程与 RAG 检索增强；
    3. 熟悉 Git 协作流程；
    4. 有 Agent 项目经验者优先。
    """

    report(RESUME, JD)
