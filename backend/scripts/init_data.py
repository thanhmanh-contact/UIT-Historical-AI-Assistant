"""
init_data.py — Tạo FAISS Vector DB từ dữ liệu raw

Sử dụng:
  # Tạo cả hai DB (UIT + CNPM):
  python scripts/init_data.py

  # Chỉ tạo DB cho CNPM (khi UIT đã có):
  python scripts/init_data.py --scope cnpm

  # Chỉ tạo DB cho UIT:
  python scripts/init_data.py --scope uit

v2.3: Thêm --scope argument, hiển thị tiến trình rõ hơn.
"""

import os
import sys
import json
import argparse
import faiss
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.config import settings
from app.services.embedding import get_embedding


def load_raw_data(file_path: str) -> list:
    if not os.path.exists(file_path):
        print(f"⚠️  Không tìm thấy file: {file_path}")
        print("💡 Vui lòng tạo file JSON trong thư mục data/raw/ trước.")
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"✅ Đã đọc {len(data)} chunks từ {file_path}")
    return data


def build_index(data: list, faiss_path: str, json_path: str, scope: str = ""):
    if not data:
        print("⚠️  Bỏ qua vì không có dữ liệu.")
        return

    label = f"[{scope.upper()}] " if scope else ""
    print(f"\n🚀 {label}Bắt đầu tạo FAISS index → {faiss_path}")
    print(f"   Số chunks cần embed: {len(data)}")

    embeddings = []
    for idx, chunk in enumerate(data, 1):
        text = chunk.get("text", "").strip()
        if not text:
            print(f"   ⏩ Bỏ qua chunk {idx} (không có text)")
            continue
        print(f"   [{idx}/{len(data)}] Đang embed: {text[:50]}...")
        vec = get_embedding(text)
        if vec is None:
            print(f"   ❌ Embedding thất bại cho chunk {idx}")
            continue
        embeddings.append((vec, chunk))

    if not embeddings:
        print("❌ Không tạo được embedding nào. Kiểm tra GOOGLE_API_KEY trong .env")
        return

    vecs = np.array([e[0] for e in embeddings]).astype("float32")
    chunks_with_embed = [e[1] for e in embeddings]
    dimension = vecs.shape[1]

    index = faiss.IndexFlatL2(dimension)
    index.add(vecs)

    os.makedirs(os.path.dirname(faiss_path), exist_ok=True)
    os.makedirs(os.path.dirname(json_path), exist_ok=True)

    faiss.write_index(index, faiss_path)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(chunks_with_embed, f, ensure_ascii=False, indent=2)

    print(f"✅ {label}Tạo Vector DB thành công!")
    print(f"   - FAISS index: {faiss_path} ({index.ntotal} vectors, dim={dimension})")
    print(f"   - Chunks JSON: {json_path} ({len(chunks_with_embed)} chunks)")


def main():
    parser = argparse.ArgumentParser(description="Tạo FAISS Vector DB cho UIT Chatbot")
    parser.add_argument(
        "--scope",
        choices=["uit", "cnpm", "all"],
        default="all",
        help="Chọn DB cần tạo: uit | cnpm | all (mặc định: all)",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  UIT Chatbot — Khởi tạo Vector Database")
    print("=" * 60)

    if not settings.GOOGLE_API_KEY:
        print("\n❌ GOOGLE_API_KEY chưa được cấu hình trong file .env")
        print("   Thêm: GOOGLE_API_KEY=<your-key>")
        sys.exit(1)

    if args.scope in ("uit", "all"):
        data_uit = load_raw_data(settings.RAW_UIT_PATH)
        build_index(data_uit, settings.FAISS_UIT_PATH, settings.DATA_UIT_PATH, scope="uit")

    if args.scope in ("cnpm", "all"):
        data_cnpm = load_raw_data(settings.RAW_CNPM_PATH)
        build_index(data_cnpm, settings.FAISS_CNPM_PATH, settings.DATA_CNPM_PATH, scope="cnpm")

    print("\n" + "=" * 60)
    print("  Hoàn tất! Khởi động lại server để áp dụng.")
    print("=" * 60)


if __name__ == "__main__":
    main()
