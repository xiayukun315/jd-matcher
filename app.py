"""jd-matcher 的界面版 v0.1
运行：streamlit run app.py
"""

import streamlit as st

from jd_matcher import match

st.set_page_config(page_title="JD 匹配器", page_icon="◎", layout="centered")

st.title("JD 匹配器")
st.caption("贴一段简历 + 一段岗位描述，看你差在哪。v0.1 关键词匹配，不调 API。")

col1, col2 = st.columns(2)
resume = col1.text_area("我的简历", height=280, placeholder="把简历正文贴进来")
jd = col2.text_area("岗位描述（JD）", height=280, placeholder="把岗位职责 + 任职要求整段贴进来")

if st.button("算一算", type="primary", use_container_width=True):
    if not resume.strip() or not jd.strip():
        st.warning("两边都要填。")
    else:
        score, hit, miss = match(resume, jd)

        st.divider()
        st.metric("匹配分", f"{score} / 100")
        st.progress(score / 100)

        a, b = st.columns(2)
        a.success("命中 " + str(len(hit)) + " 项\n\n" + ("、".join(hit) if hit else "无"))
        b.error("差距 " + str(len(miss)) + " 项\n\n" + ("、".join(miss) if miss else "无"))

        if miss:
            st.info("优先补：" + "、".join(miss[:3]))

        if score < 50:
            st.caption("结论：差距偏大。要么补技能，要么换一个更贴合的岗位。")
        elif score < 75:
            st.caption("结论：可以投。补齐差距项后成功率明显上升。")
        else:
            st.caption("结论：够格了，直接投。别再刷教程了。")
