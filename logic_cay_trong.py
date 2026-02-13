from database_connector import get_connection

# Lấy danh sách tất cả cây trồng
def lay_danh_sach_cay():
    conn = get_connection()      # mở kết nối
    cursor = conn.cursor()       # tạo con trỏ

    cursor.execute(
        "SELECT crop_id, crop_name, category, base_price FROM Crops"
    )

    crops = cursor.fetchall()    # lấy toàn bộ danh sách

    conn.close()                 # đóng kết nối
    return crops                 # trả về list tuple

# Lấy thông tin chi tiết 1 cây theo ID
def lay_chi_tiet_cay(crop_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM Crops WHERE crop_id = ?",
        (crop_id,)
    )

    crop = cursor.fetchone()     # lấy 1 dòng

    conn.close()
    return crop

# Thêm cây mới vào hệ thống
def them_cay(crop_name, category, base_price):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO Crops (crop_name, category, base_price)
        VALUES (?, ?, ?)
        """,
        (crop_name, category, base_price)
    )

    conn.commit()    # lưu thay đổi
    conn.close()

# Cập nhật thông tin cây
def sua_cay(crop_id, crop_name, category, base_price):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE Crops
        SET crop_name = ?, category = ?, base_price = ?
        WHERE crop_id = ?
        """,
        (crop_name, category, base_price, crop_id)
    )

    conn.commit()
    conn.close()

# Xóa cây khỏi hệ thống
def xoa_cay(crop_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM Crops WHERE crop_id = ?",
        (crop_id,)
    )

    conn.commit()
    conn.close()

# Lấy trạng thái đất mới nhất theo activity_id
def lay_trang_thai_dat(activity_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT soil_status, log_date
        FROM ActivityLog
        WHERE activity_id = ?
        ORDER BY log_date DESC
        LIMIT 1
        """,
        (activity_id,)
    )

    status = cursor.fetchone()

    conn.close()
    return status
