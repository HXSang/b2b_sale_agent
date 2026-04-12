from pydantic import Field
from typing import Optional, List
from .base import ProductType, BaseProductSchema

class EncoderSchema(BaseProductSchema):
    product_type: ProductType = Field(default=ProductType.ENCODER, frozen=True)

    output_type: Optional[str] = Field(default=None, description="Kiểu tín hiệu đầu ra. Ví dụ: '2-bit quadrature code'")

    pulses_per_revolution: Optional[List[int]] = Field(default=None, description="Danh sách các tùy chọn số xung trên vòng quay (PPR). Ví dụ: [9, 15, 24]")
    detent_count: Optional[List[int]] = Field(default=None, description="Danh sách các tùy chọn số khấc (detent). Ví dụ: [0, 18, 30]")

    detent_torque_raw: Optional[str] = Field(default=None, description="Nguyên văn lực vặn khấc (gf-cm) từ datasheet. Ví dụ: '100 ± 70 gf-cm'")

    has_switch: bool = Field(default=False, description="Có tùy chọn tích hợp nút nhấn (push switch) không?")
    switch_actuation_force_raw: Optional[str] = Field(default=None, description="Lực nhấn nút. Ví dụ: 'S: 350 ± 100 gf, H: 400 ± 200 gf'")
    switch_travel_raw: Optional[str] = Field(default=None, description="Hành trình nhấn nút. Ví dụ: '0.5 ± 0.3 mm, 1.5 ± 0.5 mm'")

    shaft_style: Optional[str] = Field(default=None, description="Kiểu dáng trục. Ví dụ: 'Flatted, Metal'")
    shaft_length_options_mm: Optional[List[float]] = Field(default=None, description="Các tùy chọn chiều dài trục (mm). Ví dụ: [15.0, 20.0, 25.0]")
    mounting_style: Optional[str] = Field(default=None, description="Kiểu lắp đặt/Chân cắm. Ví dụ: 'Surface mount, Gull-wing'")

    rotational_life_cycles: Optional[int] = Field(default=None, description="Tuổi thọ vòng xoay tối thiểu. Ví dụ: 100000")
    switch_life_cycles: Optional[int] = Field(default=None, description="Tuổi thọ nút nhấn tối thiểu. Ví dụ: 20000")
    operating_temp_min_c: Optional[float] = Field(default=None, description="Nhiệt độ hoạt động tối thiểu (°C). Ví dụ: -10.0")
    operating_temp_max_c: Optional[float] = Field(default=None, description="Nhiệt độ hoạt động tối đa (°C). Ví dụ: 70.0")
    ip_rating: Optional[str] = Field(default=None, description="Chuẩn bảo vệ môi trường. Ví dụ: 'IP 40'")

    contact_rating_raw: Optional[str] = Field(default=None, description="Định mức tiếp điểm. Ví dụ: '10 mA @ 5 VDC'")