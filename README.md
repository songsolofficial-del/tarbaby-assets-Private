# ⭐ STAR BABY 애셋 자동화

그림만 그리면 → 스프라이트시트 · JSON · 썸네일 · 해상도 변형 · 색상 배리에이션 · 매니페스트까지 자동으로 나오는 파이프라인.
**Aseprite 없어도 돌아감.** 어떤 픽셀 툴이든 PNG로 export만 하면 됨.

---

## 🎨 너(디자이너)가 하는 일은 딱 2개

### 1. 규격 정하기 (한 번, 5분) — `config.json`
- `canvas`: 모든 애셋 공통 캔버스 (기본 64×64)
- `anchor`: 기준점 (발끝/중심). 합성의 전제. 전 애셋 동일해야 함.
- 이거 한 번만 정하면 끝.

### 2. 그림 그려서 폴더에 넣기
픽셀 툴(Aseprite / Piskel / Figma 아무거나)에서 그리고 **PNG 프레임으로 export**.
`src/` 밑에 **폴더 하나 = 아이템 하나**, 폴더명은 `카테고리_이름`:

```
src/
  body_base-baby/     ← 카테고리(body) _ 이름(base-baby)
    frame_000.png
    frame_001.png     ← 애니메이션이면 프레임 여러 장
    frame_002.png
  hat_star/
    frame_000.png     ← 정지면 1장만
  bg_night/
    frame_000.png
```

카테고리는 `config.json`의 `layers`에 정의된 것 사용: `bg, body, face, hair, hat, top, prop`.
→ 이 순서(z-order)대로 앱에서 자동으로 겹쳐짐.

**끝. 나머지는 전부 자동.**

---

## 🤖 자동으로 나오는 것 (`dist/`)

| 항목 | 내용 |
|---|---|
| `sheets/<id>@2x.png`, `@3x.png` | 프레임 이어붙인 스프라이트시트 (픽셀 선명, nearest) |
| `meta/<id>.json` | 프레임 수 · fps · anchor · canvas |
| `thumbs/<id>.png` | 상점용 썸네일 (첫 프레임) |
| `manifest.json` | 전체 아이템 카탈로그 (layer 순 정렬) — 앱이 이걸 읽음 |

---

## 🎨→🎨 색상 배리에이션 자동 양산 (디자이너 치트키)

베이스 **1개**만 그리면 색상 N종 자동 생성.
`config.json`에서:
```json
"variants": { "body_base-baby": ["blue", "pink", "mint", "gold", "night"] }
```
색 정의는 `palettes/palettes.json`에서 `원본색 → 바꿀색` 매핑.
→ `body_base-baby` 하나 그리면 `_blue`, `_pink` ... 5종이 자동으로 시트·JSON·썸네일까지 나옴.
(전제: 원본 스킨색을 팔레트에 등록된 hex로 칠할 것)

---

## ▶️ 실행

### 로컬에서 한 번 돌려보기
```bash
pip install pillow
python make_placeholders.py   # 데모 그림 생성 (처음 테스트용, 나중에 삭제)
python build.py               # 번들 빌드 → dist/
```

### 🌙 "자는 동안" 무인 자동화 (GitHub Actions)
1. 이 폴더를 GitHub 레포로 push
2. `.github/workflows/build.yml`이 자동으로:
   - **push 할 때마다** 빌드 (신상 그려서 올리면 즉시 번들 완성)
   - **매일 00:00 KST** 자동 빌드
   - Actions 탭에서 **수동 실행**도 가능
3. 결과물은 Actions의 artifact로 다운로드 or `dist/`에 자동 커밋

→ 밤에 `src/`에 새 아이템 올리고 push해두면, 아침엔 번들 완성돼 있음.

---

## 🔁 신상 아이템 추가하는 법 (반복 작업)
1. 픽셀 툴에서 그림 → PNG export
2. `src/카테고리_이름/`에 넣기
3. push (또는 `python build.py`)
4. 끝. 매니페스트에 자동 등록 → 앱 상점에 바로 반영 (앱 심사 불필요)

---

## 📁 구조
```
starbaby-assets/
├── config.json              # 규격 (네가 정함)
├── build.py                 # 파이프라인 (건드릴 일 없음)
├── make_placeholders.py     # 데모 생성기 (나중에 삭제)
├── palettes/palettes.json   # 색상 변형 정의
├── src/                     # 👈 여기에 그림 넣기
└── dist/                    # 👈 자동 생성 결과물 (앱이 씀)
```
