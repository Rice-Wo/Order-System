# 📘 系統技術規格與 API 文件（Technical Specification）

本文件詳細記載智慧點餐系統（Order System）的核心模組 API、資料結構、轉換機制與詳細系統流程，供開發維護與架構審查參考。

---

## 🧩 核心模組與 API 規格

### 1. 菜單管理模組 (`menu.py`)

讀取 CSV 菜單資料，將餐點轉換為 `MenuItem` 物件，並提供菜單查詢功能。

#### MenuItem 資料結構

使用 Python `@dataclass` 定義：

| 屬性         | 型別        | 說明           |
|--------------|-------------|----------------|
| `item_id`    | `str`       | 餐點識別編號   |
| `name`       | `str`       | 餐點名稱       |
| `price`      | `int`       | 餐點價格       |
| `category`   | `str`       | 餐點分類       |
| `taste_tags` | `List[str]` | 口味及特性標籤 |

#### Menu 類別 API

| 方法                       | 參數           | 回傳值               | 功能說明                               |
|----------------------------|----------------|----------------------|----------------------------------------|
| `__init__(self)`           | 無             | `None`               | 初始化菜單並載入 CSV 資料              |
| `_load_menu(self)`         | 無             | `Dict[str,MenuItem]` | 讀取 CSV 並建立以 `item_id` 為鍵的字典 |
| `get_all_items(self)`      | 無             | `List[MenuItem]`     | 取得所有餐點物件                       |
| `get_by_id(self, item_id)` | `item_id: str` | `Optional[MenuItem]` | 依編號查詢餐點，不存在時回傳 `None`    |

#### 載入與例外處理機制

* 使用 `csv.DictReader` 解析 `./data/menu.csv`。
* `taste_tags` 欄位以 `|` 作為分隔符號並自動去除空白。
* 個別資料列欄位缺失或價格非整數時，記錄紀錄（Logging）並略過該列。
* 找不到 CSV 時拋出例外；若全無有效品項則拋出 `RuntimeError`。

---

### 2. 購物車模組 (`cart_module.py`)

管理餐點加入與移除、計算購物車小計，以及產生結帳明細。

#### 購物車資料格式 (`List[dict]`)

| 欄位       | 型別       | 說明     |
|------------|------------|----------|
| `item_id`  | `str`      | 餐點編號 |
| `item`     | `MenuItem` | 餐點物件 |
| `qty`      | `int`      | 購買數量 |
| `subtotal` | `int`      | 品項小計 |

#### 函式 API

| 函式                 | 參數                          | 回傳型別         | 功能與驗證規則                                             |
|----------------------|-------------------------------|------------------|------------------------------------------------------------|
| `add_item`           | `cart, item_obj, qty`         | `List[dict]`     | 新增品項或累加數量；`qty <= 0` 時拋出 `ValueError`         |
| `remove_item`        | `cart, item_id`               | `List[dict]`     | 移除指定編號品項；若編號不存在則保持原樣                   |
| `calculate_subtotal` | `cart`                        | `int`            | 重新依單價×數量計算總金額；存在負數數量時拋出 `ValueError` |
| `generate_receipt`   | `cart, final_total, discount` | `Dict[str, Any]` | 產生結構化結帳資料與格式化文字收據                         |

* `generate_receipt` 回傳字典包含：`items`、`subtotal`、`discount_value`、`discount_message`、`final_total` 及
  `receipt_text`。

---

### 3. 優惠折扣模組 (`discount_module.py`)

計算優惠碼折扣、自動判斷套餐優惠，並選擇最佳折扣方案。

#### 折扣購物車格式 (`List[dict]`)

| 欄位         | 說明                                                        |
|--------------|-------------------------------------------------------------|
| `item_id`    | 餐點編號（`M003` 被強制視為特價品，不列入優惠碼可折抵金額） |
| `price`      | 單價                                                        |
| `quantity`   | 購買數量                                                    |
| `category`   | 餐點分類                                                    |
| `is_special` | 是否為特價品                                                |

#### 函式 API

| 函式                            | 回傳型別 | 功能說明                                                      |
|---------------------------------|----------|---------------------------------------------------------------|
| `get_cart_totals(cart)`         | `tuple`  | 回傳 `(總金額, 扣除特價品後可折抵金額)`                       |
| `apply_coupon(cart, code)`      | `dict`   | 驗證優惠碼（如 `1111` 滿 300 折 111、`8888` 滿 500 打 88 折） |
| `auto_detect_combo(cart)`       | `dict`   | 自動比對「主食+飲料+副餐+甜點」組合，每套折抵 15 元           |
| `get_best_discount(cart, code)` | `dict`   | 比較套餐與優惠碼折抵金額，回傳最優解（不重複累加）            |

---

### 4. 智慧推薦模組 (`recommender.py`)

**API Signature**:
`get_recommendations(preferences: dict, menu_db: Dict[str, MenuItem]) -> List[MenuItem]`

#### 偏好參數格式 (`preferences`)

* `max_budget`: 預算上限 (預設無上限)
* `taste_like`: 喜好標籤列表
* `taste_dislike`: 避開標籤列表

#### 推薦排序邏輯

1. 過濾 `price > max_budget` 之餐點。
2. 過濾包含任何 `taste_dislike` 標籤之餐點。
3. 計算符合 `taste_like` 標籤數量作為匹配分數。
4. 依匹配分數降冪排序，回傳前 5 項餐點（同分者維持原始 CSV 順序）。

---

### 5. 介面與狀態轉換 (`ui.py`)

* `run_ui(menu_items)`：初始化 Streamlit UI 主畫面與組件。
* `convert_cart_for_discount(cart)`：將 `cart_module` 之購物車格式轉換為 `discount_module` 所需之欄位格式，解決模組間資料結構解耦帶來的銜接問題。
* **Session State**：使用 `st.session_state` 保存購物車列表，防止跨頁面/跨元件觸發 Rerun 時狀態遺失。

---

## 🔄 完整系統執行流程圖

```text
main.py
   │
   ▼
[ Menu ] 載入 data/menu.csv
   │
   ▼
[ Streamlit UI ] 啟動應用程式
   │
   ├── 購物車操作 ───────────► cart_module.py (算小計 / 生成收據)
   │
   ├── 優惠折扣計算 ──────────► ui.py: convert_cart_for_discount()
   │                                 │
   │                                 ▼
   │                            discount_module.py (自動判斷套餐與優惠碼)
   │
   └── 智慧餐點推薦 ──────────► recommender.py (標籤比對與預算過濾)
```