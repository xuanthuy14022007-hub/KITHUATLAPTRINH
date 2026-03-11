import sqlite3
from database_connector import get_connection

def init_db():
    """
    Khởi tạo cơ sở dữ liệu: tạo tất cả các bảng với ràng buộc và khóa ngoại.
    Các bảng: Users, Crops, FarmingActivities, ActivityLog, Orders, OrderItems, Cart, CostCart.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # 1. BẢNG NGƯỜI DÙNG
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('Farmer', 'Merchant')),        
        full_name TEXT,
        email TEXT UNIQUE, 
        address TEXT,
        farm_name TEXT,
        description TEXT
    )''')

    # 2. BẢNG DANH MỤC CÂY TRỒNG
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Crops (
        crop_id INTEGER PRIMARY KEY AUTOINCREMENT,
        crop_name TEXT NOT NULL,
        category TEXT,
        base_price REAL DEFAULT 0 CHECK (base_price >= 0)
    )''')

    # 3. BẢNG VỤ MÙA
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS FarmingActivities (
        activity_id INTEGER PRIMARY KEY AUTOINCREMENT,
        farmer_id INTEGER NOT NULL,
        crop_id INTEGER NOT NULL,
        plot_name TEXT NOT NULL,
        area REAL NOT NULL CHECK (area > 0),
        start_date TEXT NOT NULL,
        selling_price REAL DEFAULT NULL CHECK (selling_price >= 0),
        status TEXT DEFAULT 'Đang trồng' CHECK(status IN ('Đang trồng', 'Sẵn sàng bán', 'Đã thu hoạch')),
        FOREIGN KEY(farmer_id) REFERENCES Users(user_id) ON DELETE CASCADE,
        FOREIGN KEY(crop_id) REFERENCES Crops(crop_id) ON DELETE RESTRICT
    )''')

    # 4. BẢNG NHẬT KÝ KỸ THUẬT
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ActivityLog (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        activity_id INTEGER NOT NULL,
        plot_name TEXT NOT NULL,
        action_type TEXT NOT NULL CHECK(action_type IN ('Gieo hạt', 'Bón phân', 'Tưới nước', 'Thu hoạch', 'Khác')),
        quantity REAL DEFAULT 0,
        log_date TEXT NOT NULL,
        soil_status TEXT,
        FOREIGN KEY(activity_id) REFERENCES FarmingActivities(activity_id) ON DELETE CASCADE
    )''')

    # 5. BẢNG ĐƠN HÀNG
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        merchant_id INTEGER NOT NULL,
        farmer_id INTEGER NOT NULL,
        status TEXT DEFAULT 'Chờ xác nhận' CHECK(status IN ('Chờ xác nhận', 'Xác nhận', 'Hủy đơn')),
        total_amount REAL DEFAULT 0 CHECK (total_amount >= 0),
        order_date TEXT NOT NULL,
        FOREIGN KEY(merchant_id) REFERENCES Users(user_id) ON DELETE CASCADE,
        FOREIGN KEY(farmer_id) REFERENCES Users(user_id) ON DELETE CASCADE
    )''')

    # 6. BẢNG CHI TIẾT ĐƠN HÀNG
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS OrderItems (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        crop_id INTEGER NOT NULL,
        activity_id INTEGER NOT NULL,
        quantity REAL NOT NULL CHECK (quantity > 0),
        unit_price REAL NOT NULL CHECK (unit_price >= 0),
        FOREIGN KEY(order_id) REFERENCES Orders(order_id) ON DELETE CASCADE,
        FOREIGN KEY(crop_id) REFERENCES Crops(crop_id) ON DELETE RESTRICT,
        FOREIGN KEY(activity_id) REFERENCES FarmingActivities(activity_id) ON DELETE RESTRICT
    )''')

    # 7. BẢNG GIỎ HÀNG
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Cart (
        cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
        merchant_id INTEGER NOT NULL,
        activity_id INTEGER NOT NULL,
        quantity REAL NOT NULL CHECK (quantity > 0),
        FOREIGN KEY(merchant_id) REFERENCES Users(user_id) ON DELETE CASCADE,
        FOREIGN KEY(activity_id) REFERENCES FarmingActivities(activity_id) ON DELETE CASCADE
    )''')

    # 8. BẢNG CHI PHÍ
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS CostCart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farmer_id INTEGER NOT NULL,
        cost_type TEXT NOT NULL CHECK(cost_type IN ('Hạt giống', 'Phân bón', 'Nhân công', 'Chi phí khác')),
        amount REAL NOT NULL CHECK (amount >= 0),
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(farmer_id) REFERENCES Users(user_id) ON DELETE CASCADE
    )''')

    conn.commit()
    conn.close()
    print(">>> Hệ thống Database Nông Ơi! đã sẵn sàng.")

if __name__ == "__main__":
    init_db()
