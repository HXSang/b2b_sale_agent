from .base import BaseProductSchema, ProductType, OrderingOption
from .encoder import EncoderSchema
from .imu import IMUSchema
from .lidar import LidarSchema
from .tof import ToFSchema
from .oil_sensor import OilSensorSchema
from .air_quality import AirQualitySchema
from .quote import QuoteRequestSchema, CustomerInfo, ProductItem, ProjectContext, TechnicalRequirements

SCHEMA_REGISTRY: dict[ProductType, type[BaseProductSchema]] = {
    ProductType.ENCODER:     EncoderSchema,
    ProductType.IMU:         IMUSchema,
    ProductType.LIDAR:       LidarSchema,
    ProductType.TOF:         ToFSchema,
    ProductType.OIL_SENSOR:  OilSensorSchema,
    ProductType.AIR_QUALITY: AirQualitySchema,
}

def get_schema(product_type: ProductType) -> type[BaseProductSchema]:
    return SCHEMA_REGISTRY.get(product_type, BaseProductSchema)

__all__ = [
    "BaseProductSchema", "ProductType", "OrderingOption",
    "EncoderSchema", "IMUSchema", "LidarSchema",
    "ToFSchema", "OilSensorSchema", "AirQualitySchema",
    "QuoteRequestSchema", "CustomerInfo", "ProductItem",
    "ProjectContext", "TechnicalRequirements",
    "SCHEMA_REGISTRY", "get_schema",
]