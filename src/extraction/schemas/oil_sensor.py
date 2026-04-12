from pydantic import Field
from typing import Optional
from .base import BaseProductSchema, ProductType

class OilSensorSchema(BaseProductSchema):
    product_type: ProductType = Field(default=ProductType.OIL_SENSOR, frozen=True)

    inrush_current: Optional[str] = Field(default=None, description="Dòng khởi động (thường do bộ gia nhiệt dầu)")

    measures_viscosity: bool = Field(default=False, description="Xác định cảm biến có khả năng đo độ nhớt động học (Dynamic Viscosity) hay không")
    measures_density: bool = Field(default=False, description="Xác định cảm biến có khả năng đo tỷ trọng/mật độ (Density) hay không")
    measures_dielectric: bool = Field(default=False, description="Xác định cảm biến có khả năng đo hằng số điện môi (Dielectric constant) hay không")
    
    viscosity_range_max_cp: Optional[float] = Field(default=None, description="Dải đo độ nhớt tối đa (đơn vị: mPa-s hoặc cP). Chỉ lấy phần số.")
    viscosity_accuracy: Optional[str] = Field(default=None, description="Độ chính xác hoặc sai số khi đo độ nhớt (VD: '+/- 5%')")
    density_range_max_g_cm3: Optional[float] = Field(default=None, description="Dải đo tỷ trọng/mật độ tối đa (đơn vị: g/cm3). Chỉ lấy phần số.")
    density_accuracy: Optional[str] = Field(default=None, description="Độ chính xác hoặc sai số khi đo tỷ trọng/mật độ (VD: '+/- 3%')")
    
    oil_temperature_min_c: Optional[float] = Field(default=None, description="Nhiệt độ dầu tối thiểu mà cảm biến chịu được (đơn vị: C)")
    oil_temperature_max_c: Optional[float] = Field(default=None, description="Nhiệt độ dầu tối đa mà cảm biến chịu được (đơn vị: C)")

    max_operating_pressure_bar: Optional[float] = Field(default=None, description="Áp suất dầu hoạt động tối đa (đơn vị: Bar). Chỉ lấy phần số.")
    housing_material: Optional[str] = Field(default=None, description="Vật liệu cấu tạo phần vỏ nhúng trong dầu (VD: Stainless Steel 316L)")
    threaded_port: Optional[str] = Field(default=None, description="Chuẩn ren cơ khí để gắn vào đường ống dầu (VD: M14x1.5)")
    torque: Optional[str] = Field(default=None, description="Lực siết quy định khi vặn cảm biến vào ống (VD: 27Nm)")