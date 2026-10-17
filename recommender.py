from typing import Dict, List
from menu import MenuItem
def get_recommendations(preferences: dict, menu_db: Dict[str, MenuItem]) -> List[MenuItem]:
    """
    根據使用者的偏好設定與菜單資料庫，篩選並推薦合適的餐點。
    
    :param preferences: 包含 max_budget (int), taste_like (List[str]), taste_dislike (List[str])
    :param menu_db: 字典格式 {item_id: MenuItem}
    :return: 推薦的 MenuItem 列表
    """
    max_budget = preferences.get("max_budget", float('inf'))
    taste_like = preferences.get("taste_like", [])
    taste_dislike = preferences.get("taste_dislike", [])
    
    candidates = []
    
    for item_id, item in menu_db.items():
        # 1. 預算過濾（硬條件）
        if item.price > max_budget:
            continue
            
        # 2. 地雷標籤排除（硬條件：只要踩到任何一個討厭的標籤就跳過）
        has_dislike = any(dislike in item.taste_tags for dislike in taste_dislike)
        if has_dislike:
            continue
            
        # 3. 計算喜好標籤得分（軟條件：中了幾個喜歡的標籤）
        score = sum(1 for tag in item.taste_tags if tag in taste_like)
        
        # 放入候選名單 (分數, 品項物件)
        candidates.append((score, item))
        
    # 4. 排序：依符合的喜好分數由高到低排序
    candidates.sort(key=lambda x: x[0], reverse=True)
    
    # 5. 限制數量 : 寫死最多推薦 5 個品項
    MAX_RECOMMENDATIONS = 5
    recommended_items = [item for score, item in candidates[:MAX_RECOMMENDATIONS]]
    
    return recommended_items