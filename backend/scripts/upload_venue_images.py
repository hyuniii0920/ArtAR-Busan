"""안드로이드 앱용 장소 대표 이미지를 public GCS 버킷에 업로드.

증빙 문서가 든 비공개 버킷(artar-busan-assets)과 분리된 전용 public 버킷을 사용한다.
업로드 후 public HTTPS URL을 출력한다. (일회성 운영 스크립트)
"""

from google.cloud import storage

BUCKET = "artar-busan-public"
LOCATION = "asia-northeast3"
PREFIX = "images"
SRC_DIR = r"C:\Users\junwoo\Desktop\4학년1학기\캡스톤디자인\아트부산_더미사진"

# 원본 파일명 → 안드로이드 로컬 리소스명(타깃 키)
MAPPING = {
    "부산현대미술관 (해운대구).jpg": "museum_busan_moca.jpg",
    "F1963 (수영구).jpg": "museum_f1963.jpg",
    "부산시립미술관 (해운대구).jpg": "museum_busan_art.jpg",
    "고은사진미술관 (해운대구).jpg": "museum_goeun_photo.jpg",
    "아르떼뮤지엄 부산 (영도구).jpg": "museum_arte_busan.jpg",
    "부산근대역사관 (중구).jpg": "museum_modern_history.jpg",
    "민주공원 (중구).jpg": "museum_democracy_park.jpg",
    "금정문화회관 (금정구).jpg": "museum_geumjeong_culture.jpg",
}


def main() -> None:
    client = storage.Client()
    bucket = client.bucket(BUCKET)

    if not bucket.exists():
        bucket.iam_configuration.uniform_bucket_level_access_enabled = True
        client.create_bucket(bucket, location=LOCATION)
        print(f"created bucket: {BUCKET} ({LOCATION})")
    else:
        print(f"bucket exists: {BUCKET}")

    # allUsers 읽기 권한 (public) — 멱등
    policy = bucket.get_iam_policy(requested_policy_version=3)
    role = "roles/storage.objectViewer"
    if not any(
        b["role"] == role and "allUsers" in b.get("members", set())
        for b in policy.bindings
    ):
        policy.bindings.append({"role": role, "members": {"allUsers"}})
        bucket.set_iam_policy(policy)
        print("granted allUsers objectViewer (public read)")
    else:
        print("public read already granted")

    import os

    print("\n--- uploaded URLs ---")
    for src_name, target in MAPPING.items():
        src = os.path.join(SRC_DIR, src_name)
        key = f"{PREFIX}/{target}"
        blob = bucket.blob(key)
        blob.cache_control = "public, max-age=86400"
        blob.upload_from_filename(src, content_type="image/jpeg")
        print(f"https://storage.googleapis.com/{BUCKET}/{key}")


if __name__ == "__main__":
    main()
