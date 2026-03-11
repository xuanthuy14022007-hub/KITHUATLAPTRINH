from database_connector import get_connection

def goi_y_luan_canh(crop_id):
    """
    Gợi ý các loại cây trồng khác category với cây hiện tại để luân canh.

    Args:
        crop_id (int): ID của cây trồng hiện tại.

    Returns:
        list: Danh sách các tuple (crop_id, crop_name, category) của các cây khác category.
              Nếu không tìm thấy category hoặc lỗi, trả về [].
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT category FROM Crops WHERE crop_id = ?", (crop_id,))
        result = cursor.fetchone()
        if not result or not result[0]:
            return []
        current_category = result[0]
        cursor.execute("""
            SELECT crop_id, crop_name, category
            FROM Crops
            WHERE category != ? AND category IS NOT NULL
        """, (current_category,))
        suggestions = cursor.fetchall()
        return suggestions
    except Exception as e:
        print(f"Lỗi gợi ý luân canh: {e}")
        return []
    finally:
        conn.close()
