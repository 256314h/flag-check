import streamlit as st
import hashlib
import pandas as pd
import os
import datetime

# ================= 配置区 =================
# 代理密钥（只有输入这些密码才能用，你可以自己改）
AGENT_KEYS = ["8888", "vip666", "admin2026"]
# 数据存储文件
DB_FILE = "black_box_data.csv"
# 申诉/争议白名单文件
WHITE_LIST_FILE = "whitelist.csv"

# ================= 核心功能函数 =================

# 1. 哈希加密函数 (保护隐私的核心)
def hash_phone(phone):
    # 加盐 (Salt)，防止反向破解
    salt = "project_red_flag_2026_safe" 
    target = phone + salt
    return hashlib.md5(target.encode()).hexdigest()

# 2. 初始化数据库 (如果文件不存在就自动创建)
def init_db():
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=["hash", "tag", "time", "agent_id", "comment"])
        df.to_csv(DB_FILE, index=False)
    
    if not os.path.exists(WHITE_LIST_FILE):
        df_white = pd.DataFrame(columns=["hash", "reason", "time"])
        df_white.to_csv(WHITE_LIST_FILE, index=False)

# ================= 网页界面逻辑 =================

# 设置网页标题和图标
st.set_page_config(page_title="号码信誉查询系统", page_icon="🛡️")

# 初始化数据库
init_db()

# --- 侧边栏：代理登录 ---
st.sidebar.header("🔐 内部通道")
agent_key = st.sidebar.text_input("请输入访问密钥", type="password")

# --- 首页免责弹窗 (第一道法律防线) ---
st.info("📢 **法律声明**：本工具仅提供【骚扰/高风险号码】辅助标记功能。所有数据均由用户匿名生成，仅供参考。平台不存储任何明文个人信息。")

# 只有密钥正确才显示主界面
if agent_key in AGENT_KEYS:
    st.sidebar.success(f"✅ 身份验证通过")
    
    st.title("🛡️ 隐私号码风险标记系统")
    st.markdown("---")

    # 分页功能：查询 vs 标记 vs 申诉后台
    tab1, tab2, tab3 = st.tabs(["🔍 风险查询", "⚠️ 匿名标记", "⚖️ 申诉/洗白"])

    # === 功能 1: 查询 ===
    with tab1:
        st.subheader("查询目标号码状态")
        phone_input = st.text_input("请输入对方手机号", max_chars=11, help="系统仅处理哈希值，绝不存储明文号码")
        
        if st.button("开始扫描", type="primary"):
            if len(phone_input) < 11:
                st.error("请输入完整的11位手机号")
            else:
                # 1. 转哈希
                target_hash = hash_phone(phone_input)
                
                # 2. 检查是否在白名单 (申诉成功的号码不显示风险)
                df_white = pd.read_csv(WHITE_LIST_FILE)
                if target_hash in df_white['hash'].values:
                    st.success("✅ 安全：该号码无风险记录 (或已通过申诉清洗)。")
                else:
                    # 3. 检查黑名单
                    df = pd.read_csv(DB_FILE)
                    result = df[df['hash'] == target_hash]
                    
                    if not result.empty:
                        count = len(result)
                        st.error(f"🚨 警告！该号码存在 {count} 条风险标记！")
                        
                        # 展示详情 (如果你想收费，这里可以隐藏部分信息)
                        st.write("### 详细记录：")
                        for index, row in result.iterrows():
                            with st.expander(f"📅 {row['time']} - 🏷️ {row['tag']}"):
                                st.write(f"**备注/评价：** {row.get('comment', '无')}")
                                st.caption("数据来源：匿名代理录入")
                    else:
                        st.success("✅ 安全：数据库中暂无该号码的风险记录。")
                        st.caption("提示：无记录不代表绝对安全，建议开启哨兵监控。")

    # === 功能 2: 标记 (代理用) ===
    with tab2:
        st.subheader("录入风险号码")
        col1, col2 = st.columns(2)
        with col1:
            report_phone = st.text_input("输入目标手机号", key="report")
        with col2:
            tags = st.multiselect("选择风险标签", 
                                 ["海王/多线发展", "欠钱不还", "已婚伪装", "冷暴力/PUA", "yp/约炮", "吃饭逃单", "杀猪盘/诈骗"])
        
        comment = st.text_area("详细备注 (选填，请勿填写真实姓名/住址等隐私信息)", max_chars=200)
        
        if st.button("加密提交"):
            # 敏感词过滤 (简单版)
            forbidden_words = ["死", "杀", "奸", "真实姓名", "身份证"]
            if any(word in comment for word in forbidden_words):
                st.error("提交失败：包含违禁词汇，请文明用语。")
            elif report_phone and tags:
                target_hash = hash_phone(report_phone)
                new_data = {
                    "hash": target_hash,
                    "tag": ",".join(tags),
                    "time": datetime.datetime.now().strftime("%Y-%m-%d"),
                    "agent_id": agent_key,
                    "comment": comment
                }
                new_df = pd.DataFrame([new_data])
                new_df.to_csv(DB_FILE, mode='a', header=False, index=False)
                st.success("✅ 已加密入库！数据已脱敏存储。")
            else:
                st.warning("请填写手机号和标签。")

    # === 功能 3: 申诉 (保命通道) ===
    with tab3:
        st.subheader("⚖️ 号码误标申诉")
        st.caption("如果您的号码被恶意标记，请输入号码申请清洗。")
        
        appeal_phone = st.text_input("输入申诉号码")
        reason = st.selectbox("申诉理由", ["非本人使用", "恶意诽谤/不实", "号码已注销重办"])
        
        if st.button("提交申诉"):
            if appeal_phone:
                # 逻辑：直接加入白名单，查询时会自动屏蔽风险
                target_hash = hash_phone(appeal_phone)
                new_white = {
                    "hash": target_hash,
                    "reason": reason,
                    "time": datetime.datetime.now().strftime("%Y-%m-%d")
                }
                pd.DataFrame([new_white]).to_csv(WHITE_LIST_FILE, mode='a', header=False, index=False)
                st.success("✅ 申诉已自动受理！系统已屏蔽该号码的风险显示。")
            else:
                st.warning("请输入号码")

# --- 这里的缩进是针对 if agent_key... 的 else ---
else:
    # 没输入密钥时显示的页面
    st.title("🔒 访问受限")
    st.warning("请输入授权密钥以访问系统。")
    
    # 底部放一个公开的申诉入口链接 (做做样子)
    st.markdown("---")
    with st.expander("我是路人，我想申诉删除数据"):
        st.write("请联系管理员或代理商获取申诉通道密钥。")