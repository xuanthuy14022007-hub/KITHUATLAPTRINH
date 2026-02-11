from database_connector import get_connection

#Hàm đăng nhập
def login(username, password):
    conn = get_connection()  #mở kết nối database
    cursor = conn.cursor()  #tạo con trỏ SQL

    cursor.execute(
        "SELECT user_id, username, role, full_name, email FROM Users WHERE username = ? AND password = ?",  #tìm user hợp lệ
        (username, password)  #truyền username và password
    )
    user = cursor.fetchone()  #lấy 1 dòng dữ liệu

    conn.close()  #đóng kết nối database
    return user  #có user thì trả tuple, không có thì None

#Hàm đăng xuất
def logout():
    return None  #xóa trạng thái user đang đăng nhập trong chương trình

#Hàm đăng kí
def register(username, password, role, full_name, email):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO Users (username, password, role, full_name, email) VALUES (?, ?, ?, ?, ?)",  #thêm user mới
            (username, password, role, full_name, email)  #dữ liệu tương ứng với bảng Users
        )
        conn.commit()  #lưu thay đổi xuống database
        return True  #đăng ký thành công
    except sqlite3.IntegrityError:
        return False  # username bị trùng
    finally:
        conn.close()

#Hàm khôi phục mật khẩu
def reset_password(username, new_password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE Users SET password = ? WHERE username = ?",  #cập nhật password mới
        (new_password, username)  #mật khẩu mới và username
    )
    conn.commit()  #lưu thay đổi

    success = cursor.rowcount > 0  #kiểm tra có user được cập nhật không
    conn.close()

    return success  #True nếu đổi được, False nếu không có username


