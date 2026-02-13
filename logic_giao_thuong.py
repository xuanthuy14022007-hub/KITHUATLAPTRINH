from database_connector import get_connection

# =================================================================
# 1. DÀNH CHO MERCHANT (THƯƠNG LÁI) - ĐI CHỢ & MUA HÀNG
# =================================================================

def lay_danh_sach_nong_san(tu_khoa=""):
    """
    Hàm đa năng: 
    - Nếu không truyền tu_khoa: Lấy tất cả (phục vụ trang chủ)
    - Nếu có tu_khoa: Tìm kiếm theo yêu cầu
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    search_term = f"%{tu_khoa}%"
    
    query = """
        SELECT FarmingActivities.activity_id, Users.full_name, Crops.crop_name, 
               ActivityLog.quantity, Crops.base_price, FarmingActivities.farm_name
        FROM FarmingActivities
        JOIN Users ON FarmingActivities.farmer_id = Users.user_id
        JOIN Crops ON FarmingActivities.crop_id = Crops.crop_id
        JOIN ActivityLog ON FarmingActivities.activity_id = ActivityLog.activity_id
        WHERE FarmingActivities.status = 'Sẵn sàng bán' 
        AND ActivityLog.action_type = 'Thu hoạch'
        AND (Crops.crop_name LIKE ? OR Users.full_name LIKE ?)
    """
    
    cursor.execute(query, (search_term, search_term))
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
def lay_items_trong_don_hang(cursor, order_id):
    """Lấy danh sách sản phẩm và activity_id tương ứng để trừ/hoàn kho"""
    query = """
        SELECT OI.quantity, FA.activity_id 
        FROM OrderItems OI
        JOIN Orders O ON OI.order_id = O.order_id
        JOIN FarmingActivities FA ON O.farmer_id = FA.farmer_id AND OI.crop_id = FA.crop_id
        WHERE O.order_id = ? AND FA.status = 'Sẵn sàng bán'
    """
    cursor.execute(query, (order_id,))
    return cursor.fetchall()
def cap_nhat_trang_thai_don_hang(order_id, new_status):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # TRƯỜNG HỢP 1: XÁC NHẬN -> TRỪ KHO
        if new_status == 'Xác nhận':
            items = lay_items_trong_don_hang(cursor, order_id)
            for qty, act_id in items:
                cursor.execute("UPDATE ActivityLog SET quantity = quantity - ? WHERE activity_id = ? AND action_type = 'Thu hoạch'", (qty, act_id))

        # TRƯỜNG HỢP 2: HUỶ ĐƠN -> HOÀN KHO (Nếu trước đó đã xác nhận)
        elif new_status == 'Huỷ đơn':
            # Thuỳ có thể kiểm tra nếu đơn cũ đang là 'Xác nhận' hoặc 'Giao hàng' thì mới hoàn kho
            items = lay_items_trong_don_hang(cursor, order_id)
            for qty, act_id in items:
                cursor.execute("UPDATE ActivityLog SET quantity = quantity + ? WHERE activity_id = ? AND action_type = 'Thu hoạch'", (qty, act_id))

        # TRƯỜNG HỢP 3: CÁC TRẠNG THÁI KHÁC (Giao hàng, Hoàn thành)
        # Không làm gì với kho cả, chỉ cập nhật status ở dòng dưới cùng
        
        cursor.execute("UPDATE Orders SET status = ? WHERE order_id = ?", (new_status, order_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Lỗi: {e}")
    finally:
        conn.close()
