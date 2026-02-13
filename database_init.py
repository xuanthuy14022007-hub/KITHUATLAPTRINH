import sqlite3

def init_db():
    """
    Hàm khởi tạo cơ sở dữ liệu cho dự án Nông Ơi!
    Thủy có thể chạy độc lập file này để tạo file .db trước
    hoặc import vào main.py để khởi tạo khi mở app.
    """
    # Kết nối đến file database (Tự động tạo nếu chưa có)
    conn = sqlite3.connect('nong_oi.db')
    cursor = conn.cursor()

    # Kích hoạt tính năng khóa ngoại (Bắt buộc trong SQLite để liên kết các bảng)
    cursor.execute("PRAGMA foreign_keys = ON;")

    # --- 1. BẢNG NGƯỜI DÙNG ---
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,        
        full_name TEXT,
        email TEXT UNIQUE
    )''')

    # --- 2. BẢNG DANH MỤC CÂY TRỒNG ---
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Crops (
        crop_id INTEGER PRIMARY KEY AUTOINCREMENT,
        crop_name TEXT NOT NULL,
        category TEXT,             -- Dùng để gợi ý Luân canh
        base_price REAL DEFAULT 0
    )''')

    # --- 3. BẢNG VỤ MÙA & CHI PHÍ ---
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS FarmingActivities (
        activity_id INTEGER PRIMARY KEY AUTOINCREMENT,
        farmer_id INTEGER,
        crop_id INTEGER,
        farm_name TEXT,            -- Tên thửa đất người dùng tự đặt
        area REAL,                 -- Diện tích trồng (m2)
        start_date TEXT,           -- Ngày bắt đầu vụ (YYYY-MM-DD)
        status TEXT DEFAULT 'Đang trồng', -- Dấu hiệu quản lý vòng đời
        FOREIGN KEY(farmer_id) REFERENCES Users(user_id),
        FOREIGN KEY(crop_id) REFERENCES Crops(crop_id)
    )''')

    # --- 4. BẢNG NHẬT KÝ KỸ THUẬT ---
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ActivityLog (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        activity_id INTEGER,       -- Liên kết với vụ mùa đang chọn
        farm_name TEXT,            -- Tên thửa đất để dễ truy vấn
        action_type TEXT,          -- Gieo hạt, Bón phân, Thu hoạch...
        quantity REAL DEFAULT 0,   -- Sản lượng thực tế (chỉ dùng khi thu hoạch)
        log_date TEXT,             -- Thời gian thực hiện
        soil_status TEXT,          -- Ghi chú tình trạng đất
        FOREIGN KEY(activity_id) REFERENCES FarmingActivities(activity_id)
    )''')

    # --- 5. BẢNG ĐƠN HÀNG ---
    # Dùng để tính doanh thu cho mục Phân tích báo cáo
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        merchant_id INTEGER,
        farmer_id INTEGER,
        status TEXT DEFAULT 'Chờ xác nhận',
        total_amount REAL DEFAULT 0,
        order_date TEXT,           -- Dùng để vẽ biểu đồ theo tháng
        FOREIGN KEY(merchant_id) REFERENCES Users(user_id),
        FOREIGN KEY(farmer_id) REFERENCES Users(user_id)
    )''')

    # --- 6. BẢNG CHI TIẾT ĐƠN HÀNG ---
    # Dùng để vẽ biểu đồ tròn tỷ lệ các loại nông sản bán chạy
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS OrderItems (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        crop_id INTEGER,
        quantity REAL,
        unit_price REAL,
        FOREIGN KEY(order_id) REFERENCES Orders(order_id),
        FOREIGN KEY(crop_id) REFERENCES Crops(crop_id)
    )''')
    # --- 7. BẢNG GIỎ HÀNG (BỘ NHỚ TẠM) ---
cursor.execute('''
CREATE TABLE IF NOT EXISTS Cart (
    cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
    merchant_id INTEGER,
    activity_id INTEGER, -- Liên kết trực tiếp tới vụ mùa đang bán
    quantity REAL,
    FOREIGN KEY(merchant_id) REFERENCES Users(user_id),
    FOREIGN KEY(activity_id) REFERENCES FarmingActivities(activity_id)
)''')
    # --- 8. BẢNG CHI PHÍ (BỘ NHỚ TẠM) ---
cursor.excecute('''
CREATE TABLE CostCart (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id INTEGER,
    cost_type TEXT,    -- Sẽ lưu 1 trong 4 loại: 'Hạt giống', 'Phân bón', 'Nhân công', 'Chi phí khác'
    amount REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')

    # Lưu thay đổi và đóng kết nối
    conn.commit()
    conn.close()
    print(">>> Hệ thống Database Nông Ơi! đã sẵn sàng.")

# Cho phép chạy file này độc lập để kiểm tra
if __name__ == "__main__":
    init_db()
