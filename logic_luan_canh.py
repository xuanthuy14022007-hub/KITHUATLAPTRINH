from database_connector import get_connection

# Hàm gợi ý luân canh dựa trên crop_id hiện tại
def goi_y_luan_canh(crop_id):
    conn = get_connection()
    cursor = conn.cursor()

    # Lấy category (nhóm cây) của cây hiện tại
    cursor.execute(
        "SELECT category FROM Crops WHERE crop_id = ?",  # tìm category theo crop_id
        (crop_id,)                                       # truyền crop_id vào câu lệnh
    )
    result = cursor.fetchone()  # lấy 1 dòng kết quả (trả về tuple hoặc None)

    # Nếu không tìm thấy cây trong database
    if not result:
        conn.close()            # đóng kết nối
        return []               # trả về danh sách rỗng

    current_category = result[0]  # lấy giá trị category từ tuple

    # Tìm các cây có category khác (để luân canh)
    cursor.execute(
        "SELECT crop_id, crop_name, category FROM Crops WHERE category != ?",
        (current_category,)      # truyền category hiện tại vào
    )

    suggestions = cursor.fetchall()  # lấy tất cả cây phù hợp (danh sách tuple)

    conn.close()   # đóng kết nối database

    return suggestions  # trả về danh sách cây gợi ý
