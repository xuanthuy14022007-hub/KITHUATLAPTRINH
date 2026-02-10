import sqlite3

def seed_data():
    conn = sqlite3.connect('nong_oi.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute("DELETE FROM OrderItems")
    cursor.execute("DELETE FROM Orders")
    cursor.execute("DELETE FROM ActivityLog")
    cursor.execute("DELETE FROM FarmingActivities")
    cursor.execute("DELETE FROM Crops")
    cursor.execute("DELETE FROM Users")

    cursor.executemany("INSERT INTO Users VALUES (?, ?, ?, ?, ?)", [
        (1, 'farmer1@gmail.com', '123', 'Farmer', 'Farmer1'),
        (2, 'merchant1@gmail.com', '123', 'Merchant', 'Merchant1')
    ])

    cursor.executemany("INSERT INTO Crops VALUES (?, ?, ?, ?)", [
        (1, 'Lúa Thơm ST25', 'Họ Hòa thảo', 18000),
        (2, 'Đậu Xanh', 'Họ Đậu', 30000),
        (3, 'Cà Chua', 'Rau màu', 22000),
        (4, 'Ngô Đồng', 'Họ Hòa thảo', 15000),
        (5, 'Khoai Lang', 'Củ quả', 20000)
    ])

    # Thêm nhiều vụ mùa để tính toán chi phí dồn tích
    cursor.executemany("INSERT INTO FarmingActivities VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [
        (101, 1, 1, 'A1', 1000, 2000000, 1500000, 3000000, 500000, '2025-10-01'),
        (102, 1, 2, 'A2', 500, 1000000, 800000, 1500000, 200000, '2025-11-15'),
        (103, 1, 3, 'B1', 300, 500000, 400000, 1000000, 100000, '2026-01-10'),
        (104, 1, 4, 'B2', 800, 1500000, 1200000, 2000000, 300000, '2026-02-05')
    ])

    # Thêm các mốc nhật ký để demo luồng thời gian
    cursor.executemany("INSERT INTO ActivityLog VALUES (?, ?, ?, ?, ?, ?, ?)", [
        (1, 101, 'A1', 'Gieo hạt', 0, '2025-10-02', 'Đất đủ ẩm'),
        (2, 101, 'A1', 'Bón phân', 0, '2025-11-10', 'Cây xanh tốt'),
        (3, 101, 'A1', 'Thu hoạch', 1500, '2026-01-20', 'Đất bạc màu'),
        (4, 102, 'A2', 'Thu hoạch', 600, '2026-02-01', 'Đất cần nghỉ'),
        (5, 103, 'B1', 'Gieo hạt', 0, '2026-01-12', 'Đất tốt'),
        (6, 104, 'B2', 'Gieo hạt', 0, '2026-02-06', 'Đất bình thường')
    ])

    # Thêm đơn hàng rải rác các tháng để vẽ biểu đồ cột
    cursor.executemany("INSERT INTO Orders VALUES (?, ?, ?, ?, ?, ?)", [
        (501, 2, 1, 'Hoàn thành', 27000000, '2026-01-25'), # Doanh thu tháng 1
        (502, 2, 1, 'Hoàn thành', 18000000, '2026-02-02'), # Doanh thu tháng 2
        (503, 2, 1, 'Chờ xác nhận', 4500000, '2026-02-09'), 
        (504, 2, 1, 'Hoàn thành', 12000000, '2025-12-15')  # Doanh thu tháng 12 năm trước
    ])

    # Thêm chi tiết đơn hàng để vẽ biểu đồ tròn (Tỷ lệ các loại cây đã bán)
    cursor.executemany("INSERT INTO OrderItems VALUES (?, ?, ?, ?, ?)", [
        (1, 501, 1, 1500, 18000),
        (2, 502, 2, 600, 30000),
        (3, 503, 3, 150, 30000),
        (4, 504, 4, 800, 15000)
    ])

    conn.commit()
    conn.close()

if __name__ == "__main__":
    seed_data()
