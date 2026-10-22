import streamlit as st

from cart_module import add_item, calculate_subtotal,  generate_receipt, remove_item
from discount_module import get_best_discount
from recommender import get_recommendations


MAX_ITEM_QTY = 99

def convert_cart_for_discount(cart):
    """將正式購物車轉換成優惠模組需要的格式。"""
    discount_items = []

    for cart_item in cart:
        item = cart_item["item"]

        discount_items.append({
            "item_id": item.item_id,
            "name": item.name,
            "price": item.price,
            "quantity": cart_item["qty"],
            "category": item.category,
        })

    return discount_items


def calculate_best_discount(discount_items, coupon_code=""):
    """
    計算最佳優惠。

    M003 的價格已是特價：
    1. 不參與優惠碼。
    2. 不參與套餐組合。
    3. 仍計入購物車總額。
    """
    subtotal = sum(
        item["price"] * item.get("quantity", 1)
        for item in discount_items
    )

    special_items = [
        item for item in discount_items
        if item.get("item_id") == "M003"
    ]

    eligible_items = [
        item for item in discount_items
        if item.get("item_id") != "M003"
    ]

    special_total = sum(
        item["price"] * item.get("quantity", 1)
        for item in special_items
    )

    # 沒有一般商品時，M003 仍按其特價計算。
    if not eligible_items:
        return {
            "is_valid": False,
            "discount_value": 0,
            "new_total": subtotal,
            "subtotal": subtotal,
            "special_total": special_total,
            "message": "M003 為萬聖節特價，不參與套餐或優惠碼。",
            "discount_type": "none",
        }

    # 只將一般商品交給既有優惠模組。
    result = get_best_discount(
        eligible_items,
        coupon_code.strip(),
    )

    discount_value = (
        result["discount_value"] if result["is_valid"] else 0
    )

    # 一般商品折扣後金額 + M003 特價金額。
    new_total = (
        result["new_total"] if result["is_valid"]
        else subtotal - special_total
    ) + special_total

    if result["is_valid"]:
        message = result["message"]
    else:
        message = "目前沒有符合條件的優惠，依商品售價計算。"

    return {
        **result,
        "is_valid": result["is_valid"],
        "discount_value": discount_value,
        "new_total": new_total,
        "subtotal": subtotal,
        "special_total": special_total,
        "message": message,
    }


def calculate_selection_discount(selection, menu_db, coupon_code=""):
    """計算暫存選餐組合的最佳優惠。"""
    discount_items = []

    for item_id, qty in selection.items():
        item = menu_db.get(item_id)

        if item is not None and qty > 0:
            discount_items.append({
                "item_id": item.item_id,
                "name": item.name,
                "price": item.price,
                "quantity": qty,
                "category": item.category,
            })

    return calculate_best_discount(
        discount_items,
        coupon_code,
    )



def get_cart_item_count(cart):
    """計算購物車內的餐點總份數。"""
    return sum(item["qty"] for item in cart)


def get_selection_total(selection, menu_db):
    """計算暫存組合總額。"""
    total = 0

    for item_id, qty in selection.items():
        item = menu_db.get(item_id)

        if item is not None and qty > 0:
            total += item.price * qty

    return total


def get_selection_count(selection):
    """計算暫存組合總份數。"""
    return sum(qty for qty in selection.values() if qty > 0)


def clear_selection(selection):
    """清空指定暫存組合，不影響其他組合。"""
    selection.clear()


def add_selection_to_cart(selection, menu_db, cart):
    """將指定暫存組合加入正式購物車，回傳更新後的購物車。"""
    updated_cart = list(cart)

    for item_id, qty in list(selection.items()):
        item = menu_db.get(item_id)

        if item is not None and qty > 0:
            updated_cart = add_item(updated_cart, item, qty)

    return updated_cart


def render_quantity_controls(
    item,
    selection,
    prefix,
    disabled_increase=False,
):
    """顯示餐點數量及減少、增加按鈕。"""
    item_id = item.item_id
    qty = selection.get(item_id, 0)

    
    with st.container(border=True):
        st.write(f"**{item.name}**")

        if item.item_id == "M003":
            st.markdown("🎃 **萬聖節限定特價**")
            st.caption(
                f"{item.category}｜${item.price} / 份"
            )
            st.info("活動特價已反映於售價，不參與套餐及優惠碼折扣。")
        else:
            st.caption(f"{item.category}｜${item.price} / 份")


        if item.taste_tags:
            st.caption("標籤：" + "、".join(item.taste_tags))

        col_minus, col_qty, col_plus = st.columns([1, 1, 1])

        with col_minus:
            if st.button(
                "−",
                key=f"{prefix}_minus_{item_id}",
                disabled=(qty <= 0),
                use_container_width=True,
            ):
                if qty <= 1:
                    selection.pop(item_id, None)
                else:
                    selection[item_id] = qty - 1

                st.rerun()

        with col_qty:
            st.markdown(
                f"<div style='text-align:center; padding-top:6px'>"
                f"數量：<b>{qty}</b></div>",
                unsafe_allow_html=True,
            )

        with col_plus:
            if st.button(
                "+",
                key=f"{prefix}_plus_{item_id}",
                disabled=(
                    qty >= MAX_ITEM_QTY or disabled_increase
                ),
                use_container_width=True,
            ):
                selection[item_id] = qty + 1
                st.rerun()

        st.write(f"小計：**${item.price * qty}**")

        if disabled_increase and qty < MAX_ITEM_QTY:
            st.caption("增加一份會超出目前預算。")



def render_selection_summary(selection, menu_db, budget=None):
    """顯示暫存組合明細、優惠試算與預算資訊。"""
    selected_items = []

    for item_id, qty in selection.items():
        item = menu_db.get(item_id)

        if item is not None and qty > 0:
            selected_items.append((item, qty))

    total = sum(
        item.price * qty
        for item, qty in selected_items
    )
    count = sum(qty for _, qty in selected_items)

    coupon_code = st.session_state.get(
        "checkout_coupon_code", ""
    ).strip()

    discount_items = [
        {
            "item_id": item.item_id,
            "name": item.name,
            "price": item.price,
            "quantity": qty,
            "category": item.category,
        }
        for item, qty in selected_items
    ]

    discount_result = calculate_best_discount(
        discount_items,
        coupon_code,
    )

    payable_total = discount_result["new_total"]
    discount_value = discount_result["discount_value"]

    if not selected_items:
        st.info("目前尚未選擇餐點。")
    else:
        for item, qty in selected_items:
            st.write(
                f"- {item.name} × {qty}："
                f"${item.price} × {qty} = ${item.price * qty}"
            )

            if item.item_id == "M003":
                st.caption("🎃 萬聖節限定特價，不參與其他優惠折抵。")

    st.divider()

    # 優惠試算明細
    st.subheader("優惠試算")

    col1, col2 = st.columns(2)
    col1.metric("商品原價總額", f"${total}")
    col2.metric("M003 特價商品", f"${discount_result['special_total']}")

    if discount_value > 0:
        st.write(f"**最佳優惠：** {discount_result['message']}")
        st.write(f"**優惠折抵：** -${discount_value}")
    else:
        st.caption(discount_result["message"])

    st.caption("套餐已有折扣，所有優惠皆採擇優計算，不重複折抵。")

    if budget is None:
        st.caption(f"共選擇 {count} 份餐點")
        return total, selected_items

    remaining = budget - payable_total

    col1, col2 = st.columns(2)
    col1.metric("預算上限", f"${budget}")
    col2.metric("優惠後金額", f"${payable_total}")

    col3, col4 = st.columns(2)
    col3.metric("剩餘預算", f"${remaining}")
    col4.metric("餐點總份數", f"{count} 份")

    progress = (
        min(payable_total / budget, 1.0)
        if budget > 0
        else 0.0
    )
    st.progress(progress, text="優惠後預算使用進度")

    if payable_total > budget:
        st.error(
            f"優惠後仍超出預算 ${payable_total - budget}。"
            "請減少餐點數量後再加入購物車。"
        )
    elif selected_items:
        st.success(
            f"目前組合符合預算，尚餘 ${remaining}。"
        )
    else:
        st.info("請選擇餐點，開始組合。")

    return total, selected_items



def render_cart_sidebar(menu_db=None):
    """顯示正式購物車及結帳功能。"""
    st.sidebar.header("🛒 我的購物車")

    cart = st.session_state.cart
    subtotal = calculate_subtotal(cart)

    if not cart:
        st.sidebar.info("購物車目前是空的。")
        return

    for cart_item in cart:
        item = cart_item["item"]
        qty = cart_item["qty"]

        with st.sidebar.container(border=True):
            st.write(f"**{item.name}**")
            st.caption(
                f"${item.price} × {qty} = ${item.price * qty}"
            )

            if st.button(
                "移除餐點",
                key=f"remove_cart_{item.item_id}",
                use_container_width=True,
            ):
                st.session_state.cart = remove_item(
                    st.session_state.cart,
                    item.item_id,
                )
                st.rerun()

    st.sidebar.divider()
    st.sidebar.write(f"**商品小計：${subtotal}**")
    st.sidebar.caption(f"共 {get_cart_item_count(cart)} 份餐點")

    coupon_code = st.sidebar.text_input(
        "優惠碼",
        placeholder="例如 1111 或 8888",
        key="checkout_coupon_code",
    )

    if st.sidebar.button(
        "計算優惠並結帳",
        use_container_width=True,
        type="primary",
    ):
        discount_cart = convert_cart_for_discount(
            st.session_state.cart
        )

        result = calculate_best_discount(
            discount_cart,
            coupon_code.strip(),
        )

        receipt_data = generate_receipt(
            st.session_state.cart,
            result["new_total"],
            result,
        )

        if result["is_valid"]:
            st.sidebar.success(result["message"])
        elif coupon_code.strip():
            st.sidebar.warning(result["message"])
        else:
            st.sidebar.info(result["message"])

        st.sidebar.write(
            f"商品小計：${subtotal}"
        )
        st.sidebar.write(
            f"折抵金額：${result['discount_value']}"
        )
        st.sidebar.write(
            f"**應付金額：${result['new_total']}**"
        )

        st.sidebar.code(receipt_data["receipt_text"])


def run_ui(menu_items):
    """建立 Menu、餐點推薦、購物車及結帳介面。"""

    # --------------------------------------------------
    # 1. 初始化工作階段狀態
    # --------------------------------------------------

    defaults = {
        "cart": [],
        "menu_selection": {},
        "recommendation_selection": {},
        "recommendation_ids": [],
        "recommendation_active": False,
        "recommendation_last_mode": None,
        "recommendation_last_preferences": None,
        "recommendation_message": "",
    }

    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

    menu_db = {item.item_id: item for item in menu_items}

    categories = list(dict.fromkeys(
        item.category or "其他"
        for item in menu_items
    ))

    available_tags = sorted({
        tag
        for item in menu_items
        for tag in item.taste_tags
    })

    st.title("點餐系統")
    st.caption("自由選餐、預算組合與個人化推薦")

    menu_tab, recommendation_tab = st.tabs(["Menu", "餐點推薦"])

    # --------------------------------------------------
    # 2. Menu：獨立暫存組合，不受推薦預算限制
    # --------------------------------------------------
    with menu_tab:
        left1_column, right1_column = st.columns([3, 2], gap="large")
        with left1_column:
            st.subheader("菜單")
            st.write(
                "瀏覽菜單並調整各項數量。\n"
                "選餐暫存不會直接更動正式購物車。\n"
                "套餐組合：1主食 + 1飲料 + 1附餐 + 1甜點 = 折15元"
            )

            if not menu_items:
                st.warning("目前沒有可顯示的餐點。")
            else:
                menu_categories = st.tabs(["全部餐點"] + categories)

                with menu_categories[0]:
                    for item in menu_items:
                        render_quantity_controls(
                            item,
                            st.session_state.menu_selection,
                            "menu_all",
                        )

                for index, category in enumerate(categories, start=1):
                    with menu_categories[index]:
                        category_items = [
                            item
                            for item in menu_items
                            if (item.category or "其他") == category
                        ]

                        for item in category_items:
                            render_quantity_controls(
                                item,
                                st.session_state.menu_selection,
                                f"menu_category_{index}",
                            )

        with right1_column:
            st.subheader("Menu 暫存組合")

            menu_total, menu_selected_items = render_selection_summary(
                st.session_state.menu_selection,
                menu_db,
            )

            if st.button(
                "確認並加入購物車",
                key="menu_confirm_add",
                type="primary",
                use_container_width=True,
                disabled=not menu_selected_items,
            ):
                st.session_state.cart = add_selection_to_cart(
                    st.session_state.menu_selection,
                    menu_db,
                    st.session_state.cart,
                )

                clear_selection(st.session_state.menu_selection)

                st.success("Menu 暫存組合已加入購物車。")
                st.rerun()

            if st.button(
                "清空 Menu 暫存組合",
                key="menu_clear_selection",
                use_container_width=True,
                disabled=not st.session_state.menu_selection,
            ):
                clear_selection(st.session_state.menu_selection)
                st.rerun()

    # --------------------------------------------------
    # 3. 推薦頁面：左側設定及選餐，右側組合檢查
    # --------------------------------------------------

    with recommendation_tab:
        left2_column, right2_column = st.columns([3, 2], gap="large")

        with left2_column:
            st.subheader("推薦設定與選餐")

            with st.expander("點擊展開個人化設定", expanded=False):
                budget = st.number_input(
                    "預算上限",
                    min_value=0,
                    value=500,
                    step=50,
                    key="recommendation_budget",
                    help="這是整份推薦組合的總預算，不是單一餐點的預算。",
                )

                taste_like = st.multiselect(
                    "喜歡的口味標籤",
                    options=available_tags,
                    key="recommendation_likes",
                    help="符合越多喜歡的標籤，推薦分數越高。",
                )

                taste_dislike = st.multiselect(
                    "排除的口味標籤",
                    options=available_tags,
                    key="recommendation_dislikes",
                    help="含有任一排除標籤的餐點不會出現在推薦清單。",
                )

                mode_label = st.radio(
                    "推薦模式",
                    options=["套餐引導", "一般推薦"],
                    horizontal=True,
                    key="recommendation_mode_label",
                )

                mode = (
                    "guided"
                    if mode_label == "套餐引導"
                    else "general"
                )

                preferences = {
                    "max_budget": int(budget),
                    "taste_like": taste_like,
                    "taste_dislike": taste_dislike,
                }

                duplicate_tags = set(taste_like) & set(taste_dislike)

                if duplicate_tags:
                    st.warning(
                        "以下標籤同時被設定為喜歡及排除，"
                        "請調整選擇：" + "、".join(sorted(duplicate_tags))
                    )

                def update_recommendations():
                    """更新推薦清單，但不修改已選組合。"""
                    results = get_recommendations(
                        preferences,
                        menu_db,
                        limit=5,
                        mode=mode,
                    )

                    st.session_state.recommendation_ids = [
                        item.item_id for item in results
                    ]
                    st.session_state.recommendation_active = True
                    st.session_state.recommendation_last_mode = mode
                    st.session_state.recommendation_last_preferences = {
                        "max_budget": int(budget),
                        "taste_like": list(taste_like),
                        "taste_dislike": list(taste_dislike),
                    }
                    st.session_state.recommendation_message = ""

                # 首次進入推薦頁時，或切換推薦模式時，更新推薦清單。
                # 只改推薦清單，不清除 recommendation_selection。
                previous_preferences = (
                    st.session_state.recommendation_last_preferences
                )

                if not duplicate_tags:
                    if not st.session_state.recommendation_active:
                        update_recommendations()
                    elif st.session_state.recommendation_last_mode != mode:
                        update_recommendations()

                if st.button(
                    "取得／更新推薦餐點",
                    key="recommendation_refresh",
                    type="primary",
                    use_container_width=True,
                ):
                    if duplicate_tags:
                        st.error("請先處理重複的喜歡及排除標籤。")
                    else:
                        update_recommendations()
                        st.rerun()

            st.divider()
            st.subheader("推薦餐點")

            if duplicate_tags:
                st.info("調整標籤後即可取得推薦。")

            elif not st.session_state.recommendation_active:
                st.info("請先取得推薦餐點。")

            else:
                recommendation_ids = (
                    st.session_state.recommendation_ids
                )

                recommended_items = [
                    menu_db[item_id]
                    for item_id in recommendation_ids
                    if item_id in menu_db
                ]

                if not recommended_items:
                    st.info("目前沒有符合條件的推薦餐點。")

                elif mode == "guided":
                    # 套餐引導：依實際分類分頁，每分類最多 5 個。
                    grouped_items = {}

                    for item in recommended_items:
                        category = item.category or "其他"
                        grouped_items.setdefault(category, []).append(item)

                    st.caption(
                        "\n依分類逐步選餐。可以跳過任何分類，"
                        "各分類共用右側顯示的總預算。\n"
                        "套餐組合：1主食 + 1飲料 + 1附餐 + 1甜點 = 折15元"
                    )

                    category_tabs = st.tabs(list(grouped_items.keys()))

                    for category, category_tab in zip(
                        grouped_items.keys(),
                        category_tabs,
                    ):
                        with category_tab:
                            st.caption(
                                f"{category}："
                                f"{len(grouped_items[category])} 個推薦品項"
                            )

                            for item in grouped_items[category]:
                                selection = (
                                    st.session_state.recommendation_selection
                                )
                                
                                current_qty = selection.get(item.item_id, 0)

                                candidate_selection = dict(selection)
                                candidate_selection[item.item_id] = current_qty + 1

                                coupon_code = st.session_state.get(
                                    "checkout_coupon_code", ""
                                ).strip()

                                candidate_result = calculate_selection_discount(
                                    candidate_selection,
                                    menu_db,
                                    coupon_code,
                                )

                                would_exceed = candidate_result["new_total"] > budget

                                render_quantity_controls(
                                    item,
                                    selection,
                                    "recommendation_guided",
                                    disabled_increase=(
                                        current_qty >= MAX_ITEM_QTY
                                        or would_exceed
                                    ),
                                )

                else:
                    # 一般推薦：先全菜單統一選出最多 5 個，再依分類呈現。
                    grouped_items = {}

                    for item in recommended_items:
                        category = item.category or "其他"
                        grouped_items.setdefault(category, []).append(item)

                    st.caption(
                        f"全菜單共推薦 {len(recommended_items)} 個品項，"
                    )

                    for category, items in grouped_items.items():
                        st.markdown(f"**{category}**")

                        for item in items:
                            selection = (
                                st.session_state.recommendation_selection
                            )
                            
                            current_qty = selection.get(item.item_id, 0)

                            candidate_selection = dict(selection)
                            candidate_selection[item.item_id] = current_qty + 1

                            coupon_code = st.session_state.get(
                                "checkout_coupon_code", ""
                            ).strip()

                            candidate_result = calculate_selection_discount(
                                candidate_selection,
                                menu_db,
                                coupon_code,
                            )

                            would_exceed = candidate_result["new_total"] > budget

                            render_quantity_controls(
                                item,
                                selection,
                                "recommendation_general",
                                disabled_increase=(
                                    current_qty >= MAX_ITEM_QTY
                                    or would_exceed
                                ),
                            )

        # --------------------------------------------------
        # 4. 右側：完整推薦組合明細及預算
        # --------------------------------------------------

        with right2_column:
            st.subheader("組合明細與預算")
            st.caption(
                "顯示所有已選餐點，即使部分餐點已不在目前推薦清單中。"
            )

            recommendation_selection = (
                st.session_state.recommendation_selection
            )

            total, selected_items = render_selection_summary(
                recommendation_selection,
                menu_db,
                budget=int(budget),
            )

            coupon_code = st.session_state.get(
                "checkout_coupon_code", ""
            ).strip()

            recommendation_discount = calculate_selection_discount(
                recommendation_selection,
                menu_db,
                coupon_code,
            )

            over_budget = recommendation_discount["new_total"] > budget

            if st.button(
                "確認並加入購物車",
                key="recommendation_confirm_add",
                type="primary",
                use_container_width=True,
                disabled=(
                    not selected_items
                    or over_budget
                    or bool(duplicate_tags)
                ),
            ):
                st.session_state.cart = add_selection_to_cart(
                    recommendation_selection,
                    menu_db,
                    st.session_state.cart,
                )

                clear_selection(recommendation_selection)

                st.success("推薦暫存組合已加入購物車。")
                st.rerun()

            if st.button(
                "清空推薦暫存組合",
                key="recommendation_clear_selection",
                use_container_width=True,
                disabled=not recommendation_selection,
            ):
                clear_selection(recommendation_selection)
                st.rerun()

    # --------------------------------------------------
    # 5. 正式購物車與結帳
    # --------------------------------------------------

    render_cart_sidebar(menu_db)


if __name__ == "__main__":
    from menu import Menu

    menu_manager = Menu()
    run_ui(menu_manager.get_all_items())
