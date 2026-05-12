import os
import sys
import json
import faiss
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.config import settings
from app.services.embedding import get_embedding

# Đọc dữ liệu từ file JSON trong thư mục raw/
def load_raw_data(file_path):
    if not os.path.exists(file_path):
        print(f"⚠️ Không tìm thấy file: {file_path}")
        print("💡 Vui lòng tạo file JSON trong thư mục data/raw/ trước.")
        return[]
        
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# Xây dựng Vector DB
def build_index(data, faiss_path, json_path):
    if not data:
        print("Bỏ qua vì không có dữ liệu.")
        return
        
    print(f"🚀 Đang khởi tạo cơ sở dữ liệu Vector lưu tại: {faiss_path}...")
    
    embeddings =[]
    for chunk in data:
        print(f"Đang nhúng (embed) đoạn: {chunk['text'][:30]}...")
        vec = get_embedding(chunk["text"]) 
        if vec is None:
            print("❌ Embedding failed")
            continue
        embeddings.append(vec)
        
    embedding_matrix = np.array(embeddings).astype("float32")
    if len(embeddings) == 0:
        raise ValueError("Không tạo được embedding nào")
    dimension = embedding_matrix.shape[1]
    
    index = faiss.IndexFlatL2(dimension)
    index.add(embedding_matrix)
    
    os.makedirs(os.path.dirname(faiss_path), exist_ok=True)
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    
    faiss.write_index(index, faiss_path)
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    print(f"✅ Tạo Vector DB thành công!\n")


if __name__ == "__main__":
    print("=== TIẾN HÀNH ĐỌC DỮ LIỆU TỪ THƯ MỤC RAW ===\n")
    
    # 1. Load dữ liệu từ file JSON
    data_uit = load_raw_data(settings.RAW_UIT_PATH)
    data_cnpm = load_raw_data(settings.RAW_CNPM_PATH)
    
    # 2. Xây dựng DB cho UIT
    print("=== TẠO DB CHO UIT ===")
    build_index(data_uit, settings.FAISS_UIT_PATH, settings.DATA_UIT_PATH)
    
    # 3. Xây dựng DB cho CNPM
    print("=== TẠO DB CHO KHOA CNPM ===")
    build_index(data_cnpm, settings.FAISS_CNPM_PATH, settings.DATA_CNPM_PATH)