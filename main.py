from menu import Menu
from cart_module import add_item, calculate_subtotal, generate_receipt
from ui import run_ui

def main():
    # 1. 初始化菜單物件
    menu_manager = Menu()
    
    # 2. 取得所有菜單品項
    menu_items = menu_manager.get_all_items()

    # 3. 啟動 Streamlit 介面
    run_ui(menu_items)

if __name__ == "__main__":
    main()