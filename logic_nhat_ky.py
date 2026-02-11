from database_connector import get_connection

# --- LẤY DANH SÁCH ---
def lay_tat_ca_nhat_ky():
    conn = get_connection()
    cursor = conn.cursor()
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
    rows = cursor.fetchall()
    conn.close()
    return rows

# --- THÔNG TIN BỔ TRỢ ---
def lay_thong_tin_vu_mua(activity_id):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT FarmingActivities.farm_name, Crops.crop_name 
        FROM FarmingActivities
        JOIN Crops ON FarmingActivities.crop_id = Crops.crop_id
        WHERE FarmingActivities.activity_id = ?
    """
    cursor.execute(query, (activity_id,))
    result = cursor.fetchone()
    conn.close()
    return result

# --- THÊM NHẬT KÝ (ĐÃ FIX) ---
def them_nhat_ky(activity_id, action_type, log_date, soil_status):
    thong_tin = lay_thong_tin_vu_mua(activity_id)
    if not thong_tin:
        print("Lỗi: Không tìm thấy vụ mùa!")
        return
    
    ten_thua_dat = thong_tin[0]
    
    conn = get_connection()
    cursor = conn.cursor()
    # Thêm 'quantity' vào query và set mặc định là 0
    query = """
        INSERT INTO ActivityLog (activity_id, farm_name, action_type, quantity, log_date, soil_status)
        VALUES (?, ?, ?, 0, ?, ?)
    """
    cursor.execute(query, (activity_id, ten_thua_dat, action_type, log_date, soil_status))
    conn.commit()
    conn.close()

# --- SỬA NHẬT KÝ (ĐÃ FIX) ---
def sua_nhat_ky(log_id, action_type, log_date, soil_status):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        UPDATE ActivityLog 
        SET action_type = ?, log_date = ?, soil_status = ?
        WHERE log_id = ?
    """
    # Chỉ truyền đúng 4 tham số tương ứng với 4 dấu hỏi
    cursor.execute(query, (action_type, log_date, soil_status, log_id))
    conn.commit()
    conn.close()

# --- XÓA NHẬT KÝ ---
def xoa_nhat_ky(log_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ActivityLog WHERE log_id = ?", (log_id,))
    conn.commit()
    conn.close()
