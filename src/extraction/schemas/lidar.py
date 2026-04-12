from pydantic import Field
from typing import Optional, List
from .base import BaseProductSchema, ProductType

class LidarSchema(BaseProductSchema):
    product_type: ProductType = Field(default=ProductType.LIDAR, frozen=True)

    blind_zone_m: Optional[float] = Field(default=None, description="Vùng mù của cảm biến (m). Ví dụ: 0.1")
    distance_resolution_cm: Optional[float] = Field(default=None, description="Độ phân giải khoảng cách (cm). Ví dụ: 1.0")

    detection_range_max_m: Optional[float] = Field(
        default=None, 
        description="Tầm xa tối đa (m) ở mức phản xạ cao nhất. Dùng để DB filter."
    )
    detection_range_min_reflectivity_m: Optional[float] = Field(
        default=None, 
        description="Tầm xa tối đa (m) ở mức phản xạ thấp nhất (môi trường thực tế nhất). Dùng để DB filter."
    )
    detection_range_raw: Optional[str] = Field(
        default=None, 
        description="Toàn bộ text về range và độ phản xạ từ datasheet để Agent suy luận. Ví dụ: '290m@90%, 170m@30%, 100m@10%'"
    )

    accuracy: Optional[str] = Field(default=None, description="Độ chính xác. Ví dụ: ± 10 cm (<10 m), 1% (≥ 10 m)")
    frame_rate_max_hz: Optional[float] = Field(default=None, description="Tốc độ quét tối đa (Hz)")
    frame_rate_default_hz: Optional[float] = Field(default=None, description="Tốc độ quét mặc định (Hz)")
    fov_deg: Optional[float] = Field(default=None, description="Góc nhìn FOV (độ). Ví dụ: 0.5")
    ambient_light_resistance_klux: Optional[float] = Field(default=None, description="Khả năng kháng sáng (kLux)")
    light_source: Optional[str] = Field(default=None, description="Nguồn sáng. Ví dụ: EEL, 905 nm")

    power_supply_v: Optional[str] = Field(default=None, description="Nguồn điện cấp. Ví dụ: DC 5V ± 10%")
    avg_power_consumption_w: Optional[float] = Field(default=None, description="Công suất tiêu thụ trung bình (W). Ví dụ: 0.45")
    interfaces: Optional[List[str]] = Field(default=None, description="Giao thức kết nối. Ví dụ: ['UART', 'CAN']")
    ip_rating: Optional[str] = Field(default=None, description="Chuẩn chống nước/bụi. Ví dụ: IP67")
    operating_temp_min_c: Optional[float] = Field(default=None, description="Nhiệt độ hoạt động tối thiểu (°C)")
    operating_temp_max_c: Optional[float] = Field(default=None, description="Nhiệt độ hoạt động tối đa (°C)")
    weight_g: Optional[float] = Field(default=None, description="Trọng lượng (g). Ví dụ: 34.5")