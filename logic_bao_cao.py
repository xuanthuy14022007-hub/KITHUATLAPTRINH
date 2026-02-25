from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from openpyxl import Workbook
from datetime import datetime
from logic_tinh_toan import lay_ket_qua_tai_chinh_tong_quat, tinh_co_cau_tai_chinh_theo_doanh_thu

# Đăng ký font Unicode (bạn cần có file Roboto-Regular.ttf trong cùng thư mục)
pdfmetrics.registerFont(TTFont('Roboto', 'Roboto.ttf'))

def xuat_bao_cao_tai_chinh(farmer_id, file_type="pdf"):
    """
    Xuất báo cáo tài chính cho farmer_id
    file_type: 'pdf' hoặc 'xlsx'
    """
    data = lay_ket_qua_tai_chinh_tong_quat(farmer_id)
    co_cau = tinh_co_cau_tai_chinh_theo_doanh_thu(farmer_id)

    if file_type == "pdf":
        pdf_file = f"bao_cao_tai_chinh_{farmer_id}.pdf"
        c = canvas.Canvas(pdf_file, pagesize=A4)
        c.setFont("Roboto", 16)
        c.drawString(100, 800, "BÁO CÁO TÀI CHÍNH NÔNG ƠI!")

        c.setFont("Roboto", 12)
        c.drawString(100, 770, f"Nông dân ID: {farmer_id}")
        c.drawString(100, 750, f"Ngày xuất: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

        c.drawString(100, 720, f"Doanh thu: {data['doanh_thu']:,} VND")
        c.drawString(100, 700, f"Tổng chi phí: {data['chi_phi']:,} VND")
        c.drawString(100, 680, f"Lợi nhuận: {data['loi_nhuan']:,} VND")

        if co_cau:
            c.drawString(100, 650, "Cơ cấu chi phí theo doanh thu (%):")
            y = 630
            for loai, ty_le in co_cau.items():
                c.drawString(120, y, f"{loai}: {ty_le}%")
                y -= 20

        c.save()
        print(f"✅ Đã tạo file PDF: {pdf_file}")

    elif file_type == "xlsx":
        excel_file = f"bao_cao_tai_chinh_{farmer_id}.xlsx"
        wb = Workbook()
        ws = wb.active
        ws.title = "Báo cáo tài chính"

        ws.append(["BÁO CÁO TÀI CHÍNH NÔNG DÂN"])
        ws.append([])
        ws.append(["Nông dân ID", farmer_id])
        ws.append(["Ngày xuất", datetime.now().strftime("%d/%m/%Y %H:%M")])
        ws.append([])
        ws.append(["Doanh thu", data["doanh_thu"]])
        ws.append(["Tổng chi phí", data["chi_phi"]])
        ws.append(["Lợi nhuận", data["loi_nhuan"]])
        ws.append([])

        if co_cau:
            ws.append(["Cơ cấu chi phí theo doanh thu (%)"])
            for loai, ty_le in co_cau.items():
                ws.append([loai, ty_le])

        wb.save(excel_file)
        print(f"✅ Đã tạo file Excel: {excel_file}")

    else:
        print("❌ Định dạng không hợp lệ. Chọn 'pdf' hoặc 'xlsx'.")

# ====== CHẠY THỬ ======
if __name__ == "__main__":
    # Ví dụ: xuất báo cáo cho farmer_id = 1
    xuat_bao_cao_tai_chinh(1, file_type="pdf")   # hoặc "xlsx"
