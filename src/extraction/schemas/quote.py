from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
import uuid

class CustomerInfo(BaseModel):
    contact_name: str = Field(..., description="Tên người liên hệ")
    company: Optional[str] = Field(None, description="Tên công ty")
    phone_zalo: Optional[str] = Field(None, description="Số điện thoại hoặc Zalo")
    email: Optional[str] = Field(None, description="Email")
    industry: Optional[str] = Field(None, description="Ngành nghề")

class ProductItem(BaseModel):
    product_name: str = Field(..., description="Tên sản phẩm")
    product_type: str = Field(..., description="Loại thiết bị (LiDAR, IMU, Encoder...)")
    manufacturer: Optional[str] = Field(None)
    quantity: int = Field(..., gt=0, description="Số lượng")
    unit: str = Field(default="cái")
    key_specs: dict = Field(default_factory=dict)

class ProjectContext(BaseModel):
    application: str = Field(..., description="Ứng dụng thực tế")
    environment: Literal["indoor", "outdoor", "harsh_environment", "unknown"] = Field(default="unknown")
    timeline: Optional[str] = Field(None)
    quantity_type: Literal["sample_first", "pilot_batch", "mass_order", "unknown"] = Field(default="unknown")

class TechnicalRequirements(BaseModel):
    certifications_needed: List[str] = Field(default_factory=list)
    integration_support_needed: bool = Field(default=False)
    warranty_requirement_months: int = Field(default=12)

class QuoteRequestSchema(BaseModel):
    quote_id: str = Field(
        default_factory=lambda: f"QR-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
    )
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    status: Literal["pending"] = Field(default="pending")
    priority: Literal["low", "medium", "high"] = Field(
        ...,
        description="high: timeline gấp/số lượng lớn/so sánh đối thủ. medium: có dự án cụ thể. low: hỏi thăm dò."
    )
    customer: CustomerInfo
    items: List[ProductItem]
    project_context: ProjectContext
    technical_requirements: TechnicalRequirements
    sales_notes: str = Field(
        ...,
        description="Insight cho Sales: pain point, đối thủ đang so sánh, người ra quyết định, tín hiệu chốt deal, rủi ro."
    )