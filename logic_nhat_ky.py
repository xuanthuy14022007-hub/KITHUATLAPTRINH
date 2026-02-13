from database_connector import get_connection

# --- LẤY DANH SÁCH ---
def lay_nhat_ky_theo_mua_vu(activity_id):
    """
    Input: activity_id (Mã của mùa vụ/loại cây được chọn)
    Output: Danh sách các nhật ký gần đây của riêng mùa vụ đó.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT 
            log_id, 
            action_type, 
            quantity, 
            log_date, 
            soil_status
        FROM ActivityLog
        WHERE activity_id = ?
        ORDER BY log_date DESC
        LIMIT 3 -- Chỉ lấy 3 nhật ký gần nhất để hiện màn hình chính
    """
    cursor.execute(query, (activity_id,))
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
        VALUES (?, ?, ?, NULL, ?, ?)
    """
    cursor.execute(query, (activity_id, ten_thua_dat, action_type, log_date, soil_status))
    conn.commit()
    conn.close()
# --- HÀM NHẬT KÝ 2: DÙNG KHI THU HOẠCH ---
def ghi_nhan_thu_hoach(activity_id, harvest_quantity, log_date, note):
    thong_tin = lay_thong_tin_vu_mua(activity_id)
    if not thong_tin: return
    ten_thua_dat = thong_tin[0]
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # A. Thêm dòng 'Thu hoạch' vào nhật ký
        query_log = """
            INSERT INTO ActivityLog (activity_id, farm_name, action_type, quantity, log_date, soil_status)
            VALUES (?, ?, 'Thu hoạch', ?, ?, ?)
        """
        cursor.execute(query_log, (activity_id, ten_thua_dat, harvest_quantity, log_date, note))
        
        # B. Tự động đổi trạng thái vụ mùa sang 'Sẵn sàng bán'
        query_status = "UPDATE FarmingActivities SET status = 'Sẵn sàng bán' WHERE activity_id = ?"
        cursor.execute(query_status, (activity_id,))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Lỗi: {e}")
    finally:
        conn.close()

# --- SỬA NHẬT KÝ (ĐÃ FIX) ---
def sua_nhat_ky(log_id, action_type, log_date, soil_status, quantity=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if action_type == 'Thu hoạch' and quantity is not None:
            # Cập nhật có kèm sản lượng
            query = """
                UPDATE ActivityLog 
                SET action_type = ?, quantity = ?, log_date = ?, soil_status = ?
                WHERE log_id = ?
            """
            cursor.execute(query, (action_type, quantity, log_date, soil_status, log_id))
        else:
            # Cập nhật thông thường, ép quantity về NULL để đảm bảo tính đồng bộ
            query = """
                UPDATE ActivityLog 
                SET action_type = ?, quantity = NULL, log_date = ?, soil_status = ?
                WHERE log_id = ?
            """
            cursor.execute(query, (action_type, log_date, soil_status, log_id))
        conn.commit()
    except Exception as e:
        print(f"Lỗi khi sửa: {e}")
        conn.rollback()
    finally:
        conn.close()

# --- XÓA NHẬT KÝ ---
def xoa_nhat_ky(log_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ActivityLog WHERE log_id = ?", (log_id,))
    conn.commit()
    conn.close()
