def lay_ket_qua_tai_chinh_tong_quat(farmer_id):
    """
    Hàm trả về Doanh thu (từ đơn hàng) và Lợi nhuận (Doanh thu - Tổng chi phí tạm)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Tính Tổng doanh thu từ các đơn hàng đã 'Hoàn thành'
        cursor.execute("""
            SELECT SUM(total_amount) FROM Orders 
            WHERE farmer_id = ? AND status = 'Hoàn thành'
        """, (farmer_id,))
        doanh_thu = cursor.fetchone()[0] or 0
        
        # 2. Tính Tổng chi phí từ bảng tạm CostCart
        cursor.execute("SELECT SUM(amount) FROM CostCart WHERE farmer_id = ?", (farmer_id,))
        tong_chi_phi = cursor.fetchone()[0] or 0
        
        # 3. Tính Lợi nhuận
        loi_nhuan = doanh_thu - tong_chi_phi
        
        return { "chi_phi": tong_chi_phi,
            "doanh_thu": doanh_thu,
            "loi_nhuan": loi_nhuan
        }
    except Exception as e:
        print(f"Lỗi hàm tai_chinh_tong_quat: {e}")
        return {"doanh_thu": 0, "loi_nhuan": 0}
    finally:
        conn.close()

def tinh_co_cau_tai_chinh_theo_doanh_thu(farmer_id):
    """
    Coi Doanh thu là 100%. Tính tỷ suất của:
    1. Hạt giống / Doanh thu
    2. Phân bón / Doanh thu
    3. Nhân công / Doanh thu
    4. Chi phí khác / Doanh thu
    5. Lợi nhuận / Doanh thu
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Tính Tổng doanh thu (Mẫu số - 100%)
        cursor.execute("""
            SELECT SUM(total_amount) FROM Orders 
            WHERE farmer_id = ? AND status = 'Hoàn thành'
        """, (farmer_id,))
        doanh_thu = cursor.fetchone()[0] or 0
        
        if doanh_thu == 0:
            return None # Tránh chia cho 0 nếu chưa có doanh thu

        # 2. Lấy chi phí theo từng loại từ bảng tạm CostCart
        cac_loai_cp = ["Hạt giống", "Phân bón", "Nhân công", "Chi phí khác"]
        ket_qua_ty_suat = {}
        tong_chi_phi = 0
        
        for loai in cac_loai_cp:
            cursor.execute("SELECT SUM(amount) FROM CostCart WHERE farmer_id = ? AND cost_type = ?", (farmer_id, loai))
            tien_cp = cursor.fetchone()[0] or 0
            tong_chi_phi += tien_cp
            
            # Tính tỷ suất % so với Doanh thu
            ty_suat = (tien_cp / doanh_thu) * 100
            ket_qua_ty_suat[loai] = round(ty_suat, 2)
        
        # 3. Tính tỷ suất Lợi nhuận thuần
        loi_nhuan = doanh_thu - tong_chi_phi
        ty_suat_loi_nhuan = (loi_nhuan / doanh_thu) * 100
        ket_qua_ty_suat["Lợi nhuận"] = round(ty_suat_loi_nhuan, 2)
        
        return ket_qua_ty_suat

    except Exception as e:
        print(f"Lỗi tính tỷ suất: {e}")
        return None
    finally:
        conn.close()
