from database_connector import get_connection

# Hàm lấy thông tin người dùng theo ID
def lay_thong_tin_nguoi_dung(user_id):
    conn = get_connection()      # mở kết nối database
    cursor = conn.cursor()       # tạo con trỏ SQL

    cursor.execute(
        "SELECT user_id, username, role, full_name, email FROM Users WHERE user_id = ?",
        (user_id,)               # truyền user_id vào câu lệnh
    )

    user = cursor.fetchone()     # lấy 1 dòng dữ liệu (tuple hoặc None)

    conn.close()                 # đóng kết nối

    return user                  # trả về thông tin người dùng

# Hàm cập nhật thông tin người dùng
def cap_nhat_thong_tin_nguoi_dung(user_id, username, role, full_name):
    conn = get_connection()      # mở kết nối database
    cursor = conn.cursor()       # tạo con trỏ SQL

    cursor.execute(
        """
        UPDATE Users
        SET username = ?, role = ?, full_name = ?,  email = ?
        WHERE user_id = ?
        """,
        (username, role, full_name, email, user_id)  # truyền dữ liệu mới vào
    )

    conn.commit()                # lưu thay đổi xuống database

    success = cursor.rowcount > 0  # kiểm tra có dòng nào được cập nhật không

    conn.close()                 # đóng kết nối

    return success               # True nếu cập nhật thành công, False nếu không
