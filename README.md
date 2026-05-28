# ai-svc

E-ON 플랫폼의 AI 추천 도메인을 담당하는 마이크로서비스입니다.
한국어 문장 임베딩 모델(KR-SBERT)을 사용해 사용자 프로필과 챌린지 간 유사도를 계산하고 추천 ID를 반환합니다.

## 📁 프로젝트 구조

```
ai-svc/
├── server.py        # Flask 서버 진입점
├── requirements.txt
├── Dockerfile
├── .env.example
└── .gitignore
```

## 🚀 로컬 실행 방법

```bash
# 1. 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2. 패키지 설치
pip install -r requirements.txt

# 3. 서버 실행
python server.py
```

서버가 정상적으로 실행되면 아래 메시지가 출력됩니다.

```
 * Running on http://0.0.0.0:8086
```

> 최초 실행 시 모델(`snunlp/KR-SBERT-V40K-klueNLI-augSTS`) 다운로드가 자동으로 진행됩니다. 수백 MB 크기이므로 시간이 걸릴 수 있습니다.

## 🐳 Docker 실행 방법

```bash
# 이미지 빌드 (모델 사전 다운로드 포함)
docker build -t ai-svc .

# 컨테이너 실행
docker run -p 8086:8086 --env-file .env ai-svc
```

## 🔗 API

이 서비스는 외부에 직접 노출되지 않고 recommendation-svc에서만 호출합니다.

### `GET /internal/health`

서버 상태 확인 (Docker healthcheck 용)

**Response**
```json
{
  "status": "ok",
  "model": "KR-SBERT-V40K-klueNLI-augSTS"
}
```

---

### `POST /internal/recommend`

사용자 텍스트와 챌린지 목록을 받아 유사도 기반 추천 ID를 반환합니다.

**Request Body**
```json
{
  "user_text": "관심사: 코딩, 환경. 진로: 개발자. 참여한 챌린지: ...",
  "challenges": [
    { "id": 1, "text": "챌린지 제목: 코딩 챌린지. 설명: ..." },
    { "id": 2, "text": "챌린지 제목: 환경 지킴이. 설명: ..." }
  ]
}
```

**Response**
```json
{
  "recommended_ids": [2, 1]
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| `user_text` | string | 필수. 사용자 활동/관심사 요약 문장 |
| `challenges` | array | 필수. 추천 후보 챌린지 목록 |
| `challenges[].id` | integer | 챌린지 ID |
| `challenges[].text` | string | 임베딩에 사용할 챌린지 설명 텍스트 |

## 🤖 추천 흐름

```
recommendation-svc
  └── POST /internal/recommend
              ↓
        user_text 임베딩 (KR-SBERT)
        challenges 임베딩 (KR-SBERT)
              ↓
        코사인 유사도 계산
              ↓
        상위 TOP_K개 ID 반환
              ↓
  recommendation-svc에서 순서대로 챌린지 정렬
```

## ⚙️ 환경변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `PORT` | `8086` | 서버 포트 |
| `TOP_K` | `5` | 반환할 추천 챌린지 개수 |

## 📝 커밋 컨벤션

| 타입 | 설명 |
|------|------|
| `feat` | 새 기능 추가 |
| `fix` | 버그 수정 |
| `docs` | 문서 작업 |
| `refactor` | 기능 변경 없이 코드 구조 개선 |
| `chore` | 빌드, 패키지, 설정 변경 |

## 🌿 브랜치 전략

```
main
└── feat/#이슈번호-작업내용
```

```bash
# 브랜치 생성 예시
git checkout -b feat/#1-embedding-recommend
```
