import sqlite3

def seed_data():
    conn = sqlite3.connect('nong_oi.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")


    try:
        cursor.execute("ALTER TABLE Users ADD COLUMN address TEXT")
    except sqlite3.OperationalError:
        pass # Nếu có rồi thì bỏ qua


    tables = ['OrderItems', 'Orders', 'ActivityLog', 'FarmingActivities', 'Crops', 'Users', 'Cart', 'CostCart']
    for table in tables:
        cursor.execute(f"DELETE FROM {table}")

    # --- 1. USERS ---
    users = [
        (1, 'farmer1', '123', 'Farmer', 'Nguyễn Văn Ruộng', 'farmer1@gmail.com', 'Thôn 1, Tỉnh C'),
        (2, 'merchant1', '123', 'Merchant', 'Trần Thị Chợ', 'merchant1@gmail.com', 'Quận Z, TP. Hồ Chí Minh')
    ]
    cursor.executemany("INSERT INTO Users (user_id, username, password, role, full_name, email, address) VALUES (?,?,?,?,?,?,?)", users)

    # --- 2. CROPS ---
    crops = [
        (1, 'Lúa Thơm ST25', 'Họ Hòa thảo', 18000),
        (2, 'Đậu Xanh', 'Họ Đậu', 30000),
        (3, 'Cà Chua Bi', 'Rau màu', 22000),
        (4, 'Khoai Tây', 'Củ quả', 15000),
        (5, 'Rau Má', 'Rau', 10000)
    ]
    cursor.executemany("INSERT INTO Crops (crop_id, crop_name, category, base_price) VALUES (?,?,?,?)", crops)

    # --- 3. FARMING ACTIVITIES ---
    activities = [
        (101, 1, 1, 'A1', 1000, '2025-10-01', 'Sẵn sàng bán'),
        (102, 1, 2, 'A2', 500, '2025-11-15', 'Sẵn sàng bán'),
        (103, 1, 3, 'B1', 300, '2026-01-10', 'Đang trồng'),
    ]
    cursor.executemany("INSERT INTO FarmingActivities (activity_id, farmer_id, crop_id, farm_name, area, start_date, status) VALUES (?,?,?,?,?,?,?)", activities)

    # --- 4. ORDERS (Doanh thu: 108 Triệu) ---
    orders = [
        (501, 2, 1, 'Hoàn thành', 70000000, '2026-02-25'),
        (502, 2, 1, 'Hoàn thành', 38000000, '2026-03-02'),
    ]
    cursor.executemany("INSERT INTO Orders (order_id, merchant_id, farmer_id, status, total_amount, order_date) VALUES (?,?,?,?,?,?)", orders)

    # --- 5. ORDER ITEMS (Dữ liệu để vẽ biểu đồ Tỉ lệ đơn hàng) ---
    order_items = [
        (1, 501, 3, 101, 50, 22000), # Cà chua bi
        (2, 501, 5, 102, 100, 10000), # Rau má
        (3, 502, 4, 101, 80, 15000), # Khoai tây
    ]
    cursor.executemany("INSERT INTO OrderItems (item_id, order_id, crop_id, activity_id, quantity, unit_price) VALUES (?,?,?,?,?,?)", order_items)

    # --- 6. COST CART (Dữ liệu để vẽ biểu đồ Cơ cấu chi phí - Giống ảnh Dashboard) ---
    # Tổng chi phí: 36.000.000 (Lợi nhuận sẽ là 108M - 36M = 72M)
    costs = [
        (1, 1, 'Phân bón', 10000000),
        (2, 1, 'Nhân công', 9000000),
        (3, 1, 'Hạt giống', 3000000),
        (4, 1, 'Chi phí khác', 2000000)
    ]
    # Chỉ chèn các cột cần thiết,created_at tự động
    cursor.executemany("INSERT INTO CostCart (id, farmer_id, cost_type, amount) VALUES (?,?,?,?)", costs)

    conn.commit()
    conn.close()
    print(">>> Dữ liệu mẫu 'Nông Ơi!' chuẩn Dashboard đã sẵn sàng.")

if __name__ == "__main__":
    seed_data()