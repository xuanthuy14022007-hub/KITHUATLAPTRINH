from database_connector import get_connection
import sqlite3

# ================== MERCHANT ==================

def lay_danh_sach_nong_san(tu_khoa=""):
    """
    Hàm tìm kiếm và lấy danh sách nông sản đang sẵn sàng bán.
    Nếu có từ khóa, tìm theo tên cây trồng hoặc tên người bán.
    """
    conn = get_connection()          # Mở kết nối database
    cursor = conn.cursor()           # Tạo con trỏ để thực thi SQL
    search_term = f"%{tu_khoa}%"      # Thêm ký tự đại diện % để tìm kiếm LIKE

    # Truy vấn: lấy thông tin vụ mùa (activity_id), tên người bán, tên cây,
    # số lượng thu hoạch (từ ActivityLog), giá cơ bản, tên thửa đất
    # Điều kiện: vụ mùa có trạng thái 'Sẵn sàng bán' và có lần thu hoạch
    query = """
        SELECT fa.activity_id, u.full_name, c.crop_name, 
               al.quantity, c.base_price, fa.farm_name
        FROM FarmingActivities fa
        JOIN Users u ON fa.farmer_id = u.user_id
        JOIN Crops c ON fa.crop_id = c.crop_id
        LEFT JOIN ActivityLog al ON fa.activity_id = al.activity_id AND al.action_type = 'Thu hoạch'
        WHERE fa.status = 'Sẵn sàng bán'
          AND (c.crop_name LIKE ? OR u.full_name LIKE ?)
    """
    cursor.execute(query, (search_term, search_term))  # Thực thi với tham số tìm kiếm
    rows = cursor.fetchall()          # Lấy tất cả kết quả trả về
    conn.close()                      # Đóng kết nối
    return rows                       # Trả về danh sách tuple

def them_vao_gio_hang(merchant_id, activity_id, quantity):
    """
    Thêm sản phẩm vào giỏ hàng của merchant.
    Nếu sản phẩm (activity_id) đã có trong giỏ, cộng dồn số lượng.
    """
    conn = get_connection()
    cursor = conn.cursor()
    # Kiểm tra xem activity_id đã tồn tại trong giỏ của merchant chưa
    cursor.execute("SELECT cart_id, quantity FROM Cart WHERE merchant_id = ? AND activity_id = ?", 
                   (merchant_id, activity_id))
    item = cursor.fetchone()
    if item:
        # Nếu có, cập nhật tăng số lượng
        cursor.execute("UPDATE Cart SET quantity = quantity + ? WHERE cart_id = ?", 
                       (quantity, item[0]))
    else:
        # Nếu chưa, thêm mới vào giỏ
        cursor.execute("INSERT INTO Cart (merchant_id, activity_id, quantity) VALUES (?, ?, ?)", 
                       (merchant_id, activity_id, quantity))
    conn.commit()   # Lưu thay đổi
    conn.close()    # Đóng kết nối

def thanh_toan_gio_hang(merchant_id, order_date):
    """
    Thanh toán toàn bộ giỏ hàng của merchant.
    Tạo đơn hàng (Orders) và chi tiết đơn hàng (OrderItems) cho từng nông dân.
    Lưu activity_id vào OrderItems để quản lý kho chính xác.
    Xóa toàn bộ giỏ hàng sau khi thanh toán.
    """
    conn = get_connection()
    cursor = conn.cursor()
    # Lấy tất cả mặt hàng trong giỏ của merchant, kèm theo giá và thông tin nông dân
    cursor.execute("""
        SELECT Cart.quantity, Crops.base_price, FarmingActivities.farmer_id, 
               FarmingActivities.crop_id, Cart.activity_id
        FROM Cart
        JOIN FarmingActivities ON Cart.activity_id = FarmingActivities.activity_id
        JOIN Crops ON FarmingActivities.crop_id = Crops.crop_id
        WHERE Cart.merchant_id = ?
    """, (merchant_id,))
    items = cursor.fetchall()
    if not items:          # Giỏ hàng trống thì thoát
        conn.close()
        return

    try:
        # Nhóm các mặt hàng theo từng nông dân
        farmer_orders = {}
        for qty, price, f_id, c_id, act_id in items:
            if f_id not in farmer_orders:
                farmer_orders[f_id] = []
            farmer_orders[f_id].append((qty, price, c_id, act_id))

        # Với mỗi nông dân, tạo một đơn hàng riêng
        for f_id, f_items in farmer_orders.items():
            total_amt = sum(q * p for q, p, c, a in f_items)   # Tính tổng tiền
            cursor.execute("""
                INSERT INTO Orders (merchant_id, farmer_id, status, total_amount, order_date)
                VALUES (?, ?, 'Chờ xác nhận', ?, ?)
            """, (merchant_id, f_id, total_amt, order_date))
            order_id = cursor.lastrowid   # Lấy ID của đơn hàng vừa tạo

            # Thêm từng mặt hàng vào bảng OrderItems
            for q, p, c, a in f_items:
                cursor.execute("""
                    INSERT INTO OrderItems (order_id, crop_id, activity_id, quantity, unit_price)
                    VALUES (?, ?, ?, ?, ?)
                """, (order_id, c, a, q, p))

        # Xóa toàn bộ giỏ hàng sau khi đã thanh toán
        cursor.execute("DELETE FROM Cart WHERE merchant_id = ?", (merchant_id,))
        conn.commit()      # Xác nhận tất cả các thay đổi
    except Exception as e:
        conn.rollback()    # Có lỗi thì hoàn tác
        print(f"Lỗi thanh toán: {e}")
    finally:
        conn.close()       # Đóng kết nối

# ================== FARMER ==================

def lay_danh_sach_don_hang_den(farmer_id):
    """
    Lấy danh sách các đơn hàng mà nông dân (farmer_id) nhận được từ các thương lái.
    Sắp xếp theo ngày đặt hàng giảm dần (mới nhất lên đầu).
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
    Lấy chi tiết các mặt hàng trong một đơn hàng cụ thể.
    Input: order_id (int) - ID của đơn hàng cần xem.
    Output: Danh sách các tuple, mỗi tuple chứa:
        (crop_name, quantity, unit_price, thanh_tien, farm_name)
    """
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT c.crop_name, oi.quantity, oi.unit_price, 
               (oi.quantity * oi.unit_price) as thanh_tien,
               fa.farm_name
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
    Lấy danh sách các mặt hàng (gồm số lượng và activity_id) thuộc một đơn hàng.
    Dùng để cập nhật tồn kho khi xác nhận hoặc hủy đơn.
    """
    cursor.execute("""
        SELECT quantity, activity_id
        FROM OrderItems
        WHERE order_id = ?
    """, (order_id,))
    return cursor.fetchall()

def cap_nhat_trang_thai_don_hang(order_id, new_status):
    """
    Cập nhật trạng thái đơn hàng và điều chỉnh tồn kho tương ứng.
    - Nếu xác nhận: trừ số lượng đã bán khỏi ActivityLog.
    - Nếu hủy: cộng lại số lượng vào ActivityLog (hoàn kho).
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if new_status == 'Xác nhận':
            # Lấy danh sách các mặt hàng cần trừ
            items = lay_items_trong_don_hang(cursor, order_id)
            for qty, act_id in items:
                # Trừ số lượng bán ra khỏi lần thu hoạch tương ứng
                cursor.execute("""
                    UPDATE ActivityLog 
                    SET quantity = quantity - ? 
                    WHERE activity_id = ? AND action_type = 'Thu hoạch'
                """, (qty, act_id))

        elif new_status == 'Huỷ đơn':
            # Lấy danh sách các mặt hàng cần hoàn lại
            items = lay_items_trong_don_hang(cursor, order_id)
            for qty, act_id in items:
                # Cộng lại số lượng đã bán (hoàn kho)
                cursor.execute("""
                    UPDATE ActivityLog 
                    SET quantity = quantity + ? 
                    WHERE activity_id = ? AND action_type = 'Thu hoạch'
                """, (qty, act_id))

        # Cập nhật trạng thái đơn hàng
        cursor.execute("UPDATE Orders SET status = ? WHERE order_id = ?", (new_status, order_id))
        conn.commit()   # Lưu thay đổi
    except Exception as e:
        conn.rollback() # Hoàn tác nếu lỗi
        print(f"Lỗi: {e}")
    finally:
        conn.close()    # Đóng kết nối
