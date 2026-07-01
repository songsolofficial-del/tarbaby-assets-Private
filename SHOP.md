# 상점 가격 구조

모든 아이템 매니페스트에 필드 추가됨:
  shop      : 상점 판매 여부 (기본 아기만 false)
  starCost  : 별 가격 (지금은 비어있음 null)

## 가격 넣는 법 (나중에)
config.json 의 itemMeta 에 숫자만 채우기:

  "itemMeta": {
    "hat_summer":  { "starCost": 10 },
    "hat_wizard":  { "starCost": 12 },
    "face_smile":  { "starCost": 8 },
    "face_sleep":  { "starCost": 6 }
  }

python3 build.py 돌리면 매니페스트 dist/manifest.json 에 자동 반영.
색상 아기(_rose 등)도 팔고 싶으면 itemMeta 에 추가하면 됨.

## 반영
build.py + config.json 을 clone 폴더에 덮어쓰기 -> commit -> push
