from database_connector import get_connection

def lay_thong_tin_nguoi_dung(user_id):
    """
    Lấy thông tin người dùng theo ID.
    
    Args:
        user_id (int): ID của người dùng.
    
    Returns:
        tuple: (user_id, username, role, full_name, email, address, farm_name, description)
               None nếu không tìm thấy.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT user_id, username, role, full_name, email, address, farm_name, description FROM Users WHERE user_id = ?",
        (user_id,)
    )
    user = cursor.fetchone()
    conn.close()
    return user

def cap_nhat_thong_tin_nguoi_dung(user_id, username, role, full_name, email, address, farm_name, description):
    """
    Cập nhật thông tin người dùng.
    
    Args:
        user_id (int): ID của người dùng.
        username (str): Tên đăng nhập mới.
        role (str): Vai trò mới.
        full_name (str): Họ tên mới.
        email (str): Email mới.
        address (str): Địa chỉ mới.
        farm_name (str): Tên nông trại/vựa mới.
        description (str): Mô tả mới.
    
    Returns:
        bool: True nếu cập nhật thành công, False nếu không tìm thấy user.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE Users
        SET username = ?, role = ?, full_name = ?, email = ?, address = ?, farm_name = ?, description = ?
        WHERE user_id = ?
        """,
        (username, role, full_name, email, address, farm_name, description, user_id)
    )
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success
