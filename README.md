## 💬 커밋 메시지 컨벤션
| Tag              | Description                                 |
|------------------|---------------------------------------------|
| `feat`      | 새로운 기능 추가                             |
| `fix`       | 버그 수정                                    |
| `docs`      | 문서 추가, 수정                                 |
| `test`      | 테스트 코드 추가, 수정                   |
| `style`     | 코드 포맷팅, 세미콜론 누락 등 (로직 변경 없음) |
| `refactor`  | 코드 리팩토링                                |
| `build`     | 빌드 시스템 또는 의존성 변경                  |
| `deploy`    | 배포 관련 변경                            |
| `chore`     | 설정 파일, 기타 잡일                         |
<br/>

## 🗂️ 프로젝트 구조

```
tripto/
├── .github/              # GitHub 관련 설정
├── app/                  # 메인 애플리케이션 로직
│   ├── agent/            # AI 에이전트 관련 로직
│   ├── api/              # API 엔드포인트 및 라우터 설정
│   │   ├── __init__.py
│   │   ├── api.py              
│   │   └── v1/
│   │       └── endpoints/
│   │           ├── user.py       # 유저/친구 관련 API
│   │           ├── plan.py       # 여행 관련 API
│   │           ├── vote.py       # 투표 관련 API
│   │           ├── chat.py       # 채팅 관련 API
│   │           ├── notification.py # 알림 관련 API
│   │           └── place.py      # 장소 검색 및 추천 장소 조회 API
│   ├── core/             # 공통 설정
│   │   ├── __init__.py
│   │   ├── config.py             # 환경 변수 (Pydantic Settings - API Keys, DB URL)
│   │   ├── database.py           # DB 연결 설정
│   │   └── security.py           # 인증/인가
│   ├── infra/            # 외부 인프라 연결
│   ├── models/           # SQLAlchemy DB 모델 정의
│   │   ├── user_models.py
|   |   ├── plan_models.py
|   |   ├── vote_models.py
|   |   ├── chat_models.py
|   |   ├── notification_models.py
|   |   └── place_models.py
│   ├── schemas/          # Pydantic 데이터 검증 스키마
│   │   ├── user_schemas.py
|   |   ├── plan_schemas.py
|   |   ├── vote_schemas.py
|   |   ├── chat_schemas.py
|   |   ├── notification_schemas.py
|   |   └── place_schemas.py
│   ├── services/         # 비즈니스 로직 처리
│   │   ├── user_services.py
|   |   ├── plan_services.py
|   |   ├── vote_services.py
|   |   ├── chat_services.py
|   |   ├── notification_services.py
|   |   └── place_services.py
│   └── main.py           # 애플리케이션 실행 진입점
├── migrations/           # Alembic 데이터베이스 마이그레이션 파일 - git 제외
│   ├── versions/
│   └── env.py
├── .env                  # 환경 변수 설정 파일 - git 제외
├── .gitignore            # Git 제외 설정
├── alembic.ini           # Alembic 설정 파일 - git 제외
└── requirements.txt      # 프로젝트 의존성 라이브러리 목록
```
