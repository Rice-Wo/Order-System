# Order-System

我不知道啊，隨便寫   
下面都是ChatGPT說的，單純讓我們有東西好討論而已。

## 初步架構
```text
點餐系統
├── UI
├── Menu
├── Order
├── Recommendation

```

### 初步分工

1. 菜單與資料管理
2. 購物車與結帳
3. 優惠與套餐
4. 推薦系統
5. 介面與整合  

# 🍔 智慧點餐系統（Order System）
## 📌 專案簡介（Project Overview）

本專案使用 Python 與 Streamlit 開發互動式智慧點餐系統，提供菜單瀏覽、購物車管理、優惠折扣計算、訂單明細產生及個人化餐點推薦等功能。

系統採用模組化設計，將菜單管理、購物車操作、優惠計算、餐點推薦與使用者介面分開實作，提升程式碼的可讀性、可維護性及擴充性。

### ✨ 主要功能
菜單管理： 讀取 CSV 菜單資料，提供餐點清單及編號查詢。
購物車管理： 支援新增餐點、移除品項、數量累加及小計計算。
優惠折扣： 支援固定金額折抵、百分比折扣及自動套餐優惠。
智慧推薦： 根據預算、喜好標籤及排除標籤篩選推薦餐點。
結帳明細： 產生結構化訂單資料及文字版收據。
互動式介面： 使用 Streamlit 提供菜單、購物車、優惠結帳及推薦功能。

## 📂 專案架構（Project Structure）
```text
Order-System/
├── data/
│   └── menu.csv              # 菜單原始資料
├── main.py                   # 主程式進入點
├── ui.py                     # Streamlit 使用者介面
├── menu.py                   # 菜單資料管理
├── cart_module.py            # 購物車及收據處理
├── discount_module.py        # 優惠碼及套餐折扣
├── recommender.py            # 智慧餐點推薦
├── requirements.txt          # Python 套件清單
├── README.md                 # 專案說明文件
└── Kill_Bug.txt              # 專案相關紀錄（若有）
```

### 📋 模組職責
|檔案|主要職責|
|---|---|
|main.py|初始化菜單並啟動使用者介面|
|ui.py|整合點餐、購物車、折扣及推薦功能|
|menu.py|讀取 CSV、建立餐點物件及查詢菜單|
|cart_module.py|管理購物車、計算小計及產生收據|
|discount_module.py|計算優惠碼折扣及套餐優惠|
|recommender.py|根據預算與口味標籤推薦餐點|
|data/menu.csv|儲存菜單資料|

## 🧩 核心模組與 API 說明
### 1. 菜單管理模組（menu.py）
模組目的： 讀取 CSV 菜單資料，將餐點轉換為 MenuItem 物件，並提供菜單查詢功能。
#### MenuItem
使用 Python 的 @dataclass 定義餐點資料類別。

|屬性|型別|說明|
|---|---|---|
|item_id|`str`|餐點識別編號|
|name|`str`|餐點名稱|
|price|`int`|餐點價格|
|category|`str`|`餐點分類|
|taste_tags|`List[str]`|口味及特性標籤|

#### Menu

菜單資料管理類別，透過內部字典保存餐點物件。

|方法|參數|回傳值|功能|
|---|---|---|---|
|__init__(self)|無|None|初始化菜單並載入 CSV 資料|
|_load_menu(self)|無|Dict[str, MenuItem]|讀取 CSV 並建立以 item_id 為鍵的字典|
|get_all_items(self)|無|List[MenuItem]|取得所有餐點物件|
|get_by_id(self, item_id)|item_id: str|Optional[MenuItem]|依編號查詢餐點，不存在時回傳 None|

#### 菜單載入機制
- 使用 csv.DictReader 讀取 CSV。
- 使用 taste_tags 欄位中的 | 分隔標籤，並移除多餘空白。
- 將價格轉換為整數。
- 遇到個別資料列的欄位缺失或價格格式錯誤時，記錄錯誤並略過該品項。
- 找不到 CSV 檔案時，記錄錯誤並重新拋出例外。
- 如果沒有任何有效品項，則拋出 RuntimeError。
- 使用 Python logging 記錄載入狀態及錯誤。

預設 CSV 路徑為 ./data/menu.csv。

### 2. 購物車模組（cart_module.py）
模組目的： 管理餐點加入與移除、計算購物車小計，以及產生結帳明細。

#### 購物車資料格式
購物車使用 List[dict] 儲存，每筆資料包含：

|欄位|型別|說明|
|---|---|---|
|item_id|str|餐點編號|
|item|MenuItem|餐點物件|
|qty|int|購買數量|
|subtotal|int|品項小計|

#### 函式 API
|函式|回傳型別|功能|
|---|---|---|
|add_item(cart, item_obj, qty)|List[dict]|新增餐點；相同品項會累加數量並更新小計|
|remove_item(cart, item_id)|List[dict]|移除指定編號的餐點|
|calculate_subtotal(cart)|int|重新計算所有品項的總金額|
|generate_receipt(cart, final_total, discount)|Dict[str, Any]|產生結構化結帳資料與文字收據|

**add_item(cart, item_obj, qty)**
- cart：目前購物車列表。
- item_obj：欲加入的 MenuItem。
- qty：新增數量，必須大於 0。
- 回傳值： 更新後的購物車列表。

當 qty <= 0 時，拋出 ValueError。

**remove_item(cart, item_id)**
- cart：目前購物車列表。
- item_id：欲移除的餐點編號。
- 回傳值： 移除指定品項後的列表。

找不到指定編號時，其他品項保持不變。

**calculate_subtotal(cart)**

依照每筆餐點的價格與數量重新計算金額，不直接信任原有的 subtotal 欄位。

- 若購物車中存在負數數量，會拋出 ValueError。
- 空購物車的小計為 0。

**generate_receipt(cart, final_total, discount)**

回傳字典包含：

|欄位|說明|
|---|---|
|items|品項編號、名稱、單價、數量及小計|
|subtotal	|商品小計|
|discount_value|折扣金額|
|discount_message|優惠說明|
|final_total|最終應付金額|
|receipt_text|格式化後的文字收據|

discount 可包含 is_valid、discount_value、new_total 及 message 等欄位。

此函式會計算商品小計並產生收據，但最終應付金額使用呼叫端傳入的 final_total。

### 3. 優惠折扣模組（discount_module.py）

模組目的： 計算優惠碼折扣、自動判斷套餐優惠，並比較符合條件的折扣方案。

#### 購物車資料格式

本模組使用字典列表，每筆資料可包含：

|欄位|	說明|
|---|---|
|item_id|	餐點編號|
|price	|單價|
|quantity|	購買數量|
|category	|餐點分類|
|is_special|	是否為特價品|

其中，item_id == "M003" 會被強制視為特價品，不列入優惠碼的可折抵金額。

#### 函式 API
|函式|	回傳型別	|功能|
|---|---|---|
|get_cart_totals(cart)	|tuple	|計算總金額及符合優惠碼折抵條件的金額|
|apply_coupon(cart, code)	|dict|	驗證優惠碼並計算折扣|
|auto_detect_combo(cart)	|dict|	偵測套餐組合並計算折扣|
|get_best_discount(cart, code="")|	dict|	比較優惠碼及套餐優惠，回傳採用的優惠結果|

**get_cart_totals(cart)**

計算並回傳兩個金額：

1. 購物車全部品項的總金額。
2. 排除特價品後，可用於計算優惠碼折扣的金額。

此函式使用 price、quantity 等字典欄位。

**apply_coupon(cart, code)**

目前設定的優惠碼如下：

|優惠碼	|條件	|優惠內容|
|---|---|---|
|1111|	可折抵金額滿 300 元	|折抵 111 元|
|8888	|可折抵金額滿 500 元|	可折抵金額打 88 折|

折扣計算時，特價品不列入最低消費金額與折扣計算。

回傳字典包含：

- is_valid：優惠是否有效。
- discount_value：折扣金額。
- new_total：折扣後總金額。
- message：優惠結果說明。
- auto_detect_combo(cart)

自動檢查購物車是否包含完整套餐。

一份套餐需要同時包含：

- 一份主食（分類為「主餐」、「米漢堡」或「台式餐點」）。
- 一份飲料。
- 一份附餐。
- 一份甜點。

每份完整套餐折抵 15 元。若各類餐點數量不同，系統會依四類餐點中最少的數量決定可組成的套餐數。

**get_best_discount(cart, code="")**

比較套餐優惠與有效的優惠碼結果，一次採用一種優惠，不累加兩種折扣。

- 當兩種有效優惠的折扣金額相同時，會優先回傳套餐優惠結果。
- 若沒有輸入優惠碼，或優惠碼無效，則回傳套餐判斷結果。
### 4. 智慧推薦模組（recommender.py）

模組目的： 根據使用者預算及口味偏好篩選餐點，提供最多五項推薦。

**get_recommendations(preferences: dict, menu_db: Dict[str, MenuItem]) -> List[MenuItem]**

參數說明
|參數|	型別|	說明|
|---|---|---|
|preferences	|dict	|使用者的預算與口味偏好|
|menu_db	|Dict[str, MenuItem]|	以餐點編號為鍵的菜單字典|

**preferences** 支援以下欄位：

|欄位|	說明|
|---|---|
|max_budget	|預算上限，預設為無限大|
|taste_like	|喜歡的口味或特性標籤|
|taste_dislike	|希望排除的標籤|

#### 推薦流程
1. 排除價格高於預算上限的餐點。
2. 排除包含任何不喜歡標籤的餐點。
3. 計算每項餐點符合多少個喜好標籤。
4. 依符合標籤的分數由高至低排序。
5. 回傳最多五項餐點。

**注意： 此推薦函式只使用喜好標籤計算分數，不會另外考慮價格便宜程度；同分餐點的相對順序取決於原始菜單的走訪順序。**

### 5. 使用者介面模組（ui.py）

模組目的： 使用 Streamlit 建立網頁點餐介面，整合其他模組的功能。

**run_ui(menu_items)**

接收菜單品項列表，建立點餐介面。

主要功能：

- 顯示餐點名稱、價格、分類及標籤。
- 提供餐點數量選擇及加入購物車功能。
- 顯示購物車品項及小計。
- 提供移除購物車品項的操作。
- 輸入優惠碼並計算優惠結果。
- 產生結帳收據。
- 根據預算及口味偏好提供餐點推薦。

**convert_cart_for_discount(cart)**

將 cart_module.py 的購物車格式轉換成 discount_module.py 所需的格式。

轉換內容包含餐點編號、名稱、價格、數量、分類及特價標記。

此函式用於整合兩個模組，避免因資料欄位名稱不同而導致折扣計算失敗。

#### 購物車狀態管理

介面使用 Streamlit 的 st.session_state 保存購物車，讓使用者操作介面時，購物車內容能在重新執行程式後保留於目前的使用者工作階段。

### 6. 主程式模組（main.py）

模組目的： 負責初始化菜單並啟動使用者介面。

**main()**

執行流程：

1. 建立 Menu 物件。
2. 呼叫 get_all_items() 取得所有餐點。
3. 將菜單品項傳入 run_ui(menu_items)。
4. 啟動 Streamlit 點餐介面。

此模組作為程式的進入點，不直接負責購物車操作或折扣計算。

## 🔄 系統執行流程（System Workflow）

```text
main.py
   │
   ▼
建立 Menu 物件
   │
   ▼
讀取 data/menu.csv
   │
   ▼
取得菜單品項
   │
   ▼
啟動 Streamlit UI
   │
   ├── 瀏覽菜單及加入購物車
   │        │
   │        ▼
   │   cart_module.py
   │        │
   │        ▼
   │   計算商品小計
   │
   ├── 輸入優惠碼及判斷套餐
   │        │
   │        ▼
   │   轉換購物車資料格式
   │        │
   │        ▼
   │   discount_module.py
   │        │
   │        ▼
   │   取得折扣結果及應付金額
   │
   └── 輸入預算與口味偏好
            │
            ▼
       recommender.py
            │
            ▼
       顯示推薦餐點
```

## 🚀 快速開始（Quick Start）
### 1. 取得專案

如果專案已上傳至 GitHub，可執行：

git clone https://github.com/Rice-Wo/Order-System.git
cd Order-System

### 2. 建立虛擬環境（建議）

Windows：

python -m venv .venv
.venv\Scripts\activate


macOS / Linux：

python3 -m venv .venv
source .venv/bin/activate

### 3. 安裝相依套件

如果專案已建立 requirements.txt：

pip install -r requirements.txt


若尚未建立，安裝目前程式所需的 Streamlit：

`pip install streamlit`


其他匯入的 csv、logging、dataclasses、typing 均屬於 Python 標準函式庫，不需要另外安裝。

### 4. 啟動系統

在專案根目錄執行：

`streamlit run main.py`


成功啟動後，使用瀏覽器開啟 Streamlit 提供的本機網址，即可操作點餐系統。

## 🛠️ 開發環境與技術（Technology Stack）
|項目	|技術|
|---|---|
|程式語言	|Python|
|網頁介面框架	|Streamlit|
|資料格式	|CSV|
|版本控制	|Git / GitHub|

實際 Python 版本及套件版本需求，請依專案環境確認。

## 👥 小組分工與協作（Team Collaboration）

本專案採用模組化設計，將各項功能拆分為獨立模組，以利多人協作、功能測試及後續維護。

|工作項目|	主要內容|
|---|---|
|菜單管理	|CSV 資料讀取、餐點物件建立及查詢|
|購物車管理	|餐點新增、移除、數量累加及小計計算|
|優惠折扣	|優惠碼驗證、套餐偵測及折扣比較|
|智慧推薦	|預算過濾、口味標籤比對及餐點排序|
|介面與整合	|Streamlit 介面、狀態管理及模組串接|

實際成員姓名與個別負責內容，可依小組的工作分配補充。

## 📌 設計特色與注意事項（Design Highlights & Notes）
### 模組化設計
- 透過不同 Python 模組分離資料管理、購物車邏輯、折扣運算、推薦功能及 UI。
- 各模組透過函式與資料物件互相串接，降低功能之間的耦合。
### 資料格式整合
- 菜單模組使用 MenuItem 物件保存餐點資料。
- 購物車模組使用包含 item、qty 等欄位的字典列表。
- 優惠模組使用 price、quantity、category 等欄位進行計算。
- UI 透過資料轉換函式串接購物車及優惠模組。
### 目前功能範圍
- 系統目前提供點餐、購物車、折扣試算及餐點推薦。
- 目前未實作實際付款、資料庫訂單儲存或會員系統。
- 優惠碼與套餐優惠的計算規則依 discount_module.py 中的實作為準。
- 菜單分類名稱及 CSV 欄位須與程式碼的讀取及判斷規則一致。
### 🔮 未來改進方向（Future Improvements）
- 增加訂單歷史紀錄及訂單查詢功能。
- 加入會員系統及個人化偏好儲存。
- 增加單元測試及整合測試。
- 改善錯誤處理及輸入資料驗證。
- 擴充優惠規則及套餐組合設定。
- 改善推薦演算法及推薦結果解釋。
- 增加資料庫支援，以管理更多菜單及訂單資料。