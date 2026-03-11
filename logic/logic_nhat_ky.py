from database.database_connector import get_connection

def lay_nhat_ky_theo_mua_vu(activity_id, limit=3):
    """
    Lấy danh sách nhật ký của một vụ mùa, giới hạn số bản ghi.

    Args:
        activity_id (int): ID của vụ mùa.
        limit (int): Số lượng nhật ký tối đa (mặc định 3).

    Returns:
        list: Danh sách các tuple (log_id, action_type, quantity, log_date, soil_status, plot_name).
    """
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT log_id, action_type, quantity, log_date, soil_status, plot_name
        FROM ActivityLog
        WHERE activity_id = ?
        ORDER BY log_date DESC
        LIMIT ?
    """
    cursor.execute(query, (activity_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return rows

def lay_thong_tin_vu_mua(activity_id):
    """
    Lấy tên mảnh đất và tên cây trồng của vụ mùa.

    Args:
        activity_id (int): ID của vụ mùa.

    Returns:
        tuple: (plot_name, crop_name) nếu tìm thấy, None nếu không.
    """
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT fa.plot_name, c.crop_name
        FROM FarmingActivities fa
        JOIN Crops c ON fa.crop_id = c.crop_id
        WHERE fa.activity_id = ?
    """
    cursor.execute(query, (activity_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def them_nhat_ky(activity_id, action_type, log_date, soil_status):
    """
    Thêm một nhật ký canh tác (không phải thu hoạch). Tự động lấy plot_name từ vụ mùa.

    Args:
        activity_id (int): ID của vụ mùa.
        action_type (str): Loại hành động ('Gieo hạt', 'Bón phân', 'Tưới nước', 'Khác').
        log_date (str): Ngày thực hiện (YYYY-MM-DD).
        soil_status (str): Ghi chú tình trạng đất.

    Returns:
        None
    """
    thong_tin = lay_thong_tin_vu_mua(activity_id)
    if not thong_tin:
        print("Lỗi: Không tìm thấy vụ mùa!")
        return
    plot_name = thong_tin[0]
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO ActivityLog (activity_id, plot_name, action_type, quantity, log_date, soil_status)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    cursor.execute(query, (activity_id, plot_name, action_type, 0, log_date, soil_status))
    conn.commit()
    conn.close()

def ghi_nhan_thu_hoach(activity_id, harvest_quantity, log_date, note):
    """
    Ghi nhận thu hoạch: thêm nhật ký 'Thu hoạch' và chuyển trạng thái vụ mùa thành 'Đã thu hoạch'.

    Args:
        activity_id (int): ID của vụ mùa.
        harvest_quantity (float): Sản lượng thu hoạch (kg).
        log_date (str): Ngày thu hoạch (YYYY-MM-DD).
        note (str): Ghi chú (tình trạng đất).

    Returns:
        None
    """
    thong_tin = lay_thong_tin_vu_mua(activity_id)
    if not thong_tin:
        print("Lỗi: Không tìm thấy vụ mùa!")
        return
    plot_name = thong_tin[0]
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query_log = """
            INSERT INTO ActivityLog (activity_id, plot_name, action_type, quantity, log_date, soil_status)
            VALUES (?, ?, 'Thu hoạch', ?, ?, ?)
        """
        cursor.execute(query_log, (activity_id, plot_name, harvest_quantity, log_date, note))
        query_status = "UPDATE FarmingActivities SET status = 'Đã thu hoạch' WHERE activity_id = ?"
        cursor.execute(query_status, (activity_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Lỗi khi ghi nhận thu hoạch: {e}")
    finally:
        conn.close()

def sua_nhat_ky(log_id, action_type, log_date, soil_status, quantity=None):
    """
    Sửa thông tin một nhật ký.

    Args:
        log_id (int): ID của nhật ký.
        action_type (str): Loại hành động mới.
        log_date (str): Ngày thực hiện mới.
        soil_status (str): Tình trạng đất mới.
        quantity (float, optional): Sản lượng (chỉ dùng nếu action_type là 'Thu hoạch').

    Returns:
        None
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if action_type == 'Thu hoạch' and quantity is not None:
            query = """
                UPDATE ActivityLog
                SET action_type = ?, quantity = ?, log_date = ?, soil_status = ?
                WHERE log_id = ?
            """
            cursor.execute(query, (action_type, quantity, log_date, soil_status, log_id))
        else:
            query = """
                UPDATE ActivityLog
                SET action_type = ?, quantity = 0, log_date = ?, soil_status = ?
                WHERE log_id = ?
            """
            cursor.execute(query, (action_type, log_date, soil_status, log_id))
        conn.commit()
    except Exception as e:
        print(f"Lỗi khi sửa nhật ký: {e}")
        conn.rollback()
    finally:
        conn.close()

def xoa_nhat_ky(log_id):
    """
    Xóa một nhật ký.

    Args:
        log_id (int): ID của nhật ký.

    Returns:
        None
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ActivityLog WHERE log_id = ?", (log_id,))
    conn.commit()
    conn.close()
