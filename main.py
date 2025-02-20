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

# データ読み込みの最適化
@st.cache_data
def load_menu_data():
    with open("data/menu.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        menu_items = data["menu_items"]

    # 重複を除去（同じ名前のメニューは最新のものを保持）
    unique_menu_items = {}
    for item in menu_items:
        unique_menu_items[item["name"]] = item

    items = list(unique_menu_items.values())
    categories = sorted(set(item["category"] for item in items))
    return items, categories

# CSSの読み込み
@st.cache_data
def load_css():
    css_file = Path("styles/styles.css").read_text()
    return css_file

# カテゴリーの選択を切り替える関数
def toggle_category(category, current_categories):
    if category in current_categories:
        current_categories.remove(category)
    else:
        current_categories.add(category)
    return current_categories

# 予算内のメニューをランダムに選択
def select_random_menu(budget, menu_items, selected_categories):
    filtered_items = [item for item in menu_items if item["category"] in selected_categories]
    available_items = [item for item in filtered_items if item["price"] <= budget]

    if not available_items:
        return None

    selected_items = []
    remaining_budget = budget
    used_items = set()

    while remaining_budget > 0:
        affordable_items = [
            item for item in available_items 
            if item["price"] <= remaining_budget and item["id"] not in used_items
        ]

        if not affordable_items:
            break

        item = random.choice(affordable_items)
        selected_items.append(item)
        used_items.add(item["id"])
        remaining_budget -= item["price"]

    return selected_items

# メインアプリケーション
def main():
    # キャッシュされたデータの読み込み
    menu_items, categories = load_menu_data()

    # CSSの適用
    st.markdown(f"<style>{load_css()}</style>", unsafe_allow_html=True)

    # ヘッダー
    st.markdown('<h1 class="main-header">サイゼリヤ メニュー推薦</h1>', unsafe_allow_html=True)

    # カテゴリー選択の初期化
    if 'selected_categories' not in st.session_state:
        st.session_state.selected_categories = set(categories)

    st.markdown("###### カテゴリーで絞り込む")

    # カテゴリー選択のボタン
    cols = st.columns(len(categories))
    for idx, category in enumerate(categories):
        with cols[idx]:
            is_selected = category in st.session_state.selected_categories
            button_key = f"cat_{category}"
            if st.button(
                category,
                key=button_key,
                type="primary" if is_selected else "secondary",
                use_container_width=True
            ):
                st.session_state.selected_categories = toggle_category(
                    category, 
                    st.session_state.selected_categories
                )

    st.markdown("###### 予算を入力してください")

    # 予算入力
    budget = st.number_input(
        "テキスト",
        min_value=0,
        max_value=10000,
        value=1000,
        step=100,
        label_visibility="collapsed"
    )

    # 推薦ボタン
    if st.button("メニューを推薦する", type="primary"):
        if budget < 199:
            st.markdown(
                '<div class="error-message">予算が少なすぎます。最低199円以上を設定してください。</div>',
                unsafe_allow_html=True
            )
        else:
            with st.spinner("メニューを選択中..."):
                selected_items = select_random_menu(
                    budget, 
                    menu_items, 
                    st.session_state.selected_categories
                )

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

    # カテゴリーでフィルタリングされたメニューを表示
    filtered_items = [item for item in menu_items if item["category"] in st.session_state.selected_categories]

    menu_df = pd.DataFrame([{
        "name": item["name"],
        "price": item["price"],
        "category": item["category"],
        "description": item["description"]
    } for item in filtered_items])

    st.dataframe(
        menu_df.rename(columns={
            "name": "メニュー名",
            "price": "価格",
            "category": "カテゴリー",
            "description": "説明"
        }),
        hide_index=True
    )

if __name__ == "__main__":
    main()