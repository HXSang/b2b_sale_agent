import sys, os, uuid
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database.data_pipeline.pdf_processor import BandoCatalogChunker
from src.database.qdrant_core import QdrantManager
from src.ai.embedder import OpenAIEmbedding
from qdrant_client import models

COLLECTION = "b2b_catalog_chunks"

INDEXES = {
    "section_type":     models.PayloadSchemaType.KEYWORD,
    "product_type":     models.PayloadSchemaType.KEYWORD,
    "belt_pitch":       models.PayloadSchemaType.KEYWORD,
    "brand":            models.PayloadSchemaType.KEYWORD,
    "contains_table":   models.PayloadSchemaType.BOOL,
    "contains_formula": models.PayloadSchemaType.BOOL,
    "source_file":      models.PayloadSchemaType.KEYWORD,
}

def main():
    pdf_path = "./data/raw_pdfs/bandojapan-catalog.pdf"

    print("KHỞI ĐỘNG CATALOG INGESTION PIPELINE")
    print(f"File: {pdf_path}")

    # Setup
    db      = QdrantManager()
    embedder = OpenAIEmbedding()
    chunker  = BandoCatalogChunker()

    # Tạo collection riêng cho catalog chunks
    # Lưu ý: dùng collection KHÁC với b2b_sensors
    db.setup_collection(COLLECTION, vector_size=3072, index_config=INDEXES)

    # Process PDF
    points = chunker.process(pdf_path)

    # Embed + Upsert
    print(f"\nĐang embed và nạp {len(points)} chunks...")
    batch = []
    for i, p in enumerate(points):
        print(f"  Embedding {i+1}/{len(points)}: {p['payload']['title'][:40]}")
        vector = embedder.get_embedding(p["search_text"])
        if not vector:
            print(f"  ⚠ Skip chunk {i+1} (embed thất bại)")
            continue

        batch.append({
            "id":      str(uuid.uuid4()),
            "vector":  vector,
            "payload": p["payload"]
        })

    db.upsert_batch(COLLECTION, batch)
    print(f"\nHoàn tất! Đã nạp {len(batch)}/{len(points)} chunks vào '{COLLECTION}'")

    by_type = {}
    for p in points:
        t = p["payload"]["section_type"]
        by_type[t] = by_type.get(t, 0) + 1

    print("\nPhân bố theo section type:")
    for t, count in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"  {t:20s}: {count} chunks")

if __name__ == "__main__":
    main()