from pydantic import Field
from typing import Optional, List
from .base import ProductType, BaseProductSchema

class IMUSchema(BaseProductSchema):
    product_type: ProductType = Field(default=ProductType.IMU, frozen=True)

    has_vru_option: bool = Field(default=False, description="Hỗ trợ VRU (tính Roll, Pitch)")
    has_ahrs_option: bool = Field(default=False, description="Hỗ trợ AHRS (tính Yaw/Heading)")
    output_rate_max_hz: Optional[float] = Field(default=None, description="Tần số output tối đa (Hz). Ví dụ: 2000.0")

    gyro_full_range_dps: Optional[float] = Field(default=None, description="Dải đo Gyroscope (°/s). Ví dụ: 300.0")
    gyro_in_run_bias_stability_deg_hr: Optional[float] = Field(default=None, description="In-run bias stability Gyro (°/h). Ví dụ: 8.0")

    accel_full_range_g: Optional[float] = Field(default=None, description="Dải đo Accelerometer (g). Ví dụ: 8.0")
    accel_in_run_bias_stability_ug: Optional[float] = Field(default=None, description="In-run bias stability Accel (µg). Ví dụ: 15.0")

    has_magnetometer: bool = Field(default=False, description="Có tích hợp cảm biến từ trường (Magnetometer) không?")
    mag_full_range_g: Optional[float] = Field(default=None, description="Dải đo Magnetometer (G - Gauss). Ví dụ: 8.0")
    mag_total_rms_noise_mg: Optional[float] = Field(default=None, description="Nhiễu tổng hợp RMS của Magnetometer (mG). Ví dụ: 1.0")

    roll_pitch_accuracy_deg: Optional[float] = Field(default=None, description="Độ chính xác Roll/Pitch RMS (°). Ví dụ: 0.2")
    yaw_heading_accuracy_deg: Optional[float] = Field(default=None, description="Độ chính xác Yaw/Heading RMS (°). Ví dụ: 1.0")

    supply_voltage_min_v: Optional[float] = Field(default=None, description="Điện áp tối thiểu (V). Ví dụ: 3.2")
    supply_voltage_max_v: Optional[float] = Field(default=None, description="Điện áp tối đa (V). Ví dụ: 51.0")
    power_consumption_w: Optional[float] = Field(default=None, description="Công suất tiêu thụ trung bình (W). Ví dụ: 0.5")

    interfaces: Optional[List[str]] = Field(default=None, description="Danh sách giao tiếp hỗ trợ sẵn. Ví dụ: ['UART', 'SPI', 'I2C', 'CAN']")
    interfaces_raw: Optional[str] = Field(default=None, description="Nguyên văn phần giao tiếp để lấy ngữ cảnh phụ trợ (như RS232/RS422 cần DK).")

    ip_rating: Optional[str] = Field(default=None, description="Chuẩn bảo vệ. Ví dụ: 'IP51'")
    operating_temp_min_c: Optional[float] = Field(default=None, description="Nhiệt độ min (°C). Ví dụ: -40.0")
    operating_temp_max_c: Optional[float] = Field(default=None, description="Nhiệt độ max (°C). Ví dụ: 85.0")
    weight_g: Optional[float] = Field(default=None, description="Khối lượng (g). Ví dụ: 35.2")