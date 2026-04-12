from pydantic import Field
from typing import Optional, List
from .base import ProductType, BaseProductSchema

class ToFSchema(BaseProductSchema):
    product_type: ProductType = Field(default=ProductType.TOF, frozen=True)

    measurement_range_min_mm: Optional[float] = Field(default=None, description="Khoảng cách đo tối thiểu (mm). Ví dụ: 10.0")
    measurement_range_max_mm: Optional[float] = Field(default=None, description="Khoảng cách đo tối đa (mm). Ví dụ: 11000.0")
    distance_resolution_mm: Optional[float] = Field(default=None, description="Độ chia nhỏ nhất/Độ phân giải khoảng cách (mm). Ví dụ: 0.25")

    fov_degrees_max: Optional[float] = Field(default=None, description="Góc nhìn tối đa (độ), dùng để DB filter range. Ví dụ: 80.0")
    fov_raw: Optional[str] = Field(default=None, description="Nguyên văn góc nhìn. Ví dụ: '80° (diagonal, aspect ratio 4:3)'")

    resolution_zones_supported: Optional[List[str]] = Field(default=None, description="Danh sách các chế độ độ phân giải hỗ trợ. Ví dụ: ['8x8', '16x16', '32x32', '48x32']")

    max_objects_per_zone: Optional[int] = Field(default=None, description="Số lượng vật thể tối đa có thể nhận diện trên 1 điểm ảnh (Multi-object). Ví dụ: 4")
    max_frame_rate_hz: Optional[float] = Field(default=None, description="Tốc độ khung hình tối đa (Hz).")
    ambient_light_immunity_klux: Optional[float] = Field(default=None, description="Khả năng chống nhiễu ánh sáng môi trường (kLux).")
    wavelength_nm: Optional[int] = Field(default=None, description="Bước sóng ánh sáng (nm). Ví dụ: 850 hoặc 940")

    interfaces: Optional[List[str]] = Field(default=None, description="Danh sách chuẩn giao tiếp hỗ trợ. Ví dụ: ['I3C', 'I2C', 'SPI']")
    supply_voltage_options_v: Optional[List[float]] = Field(default=None, description="Các mức điện áp I/O hỗ trợ (V). Ví dụ: [1.2, 1.8, 3.0]")

    operating_temperature_min_c: Optional[float] = Field(default=None, description="Nhiệt độ hoạt động min (°C). Ví dụ: -40.0")
    operating_temperature_max_c: Optional[float] = Field(default=None, description="Nhiệt độ hoạt động max (°C). Ví dụ: 85.0")
    dimensions_raw: Optional[str] = Field(default=None, description="Kích thước vật lý (Dài x Rộng x Cao). Ví dụ: '5.7 mm x 2.9 mm x 1.5 mm'")