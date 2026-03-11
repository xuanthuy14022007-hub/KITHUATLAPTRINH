import io
import matplotlib.pyplot as plt
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Table, TableStyle
from logic_tinh_toan import (
    lay_ket_qua_tai_chinh_tong_quat,
    tinh_co_cau_tai_chinh_theo_doanh_thu,
    lay_ti_le_don_hang
)

# Cấu hình font 
plt.rcParams['font.family'] = 'Arial'
try:
    pdfmetrics.registerFont(TTFont('Roboto', 'Roboto-Regular.ttf'))
    pdfmetrics.registerFont(TTFont('Roboto-Bold', 'Roboto-Bold.ttf'))
    F_REG, F_BOLD = "Roboto", "Roboto-Bold"
except:
    F_REG, F_BOLD = "Helvetica", "Helvetica-Bold"

def tao_anh_bieu_do(data_dict, title):
    """
    Tạo biểu đồ tròn từ dữ liệu và trả về dạng BytesIO để nhúng vào PDF.
    
    Args:
        data_dict (dict): Dữ liệu với key là nhãn, value là số liệu (ví dụ tỷ lệ %).
        title (str): Tiêu đề của biểu đồ.
    
    Returns:
        BytesIO or None: Đối tượng chứa dữ liệu ảnh PNG nếu thành công,
                          None nếu data_dict rỗng hoặc không hợp lệ.
    """
    if not data_dict or sum(data_dict.values()) <= 0:
        return None
    fig = plt.figure(figsize=(5, 5))
    ax = fig.add_axes([0.15, 0.1, 0.75, 0.75])
    labels = list(data_dict.keys())
    values = list(data_dict.values())
    colors_theme = ['#4db6ac', '#9575cd', '#9ccc65', '#ffb74d', '#ff8a65']
    def my_pct(pct):
        return ('%1.0f%%' % pct) if pct > 0 else ''
    ax.pie(values, labels=labels, autopct=my_pct, startangle=140,
           colors=colors_theme, pctdistance=0.75, radius=1,
           wedgeprops={'edgecolor': 'white', 'linewidth': 1.5})
    ax.set_title(title, fontsize=14, fontweight='bold', pad=30)
    ax.axis('equal')
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=120, transparent=True)
    plt.close(fig)
    buf.seek(0)
    return buf

def xuat_bao_cao(farmer_id):
    """
    Xuất báo cáo tài chính dạng PDF cho nông dân có ID cho trước.
    Báo cáo bao gồm: doanh thu, chi phí, lợi nhuận, bảng chi tiết chi phí,
    biểu đồ cơ cấu tài chính và biểu đồ tỷ lệ đơn hàng theo sản phẩm.
    
    Args:
        farmer_id (int): ID của nông dân cần xuất báo cáo.
    
    Returns:
        None: Tạo file PDF với tên "Bao_cao_tai_chinh_{farmer_id}.pdf" trong thư mục hiện tại.
    """
    stats = lay_ket_qua_tai_chinh_tong_quat(farmer_id)
    co_cau_pct = tinh_co_cau_tai_chinh_theo_doanh_thu(farmer_id)
    ti_le_sp = lay_ti_le_don_hang(farmer_id)

    pdf_file = f"Bao_cao_tai_chinh_{farmer_id}.pdf"
    c = canvas.Canvas(pdf_file, pagesize=A4)
    W, H = A4

    # --- Header ---
    c.setFillColorRGB(0.13, 0.55, 0.13)
    c.rect(0, H - 70, W, 70, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont(F_BOLD, 20)
    c.drawString(50, H - 45, "BÁO CÁO TÌNH HÌNH TÀI CHÍNH NÔNG ƠI!")

    # --- Thông tin cơ bản ---
    c.setFillColor(colors.black)
    c.setFont(F_REG, 10)
    c.drawString(50, H - 90, f"Ngày xuất: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    c.setStrokeColor(colors.lightgrey)
    c.roundRect(50, H - 170, 500, 65, 8, stroke=1)
    c.setFont(F_BOLD, 13)
    c.drawString(70, H - 135, f"LỢI NHUẬN: {stats['loi_nhuan']:,} VND")
    c.setFont(F_REG, 11)
    c.drawString(70, H - 160, f"Doanh thu: {stats['doanh_thu']:,} VND  |  Chi phí: {stats['chi_phi']:,} VND")

    # --- Bảng chi phí ---
    c.setFont(F_BOLD, 12)
    c.drawString(50, H - 200, "CHI TIẾT CHI PHÍ SẢN XUẤT:")

    data_table = [['Hạng mục', 'Số tiền (VND)']]
    if co_cau_pct:
        for k, v in co_cau_pct.items():
            if k != "Lợi nhuận":
                tien = int((v / 100) * stats['doanh_thu'])
                data_table.append([k, f"{tien:,}"])
    else:
        data_table.append(['Không có dữ liệu', ''])

    table = Table(data_table, colWidths=[200, 150])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.honeydew),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, -1), F_REG),
        ('FONTNAME', (0, 0), (-1, 0), F_BOLD),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))

    table_w, table_h = table.wrap(0, 0)
    y_table = H - 215 - table_h
    table.drawOn(c, 50, y_table)

    # --- Biểu đồ 1: Cơ cấu tài chính ---
    CHART_SIZE = 240
    CENTER_X = (W - CHART_SIZE) / 2

    img1 = tao_anh_bieu_do(co_cau_pct, "Cơ cấu tài chính (%)")
    if img1:
        y_img1 = y_table - CHART_SIZE - 10
        c.drawImage(ImageReader(img1), CENTER_X, y_img1, width=CHART_SIZE, height=CHART_SIZE, preserveAspectRatio=True)
    else:
        y_img1 = y_table - CHART_SIZE - 10  # vẫn giữ khoảng cách

    # --- Biểu đồ 2: Tỉ lệ đơn hàng ---
    img2 = tao_anh_bieu_do(ti_le_sp, "Tỉ lệ đơn hàng (%)")
    if img2:
        y_img2 = y_img1 - CHART_SIZE + 20
        c.drawImage(ImageReader(img2), CENTER_X, y_img2, width=CHART_SIZE, height=CHART_SIZE, preserveAspectRatio=True)

    # --- Footer ---
    c.setFont(F_REG, 9)
    c.setFillColor(colors.grey)
    c.line(50, 20, W - 50, 20)
    c.drawCentredString(W / 2, 10, "Hệ thống quản lý Nông Ơi! - Chúc bạn mùa màng bội thu")
    c.save()
    print(f"✅ Đã xuất báo cáo: {pdf_file}")

if __name__ == "__main__":
    # Ví dụ: xuất báo cáo cho farmer_id = 1
    xuat_bao_cao(1)
