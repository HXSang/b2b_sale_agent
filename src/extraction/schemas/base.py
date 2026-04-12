from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from enum import Enum 

class ProductType(str, Enum):
    ENCODER = "encoder"
    AIR_QUALITY = "air_quality"
    TOF = "tof"
    LIDAR = "lidar"
    IMU = "imu"
    OIL_SENSOR = "oil_sensor"
    UNKNOWN = "unknown"
    
class OrderingOption(BaseModel):
    description: str = Field(description="Mô tả chi tiết cấu hình/phiên bản sản phẩm (VD: 'OPS3 C4-A 12/24V - No Rp')")
    part_number: str = Field(description="Mã Part Number hoặc SKU để đặt hàng tương ứng với mô tả (VD: '10131380-06')")

class BaseProductSchema(BaseModel):
    product_name: str
    manufacturer: str
    product_type: ProductType
    general_description_raw: Optional[str] = Field(default=None, description="Đoạn văn xuôi tóm tắt giới thiệu sản phẩm. Rất quan trọng để AI làm ngữ cảnh Vector Search.")
    
    ordering_options: List[OrderingOption] = Field(
        default_factory=list, 
        description="Danh sách toàn bộ các mã part number để đặt hàng và mô tả cấu hình đi kèm."
    )

    supply_voltage_min_v: Optional[float] = Field(default=None, description="Điện áp hoạt động tối thiểu (V)")
    supply_voltage_max_v: Optional[float] = Field(default=None, description="Điện áp hoạt động tối đa (V)")
    current_consumption_max_ma: Optional[float] = Field(default=None, description="Dòng điện tiêu thụ tối đa (mA) dùng để DB filter")
    electrical_parameters_raw: Optional[str] = Field(default=None, description="Nguyên văn thông số điện năng tiêu thụ (VD: '10 mA @ 5 VDC')")

    interfaces: List[str] = Field(default_factory=list, description= "Danh sách chuẩn giao tiếp để DB filter: ['UART', 'I2C', 'CAN']")
    interfaces_raw: Optional[str] = Field(default=None, description="Nguyên văn phần giao tiếp để lấy ngữ cảnh phụ trợ (VD: RS232 cần thiết bị ngoại vi).")
    connector_type: Optional[str] = Field(default=None, description="Mã giắc cắm/connector (nếu có)")

    ip_rating: Optional[str] = Field(default=None, description="Tiêu chuẩn chống nước, bụi (VD: 'IP67')")
    operating_temp_min_c: Optional[float] = Field(default=None, description="Nhiệt độ hoạt động mạch điện tối thiểu (°C)")
    operating_temp_max_c: Optional[float] = Field(default=None, description="Nhiệt độ hoạt động mạch điện tối đa (°C)")
    storage_temp_min_c: Optional[float] = Field(default=None, description="Nhiệt độ lưu kho tối thiểu (°C)")
    storage_temp_max_c: Optional[float] = Field(default=None, description="Nhiệt độ lưu kho tối đa (°C)")
    
    dimensions_raw: Optional[str] = Field(default=None, description="Kích thước vật lý nguyên văn (VD: '36.8x40x15.7 mm')")
    weight_g: Optional[float] = Field(default=None, description="Trọng lượng tính bằng gram (g)")

    certifications: List[str] = Field(default_factory=list, description="Chứng nhận thương mại: ['CE', 'RoHS', 'REACH']")
    compliance_standards: List[str] = Field(default_factory=list, description="Tiêu chuẩn thử nghiệm kỹ thuật: ['IEC 60825-1', 'ISO 9001']")
   
    source_file: Optional[str] = Field(default=None, description="Tên file PDF gốc")
    page_numbers: List[int] = Field(default_factory=list, description="Danh sách các trang PDF chứa thông tin sản phẩm này (VD: [1, 2])")
    
    @field_validator('product_type', mode='before')
    @classmethod
    def normalize_product_type(cls, value):
        if isinstance(value, str):
            return value.lower()
        return value