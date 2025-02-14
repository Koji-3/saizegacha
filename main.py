import streamlit as st
import json
import random
import pandas as pd
from pathlib import Path
from database import init_db, get_db, MenuItem, get_all_menu_items, add_menu_item

# データベース初期化
init_db()

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

# 初回のみメニューデータをデータベースに登録
def load_initial_data():
    if "initial_load" not in st.session_state:
        db = next(get_db())
        # 既存のメニューデータを確認
        existing_items = get_all_menu_items(db)
        if not existing_items:
            # JSONからデータを読み込んでデータベースに登録
            with open("data/menu.json", "r", encoding="utf-8") as f:
                menu_data = json.load(f)
                for item in menu_data["menu_items"]:
                    add_menu_item(db, item)
        st.session_state.initial_load = True

# カテゴリーの選択を切り替える関数
def toggle_category(category):
    if category in st.session_state.selected_categories:
        st.session_state.selected_categories.remove(category)
    else:
        st.session_state.selected_categories.add(category)
    # 即座に状態を反映するために再描画
    st.rerun()

# 予算内のメニューをランダムに選択
def select_random_menu(budget, menu_items):
    # カテゴリーでフィルタリング
    if st.session_state.selected_categories:
        menu_items = [item for item in menu_items if item.category in st.session_state.selected_categories]

    available_items = [item for item in menu_items if item.price <= budget]
    if not available_items:
        return None

    selected_items = []
    remaining_budget = budget

    while remaining_budget > 0:
        affordable_items = [item for item in available_items if item.price <= remaining_budget]
        if not affordable_items:
            break

        item = random.choice(affordable_items)
        selected_items.append(item)
        remaining_budget -= item.price

    return selected_items

# メインアプリケーション
def main():
    load_css()
    load_initial_data()

    # ヘッダー
    st.markdown('<h1 class="main-header">サイゼリヤ メニュー推薦</h1>', unsafe_allow_html=True)

    # メニューデータの読み込み
    db = next(get_db())
    menu_items = get_all_menu_items(db)

    # カテゴリー一覧の取得と初期化
    categories = sorted(set(item.category for item in menu_items))
    if 'selected_categories' not in st.session_state:
        # デフォルトですべてのカテゴリーを選択状態に
        st.session_state.selected_categories = set(categories)

    st.markdown("### カテゴリーで絞り込む")

    # カテゴリー選択のボタン
    cols = st.columns(len(categories))
    for idx, category in enumerate(categories):
        with cols[idx]:
            is_selected = category in st.session_state.selected_categories
            button_label = f"{category}"
            if st.button(
                button_label,
                key=f"cat_{category}",
                type="primary" if is_selected else "secondary",
                use_container_width=True,
                disabled=not is_selected
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
                    total_price = sum(item.price for item in selected_items)

                    st.success(f"予算: {budget}円 中 {total_price}円のメニューを提案します！")

                    # 選択されたメニューの表示
                    for item in selected_items:
                        st.markdown(
                            f'''
                            <div class="menu-card">
                                <div class="menu-title">{item.name}</div>
                                <div class="menu-price">{item.price}円</div>
                                <div class="menu-description">{item.description}</div>
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
        filtered_items = [item for item in menu_items if item.category in st.session_state.selected_categories]

    menu_df = pd.DataFrame([{
        "name": item.name,
        "price": item.price,
        "category": item.category,
        "description": item.description
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