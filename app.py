import os
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

load_dotenv() 

if "OPENAI_API_KEY" not in os.environ and "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# --- LLM初期化　---
def _init_llm():
    try:
        return ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    except TypeError:
        return ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

LLM = _init_llm()

# --- 専門家の振る舞い ---
EXPERT_SYSTEM_PROMPTS = {
    "キャリアコーチ（IT転職）": (
        "あなたは思考の言語化が得意なプロのキャリアコーチです。"
        "受講者の不安や前提を丁寧にほどき、選択肢とトレードオフを並べ、"
        "短いアクションプランを提示してください。断定しすぎず、根拠も添えること。"
    ),
    "面接官（採用人事・辛口）」": (
        "あなたはIT業界の採用担当者です。応募者の強み・弱み・懸念点を実務目線で指摘し、"
        "評価基準の観点（スキル適合・再現性・協働・学習性）で具体的にコメントし、"
        "改善提案を端的に示してください。オブラートは不要、ただし建設的に。"
    ),
}

# --- LLM呼び出し関数 ---
def ask_llm(user_text: str, expert_key: str) -> str:
    """選択された専門家ペルソナに合わせてシステムプロンプトを切替え、LLMの回答を返す。"""
    system_prompt = EXPERT_SYSTEM_PROMPTS.get(expert_key, "You are a helpful assistant.")
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_text),
    ]
    result = LLM(messages)
    return result.content

# --- Streamlit UI ---
st.set_page_config(page_title="転職支援アプリ\n\n（Streamlit × LangChain）", page_icon="🧪", layout="centered")

st.title("転職支援アプリ\n\n（Streamlit × LangChain）")

st.markdown("### 概要")
st.write(
    "転職に詳しい専門家を選んで回答を得るミニアプリ\n\n"
    "使い方\n\n"
    "① 専門家を選ぶ  ② 相談内容を入力  ③ 送信\n\n"
    "※ローカル実行は .env に OPENAI_API_KEY を保存。Cloudは Secrets に設定。\n\n"
)

expert = st.radio(
    "専門家の種類（振る舞い）を選択：",
    list(EXPERT_SYSTEM_PROMPTS.keys()),
    horizontal=True,
)

user_text = st.text_area(
    "相談内容 / 質問を入力（例：職務経歴を要約して、自己PRを作りたい）",
    height=150,
    placeholder="ここにテキストを入力…",
)

col1, col2 = st.columns([1, 3])
with col1:
    submitted = st.button("送信", type="primary")

# 送信時の処理
if submitted:
    if not os.environ.get("OPENAI_API_KEY"):
        st.error("OpenAI APIキーが見つかりません。.env または Streamlit Secrets に OPENAI_API_KEY を設定してください。")
    elif not user_text.strip():
        st.error("入力テキストを入れてください。")
    else:
        with st.spinner("LLMが考え中…"):
            try:
                answer = ask_llm(user_text.strip(), expert)
                st.success("回答")
                st.write(answer)
            except Exception as e:
                st.error(f"エラーが発生しました：{e}")

st.divider()
st.markdown(
    "#### 注意\n"
    "- APIキーは**絶対にGitHubへコミットしない**（.envは.gitignore対象）。\n"
    "- 本番（Streamlit Community Cloud）では **Secrets** に `OPENAI_API_KEY` を設定。\n"
    "- このアプリは学習用途。重要判断は自己責任で。"
)