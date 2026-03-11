"""
Tạo dữ liệu mẫu cho cơ sở dữ liệu Nông Ơi! với 1 farmer và 1 merchant.
Dữ liệu bao gồm: users, crops, farming activities, activity logs, orders, order items.
Bảng CostCart để trống để người dùng tự nhập khi demo.
"""

import sqlite3

def seed_data():
    conn = sqlite3.connect('nong_oi.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Xóa dữ liệu cũ
    cursor.execute("DELETE FROM OrderItems")
    cursor.execute("DELETE FROM Orders")
    cursor.execute("DELETE FROM Cart")
    cursor.execute("DELETE FROM CostCart")
    cursor.execute("DELETE FROM ActivityLog")
    cursor.execute("DELETE FROM FarmingActivities")
    cursor.execute("DELETE FROM Crops")
    cursor.execute("DELETE FROM Users")

    # ==================== USERS ====================
    users = [
        (1, 'farmer1', '123', 'Farmer', 'Nguyễn Văn A', 'farmer1@gmail.com',
         'Thôn 1, Xã B, Huyện C, Tỉnh D', 'Trại Nông Sản Xanh',
         'Chuyên canh lúa, rau củ quả sạch theo tiêu chuẩn VietGAP'),
        (2, 'merchant1', '123', 'Merchant', 'Trần Văn C', 'merchant1@gmail.com',
         'Số 10, Đường Lê Lợi, Phường 1, Quận 2, TP. HCM', 'Vựa Nông Sản Miền Tây',
         'Thu mua sỉ và lẻ các loại nông sản từ các tỉnh')
    ]
    cursor.executemany(
        "INSERT INTO Users (user_id, username, password, role, full_name, email, address, farm_name, description) VALUES (?,?,?,?,?,?,?,?,?)",
        users
    )

    # ==================== CROPS ====================
    crops = [
        (1, 'Lúa ST25', 'Lúa', 18000),
        (2, 'Lúa Nàng Hương', 'Lúa', 17000),
        (3, 'Đậu Xanh', 'Đậu', 30000),
        (4, 'Đậu Đen', 'Đậu', 28000),
        (5, 'Đậu Nành', 'Đậu', 25000),
        (6, 'Cà Chua Bi', 'Rau màu', 22000),
        (7, 'Cà Chua Beef', 'Rau màu', 25000),
        (8, 'Ớt Chuông', 'Rau màu', 35000),
        (9, 'Ớt Chỉ Thiên', 'Gia vị', 40000),
        (10, 'Bắp Cải', 'Rau', 14000),
        (11, 'Súp Lơ', 'Rau', 20000),
        (12, 'Cải Thìa', 'Rau', 12000),
        (13, 'Cải Ngọt', 'Rau', 13000),
        (14, 'Khoai Lang', 'Củ', 20000),
        (15, 'Khoai Tây', 'Củ', 22000),
        (16, 'Khoai Môn', 'Củ', 25000),
        (17, 'Ngô Ngọt', 'Ngũ cốc', 15000),
        (18, 'Ngô Nếp', 'Ngũ cốc', 18000),
        (19, 'Đậu Phộng', 'Đậu', 27000),
        (20, 'Mè', 'Gia vị', 50000)
    ]
    cursor.executemany(
        "INSERT INTO Crops (crop_id, crop_name, category, base_price) VALUES (?,?,?,?)",
        crops
    )

    # ==================== FARMING ACTIVITIES ====================
    activities = [
        (101, 1, 1, 'A1', 1000, '2025-10-01', 19000, 'Sẵn sàng bán'),
        (102, 1, 3, 'A2', 500, '2025-11-15', 32000, 'Sẵn sàng bán'),
        (103, 1, 6, 'B1', 300, '2026-01-10', 23000, 'Sẵn sàng bán'),
        (104, 1, 10, 'B2', 800, '2026-02-05', None, 'Đã thu hoạch'),
        (105, 1, 14, 'C1', 400, '2026-03-01', None, 'Đã thu hoạch'),
        (106, 1, 8, 'C2', 200, '2026-04-01', None, 'Đang trồng'),
        (107, 1, 12, 'D1', 150, '2026-04-10', None, 'Đang trồng')
    ]
    cursor.executemany(
        "INSERT INTO FarmingActivities (activity_id, farmer_id, crop_id, plot_name, area, start_date, selling_price, status) VALUES (?,?,?,?,?,?,?,?)",
        activities
    )

    # ==================== ACTIVITY LOG ====================
    logs = [
        (1, 101, 'A1', 'Gieo hạt', 0, '2025-10-02', 'Đất đủ ẩm'),
        (2, 101, 'A1', 'Bón phân', 0, '2025-11-10', 'Cây xanh tốt'),
        (3, 101, 'A1', 'Thu hoạch', 1500, '2026-01-20', 'Đất bạc màu'),
        (4, 102, 'A2', 'Gieo hạt', 0, '2025-11-16', 'Đất tốt'),
        (5, 102, 'A2', 'Bón phân', 0, '2025-12-20', 'Phát triển tốt'),
        (6, 102, 'A2', 'Thu hoạch', 600, '2026-02-01', 'Đất cần nghỉ'),
        (7, 103, 'B1', 'Gieo hạt', 0, '2026-01-12', 'Đất ẩm'),
        (8, 103, 'B1', 'Thu hoạch', 280, '2026-04-10', 'Thu hoạch sớm'),
        (9, 104, 'B2', 'Gieo hạt', 0, '2026-02-06', 'Đất bình thường'),
        (10, 104, 'B2', 'Thu hoạch', 750, '2026-05-20', 'Đất ổn'),
        (11, 105, 'C1', 'Gieo hạt', 0, '2026-03-02', 'Đất ẩm'),
        (12, 105, 'C1', 'Thu hoạch', 380, '2026-06-10', 'Đất tốt'),
        (13, 106, 'C2', 'Gieo hạt', 0, '2026-04-02', 'Đất tốt'),
        (14, 107, 'D1', 'Gieo hạt', 0, '2026-04-11', 'Đất ẩm')
    ]
    cursor.executemany(
        "INSERT INTO ActivityLog (log_id, activity_id, plot_name, action_type, quantity, log_date, soil_status) VALUES (?,?,?,?,?,?,?)",
        logs
    )

    # ==================== ORDERS ====================
    orders = [
        (501, 2, 1, 'Xác nhận', 28500000, '2026-01-25'),
        (502, 2, 1, 'Xác nhận', 19200000, '2026-02-02'),
        (503, 2, 1, 'Xác nhận', 6440000, '2026-04-15'),
        (504, 2, 1, 'Xác nhận', 10500000, '2026-05-25'),
        (505, 2, 1, 'Xác nhận', 7600000, '2026-06-15'),
        # Sửa đơn 506: dùng activity_id = 104 (vụ đã thu hoạch, còn hàng)
        (506, 2, 1, 'Chờ xác nhận', 10500000, '2026-07-01')  # 750kg * 14000 = 10.500.000
    ]
    cursor.executemany(
        "INSERT INTO Orders (order_id, merchant_id, farmer_id, status, total_amount, order_date) VALUES (?,?,?,?,?,?)",
        orders
    )

    # ==================== ORDER ITEMS ====================
    order_items = [
        (1, 501, 1, 101, 1500, 19000),
        (2, 502, 3, 102, 600, 32000),
        (3, 503, 6, 103, 280, 23000),
        (4, 504, 10, 104, 750, 14000),   # vụ 104 bán 750kg (giá base)
        (5, 505, 14, 105, 380, 20000),    # vụ 105 bán 380kg
        (6, 506, 10, 104, 750, 14000)     # đơn 506 cũng mua 750kg vụ 104 (chờ xác nhận)
    ]
    cursor.executemany(
        "INSERT INTO OrderItems (item_id, order_id, crop_id, activity_id, quantity, unit_price) VALUES (?,?,?,?,?,?)",
        order_items
    )

    # ==================== COST CART ====================
    # KHÔNG INSERT DỮ LIỆU, để trống

    conn.commit()
    conn.close()
    print(">>> Dữ liệu mẫu Nông Ơi! đã được nạp thành công (1 farmer, 1 merchant).")
    print("   - Tổng số users: 2")
    print("   - Tổng số crops: 20")
    print("   - Tổng số vụ mùa: 7")
    print("   - Tổng số nhật ký: 14")
    print("   - Tổng số đơn hàng: 6")
    print("   - Tổng số chi tiết đơn: 6")
    print("   - Bảng CostCart để trống (sẽ nhập khi demo).")

if __name__ == "__main__":
    seed_data()
