from database_connector import get_connection

def lay_danh_sach_cay():
    """
    Lấy danh sách tất cả các loại cây trồng trong danh mục.
    
    Returns:
        list: Danh sách các tuple (crop_id, crop_name, category, base_price).
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT crop_id, crop_name, category, base_price FROM Crops")
    crops = cursor.fetchall()
    conn.close()
    return crops

def lay_chi_tiet_cay(crop_id):
    """
    Lấy thông tin chi tiết một loại cây trồng.
    
    Args:
        crop_id (int): ID của cây trồng.
    
    Returns:
        tuple: (crop_id, crop_name, category, base_price) nếu tìm thấy, None nếu không.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Crops WHERE crop_id = ?", (crop_id,))
    crop = cursor.fetchone()
    conn.close()
    return crop
