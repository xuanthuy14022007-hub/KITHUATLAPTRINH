from database_connector import get_connection

def lay_danh_sach_vu_mua(farmer_id):
    """
    Lấy danh sách các vụ mùa của một nông dân.
    
    Args:
        farmer_id (int): ID của nông dân.
    
    Returns:
        list: Danh sách các tuple (activity_id, crop_name, plot_name, area, start_date, selling_price, status).
    """
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT fa.activity_id, c.crop_name, fa.plot_name, fa.area, fa.start_date, 
               fa.selling_price, fa.status
        FROM FarmingActivities fa
        JOIN Crops c ON fa.crop_id = c.crop_id
        WHERE fa.farmer_id = ?
        ORDER BY fa.start_date DESC
    """
    cursor.execute(query, (farmer_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def lay_chi_tiet_vu_mua(activity_id):
    """
    Lấy thông tin chi tiết một vụ mùa.
    
    Args:
        activity_id (int): ID của vụ mùa.
    
    Returns:
        tuple: (activity_id, farmer_id, crop_id, plot_name, area, start_date, selling_price, status)
               None nếu không tìm thấy.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM FarmingActivities WHERE activity_id = ?", (activity_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def them_vu_mua(farmer_id, crop_id, plot_name, area, start_date, status='Đang trồng'):
    """
    Thêm một vụ mùa mới (giá bán mặc định NULL).
    
    Args:
        farmer_id (int): ID của nông dân.
        crop_id (int): ID của cây trồng.
        plot_name (str): Tên mảnh đất.
        area (float): Diện tích (m2).
        start_date (str): Ngày bắt đầu (YYYY-MM-DD).
        status (str): Trạng thái (mặc định 'Đang trồng').
    
    Returns:
        int: ID của vụ mùa vừa tạo.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO FarmingActivities (farmer_id, crop_id, plot_name, area, start_date, selling_price, status)
        VALUES (?, ?, ?, ?, ?, NULL, ?)
    """, (farmer_id, crop_id, plot_name, area, start_date, status))
    conn.commit()
    activity_id = cursor.lastrowid
    conn.close()
    return activity_id

def sua_vu_mua(activity_id, crop_id, plot_name, area, start_date, selling_price, status):
    """
    Cập nhật thông tin vụ mùa (bao gồm giá bán).
    
    Args:
        activity_id (int): ID của vụ mùa.
        crop_id (int): ID cây trồng mới.
        plot_name (str): Tên mảnh đất mới.
        area (float): Diện tích mới.
        start_date (str): Ngày bắt đầu mới.
        selling_price (float or None): Giá bán mới (có thể None).
        status (str): Trạng thái mới.
    
    Returns:
        None
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE FarmingActivities
        SET crop_id = ?, plot_name = ?, area = ?, start_date = ?, selling_price = ?, status = ?
        WHERE activity_id = ?
    """, (crop_id, plot_name, area, start_date, selling_price, status, activity_id))
    conn.commit()
    conn.close()

def cap_nhat_gia_ban(activity_id, selling_price):
    """
    Cập nhật giá bán cho vụ mùa (thường dùng khi chuẩn bị đăng bán).
    
    Args:
        activity_id (int): ID của vụ mùa.
        selling_price (float or None): Giá bán mới.
    
    Returns:
        None
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE FarmingActivities
        SET selling_price = ?
        WHERE activity_id = ?
    """, (selling_price, activity_id))
    conn.commit()
    conn.close()

def xoa_vu_mua(activity_id):
    """
    Xóa vụ mùa (chỉ khi chưa có nhật ký canh tác).
    
    Args:
        activity_id (int): ID của vụ mùa.
    
    Raises:
        Exception: Nếu vụ mùa đã có nhật ký.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM ActivityLog WHERE activity_id = ?", (activity_id,))
    if cursor.fetchone()[0] > 0:
        conn.close()
        raise Exception("Không thể xóa vụ mùa đã có nhật ký canh tác!")
    cursor.execute("DELETE FROM FarmingActivities WHERE activity_id = ?", (activity_id,))
    conn.commit()
    conn.close()
