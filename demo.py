import sqlite3

def seed_data():
    conn = sqlite3.connect('nong_oi.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Xóa dữ liệu cũ
    cursor.execute("DELETE FROM OrderItems")
    cursor.execute("DELETE FROM Orders")
    cursor.execute("DELETE FROM ActivityLog")
    cursor.execute("DELETE FROM FarmingActivities")
    cursor.execute("DELETE FROM Crops")
    cursor.execute("DELETE FROM Users")

    # --- USERS: thêm cột address ---
    cursor.executemany("INSERT INTO Users VALUES (?, ?, ?, ?, ?, ?, ?)", [
        (1, 'farmer1', '123', 'Farmer', 'Nguyễn Văn Ruộng', 'farmer1@gmail.com', 'Thôn 1, Xã A, Huyện B, Tỉnh C'),
        (2, 'merchant1', '123', 'Merchant', 'Trần Thị Chợ', 'merchant1@gmail.com', 'Số 123, Đường X, Phường Y, Quận Z, Thành phố H')
    ])

    # --- CROPS ---
    cursor.executemany("INSERT INTO Crops VALUES (?, ?, ?, ?)", [
        (1, 'Lúa Thơm ST25', 'Họ Hòa thảo', 18000),
        (2, 'Đậu Xanh', 'Họ Đậu', 30000),
        (3, 'Cà Chua', 'Rau màu', 22000),
        (4, 'Ngô Đồng', 'Họ Hòa thảo', 15000),
        (5, 'Khoai Lang', 'Củ quả', 20000)
    ])

    # --- FARMING ACTIVITIES ---
    cursor.executemany("INSERT INTO FarmingActivities VALUES (?, ?, ?, ?, ?, ?, ?)", [
        (101, 1, 1, 'A1', 1000, '2025-10-01', 'Sẵn sàng bán'),
        (102, 1, 2, 'A2', 500, '2025-11-15', 'Sẵn sàng bán'),
        (103, 1, 3, 'B1', 300, '2026-01-10', 'Đang trồng'),
        (104, 1, 4, 'B2', 800, '2026-02-05', 'Đang trồng')
    ])

    # --- ACTIVITY LOG ---
    cursor.executemany("INSERT INTO ActivityLog VALUES (?, ?, ?, ?, ?, ?, ?)", [
        (1, 101, 'A1', 'Gieo hạt', 0, '2025-10-02', 'Đất đủ ẩm'),
        (2, 101, 'A1', 'Bón phân', 0, '2025-11-10', 'Cây xanh tốt'),
        (3, 101, 'A1', 'Thu hoạch', 1500, '2026-01-20', 'Đất bạc màu'),
        (4, 102, 'A2', 'Thu hoạch', 600, '2026-02-01', 'Đất cần nghỉ'),
        (5, 103, 'B1', 'Gieo hạt', 0, '2026-01-12', 'Đất tốt'),
        (6, 104, 'B2', 'Gieo hạt', 0, '2026-02-06', 'Đất bình thường')
    ])

    # --- ORDERS ---
    cursor.executemany("INSERT INTO Orders VALUES (?, ?, ?, ?, ?, ?)", [
        (501, 2, 1, 'Hoàn thành', 27000000, '2026-01-25'),
        (502, 2, 1, 'Hoàn thành', 18000000, '2026-02-02'),
    ])

    # --- ORDER ITEMS ---
    cursor.executemany("INSERT INTO OrderItems VALUES (?, ?, ?, ?, ?, ?)", [
        (1, 501, 1, 101, 1500, 18000),
        (2, 502, 2, 102, 600, 30000),
    ])

    conn.commit()
    conn.close()
    print(">>> Dữ liệu mẫu Nông Ơi! đã được nạp thành công.")

if __name__ == "__main__":
    seed_data()
