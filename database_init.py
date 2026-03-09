import sqlite3

def init_db():
    conn = sqlite3.connect('nong_oi.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. BẢNG NGƯỜI DÙNG
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,        
        full_name TEXT,
        email TEXT UNIQUE, 
        address TEXT
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
        farmer_id INTEGER,
        crop_id INTEGER,
        farm_name TEXT,
        area REAL CHECK (area > 0),
        start_date TEXT,
        status TEXT DEFAULT 'Đang trồng',
        FOREIGN KEY(farmer_id) REFERENCES Users(user_id),
        FOREIGN KEY(crop_id) REFERENCES Crops(crop_id)
    )''')

    # 4. NHẬT KÝ KỸ CHĂM SÓC
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ActivityLog (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        activity_id INTEGER,
        farm_name TEXT,
        action_type TEXT,
        quantity REAL DEFAULT 0,
        log_date TEXT,
        soil_status TEXT,
        FOREIGN KEY(activity_id) REFERENCES FarmingActivities(activity_id)
    )''')

    # 5. ĐƠN HÀNG
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        merchant_id INTEGER,
        farmer_id INTEGER,
        status TEXT DEFAULT 'Chờ xác nhận',
        total_amount REAL DEFAULT 0 CHECK (total_amount >= 0),
        order_date TEXT,
        FOREIGN KEY(merchant_id) REFERENCES Users(user_id),
        FOREIGN KEY(farmer_id) REFERENCES Users(user_id)
    )''')

    # 6. CHI TIẾT ĐƠN HÀNG
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS OrderItems (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        crop_id INTEGER,
        activity_id INTEGER,
        quantity REAL CHECK (quantity > 0),
        unit_price REAL CHECK (unit_price >= 0),
        FOREIGN KEY(order_id) REFERENCES Orders(order_id),
        FOREIGN KEY(crop_id) REFERENCES Crops(crop_id),
        FOREIGN KEY(activity_id) REFERENCES FarmingActivities(activity_id)
    )''')

    # 7. GIỎ HÀNG
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Cart (
        cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
        merchant_id INTEGER,
        activity_id INTEGER,
        quantity REAL CHECK (quantity > 0),
        FOREIGN KEY(merchant_id) REFERENCES Users(user_id),
        FOREIGN KEY(activity_id) REFERENCES FarmingActivities(activity_id)
    )''')

    # 8. CHI PHÍ 
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS CostCart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farmer_id INTEGER,
        cost_type TEXT, 
        amount REAL CHECK (amount >= 0),
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(farmer_id) REFERENCES Users(user_id)
    )''')

    conn.commit()
    conn.close()
    print(">>> Hệ thống Database Nông Ơi! đã sẵn sàng.")

if __name__ == "__main__":

    init_db()
