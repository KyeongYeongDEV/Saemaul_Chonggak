# [Plan] env-config

> `.env` 파일 기반 환경변수 관리 — 로컬/운영 환경 분리 및 시크릿 안전 관리

---

## 1. 개요

| 항목 | 내용 |
|------|------|
| 기능명 | Environment Variable Config (.env 기반 환경변수 관리) |
| 연관 프로젝트 | Saemaul Chonggak Shopping Server |
| 핵심 목표 | 시크릿(DB 비밀번호, JWT 키 등)을 `.env` 파일로 중앙 관리 |
| 적용 범위 | 로컬 개발, Docker Compose, CI/CD (GitHub Actions) |

---

## 2. 현재 상태 및 문제점

### 2.1 현재 구조

```
application.yml             ← 공통 설정 (공개 가능)
application-local.yml       ← 로컬 시크릿 (gitignore) ← 현재: YOUR_DB_PASSWORD 하드코딩
application-local.yml.example ← 로컬 템플릿
application-prod.yml        ← 운영 시크릿 (gitignore) ← 이미 ${ENV_VAR} 방식
application-prod.yml.example  ← 운영 템플릿
```

### 2.2 문제점

- `application-local.yml`은 `YOUR_DB_PASSWORD` 하드코딩 방식 → 실수로 시크릿 노출 위험
- 로컬 개발과 Docker Compose 환경이 따로 관리됨 (중복)
- 신규 개발자가 값을 알기 어려움 (어디에 뭘 입력해야 하는지 불명확)

---

## 3. 목표 구조 (.env 방식)

### 3.1 환경변수 흐름

```
.env                       ← 시크릿 실제 값 (gitignore, 로컬 전용)
.env.example               ← 변수명만 있는 템플릿 (git 포함, 신규 개발자 가이드)
    │
    ├── application-local.yml  ← ${DB_PASSWORD} 방식으로 읽음
    │   (spring-dotenv 또는 IntelliJ env 설정)
    │
    └── docker-compose.local.yml  ← env_file: .env 로 컨테이너에 주입
```

### 3.2 환경별 시크릿 주입 방식

| 환경 | 방식 | 파일 |
|------|------|------|
| 로컬 (IDE 직접 실행) | spring-dotenv 라이브러리 | `.env` 자동 로드 |
| 로컬 (Docker Compose) | `env_file: .env` | `.env` 자동 로드 |
| 운영 (EC2) | OS 환경변수 또는 GitHub Actions Secrets | 별도 파일 없음 |
| CI/CD (GitHub Actions) | Secrets → 환경변수 주입 | `.env` 미사용 |

---

## 4. 기능 범위 (Scope)

### 4.1 포함 (In-Scope)

- [ ] **`.env.example` 작성**: 전체 환경변수 목록 (변수명 + 설명, 값은 빈칸)
- [ ] **`application-local.yml` 전환**: `YOUR_DB_PASSWORD` → `${DB_PASSWORD}` 방식
- [ ] **`docker-compose.local.yml` 업데이트**: `env_file: .env` 적용
- [ ] **`spring-dotenv` 라이브러리 추가**: IDE 직접 실행 시 `.env` 자동 로드
- [ ] **신규 개발자 온보딩 가이드 작성**: `.env` 설정 절차 문서화 (README 또는 CONTRIBUTING.md)

### 4.2 제외 (Out-of-Scope)

- 운영 환경 시크릿 관리 (AWS Secrets Manager, Vault 등) — 현재는 GitHub Actions Secrets 유지
- Firebase 서비스 계정 JSON 파일 관리 (별도 처리 필요)

---

## 5. 환경변수 목록

### 5.1 전체 변수 정의

| 변수명 | 예시값 | 설명 | 필수 |
|--------|--------|------|------|
| **DB** | | | |
| `DB_HOST` | `localhost` | MySQL 호스트 | ✅ |
| `DB_PORT` | `3306` | MySQL 포트 | ✅ |
| `DB_NAME` | `saemaul_chonggak` | 데이터베이스명 | ✅ |
| `DB_USERNAME` | `root` | DB 사용자명 | ✅ |
| `DB_PASSWORD` | `your_password` | DB 비밀번호 | ✅ |
| **Redis** | | | |
| `REDIS_HOST` | `localhost` | Redis 호스트 | ✅ |
| `REDIS_PORT` | `6379` | Redis 포트 | ✅ |
| **JWT** | | | |
| `JWT_SECRET` | `min-32-char-random-string` | JWT 서명 키 (32자 이상) | ✅ |
| **OAuth2** | | | |
| `KAKAO_CLIENT_ID` | `abc123` | 카카오 앱 REST API 키 | ✅ |
| `KAKAO_CLIENT_SECRET` | `secret` | 카카오 Client Secret | ✅ |
| `NAVER_CLIENT_ID` | `xyz789` | 네이버 클라이언트 ID | ✅ |
| `NAVER_CLIENT_SECRET` | `secret` | 네이버 클라이언트 시크릿 | ✅ |
| **AWS** | | | |
| `AWS_ACCESS_KEY` | `AKIA...` | AWS IAM 액세스 키 | ✅ |
| `AWS_SECRET_KEY` | `wJalrXUt...` | AWS IAM 시크릿 키 | ✅ |
| `AWS_REGION` | `ap-northeast-2` | AWS 리전 | ✅ |
| `S3_BUCKET_NAME` | `saemaul-chonggak-dev` | S3 버킷명 | ✅ |
| **토스페이먼츠** | | | |
| `TOSS_SECRET_KEY` | `test_sk_...` | 토스 시크릿 키 (테스트/운영 구분) | ✅ |
| `TOSS_CLIENT_KEY` | `test_ck_...` | 토스 클라이언트 키 | ✅ |
| **앱 설정** | | | |
| `SPRING_PROFILES_ACTIVE` | `local` | 활성 프로파일 | ✅ |
| `APP_BASE_URL` | `http://localhost:8080` | 앱 기본 URL (OAuth redirect 등) | ✅ |

### 5.2 `.env.example` 형식

```dotenv
# ── Database ─────────────────────────────────
DB_HOST=localhost
DB_PORT=3306
DB_NAME=saemaul_chonggak
DB_USERNAME=root
DB_PASSWORD=

# ── Redis ────────────────────────────────────
REDIS_HOST=localhost
REDIS_PORT=6379

# ── JWT (32자 이상 랜덤 문자열) ──────────────
JWT_SECRET=

# ── OAuth2 ───────────────────────────────────
KAKAO_CLIENT_ID=
KAKAO_CLIENT_SECRET=
NAVER_CLIENT_ID=
NAVER_CLIENT_SECRET=

# ── AWS ──────────────────────────────────────
AWS_ACCESS_KEY=
AWS_SECRET_KEY=
AWS_REGION=ap-northeast-2
S3_BUCKET_NAME=saemaul-chonggak-dev

# ── 토스페이먼츠 (테스트: test_sk_... / 운영: live_sk_...) ─
TOSS_SECRET_KEY=
TOSS_CLIENT_KEY=

# ── App ──────────────────────────────────────
SPRING_PROFILES_ACTIVE=local
APP_BASE_URL=http://localhost:8080
```

---

## 6. 기술 전략

### 6.1 spring-dotenv 라이브러리

```
역할: IDE(IntelliJ/VS Code)에서 Spring Boot 직접 실행 시 .env 파일 자동 로드
위치: src/main/resources/.env (또는 프로젝트 루트 .env)
방식: Spring PropertySource로 자동 등록
```

**의존성 추가** (`build.gradle.kts`):
```kotlin
implementation("me.paulschwarz:spring-dotenv:4.0.0")
```

> 라이브러리 없이 쓰려면: IntelliJ Run Configuration > "EnvFile" 플러그인으로 .env 로드

### 6.2 application-local.yml 변경 방향

```yaml
# 변경 전 (하드코딩 방식)
spring:
  datasource:
    password: YOUR_DB_PASSWORD

# 변경 후 (.env 연동 방식)
spring:
  datasource:
    url: jdbc:mysql://${DB_HOST}:${DB_PORT}/${DB_NAME}?useSSL=false&...
    username: ${DB_USERNAME}
    password: ${DB_PASSWORD}
```

### 6.3 docker-compose.local.yml 변경 방향

```yaml
services:
  app_blue:
    env_file:
      - .env
    environment:
      SPRING_PROFILES_ACTIVE: local

  redis:
    ...

  mysql:
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_PASSWORD}
      MYSQL_DATABASE: ${DB_NAME}
```

---

## 7. 신규 개발자 온보딩 절차

```
1. git clone 후:
   cp .env.example .env

2. .env 파일을 열어 실제 값 입력
   (팀원에게 값 공유받거나 각자 발급)

3. 로컬 DB/Redis 실행:
   docker-compose -f docker-compose.local.yml up -d mysql redis

4. Spring Boot 실행:
   ./gradlew bootRun
   (spring-dotenv가 .env 자동 로드)
```

---

## 8. 보안 고려사항

- `.env`는 절대 git 커밋 금지 (`.gitignore`에 이미 포함)
- `.env.example`에는 실제 값 입력 금지 (빈 값 또는 예시 형식만)
- AWS IAM 키는 개발/운영 분리 (최소 권한 원칙)
- JWT_SECRET은 `openssl rand -base64 64` 로 생성 권장

---

## 9. 미결 사항 (Open Questions)

- [ ] Firebase 서비스 계정 JSON 파일 관리 방법 결정 (env var로 JSON 경로 지정 vs 파일 직접 관리)
- [ ] 팀 시크릿 공유 방법 결정 (1Password, Slack DM, GitHub Codespaces Secrets 등)

---

**작성일**: 2026-02-28
**작성자**: Claude Code (Sonnet 4.6)
**상태**: Draft
**연관 설계**: shopping-server.design.md (Section 10.2 application.yml)
