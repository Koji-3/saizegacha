import streamlit as st
import json
import random
import pandas as pd
from pathlib import Path

# ページの設定
st.set_page_config(
    page_title="サイゼリヤ メニュー推薦",
    page_icon="🍝",
    layout="wide"
)

# CSSの読み込み
def load_css():
    css_file = Path("styles/styles.css").read_text()
    st.markdown(f"<style>{css_file}</style>", unsafe_allow_html=True)

# メニューデータの読み込み
@st.cache_data
def load_menu_data():
    with open("data/menu.json", "r", encoding="utf-8") as f:
        return json.load(f)["menu_items"]

# 予算内のメニューをランダムに選択
def select_random_menu(budget, menu_items):
    available_items = [item for item in menu_items if item["price"] <= budget]
    if not available_items:
        return None
    
    selected_items = []
    remaining_budget = budget
    
    while remaining_budget > 0:
        affordable_items = [item for item in available_items if item["price"] <= remaining_budget]
        if not affordable_items:
            break
        
        item = random.choice(affordable_items)
        selected_items.append(item)
        remaining_budget -= item["price"]
    
    return selected_items

# メインアプリケーション
def main():
    load_css()
    
    # ヘッダー
    st.markdown('<h1 class="main-header">サイゼリヤ メニュー推薦</h1>', unsafe_allow_html=True)
    
    # メニューデータの読み込み
    menu_items = load_menu_data()
    
    # 予算入力
    st.markdown('<div class="budget-input">', unsafe_allow_html=True)
    budget = st.number_input(
        "予算を入力してください（円）",
        min_value=0,
        max_value=10000,
        value=1000,
        step=100
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 推薦ボタン
    if st.button("メニューを推薦する"):
        if budget < 199:  # 最小価格のメニュー価格
            st.markdown(
                '<div class="error-message">予算が少なすぎます。最低199円以上を設定してください。</div>',
                unsafe_allow_html=True
            )
        else:
            with st.spinner("メニューを選択中..."):
                selected_items = select_random_menu(budget, menu_items)
                
                if selected_items:
                    total_price = sum(item["price"] for item in selected_items)
                    
                    st.success(f"予算: {budget}円 中 {total_price}円のメニューを提案します！")
                    
                    # 選択されたメニューの表示
                    for item in selected_items:
                        st.markdown(
                            f'''
                            <div class="menu-card">
                                <div class="menu-title">{item["name"]}</div>
                                <div class="menu-price">{item["price"]}円</div>
                                <div class="menu-description">{item["description"]}</div>
                            </div>
                            ''',
                            unsafe_allow_html=True
                        )
                else:
                    st.error("指定された予算内でメニューを見つけることができませんでした。")
    
    # メニュー一覧の表示
    st.markdown("### 全メニュー一覧")
    df = pd.DataFrame(menu_items)
    st.dataframe(
        df[["name", "price", "category", "description"]].rename(columns={
            "name": "メニュー名",
            "price": "価格",
            "category": "カテゴリー",
            "description": "説明"
        }),
        hide_index=True
    )

if __name__ == "__main__":
    main()
