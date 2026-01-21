import streamlit as st
import hashlib
import pandas as pd
import os
import datetime

# ================= 配置区 =================
# 管理员/代理密钥 (你自己或者大代理用这个密码进去)
AGENT_KEYS = ["8888", "vip666", "admin2026"]
# 数据文件
DB_FILE = "black_box_data.csv"
# 白名单文件
WHITE_LIST_FILE = "whitelist.csv"

# ================= 核心函数 =================
def hash_phone(phone):
    salt = "project_girls_help_girls_2026" 
    target = phone + salt
    return hashlib.md5(target.encode()).hexdigest()

def init_db():
    if not os.path.exists(DB_FILE):
        # 注意：这里删除了 comment 字段，只留 tag，为了安全
        df = pd.DataFrame(columns=["hash", "tag", "time", "agent_id"])
        df.to_csv(DB_FILE, index=False)
    if not os.path.exists(WHITE_LIST_FILE):
        df_white = pd.DataFrame(columns=["hash", "reason", "time"])
        df_white.to_csv(WHITE_LIST_FILE, index=False)

# ================= 网页界面 =================
st.set_page_config(page_title="女性互助避雷系统", page_icon="🚫")
init_db()

# --- 侧边栏 ---
st.sidebar.title("🚫 互助避雷联盟")
st.sidebar.info("这是一个只有女性知道的秘密基地。\n在这里，我们共享信息，让渣男无处遁形。")
agent_key = st.sidebar.text_input("请输入通行密钥", type="password")

# --- 法律免责悬浮窗 ---
st.warning("📢 **严正声明**：本平台数据由用户匿名自发标记，仅供参考。为了保护隐私，系统仅存储哈希加密数据，不保留明文手机号。禁止恶意诽谤。")

if agent_key in AGENT_KEYS:
    st.title("大数据不会说谎 💔")
    st.markdown("### —— 别让你的眼泪，变成下一个姐妹的学费。")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["🔍 查查现在的他", "💣 曝光那个渣男", "🛡️ 误伤申诉"])

    # === 功能1：查询 (带诱导逻辑) ===
    with tab1:
        st.subheader("输入号码，查看他的“成分”")
        phone_input = st.text_input("请输入他的手机号", max_chars=11)
        
        if st.button("立即检测", type="primary"):
            if len(phone_input) < 11:
                st.error("手机号都不对，怎么查？")
            else:
                target_hash = hash_phone(phone_input)
                
                # 先查白名单
                df_white = pd.read_csv(WHITE_LIST_FILE)
                if target_hash in df_white['hash'].values:
                    st.success("✅ 该号码已通过申诉清洗，暂无风险。")
                else:
                    # 查黑名单
                    df = pd.read_csv(DB_FILE)
                    result = df[df['hash'] == target_hash]
                    
                    if not result.empty:
                        st.error(f"🚨 **高能预警！** 数据库中发现 {len(result)} 条关于他的记录！")
                        st.write("### 他的标签：")
                        for index, row in result.iterrows():
                            # 用醒目的红色显示标签
                            st.markdown(f"#### 🚩 **{row['tag']}**")
                            st.caption(f"标记时间: {row['time']}")
                        st.markdown("---")
                        st.error("大数据建议：快跑！别回头！")
                    else:
                        # === 核心诱导逻辑 ===
                        st.success("🍃 暂时安全：目前没有姐妹标记过这个号码。")
                        
                        st.markdown("---")
                        st.info("💡 **但是......别高兴得太早。**")
                        st.markdown("""
                        **大数据的力量来源于每一个“你”。**
                        你查的这个人可能是干净的。
                        **但那个曾经伤害过你的前任呢？**
                        他现在可能正在欺骗另一个无辜的女生。
                        """)
                        st.markdown("👉 **举手之劳，救人一命。去【曝光那个渣男】页面，把他挂上去！**")

    # === 功能2：标记 (只能选，不能写) ===
    with tab2:
        st.subheader("匿名录入，造福姐妹")
        st.caption("放心，系统采用 MD5 不可逆加密，没人知道是你发的。")
        
        col1, col2 = st.columns(2)
        with col1:
            report_phone = st.text_input("渣男手机号", key="report")
        with col2:
            # 这里的标签你可以自己加，越毒越好
            tags = st.selectbox("他做了什么？(单选)", 
                               ["请选择...", 
                                "海王/时间管理大师", 
                                "借钱不还/软饭男", 
                                "隐瞒已婚/有对象", 
                                "冷暴力/PUA高手", 
                                "yp/私生活混乱", 
                                "吃饭逃单/抠门", 
                                "妈宝男",
                                "有暴力倾向"])
        
        if st.button("⚡ 加密挂墙"):
            if report_phone and tags != "请选择...":
                target_hash = hash_phone(report_phone)
                new_data = {
                    "hash": target_hash,
                    "tag": tags,
                    "time": datetime.datetime.now().strftime("%Y-%m-%d"),
                    "agent_id": agent_key
                }
                new_df = pd.DataFrame([new_data])
                new_df.to_csv(DB_FILE, mode='a', header=False, index=False)
                st.balloons() # 放个气球庆祝一下
                st.success(f"已成功标记！你做了一件好事。")
            else:
                st.warning("号码和标签都得填哦。")

    # === 功能3：申诉 ===
    with tab3:
        st.write("如果是误伤，或者他已经改过自新（可能吗？），可以在此申诉。")
        appeal_phone = st.text_input("申诉号码")
        if st.button("提交申诉"):
            if appeal_phone:
                target_hash = hash_phone(appeal_phone)
                new_white = {
                    "hash": target_hash,
                    "reason": "用户自主申诉",
                    "time": datetime.datetime.now().strftime("%Y-%m-%d")
                }
                pd.DataFrame([new_white]).to_csv(WHITE_LIST_FILE, mode='a', header=False, index=False)
                st.success("申诉已受理，风险提示已屏蔽。")

else:
    st.title("🚫 访问受限")
    st.error("这是内部互助系统，需要密钥才能进入。")
    st.info("如果你也想加入【女性互助避雷联盟】，请私信管理员获取密钥。")
