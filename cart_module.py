from typing import List, Dict, Any

try:
    from models import MenuItem
except ImportError:
    from menu import MenuItem


def add_item(cart: List[dict], item_obj: MenuItem, qty: int) -> List[dict]:
    """
    將餐點加入購物車。

    購物車每筆資料格式：
    {
        "item_id": str,
        "item": MenuItem,
        "qty": int,
        "subtotal": int
    }

    如果購物車已經有相同品項，會直接增加數量。
    """
    if qty <= 0:
        raise ValueError("qty 必須大於 0")

    new_cart = list(cart)

    for cart_item in new_cart:
        if cart_item["item_id"] == item_obj.item_id:
            cart_item["qty"] += qty
            cart_item["subtotal"] = cart_item["qty"] * item_obj.price
            return new_cart

    new_cart.append({
        "item_id": item_obj.item_id,
        "item": item_obj,
        "qty": qty,
        "subtotal": item_obj.price * qty,
    })

    return new_cart


def remove_item(cart: List[dict], item_id: str) -> List[dict]:
    """
    從購物車移除指定品項。

    找不到指定 item_id 時，原購物車內容不變。
    """
    return [
        cart_item
        for cart_item in cart
        if cart_item["item_id"] != item_id
    ]


def calculate_subtotal(cart: List[dict]) -> int:
    """
    計算購物車目前的小計。

    會依 MenuItem.price × qty 重新計算，
    避免購物車中的 subtotal 資料過期。
    """
    subtotal = 0

    for cart_item in cart:
        item = cart_item["item"]
        qty = cart_item["qty"]

        if qty < 0:
            raise ValueError("購物車中的 qty 不可小於 0")

        subtotal += item.price * qty

    return subtotal


def generate_receipt(
    cart: List[dict],
    final_total: int,
    discount: dict
) -> Dict[str, Any]:
    """
    產生結構化結帳明細資料字典，供上層解析或前端渲染使用。

    discount 預期格式：
    {
        "is_valid": bool,
        "discount_value": int,
        "new_total": int,
        "message": str
    }

    回傳字典格式：
    {
        "items": List[dict],     # 各品項明細列表
        "subtotal": int,         # 商品小計
        "discount_value": int,   # 折扣金額
        "discount_message": str, # 折扣說明
        "final_total": int,      # 應付金額
        "receipt_text": str      # 排版好的文字版明細
    }
    """
    subtotal = calculate_subtotal(cart)
    
    items_detail = []
    for cart_item in cart:
        item = cart_item["item"]
        qty = cart_item["qty"]
        item_total = item.price * qty
        items_detail.append({
            "item_id": item.item_id,
            "name": item.name,
            "price": item.price,
            "qty": qty,
            "subtotal": item_total
        })

    discount_value = 0
    discount_message = ""
    if discount:
        discount_value = discount.get("discount_value", 0)
        discount_message = discount.get("message", "")

    # 建立文字版明細 (receipt_text)
    lines = []
    lines.append("=" * 32)
    lines.append("           點餐明細")
    lines.append("=" * 32)

    if not cart:
        lines.append("購物車是空的")
        lines.append("-" * 32)
        lines.append(f"應付金額：${final_total}")
        lines.append("=" * 32)
        receipt_text = "\n".join(lines)
        return {
            "items": [],
            "subtotal": 0,
            "discount_value": 0,
            "discount_message": "",
            "final_total": final_total,
            "receipt_text": receipt_text
        }

    for item_detail in items_detail:
        lines.append(
            f"{item_detail['name']} x {item_detail['qty']}  ${item_detail['subtotal']}"
        )

    lines.append("-" * 32)
    lines.append(f"商品小計：${subtotal}")

    if discount_value > 0:
        lines.append(f"優惠折扣：-${discount_value}")

    if discount_message:
        lines.append(f"優惠資訊：{discount_message}")

    lines.append(f"應付金額：${final_total}")
    lines.append("=" * 32)
    
    receipt_text = "\n".join(lines)

    return {
        "items": items_detail,
        "subtotal": subtotal,
        "discount_value": discount_value,
        "discount_message": discount_message,
        "final_total": final_total,
        "receipt_text": receipt_text
    }


if __name__ == "__main__":
    from menu import Menu

    menu = Menu()
    cart = []

    item1 = menu.get_by_id("M001")
    item2 = menu.get_by_id("S001")

    if item1 and item2:
        cart = add_item(cart, item1, 2)
        cart = add_item(cart, item2, 1)
        cart = add_item(cart, item1, 1)

        print("購物車小計：", calculate_subtotal(cart))

        discount = {
            "is_valid": True,
            "discount_value": 20,
            "new_total": calculate_subtotal(cart) - 20,
            "message": "滿額折 $20",
        }

        receipt_data = generate_receipt(
            cart,
            discount["new_total"],
            discount
        )

        # 測試列印文字版明細
        print(receipt_data["receipt_text"])
        
        # 測試上層存取結構化資料
        print("結構化品項數量：", len(receipt_data["items"]))
        print("最終應付金額：", receipt_data["final_total"])
