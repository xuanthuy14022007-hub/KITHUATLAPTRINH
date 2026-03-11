from database.database_connector import get_connection
import sqlite3

def login(username, password):
    """
    Xác thực đăng nhập.

    Args:
        username (str): Tên đăng nhập.
        password (str): Mật khẩu.

    Returns:
        tuple: (user_id, username, role, full_name, email, address, farm_name, description)
               nếu thành công, None nếu thất bại.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT user_id, username, role, full_name, email, address, farm_name, description FROM Users WHERE username = ? AND password = ?",
        (username, password)
    )
    user = cursor.fetchone()
    conn.close()
    return user

def logout():
    """
    Đăng xuất (hàm giữ chỗ).
    Returns:
        None
    """
    return None

def register(username, password, role, full_name, email, address, farm_name, description):
    """
    Đăng ký tài khoản mới.

    Args:
        username (str): Tên đăng nhập.
        password (str): Mật khẩu.
        role (str): 'Farmer' hoặc 'Merchant'.
        full_name (str): Họ tên.
        email (str): Email.
        address (str): Địa chỉ.
        farm_name (str): Tên nông trại/vựa.
        description (str): Mô tả.

    Returns:
        bool: True nếu thành công, False nếu username/email đã tồn tại.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Users (username, password, role, full_name, email, address, farm_name, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (username, password, role, full_name, email, address, farm_name, description)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def reset_password(username, new_password):
    """
    Đặt lại mật khẩu cho người dùng.

    Args:
        username (str): Tên đăng nhập.
        new_password (str): Mật khẩu mới.

    Returns:
        bool: True nếu cập nhật thành công, False nếu username không tồn tại.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Users SET password = ? WHERE username = ?", (new_password, username))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

