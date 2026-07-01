# 업데이트 내용
- 베이스 아기 새 버전으로 통일 (둥근 후드, 깜빡+숨쉬기 16프레임)
- 모자 2종: hat_summer(밀짚), hat_wizard(마법사)
- 색상 변형 자동화: config.json variants + palettes/palettes.json (후드 5색: sky/rose/mint/butter/night)
- 새 도구 2개:
  - fit_item.py : 이미지 던지면 자동 변환+정렬+흔들림
      python3 fit_item.py <이미지> hat_이름 --width 46 --y 20
      (색 뭉개지면 --colors 8, 위치는 --y 로 조절)
  - breathe_item.py : 정지 아이템 1장 -> 16프레임 흔들림

# 반영
1. 이 파일들을 clone 폴더에 덮어쓰기 (config.json, palettes/, src/, fit_item.py, breathe_item.py)
2. GitHub Desktop -> commit -> push
3. Actions 초록 = 색상 5종 + 모자 2종까지 자동 빌드 완료
