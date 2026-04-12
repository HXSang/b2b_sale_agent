from qdrant_client import QdrantClient, models
import os
from dotenv import load_dotenv

load_dotenv()

class QdrantManager:
    def __init__(self, path=None):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        default_db_path = os.path.join(project_root, "qdrant_db")
        
        self.db_path = path or os.getenv("QDRANT_DB_PATH", default_db_path)
        self.client = QdrantClient(path=self.db_path)
        
    def create_indexes(self, collection_name, index_config: dict):
        if not index_config:
            print(" - [SKIP] Không có cấu hình index nào được truyền vào.")
            return
            
        print(f"Bắt đầu tạo {len(index_config)} indexes cho collection '{collection_name}'...")
        for field_name, schema_type in index_config.items():
            try:
                self.client.create_payload_index(
                    collection_name=collection_name,
                    field_name=field_name,
                    field_schema=schema_type,
                )
                print(f" - [OK] Indexed: {field_name}")
            except Exception as e:
                print(f" - [SKIP] {field_name} (Có thể đã tồn tại hoặc lỗi: {e})")

    def setup_collection(self, collection_name, vector_size=3072, index_config=None):
        if not self.client.collection_exists(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=models.Distance.COSINE,
                ),
                quantization_config=models.ScalarQuantization(
                    scalar=models.ScalarQuantizationConfig(
                        type=models.ScalarType.INT8,
                        always_ram=True,
                    )
                ),
            )
            print(f" - [OK] Đã tạo collection: {collection_name}")
            if index_config:
                self.create_indexes(collection_name, index_config)
        else:
            print(f" - [SKIP] Collection '{collection_name}' đã tồn tại")

    def upsert_point(self, collection_name, point_id, vector, payload):
        self.client.upsert(
            collection_name=collection_name,
            points=[models.PointStruct(id=point_id, vector=vector, payload=payload)],
        )

    def upsert_batch(self, collection_name, points: list[dict], batch_size=100):
        if not points:
            return
            
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.client.upsert(
                collection_name=collection_name,
                points=[
                    models.PointStruct(
                        id=p["id"], vector=p["vector"], payload=p["payload"]
                    )
                    for p in batch
                ],
            )
            print(f" - [OK] Upserted {min(i + batch_size, len(points))}/{len(points)}")

    def search(
        self,
        collection_name: str,
        query_vector: list[float],
        filters: models.Filter | None = None,
        limit: int = 10, 
        score_threshold: float = 0.4, 
    ) -> list:
        try:
            response = self.client.query_points(
                collection_name=collection_name,
                query=query_vector,        
                query_filter=filters,
                limit=limit,
                score_threshold=score_threshold,
                with_payload=True,
            )
            return response.points
        except Exception as e:
            print(f"[Qdrant Search Error]: {e}")
            return []