// メニューデータとカテゴリの状態を保持する変数
let menuItems = [];
let categories = [];
let selectedCategories = new Set();
const categoryOrder = ["サラダ", "スープ", "パン", "サイドメニュー", "ピザ", "ドリア", "パスタ", "肉メイン", "ライス", "デザート", "お酒", "トッピング"];

// ページ読み込み時の初期処理
document.addEventListener('DOMContentLoaded', async () => {
    await loadMenuData();
    setupEventListeners();
    renderCategoryButtons();
    renderMenuTable();
});

// メニューデータの読み込み
async function loadMenuData() {
    try {
        const response = await fetch('data/menu.json');
        const data = await response.json();
        
        // 重複を除去（同じ名前のメニューは最新のものを保持）
        const uniqueMenuItems = {};
        data.menu_items.forEach(item => {
            uniqueMenuItems[item.name] = item;
        });
        
        menuItems = Object.values(uniqueMenuItems);
        
        // カテゴリのセット作成
        const categorySet = new Set(menuItems.map(item => item.category));
        
        // カテゴリを定義順に並び替え
        categories = categoryOrder.filter(cat => categorySet.has(cat));
        
        // 初期状態では全カテゴリを選択
        selectedCategories = new Set(categories);
    } catch (error) {
        console.error('メニューデータの読み込み中にエラーが発生しました:', error);
    }
}

// イベントリスナーの設定
function setupEventListeners() {
    // ガチャボタンのイベントリスナー
    document.getElementById('gacha-button').addEventListener('click', () => {
        const budget = parseInt(document.getElementById('budget').value);
        runGacha(budget);
    });
}

// カテゴリーボタンの描画
function renderCategoryButtons() {
    const container = document.getElementById('category-buttons');
    container.innerHTML = '';
    
    categories.forEach(category => {
        const button = document.createElement('button');
        button.textContent = category;
        button.className = 'category-button';
        if (selectedCategories.has(category)) {
            button.classList.add('selected');
        }
        
        button.addEventListener('click', () => {
            toggleCategory(category);
        });
        
        container.appendChild(button);
    });
}

// カテゴリーの選択を切り替える
function toggleCategory(category) {
    if (selectedCategories.has(category)) {
        selectedCategories.delete(category);
    } else {
        selectedCategories.add(category);
    }
    
    renderCategoryButtons();
    renderMenuTable();
}

// メニューテーブルの描画
function renderMenuTable() {
    const tbody = document.querySelector('#menu-table tbody');
    tbody.innerHTML = '';
    
    // 選択されたカテゴリーに属するメニューのみをフィルタリング
    const filteredItems = menuItems.filter(item => selectedCategories.has(item.category));
    
    filteredItems.forEach(item => {
        const tr = document.createElement('tr');
        
        const idTd = document.createElement('td');
        idTd.textContent = item.id;
        tr.appendChild(idTd);
        
        const nameTd = document.createElement('td');
        nameTd.textContent = item.name;
        tr.appendChild(nameTd);
        
        const priceTd = document.createElement('td');
        priceTd.textContent = `${item.price}円`;
        tr.appendChild(priceTd);
        
        const categoryTd = document.createElement('td');
        categoryTd.textContent = item.category;
        tr.appendChild(categoryTd);
        
        const descTd = document.createElement('td');
        descTd.textContent = item.description || '';
        tr.appendChild(descTd);
        
        tbody.appendChild(tr);
    });
}

// ガチャを実行
function runGacha(budget) {
    // エラーメッセージと結果コンテナの表示状態をリセット
    document.getElementById('error-message').style.display = 'none';
    document.getElementById('result-container').style.display = 'none';
    document.getElementById('selected-menu-container').innerHTML = '';
    
    // 予算チェック
    if (budget < 199) {
        document.getElementById('error-message').style.display = 'block';
        return;
    }
    
    // ローディングスピナーを表示
    document.getElementById('loading-spinner').style.display = 'flex';
    
    // 非同期処理を模倣（実際の処理は即時実行可能）
    setTimeout(() => {
        const selectedItems = selectRandomMenu(budget);
        document.getElementById('loading-spinner').style.display = 'none';
        
        if (selectedItems && selectedItems.length > 0) {
            const totalPrice = selectedItems.reduce((sum, item) => sum + item.price, 0);
            
            // 結果メッセージの表示
            document.getElementById('result-message').textContent = `予算: ${budget}円 中 ${totalPrice}円のメニューを提案します！`;
            document.getElementById('result-container').style.display = 'block';
            
            // 選択されたメニューの表示
            const menuContainer = document.getElementById('selected-menu-container');
            selectedItems.forEach(item => {
                const menuCard = document.createElement('div');
                menuCard.className = 'menu-card';
                
                const menuTitle = document.createElement('div');
                menuTitle.className = 'menu-title';
                menuTitle.textContent = item.name;
                menuCard.appendChild(menuTitle);
                
                const menuPrice = document.createElement('div');
                menuPrice.className = 'menu-price';
                menuPrice.textContent = `${item.price}円`;
                menuCard.appendChild(menuPrice);
                
                const menuDesc = document.createElement('div');
                menuDesc.className = 'menu-description';
                menuDesc.textContent = item.description || '';
                menuCard.appendChild(menuDesc);
                
                menuContainer.appendChild(menuCard);
            });
        } else {
            // メニューが見つからない場合のエラーメッセージ
            document.getElementById('result-message').innerHTML = 
                '<span style="color: #E60012;">指定された予算内でメニューを見つけることができませんでした。</span>';
            document.getElementById('result-container').style.display = 'block';
        }
    }, 500); // 処理時間を模倣するための遅延
}

// 予算内のメニューをランダムに選択
function selectRandomMenu(budget) {
    // 選択されたカテゴリーに属するメニューのみをフィルタリング
    const filteredItems = menuItems.filter(item => selectedCategories.has(item.category));
    
    // 予算内で購入可能なメニューをフィルタリング
    const availableItems = filteredItems.filter(item => item.price <= budget);
    
    if (availableItems.length === 0) {
        return null;
    }
    
    const selectedItems = [];
    let remainingBudget = budget;
    const usedItems = new Set();
    
    // 予算内でできるだけ多くのメニューを選択
    while (remainingBudget > 0) {
        // 残り予算内で購入可能なメニューをフィルタリング（既に選択したメニューは除外）
        const affordableItems = availableItems.filter(
            item => item.price <= remainingBudget && !usedItems.has(item.id)
        );
        
        if (affordableItems.length === 0) {
            break;
        }
        
        // ランダムに1つ選択
        const randomIndex = Math.floor(Math.random() * affordableItems.length);
        const selectedItem = affordableItems[randomIndex];
        
        selectedItems.push(selectedItem);
        usedItems.add(selectedItem.id);
        remainingBudget -= selectedItem.price;
    }
    
    return selectedItems;
}