from database_connector import get_connection

def them_chi_phi(farmer_id, cost_type, amount):
    """
    Thêm một khoản chi phí vào bảng CostCart.
    
    Args:
        farmer_id (int): ID của nông dân.
        cost_type (str): Loại chi phí, phải là một trong:
                         'Hạt giống', 'Phân bón', 'Nhân công', 'Chi phí khác'.
        amount (float): Số tiền chi phí (phải >= 0).
    
    Returns:
        bool: True nếu thêm thành công, False nếu có lỗi (ví dụ vi phạm ràng buộc).
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO CostCart (farmer_id, cost_type, amount) VALUES (?, ?, ?)",
            (farmer_id, cost_type, amount)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Lỗi thêm chi phí: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def lay_ket_qua_tai_chinh_tong_quat(farmer_id):
    """
    Tính tổng doanh thu, tổng chi phí và lợi nhuận của một nông dân.
    Chỉ tính các đơn hàng có trạng thái 'Xác nhận'.
    
    Args:
        farmer_id (int): ID của nông dân.
    
    Returns:
        dict: {
            'doanh_thu': float (tổng tiền từ đơn hàng),
            'chi_phi': float (tổng chi phí từ CostCart),
            'loi_nhuan': float (doanh_thu - chi_phi)
        }
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT SUM(total_amount) FROM Orders 
            WHERE farmer_id = ? AND status = 'Xác nhận'
        """, (farmer_id,))
        doanh_thu = cursor.fetchone()[0] or 0

        cursor.execute("SELECT SUM(amount) FROM CostCart WHERE farmer_id = ?", (farmer_id,))
        tong_chi_phi = cursor.fetchone()[0] or 0

        loi_nhuan = doanh_thu - tong_chi_phi
        return {"doanh_thu": doanh_thu, "chi_phi": tong_chi_phi, "loi_nhuan": loi_nhuan}
    except Exception as e:
        print(f"Lỗi lay_ket_qua_tai_chinh_tong_quat: {e}")
        return {"doanh_thu": 0, "chi_phi": 0, "loi_nhuan": 0}
    finally:
        conn.close()

def tinh_co_cau_tai_chinh_theo_doanh_thu(farmer_id):
    """
    Tính tỷ lệ phần trăm của từng loại chi phí và lợi nhuận so với doanh thu.
    Chỉ tính các đơn hàng có trạng thái 'Xác nhận'.
    
    Args:
        farmer_id (int): ID của nông dân.
    
    Returns:
        dict or None: Nếu doanh thu > 0, trả về dictionary với các key:
                      'Hạt giống', 'Phân bón', 'Nhân công', 'Chi phí khác', 'Lợi nhuận'
                      và giá trị là tỷ lệ phần trăm (float, đã làm tròn 2 chữ số).
                      Nếu doanh thu = 0, trả về None.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT SUM(total_amount) FROM Orders 
            WHERE farmer_id = ? AND status = 'Xác nhận'
        """, (farmer_id,))
        doanh_thu = cursor.fetchone()[0] or 0
        if doanh_thu == 0:
            return None

        cac_loai_cp = ["Hạt giống", "Phân bón", "Nhân công", "Chi phí khác"]
        ket_qua = {}
        tong_chi_phi = 0
        for loai in cac_loai_cp:
            cursor.execute("SELECT SUM(amount) FROM CostCart WHERE farmer_id = ? AND cost_type = ?", (farmer_id, loai))
            tien_cp = cursor.fetchone()[0] or 0
            tong_chi_phi += tien_cp
            ty_suat = (tien_cp / doanh_thu) * 100
            ket_qua[loai] = round(ty_suat, 2)

        loi_nhuan = doanh_thu - tong_chi_phi
        ket_qua["Lợi nhuận"] = round((loi_nhuan / doanh_thu) * 100, 2)
        return ket_qua
    except Exception as e:
        print(f"Lỗi tinh_co_cau_tai_chinh_theo_doanh_thu: {e}")
        return None
    finally:
        conn.close()

def lay_ti_le_don_hang(farmer_id):
    """
    Tính tỷ lệ phần trăm sản lượng bán ra của từng loại cây trồng so với tổng sản lượng.
    Chỉ tính các đơn hàng có trạng thái 'Xác nhận'.
    
    Args:
        farmer_id (int): ID của nông dân.
    
    Returns:
        dict or None: Nếu có đơn hàng, trả về dictionary với key là tên cây trồng,
                      value là tỷ lệ phần trăm (float, làm tròn 2 chữ số).
                      Nếu không có đơn hàng nào, trả về None.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT SUM(oi.quantity) 
            FROM Orders o
            JOIN OrderItems oi ON o.order_id = oi.order_id
            WHERE o.farmer_id = ? AND o.status = 'Xác nhận'
        """, (farmer_id,))
        tong_sl = cursor.fetchone()[0] or 0
        if tong_sl == 0:
            return None

        cursor.execute("""
            SELECT c.crop_name, SUM(oi.quantity) as tong_sp
            FROM Orders o
            JOIN OrderItems oi ON o.order_id = oi.order_id
            JOIN Crops c ON oi.crop_id = c.crop_id
            WHERE o.farmer_id = ? AND o.status = 'Xác nhận'
            GROUP BY c.crop_name
        """, (farmer_id,))
        ket_qua = {}
        for crop_name, tong_sp in cursor.fetchall():
            ty_le = (tong_sp / tong_sl) * 100
            ket_qua[crop_name] = round(ty_le, 2)
        return ket_qua
    except Exception as e:
        print(f"Lỗi lay_ti_le_don_hang: {e}")
        return None
    finally:
        conn.close()
