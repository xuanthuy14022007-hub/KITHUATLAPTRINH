from database.database_connector import get_connection
import sqlite3

# ================== MERCHANT ==================

def lay_danh_sach_nong_san(tu_khoa=""):
    """
    Lấy danh sách nông sản đang ở trạng thái 'Sẵn sàng bán'.
    Giá hiển thị ưu tiên selling_price, nếu không có thì lấy base_price từ Crops.

    Args:
        tu_khoa (str, optional): Từ khóa tìm kiếm (theo tên cây hoặc tên người bán).

    Returns:
        list: Danh sách các tuple (activity_id, full_name, crop_name, quantity, price, plot_name).
    """
    conn = get_connection()
    cursor = conn.cursor()
    search_term = f"%{tu_khoa}%"
    query = """
        SELECT fa.activity_id, u.full_name, c.crop_name, 
               al.quantity, 
               COALESCE(fa.selling_price, c.base_price) as price,
               fa.plot_name
        FROM FarmingActivities fa
        JOIN Users u ON fa.farmer_id = u.user_id
        JOIN Crops c ON fa.crop_id = c.crop_id
        LEFT JOIN ActivityLog al ON fa.activity_id = al.activity_id AND al.action_type = 'Thu hoạch'
        WHERE fa.status = 'Sẵn sàng bán'
          AND (c.crop_name LIKE ? OR u.full_name LIKE ?)
    """
    cursor.execute(query, (search_term, search_term))
    rows = cursor.fetchall()
    conn.close()
    return rows

def them_vao_gio_hang(merchant_id, activity_id, quantity):
    """
    Thêm sản phẩm vào giỏ hàng, có kiểm tra tồn kho.

    Args:
        merchant_id (int): ID của thương lái.
        activity_id (int): ID của vụ mùa.
        quantity (float): Số lượng muốn thêm.

    Returns:
        bool: True nếu thành công, False nếu thất bại (hết hàng, không tìm thấy).
    """
    conn = get_connection()
    cursor = conn.cursor()
    # Kiểm tra tồn kho
    cursor.execute("""
        SELECT quantity FROM ActivityLog 
        WHERE activity_id = ? AND action_type = 'Thu hoạch'
    """, (activity_id,))
    row = cursor.fetchone()
    if not row or row[0] is None:
        print("Lỗi: Không tìm thấy thông tin thu hoạch cho vụ này!")
        conn.close()
        return False
    ton_kho = row[0]
    # Tính số lượng đã có trong giỏ
    cursor.execute("SELECT SUM(quantity) FROM Cart WHERE merchant_id = ? AND activity_id = ?", 
                   (merchant_id, activity_id))
    da_co = cursor.fetchone()[0] or 0
    if da_co + quantity > ton_kho:
        print(f"Lỗi: Chỉ còn {ton_kho} kg, bạn đã có {da_co} kg trong giỏ, không thể thêm {quantity} kg.")
        conn.close()
        return False
    # Thêm hoặc cập nhật giỏ
    cursor.execute("SELECT cart_id FROM Cart WHERE merchant_id = ? AND activity_id = ?", 
                   (merchant_id, activity_id))
    item = cursor.fetchone()
    if item:
        cursor.execute("UPDATE Cart SET quantity = quantity + ? WHERE cart_id = ?", 
                       (quantity, item[0]))
    else:
        cursor.execute("INSERT INTO Cart (merchant_id, activity_id, quantity) VALUES (?, ?, ?)", 
                       (merchant_id, activity_id, quantity))
    conn.commit()
    conn.close()
    return True

def thanh_toan_gio_hang(merchant_id, order_date):
    """
    Thanh toán toàn bộ giỏ hàng của merchant.
    Tạo đơn hàng và chi tiết đơn hàng, sau đó xóa giỏ.
    Giá lấy ưu tiên selling_price, nếu không có thì lấy base_price.

    Args:
        merchant_id (int): ID của thương lái.
        order_date (str): Ngày đặt hàng (YYYY-MM-DD).

    Returns:
        None
    """
    conn = get_connection()
    cursor = conn.cursor()
    # Lấy dữ liệu từ giỏ, ưu tiên selling_price
    cursor.execute("""
        SELECT Cart.quantity, 
               COALESCE(fa.selling_price, c.base_price) as price,
               fa.farmer_id, fa.crop_id, Cart.activity_id
        FROM Cart
        JOIN FarmingActivities fa ON Cart.activity_id = fa.activity_id
        JOIN Crops c ON fa.crop_id = c.crop_id
        WHERE Cart.merchant_id = ?
    """, (merchant_id,))
    items = cursor.fetchall()
    if not items:
        conn.close()
        return

    try:
        # Nhóm theo từng nông dân
        farmer_orders = {}
        for qty, price, f_id, c_id, act_id in items:
            if f_id not in farmer_orders:
                farmer_orders[f_id] = []
            farmer_orders[f_id].append((qty, price, c_id, act_id))

        for f_id, f_items in farmer_orders.items():
            total_amt = sum(q * p for q, p, c, a in f_items)
            cursor.execute("""
                INSERT INTO Orders (merchant_id, farmer_id, status, total_amount, order_date)
                VALUES (?, ?, 'Chờ xác nhận', ?, ?)
            """, (merchant_id, f_id, total_amt, order_date))
            order_id = cursor.lastrowid
            for q, p, c, a in f_items:
                cursor.execute("""
                    INSERT INTO OrderItems (order_id, crop_id, activity_id, quantity, unit_price)
                    VALUES (?, ?, ?, ?, ?)
                """, (order_id, c, a, q, p))

        cursor.execute("DELETE FROM Cart WHERE merchant_id = ?", (merchant_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Lỗi thanh toán: {e}")
    finally:
        conn.close()

# ================== FARMER ==================

def lay_danh_sach_don_hang_den(farmer_id):
    """
    Lấy danh sách đơn hàng mà nông dân nhận được (vai trò người bán).

    Args:
        farmer_id (int): ID của nông dân.

    Returns:
        list: Danh sách các tuple (order_id, merchant_name, total_amount, order_date, status).
    """
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

def lay_chi_tiet_don_hang(order_id):
    """
    Lấy chi tiết các mặt hàng trong một đơn hàng.

    Args:
        order_id (int): ID của đơn hàng.

    Returns:
        list: Danh sách các tuple (crop_name, quantity, unit_price, thanh_tien, plot_name).
    """
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT c.crop_name, oi.quantity, oi.unit_price, 
               (oi.quantity * oi.unit_price) as thanh_tien,
               fa.plot_name
        FROM OrderItems oi
        JOIN Crops c ON oi.crop_id = c.crop_id
        JOIN FarmingActivities fa ON oi.activity_id = fa.activity_id
        WHERE oi.order_id = ?
    """
    cursor.execute(query, (order_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def lay_items_trong_don_hang(cursor, order_id):
    """
    Hàm nội bộ: lấy danh sách (quantity, activity_id) từ OrderItems để cập nhật kho.

    Args:
        cursor (sqlite3.Cursor): Cursor đang trong transaction.
        order_id (int): ID của đơn hàng.

    Returns:
        list: Danh sách các tuple (quantity, activity_id).
    """
    cursor.execute("""
        SELECT quantity, activity_id
        FROM OrderItems
        WHERE order_id = ?
    """, (order_id,))
    return cursor.fetchall()

def cap_nhat_trang_thai_don_hang(order_id, new_status):
    """
    Cập nhật trạng thái đơn hàng và điều chỉnh tồn kho.
    Chỉ hỗ trợ 2 trạng thái: 'Xác nhận' và 'Hủy đơn'.

    Args:
        order_id (int): ID của đơn hàng.
        new_status (str): Trạng thái mới ('Xác nhận' hoặc 'Hủy đơn').

    Returns:
        None
    """
    if new_status not in ['Xác nhận', 'Hủy đơn']:
        print(f"Lỗi: Trạng thái '{new_status}' không được hỗ trợ.")
        return

    conn = get_connection()
    cursor = conn.cursor()
    try:
        items = lay_items_trong_don_hang(cursor, order_id)
        if new_status == 'Xác nhận':
            for qty, act_id in items:
                cursor.execute("""
                    UPDATE ActivityLog 
                    SET quantity = quantity - ? 
                    WHERE activity_id = ? AND action_type = 'Thu hoạch'
                """, (qty, act_id))
        elif new_status == 'Hủy đơn':
            for qty, act_id in items:
                cursor.execute("""
                    UPDATE ActivityLog 
                    SET quantity = quantity + ? 
                    WHERE activity_id = ? AND action_type = 'Thu hoạch'
                """, (qty, act_id))

        cursor.execute("UPDATE Orders SET status = ? WHERE order_id = ?", (new_status, order_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Lỗi cập nhật đơn hàng: {e}")
    finally:
        conn.close()

def dang_ban(activity_id, selling_price=None):
    """
    Đăng bán một vụ mùa đã thu hoạch.
    - Nếu có selling_price, cập nhật giá bán.
    - Chuyển trạng thái thành 'Sẵn sàng bán'.

    Args:
        activity_id (int): ID của vụ mùa.
        selling_price (float, optional): Giá bán do farmer nhập. Nếu None, giữ nguyên giá cũ.

    Returns:
        bool: True nếu thành công, False nếu thất bại.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Kiểm tra vụ mùa có tồn tại và đã thu hoạch chưa
        cursor.execute("SELECT status FROM FarmingActivities WHERE activity_id = ?", (activity_id,))
        row = cursor.fetchone()
        if not row or row[0] != 'Đã thu hoạch':
            print("Lỗi: Vụ mùa không tồn tại hoặc chưa thu hoạch.")
            return False
        
        # Cập nhật giá bán nếu được cung cấp
        if selling_price is not None:
            cursor.execute("UPDATE FarmingActivities SET selling_price = ? WHERE activity_id = ?",
                           (selling_price, activity_id))
        
        # Chuyển trạng thái thành 'Sẵn sàng bán'
        cursor.execute("UPDATE FarmingActivities SET status = 'Sẵn sàng bán' WHERE activity_id = ?",
                       (activity_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Lỗi đăng bán: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
