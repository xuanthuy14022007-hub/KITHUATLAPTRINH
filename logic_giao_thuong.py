from database_connector import get_connection

# =================================================================
# 1. DÀNH CHO MERCHANT (THƯƠNG LÁI) - ĐI CHỢ & MUA HÀNG
# =================================================================

def lay_danh_sach_cho_nong_san():
    """Hiển thị các lô hàng có trạng thái 'Sẵn sàng bán'"""
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT FarmingActivities.activity_id, Users.full_name, Crops.crop_name, 
               ActivityLog.quantity, Crops.base_price, FarmingActivities.farm_name
        FROM FarmingActivities
        JOIN Users ON FarmingActivities.farmer_id = Users.user_id
        JOIN Crops ON FarmingActivities.crop_id = Crops.crop_id
        JOIN ActivityLog ON FarmingActivities.activity_id = ActivityLog.activity_id
        WHERE FarmingActivities.status = 'Sẵn sàng bán' AND ActivityLog.action_type = 'Thu hoạch'
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows

def them_vao_gio_hang(merchant_id, activity_id, quantity):
    """Bỏ hàng vào giỏ tạm, nếu trùng thì cộng dồn số lượng"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT cart_id, quantity FROM Cart WHERE merchant_id = ? AND activity_id = ?", (merchant_id, activity_id))
    item = cursor.fetchone()
    if item:
        cursor.execute("UPDATE Cart SET quantity = quantity + ? WHERE cart_id = ?", (quantity, item[0]))
    else:
        cursor.execute("INSERT INTO Cart (merchant_id, activity_id, quantity) VALUES (?, ?, ?)", (merchant_id, activity_id, quantity))
    conn.commit()
    conn.close()

def thanh_toan_gio_hang(merchant_id, order_date):
    """Chốt đơn: Tự động tách đơn hàng theo từng Nông dân"""
    conn = get_connection()
    cursor = conn.cursor()
    # Lấy dữ liệu từ giỏ hàng hiện tại
    cursor.execute("""
        SELECT Cart.quantity, Crops.base_price, FarmingActivities.farmer_id, FarmingActivities.crop_id
        FROM Cart
        JOIN FarmingActivities ON Cart.activity_id = FarmingActivities.activity_id
        JOIN Crops ON FarmingActivities.crop_id = Crops.crop_id
        WHERE Cart.merchant_id = ?
    """, (merchant_id,))
    items = cursor.fetchall()
    if not items: return

    try:
        farmer_orders = {}
        for qty, price, f_id, c_id in items:
            if f_id not in farmer_orders: farmer_orders[f_id] = []
            farmer_orders[f_id].append((qty, price, c_id))

        for f_id, f_items in farmer_orders.items():
            total_amt = sum(q * p for q, p, c in f_items)
            # Tạo đơn hàng mới, mặc định là 'Chờ xác nhận'
            cursor.execute("INSERT INTO Orders (merchant_id, farmer_id, status, total_amount, order_date) VALUES (?, ?, 'Chờ xác nhận', ?, ?)",
                           (merchant_id, f_id, total_amt, order_date))
            order_id = cursor.lastrowid
            for q, p, c in f_items:
                cursor.execute("INSERT INTO OrderItems (order_id, crop_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
                               (order_id, c, q, p))
        
        cursor.execute("DELETE FROM Cart WHERE merchant_id = ?", (merchant_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Lỗi thanh toán: {e}")
    finally:
        conn.close()

# =================================================================
# 2. DÀNH CHO FARMER (NÔNG DÂN) - QUẢN LÝ ĐƠN HÀNG ĐẾN
# =================================================================

def lay_danh_sach_don_hang_den(farmer_id):
    """Farmer xem các đơn hàng Merchant đã đặt"""
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT Orders.order_id, Users.full_name, Orders.total_amount, Orders.order_date, Orders.status
        FROM Orders
        JOIN Users ON Orders.merchant_id = Users.user_id
        WHERE Orders.farmer_id = ?
        ORDER BY Orders.order_date DESC
    """
    cursor.execute(query, (farmer_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def cap_nhat_trang_thai_don_hang(order_id, new_status):
    """Xác nhận, Giao hàng, Hoàn thành hoặc Hủy đơn"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Orders SET status = ? WHERE order_id = ?", (new_status, order_id))
    conn.commit()
    conn.close()
