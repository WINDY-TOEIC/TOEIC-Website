import os
import json
import requests
import re
from urllib.parse import urlparse

FOLDER_DATA = 'Data'
FOLDER_MEDIA = 'Media'

print("--------------------------------------------------")
print("BẮT ĐẦU TẢI DỮ LIỆU - PHÂN LOẠI THEO TỪNG ĐỀ")
print("--------------------------------------------------")

for filename in os.listdir(FOLDER_DATA):
    if filename.endswith(".txt") or filename.endswith(".json"):
        filepath = os.path.join(FOLDER_DATA, filename)
        test_name = filename.replace('.txt', '').replace('.json', '')
        
        print(f"\n=> Đang xử lý đề: {test_name}")
        
        # Tạo thư mục riêng biệt cho từng đề
        test_audio_dir = os.path.join(FOLDER_MEDIA, test_name, 'audio')
        test_images_dir = os.path.join(FOLDER_MEDIA, test_name, 'images')
        os.makedirs(test_audio_dir, exist_ok=True)
        os.makedirs(test_images_dir, exist_ok=True)
        
        with open(filepath, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file)
            except Exception as e:
                print(f"  [LỖI] File {filename} không đúng chuẩn JSON. Chi tiết: {e}")
                continue
            
        questions = data.get('data', {}).get('data', {}).get('questions', [])
        
        audio_count = 0
        image_count = 0

        for q in questions:
            # 1. TẢI AUDIO
            audio_url = q.get('audio_url')
            if audio_url and str(audio_url).lower() != "false" and "http" in str(audio_url):
                audio_filename = os.path.basename(urlparse(audio_url).path)
                audio_path = os.path.join(test_audio_dir, audio_filename)
                
                if not os.path.exists(audio_path):
                    try:
                        r = requests.get(audio_url, timeout=15)
                        if r.status_code == 200:
                            with open(audio_path, 'wb') as f:
                                f.write(r.content)
                            audio_count += 1
                    except:
                        pass
                
                # Cập nhật đường dẫn nội bộ mới (đã phân thư mục)
                q['audio_url'] = f"./Media/{test_name}/audio/{audio_filename}"

            # 2. TẢI TOÀN BỘ HÌNH ẢNH TRONG CÂU
            content_html = q.get('content', '')
            if content_html:
                # Quét TẤT CẢ link ảnh có trong chuỗi HTML của câu hỏi
                img_urls = re.findall(r'src=(?:&quot;|")([^&"]+)(?:&quot;|")', content_html)
                
                for img_url in img_urls:
                    if "http" in img_url:
                        img_filename = os.path.basename(urlparse(img_url).path)
                        img_path = os.path.join(test_images_dir, img_filename)
                        
                        if not os.path.exists(img_path):
                            try:
                                r = requests.get(img_url, timeout=15)
                                if r.status_code == 200:
                                    with open(img_path, 'wb') as f:
                                        f.write(r.content)
                                    image_count += 1
                            except:
                                pass
                                
                        # Thay thế link mạng thành link nội bộ cho MỌI ảnh tìm thấy
                        offline_link = f"./Media/{test_name}/images/{img_filename}"
                        content_html = content_html.replace(img_url, offline_link)
                
                # Cập nhật lại HTML của câu hỏi
                q['content'] = content_html

        # 3. LƯU LẠI VÀO FILE GỐC
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
            
        print(f"  -> Đã tải {audio_count} file audio và {image_count} file ảnh.")

print("\n==================================================")
print("HOÀN THÀNH TẢI XONG TẤT CẢ CÁC ĐỀ!")
print("==================================================")
