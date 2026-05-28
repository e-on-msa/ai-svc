FROM python:3.11-slim

WORKDIR /app

# 의존성 먼저 설치 (레이어 캐시 활용)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 모델 사전 다운로드 (빌드 시 캐싱 — 컨테이너 시작 시간 단축)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('snunlp/KR-SBERT-V40K-klueNLI-augSTS')"

COPY . .

EXPOSE 8086

CMD ["python", "server.py"]
