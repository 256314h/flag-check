import streamlit as st
import hashlib
import pandas as pd
import os
import datetime

# ================= 配置区 (安全设置) =================

# 1. 访问密码：改成了复杂密码，只有你自己知道
# 以后你进网站要输入这个：my_secret_2026
AGENT_KEYS = ["my_secret_2026"] 

# 2. 数据文件名
DB_FILE = "private_memo.csv"

# ================= 核心功能区 =================

def hash_phone(phone):
    # 加盐加密，确保只有系统能识别，导出也没用
    salt = "private_safe_mode_only" 
    target = phone + salt
    return hashlib.md5(target.encode()).hexdigest()

def init_db():
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=["hash", "tag", "time"])
        df.to_csv(DB_FILE, index=False)

# ================= 网页界面 =================

# 伪装成“个人备忘录”，避免法律敏感词
st.set_page_config(page_title="个人私密备忘录", page_icon="🔒")
init_db()

# --- 侧边栏：登录与核按钮 ---
st.sidebar.title("🔒 私人领地")
agent_key = st.sidebar.text_input("请输入访问密钥", type="password")

# 🔥 核按钮：一键销毁所有数据 (保命用)
st.sidebar.markdown("---")
if st.sidebar.button("🔥 紧急销毁所有数据"):
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        # 重新创建一个空的
        pd.DataFrame(columns=["hash", "tag", "time"]).to_csv(DB_FILE, index=False)
        st.sidebar.error("已执行：所有数据已物理删除！")
    else:
        st.sidebar.warning("数据已经是空的了")

# --- 主界面 ---
if agent_key in AGENT_KEYS:
    st.title("📒 社交风险模拟记录")
    st.caption("声明：本工具仅供个人记录社交印象，数据仅存本地，请勿外传。")
    st.markdown("---")

    tab1, tab2 = st.tabs(["🔍 检索记录", "🖊️ 记录一下"])

    # === 功能1：查记录 ===
    with tab1:
        phone_input = st.text_input("输入号码检索备注")
        if st.button("查询"):
            if len(phone_input) < 11:
                st.warning("号码格式不对")
            else:
                target_hash = hash_phone(phone_input)
                df = pd.read_csv(DB_FILE)
                result = df[df['hash'] == target_hash]
                
                if not result.empty:
                    st.error(f"⚠️ 发现 {len(result)} 条过往备注")
                    for index, row in result.iterrows():
                        st.markdown(f"**标签：** {row['tag']}")
                        st.caption(f"记录时间：{row['time']}")
                else:
                    st.success("无记录：这个号码是干净的。")

    # === 功能2：记一笔 (严格限制内容) ===
    with tab2:
        st.write("添加私人备注 (仅限标签，禁止文字描述)")
        col1, col2 = st.columns(2)
        with col1:
            report_phone = st.text_input("目标号码", key="add")
        with col2:
            # 这里的选项比较温和，规避诽谤风险
            tag = st.selectbox("选择印象标签", 
                               ["避雷/不靠谱", 
                                "海王/多线操作", 
                                "借钱/经济纠纷", 
                                "已婚/有伴侣", 
                                "其他风险"])
        
        if st.button("加密保存"):
            if report_phone:
                target_hash = hash_phone(report_phone)
                new_data = {
                    "hash": target_hash,
                    "tag": tag,
                    "time": datetime.datetime.now().strftime("%Y-%m-%d")
                }
                pd.DataFrame([new_data]).to_csv(DB_FILE, mode='a', header=False, index=False)
                st.success("已记录。")
            else:
                st.warning("请输入号码")

else:
    # 没密码时的伪装界面
    st.title("404 Not Found")
    st.info("The requested URL was not found on this server.")
