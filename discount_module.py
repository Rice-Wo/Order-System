from typing import List

def get_cart_totals(cart: List[dict]) -> tuple:
    """輔助函數：計算總價與可套用折扣的總價（排除特價品）"""
    total = 0
    eligible_total = 0
    
    for item in cart:
        price = item.get("price", 0)
        quantity = item.get("quantity", 1)
        
        # 假設：指定 M003 為特價品：萬聖節限定
        is_special = item.get("is_special", False)
        if item.get("item_id") == "M003":
            is_special = True
            
        row_total = price * quantity
        total += row_total
        
        # 特價品不列入折扣碼可折抵的範圍
        if not is_special:
            eligible_total += row_total
            
    return total, eligible_total

def apply_coupon(cart: List[dict], code: str) -> dict:
    """計算折扣碼優惠"""
    total, eligible_total = get_cart_totals(cart)
    
    # 優惠碼
    valid_coupons = {
        "1111": {"type": "minus", "value": 111, "min_spend": 300},  # 滿 300 折 111 元
        "8888": {"type": "percent", "value": 0.88, "min_spend": 500} # 滿 500 打 88 折
    }
    
    if not code or code not in valid_coupons:
        return {
            "is_valid": False, 
            "discount_value": 0, 
            "new_total": total, 
            "message": "無效的優惠碼"
        }
        
    coupon = valid_coupons[code]
    
    # 檢查低消
    if eligible_total < coupon["min_spend"]:
        return {
            "is_valid": False, 
            "discount_value": 0, 
            "new_total": total, 
            "message": f"未達最低消費門檻 {coupon['min_spend']} 元 (特價品不計入)"
        }
        
    discount_value = 0
    if coupon["type"] == "minus":
        # 折抵固定金額
        discount_value = min(coupon["value"], eligible_total) 
    elif coupon["type"] == "percent":
        # 打折 
        discount_value = int(eligible_total * (1 - coupon["value"]))
        
    new_total = max(0, total - discount_value)
    
    return {
        "is_valid": True,
        "discount_value": discount_value,
        "new_total": new_total,
        "message": f"成功套用優惠碼，折抵 {discount_value} 元"
    }


def auto_detect_combo(cart: List[dict]) -> dict:
    """偵測套餐優惠 (1主食 + 1飲料 + 1附餐 + 1甜點 = 折15元)"""
    total, _ = get_cart_totals(cart)
    
    main_categories = ["主餐", "米漢堡", "台式餐點"]
    
    main_count = 0
    drink_count = 0
    side_count = 0
    dessert_count = 0
    
    for item in cart:
        category = item.get("category", "")
        quantity = item.get("quantity", 1)
        
        if category in main_categories:
            main_count += quantity
        elif category == "飲料":
            drink_count += quantity
        elif category == "附餐":
            side_count += quantity
        elif category == "甜點":
            dessert_count += quantity
            
    combo_sets = min(main_count, drink_count, side_count, dessert_count)
    
    if combo_sets > 0:
        combo_discount_per_set = 15  
        discount_value = combo_sets * combo_discount_per_set
        new_total = max(0, total - discount_value)
        
        return {
            "is_valid": True,
            "discount_value": discount_value,
            "new_total": new_total,
            "message": f"已自動組合 {combo_sets} 份完整套餐 (主+飲+附+甜)，折抵 {discount_value} 元"
        }
        
    return {
        "is_valid": False,
        "discount_value": 0,
        "new_total": total,
        "message": "未符合套餐條件 (需同時包含主食、飲料、附餐與甜點)"
    }


def get_best_discount(cart: List[dict], code: str = "") -> dict:
    """比較並取得最佳優惠 (一次只能使用一個優惠，取折抵較多者，舉例：套餐折抵15<888優惠碼折扣)"""
    combo_result = auto_detect_combo(cart)
    coupon_result = apply_coupon(cart, code) if code else None
    
    if not coupon_result or not coupon_result["is_valid"]:
        return combo_result
        
    if combo_result["is_valid"] and combo_result["discount_value"] >= coupon_result["discount_value"]:
        return combo_result
    else:
        return coupon_result
