from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# データベース接続設定
DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)  # 名前をユニークに設定
    price = Column(Integer, nullable=False)
    category = Column(String, nullable=False)
    description = Column(String)

# データベース初期化
def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# データベース操作関数
def get_all_menu_items(db):
    return db.query(MenuItem).all()

def add_menu_item(db, item_data):
    # 同じ名前のメニューが存在するかチェック
    existing_item = db.query(MenuItem).filter(MenuItem.name == item_data['name']).first()
    if existing_item:
        return None  # 重複する場合はスキップ

    # 新しいメニューアイテムを作成
    menu_data = {
        'name': item_data['name'],
        'price': item_data['price'],
        'category': item_data['category'],
        'description': item_data['description']
    }
    menu_item = MenuItem(**menu_data)
    db.add(menu_item)
    try:
        db.commit()
        db.refresh(menu_item)
        return menu_item
    except Exception as e:
        db.rollback()
        raise e