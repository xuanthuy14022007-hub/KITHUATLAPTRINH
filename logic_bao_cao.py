from logic_tinh_toan import lay_ket_qua_tai_chinh_tong_quat, tinh_co_cau_tai_chinh_theo_doanh_thu

def xuat_bao_cao_tai_chinh(farmer_id):
    """
    Hàm xuất báo cáo tổng hợp gồm:
    - Chi phí
    - Doanh thu
    - Lợi nhuận
    - Cơ cấu tài chính theo doanh thu (%)
    """
    # Lấy kết quả tổng quát
    ket_qua_tong_quat = lay_ket_qua_tai_chinh_tong_quat(farmer_id)

    # Lấy cơ cấu theo doanh thu
    co_cau = tinh_co_cau_tai_chinh_theo_doanh_thu(farmer_id)

    # Ghép báo cáo
    bao_cao = {
        "Tổng chi phí": ket_qua_tong_quat.get("chi_phi", 0),
        "Tổng doanh thu": ket_qua_tong_quat.get("doanh_thu", 0),
        "Lợi nhuận": ket_qua_tong_quat.get("loi_nhuan", 0),
        "Cơ cấu theo doanh thu (%)": co_cau if co_cau else {}
    }

    return bao_cao
