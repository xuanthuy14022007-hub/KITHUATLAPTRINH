from database_connector import get_connection

def lay_tat_ca_nhat_ky():
    """Lấy danh sách tất cả nhật ký kèm tên cây trồng từ cơ sở dữ liệu"""
    conn = get_connection()
    cursor = conn.cursor()
    # Truy vấn kết hợp (JOIN) 3 bảng để lấy thông tin chi tiết
    query = """
        SELECT 
            ActivityLog.log_id, 
            ActivityLog.farm_name, 
            Crops.crop_name, 
            ActivityLog.action_type, 
            ActivityLog.quantity, 
            ActivityLog.log_date, 
            ActivityLog.soil_status
        FROM ActivityLog
        JOIN FarmingActivities ON ActivityLog.activity_id = FarmingActivities.activity_id
        JOIN Crops ON FarmingActivities.crop_id = Crops.crop_id
        ORDER BY ActivityLog.log_date DESC
    """
    cursor.execute(query)
    rows = cursor.fetchall() # Trả về danh sách các dòng dữ liệu
    conn.close()
    return rows

def xem_chi_tiet_nhat_ky(log_id):
    """Lấy thông tin chi tiết của một dòng nhật ký cụ thể qua ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ActivityLog WHERE log_id = ?", (log_id,))
    row = cursor.fetchone() # Trả về 1 dòng duy nhất hoặc None
    conn.close()
    return row

def them_nhat_ky(activity_id, farm_name, action_type, quantity, log_date, soil_status):
    """Thêm một bản ghi nhật ký canh tác mới vào kho lưu trữ"""
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO ActivityLog (activity_id, farm_name, action_type, quantity, log_date, soil_status)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    cursor.execute(query, (activity_id, farm_name, action_type, quantity, log_date, soil_status))
    conn.commit() # Xác nhận lưu dữ liệu xuống file .db
    conn.close()

def sua_nhat_ky(log_id, action_type, quantity, log_date, soil_status):
    """Cập nhật nội dung của một dòng nhật ký đã tồn tại"""
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        UPDATE ActivityLog 
        SET action_type = ?, quantity = ?, log_date = ?, soil_status = ?
        WHERE log_id = ?
    """
    cursor.execute(query, (action_type, quantity, log_date, soil_status, log_id))
    conn.commit() # Xác nhận thay đổi
    conn.close()

def xoa_nhat_ky(log_id):
    """Xóa bỏ hoàn toàn một dòng nhật ký khỏi hệ thống"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ActivityLog WHERE log_id = ?", (log_id,))
    conn.commit() # Xác nhận xóa
    conn.close()
