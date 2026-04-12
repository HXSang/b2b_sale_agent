import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

import time
import uuid
import json
from qdrant_client import models

from src.database.qdrant_core import QdrantManager
from src.ai.embedder import OpenAIEmbedding
from src.extraction.extractors.handler import CatalogExtractor

from src.extraction.schemas.base import BaseProductSchema
from src.extraction.schemas.encoder import EncoderSchema
from src.extraction.schemas.imu import IMUSchema
from src.extraction.schemas.lidar import LidarSchema
from src.extraction.schemas.tof import ToFSchema
from src.extraction.schemas.oil_sensor import OilSensorSchema


GLOBAL_INDEXES = {
    "product_type":                 models.PayloadSchemaType.KEYWORD,
    "manufacturer":                 models.PayloadSchemaType.KEYWORD,
    "ip_rating":                    models.PayloadSchemaType.KEYWORD,
    "supply_voltage_min_v":         models.PayloadSchemaType.FLOAT,
    "supply_voltage_max_v":         models.PayloadSchemaType.FLOAT,
    "current_consumption_max_ma":   models.PayloadSchemaType.FLOAT,
    "operating_temp_min_c":         models.PayloadSchemaType.FLOAT,
    "operating_temp_max_c":         models.PayloadSchemaType.FLOAT,

    "interfaces":                   models.PayloadSchemaType.KEYWORD, 
    "certifications":               models.PayloadSchemaType.KEYWORD,

    "max_operating_pressure_bar":   models.PayloadSchemaType.FLOAT,
    "measures_viscosity":           models.PayloadSchemaType.BOOL,

    "detection_range_max_m":        models.PayloadSchemaType.FLOAT,
    "measurement_range_max_mm":     models.PayloadSchemaType.FLOAT,
    "blind_zone_m":                 models.PayloadSchemaType.FLOAT,
    "fov_degrees_max":              models.PayloadSchemaType.FLOAT,

    "has_ahrs_option":              models.PayloadSchemaType.BOOL,
    "has_magnetometer":             models.PayloadSchemaType.BOOL,
    "output_rate_max_hz":           models.PayloadSchemaType.FLOAT,

    "rotational_life_cycles":       models.PayloadSchemaType.INTEGER,
    "has_switch":                   models.PayloadSchemaType.BOOL,
}

def dict_to_search_text(json_data: dict) -> str:
    if not json_data:
        return ""

    lines = []

    name = json_data.get("product_name", "sản phẩm")
    mfg = json_data.get("manufacturer", "hãng không xác định")
    ptype = json_data.get("product_type", "thiết bị")
    lines.append(f"Đây là {ptype} có tên mã {name} do hãng {mfg} sản xuất.")

    if json_data.get("general_description_raw"):
        lines.append(json_data["general_description_raw"])

    ignore_keys = [
        "product_name", "manufacturer", "product_type", "general_description_raw", 
        "ordering_options", "source_file", "page_numbers", "dimensions_raw",
        "electrical_parameters_raw", "interfaces_raw", "fov_raw", "contact_rating_raw"
    ]

    lines.append("Các thông số kỹ thuật chi tiết:")
    for key, value in json_data.items():
        if key in ignore_keys or value is None:
            continue

        clean_key = key.replace("_", " ")
        
        if isinstance(value, bool):
            if value: 
                lines.append(f"- Có hỗ trợ tính năng: {clean_key}")
        elif isinstance(value, list):
            lines.append(f"- {clean_key}: {', '.join(map(str, value))}")
        else:
            lines.append(f"- {clean_key}: {value}")

    return "\n".join(lines)

def classify_and_get_schema(text: str):
    text_lower = text.lower()
    
    if "imu" in text_lower or "gyro" in text_lower or "accelerometer" in text_lower:
        return IMUSchema
    elif "lidar" in text_lower or "blind zone" in text_lower or "benewake" in text_lower:
        return LidarSchema
    elif "encoder" in text_lower or "quadrature" in text_lower or "ppr" in text_lower:
        return EncoderSchema
    elif "tof" in text_lower or "time-of-flight" in text_lower or "spad" in text_lower:
        return ToFSchema
    elif "oil" in text_lower or "viscosity" in text_lower:
        return OilSensorSchema
    else:
        return BaseProductSchema

def clean_spec_text(text: str) -> str:
    lines = text.split('\n')
    important_lines = []
    for line in lines:
        line_clean = line.strip()
        if '|' in line_clean or line_clean.startswith(('-', '*', '#')) or any(c.isdigit() for c in line_clean):
            important_lines.append(line)
    return '\n'.join(important_lines)[:30000]

def main():
    print("KHỞI ĐỘNG HỆ THỐNG DATA INGESTION PIPELINE (BẢN OPENAI)...")

    db = QdrantManager()
    db.setup_collection("b2b_sensors", vector_size=3072, index_config=GLOBAL_INDEXES)
    
    ai_vector = OpenAIEmbedding()
    extractor = CatalogExtractor()

    pdf_folder = "./data/raw_pdfs/"
    batch_points = []

    if not os.path.exists(pdf_folder):
        print(f"Không tìm thấy thư mục {pdf_folder}. Hãy tạo và cho PDF vào nhé.")
        return

    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]
    print(f"Tìm thấy {len(pdf_files)} file PDF cần xử lý.")

    for filename in pdf_files:
        filepath = os.path.join(pdf_folder, filename)
        print(f"\nĐang xử lý: {filename}...")
        
        try:
            raw_text = extractor.extract_text_from_pdf(filepath)
            
            cleaned_text = clean_spec_text(raw_text)
            print(f"-> Tối ưu: Đã giảm từ {len(raw_text)} xuống {len(cleaned_text)} ký tự.")

            text_head = cleaned_text[:1000] 
            target_schema = classify_and_get_schema(text_head)
            print(f"-> Phân loại: {target_schema.__name__}")

            sensor_json = extractor.extract_to_schema(raw_text, target_schema)
            
            if not sensor_json:
                print(f"-> Bóc tách thất bại cho {filename}. Bỏ qua.")
                continue

            sensor_json["source_file"] = filename

            search_text = dict_to_search_text(sensor_json)
            vector_data = ai_vector.get_embedding(search_text)
            
            point_id = str(uuid.uuid4())
            batch_points.append({
                "id": point_id,
                "vector": vector_data,
                "payload": sensor_json 
            })
            print(f"-> Gói hàng thành công!")
            time.sleep(1)
            
        except Exception as e:
            print(f"-> Lỗi không xác định khi xử lý {filename}: {e}")

    if batch_points:
        print(f"\nĐang nạp {len(batch_points)} sản phẩm vào Qdrant...")
        db.upsert_batch("b2b_sensors", batch_points)
        print("PIPELINE HOÀN TẤT THÀNH CÔNG!")
    else:
        print("\nKhông có sản phẩm nào được nạp. Hãy kiểm tra lại file PDF.")

if __name__ == "__main__":
    main()