from typing import Dict, List, Optional, Tuple
from menu import MenuItem
# 新增limit參數，限制推薦品項數量
def get_recommendations(preferences: dict, menu_db: Dict[str, MenuItem], limit: Optional[int] = 5, mode: str = "general",) -> List[MenuItem]:
    """
    根據使用者的偏好設定與菜單資料庫，篩選並推薦合適的餐點。
    
    :param preferences: 包含 max_budget (int), taste_like (List[str]), taste_dislike (List[str])
    :param menu_db: 字典格式 {item_id: MenuItem}
    :return: 推薦的 MenuItem 列表

    推薦模式：
    - general：全菜單統一排序，最多回傳 limit 個品項。
    - guided：依 category 分組，每個分類最多回傳 limit 個品項。

    limit:
        general 模式：全菜單推薦數量上限。
        guided 模式：每個分類的推薦數量上限。
        None：不限制推薦數量。
        0：不推薦任何品項。

    mode: "general"(預設) 或 "guided"。
    """
    if mode not in ("general", "guided"):
        raise ValueError(
            "mode 必須是 'general' 或 'guided'"
        )

    if limit is not None and (
        not isinstance(limit, int)
        or isinstance(limit, bool)
        or limit < 0
    ):
        raise ValueError("limit 必須是非負整數或 None")

    max_budget = preferences.get("max_budget", float('inf'))
    taste_like = preferences.get("taste_like", [])
    taste_dislike = preferences.get("taste_dislike", [])

    # UI 應提示使用者調整；此處依排除條件優先處理。
    candidates: List[Tuple[int, MenuItem]] = []
    
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
    
    # 5. 一般推薦：全菜單合計最多 limit 個品項。
    if mode == "general":
        if limit is None:
            return [item for _, item in candidates]

        return [
            item
            for _, item in candidates[:limit]
        ]

    # 6. 套餐引導：依實際 category 分組。
    # 不假設菜單只有主餐、附餐、飲料或甜點。
    grouped_candidates: Dict[str, List[MenuItem]] = {}

    for _, item in candidates:
        category = item.category or "其他"

        if category not in grouped_candidates:
            grouped_candidates[category] = []

        grouped_candidates[category].append(item)

    # 7. 每個分類分別限制數量。
    recommended_items: List[MenuItem] = []

    for category_items in grouped_candidates.values():
        if limit is None:
            recommended_items.extend(category_items)
        else:
            recommended_items.extend(category_items[:limit])

    return recommended_items