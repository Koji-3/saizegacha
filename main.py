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
def load_menu_data():
    with open("data/menu.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        return data["menu_items"]

# カテゴリーの選択を切り替える関数
def toggle_category(category):
    if category in st.session_state.selected_categories:
        st.session_state.selected_categories.remove(category)
    else:
        st.session_state.selected_categories.add(category)
    st.rerun()

# 予算内のメニューをランダムに選択
def select_random_menu(budget, menu_items):
    # カテゴリーでフィルタリング
    if st.session_state.selected_categories:
        menu_items = [item for item in menu_items if item["category"] in st.session_state.selected_categories]

    available_items = [item for item in menu_items if item["price"] <= budget]
    if not available_items:
        return None

    selected_items = []
    remaining_budget = budget
    used_items = set()  # 選択済みの商品を記録

    while remaining_budget > 0:
        # まだ選択されていない商品のみをフィルタリング
        affordable_items = [
            item for item in available_items 
            if item["price"] <= remaining_budget and item["id"] not in used_items
        ]

        if not affordable_items:
            break

        item = random.choice(affordable_items)
        selected_items.append(item)
        used_items.add(item["id"])  # 選択した商品のIDを記録
        remaining_budget -= item["price"]

    return selected_items

# メインアプリケーション
def main():
    load_css()

    # ヘッダー
    st.markdown('<h1 class="main-header">サイゼリヤ メニュー推薦</h1>', unsafe_allow_html=True)

    # メニューデータの読み込み
    menu_items = load_menu_data()

    # 重複を除去（同じ名前のメニューは最新のものを保持）
    unique_menu_items = {}
    for item in menu_items:
        unique_menu_items[item["name"]] = item
    menu_items = list(unique_menu_items.values())

    # カテゴリー一覧の取得と初期化
    categories = sorted(set(item["category"] for item in menu_items))
    if 'selected_categories' not in st.session_state:
        st.session_state.selected_categories = set(categories)

    st.markdown("### カテゴリーで絞り込む")

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
                toggle_category(category)

    # 予算入力
    budget = st.number_input(
        "予算を入力してください（円）",
        min_value=0,
        max_value=10000,
        value=1000,
        step=100
    )

    # 推薦ボタン
    if st.button("メニュー を 推薦する"):
        if budget < 199:  # 最小価格のメニュー価格
            st.markdown(
                '<div class="error-message">予算が少なすぎます。最低199円以上を設定してください。</div>',
                unsafe_allow_html=True
            )
        else:
            with st.spinner("メニューを選択中..."):
                # カテゴリーでフィルタリング
                filtered_items = [item for item in menu_items if item["category"] in st.session_state.selected_categories]
                selected_items = select_random_menu(budget, filtered_items)

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
    filtered_items = menu_items
    if st.session_state.selected_categories:
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