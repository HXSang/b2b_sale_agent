from pydantic import Field
from typing import Optional
from .base import ProductType, BaseProductSchema

class AirQualitySchema(BaseProductSchema):
    product_type: ProductType = Field(default=ProductType.AIR_QUALITY, frozen=True)

    measures_pm: bool = Field(default=False, description="Có đo bụi mịn (PM) không?")
    measures_co2: bool = Field(default=False, description="Có đo khí CO2 không?")
    measures_rht: bool = Field(default=False, description="Có đo Nhiệt độ và Độ ẩm (RH & T) không?")
    measures_voc: bool = Field(default=False, description="Có đo khí VOC (Hợp chất hữu cơ bay hơi) không?")
    measures_nox: bool = Field(default=False, description="Có đo khí NOx (Nitrogen Oxides) không?")
    measures_hcho: bool = Field(default=False, description="Có đo khí HCHO (Formaldehyde) không?")

    pm_measurement_max_ug_m3: Optional[float] = Field(default=None, description="Dải đo nồng độ bụi tối đa (µg/m³), ví dụ: 1000")
    pm25_accuracy: Optional[str] = Field(default=None, description="Độ chính xác đo bụi PM2.5, ví dụ: ±5 µg/m3")

    temperature_range_min_c: Optional[float] = Field(default=None, description="Nhiệt độ đo tối thiểu (°C), ví dụ: -10")
    temperature_range_max_c: Optional[float] = Field(default=None, description="Nhiệt độ đo tối đa (°C), ví dụ: 60")
    temperature_accuracy_c: Optional[str] = Field(default=None, description="Độ chính xác đo nhiệt độ, ví dụ: ±0.45 °C")
    
    humidity_range_min_rh: Optional[float] = Field(default=None, description="Độ ẩm đo tối thiểu (%), ví dụ: 0")
    humidity_range_max_rh: Optional[float] = Field(default=None, description="Độ ẩm đo tối đa (%), ví dụ: 80")
    humidity_accuracy: Optional[str] = Field(default=None, description="Độ chính xác đo độ ẩm, ví dụ: ±4.5 %RH")
    
    voc_index_max: Optional[float] = Field(default=None, description="Dải đo VOC Index tối đa, ví dụ: 500")
    voc_accuracy: Optional[str] = Field(default=None, description="Độ chính xác đo VOC, ví dụ: < ±15 VOC Index points")
    
    nox_index_max: Optional[float] = Field(default=None, description="Dải đo NOx Index tối đa, ví dụ: 500")
    nox_accuracy: Optional[str] = Field(default=None, description="Độ chính xác đo NOx, ví dụ: < ±50 NOx Index points")
    
    co2_measurement_max_ppm: Optional[float] = Field(default=None, description="Dải đo CO2 tối đa (ppm), ví dụ: 5000")
    co2_accuracy: Optional[str] = Field(default=None, description="Độ chính xác đo CO2, ví dụ: ±(50 ppm + 5% m.v.)")
    
    hcho_measurement_max_ppb: Optional[float] = Field(default=None, description="Dải đo HCHO tối đa (ppb), ví dụ: 1000")
    hcho_accuracy: Optional[str] = Field(default=None, description="Độ chính xác đo HCHO, ví dụ: ±(15 ppb + 15% m.v.)")

    interfaces: Optional[str] = Field(default=None, description="Giao thức giao tiếp, ví dụ: I2C")
    supply_voltage_v: Optional[float] = Field(default=None, description="Điện áp hoạt động điển hình (V), ví dụ: 3.3 hoặc 5")
    lifetime_years: Optional[float] = Field(default=None, description="Tuổi thọ cảm biến (năm), ví dụ: 10")