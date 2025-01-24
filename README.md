# naver_land_homeassistant
![HACS][hacs-shield]
네이버 부동산에서 아파트 호가 추적 Component입니다.

## 사용자 구성요소를 HA에 설치하는 방법
### HACS
- HACS > Integrations > 우측상단 메뉴 > `Custom repositories` 선택
- `Add custom repository URL`에 `https://github.com/chongjae/naver_land_homeassistant` 입력
- Category 는 `Integration` 선택 후 `ADD` 클릭
- HACS > Integrations 에서 `네이버 부동산 가격 추적기` 찾아서 설치
- HomeAssistant 재시작

### 수동설치
- `https://github.com/chongjae/naver_land_homeassistant` 에서 `코드 -> 소스 코드 다운로드(zip)` 을 눌러 파일을 다운로드, 내부의 `naver_land_homeassistant` 폴더 확인
- HomeAssistant 설정폴더 `/config` 내부에 `custom_components` 폴더를 생성(이미 있으면 다음 단계)<br/>설정폴더는 `configuration.yaml` 파일이 있는 폴더를 의미합니다.
- `/config/custom_components`에 위에서 다운받은 `naver_land` 폴더를 넣기
- HomeAssistant 재시작


## 사용법
### api_id 및 area 취득 방법
https://new.land.naver.com/complexes
Chrome에서 위 사이트 진입 후, 원하는 아파트 선택 후, 거래방식 / 면적 선택
개발자모드 On시킨 후, 네트워크 탭 -> Fetch/XHR 탭으로 이동
매물 드래그해서 나오는 URL확인
<img src="https://github.com/chongjae/naver_land_homeassistant/blob/master/images/get_id.png?raw=true" title="Get APT Id" alt="Get APT Id" />
복사 하면 아래와 같은 URL이 나옴
curl 'https://new.land.naver.com/api/articles/complex/111515?realEstateType=APT%3AABYG%3AJGC%3APRE&tradeType=&tag=%3A%3A%3A%3A%3A%3A%3A%3A&rentPriceMin=0&rentPriceMax=900000000&priceMin=0&priceMax=900000000&areaMin=0&areaMax=900000000&oldBuildYears&recentlyBuildYears&minHouseHoldCount&maxHouseHoldCount&showArticle=false&sameAddressGroup=false&minMaintenanceCost&maxMaintenanceCost&priceType=RETAIL&directions=&page=2&complexNo=111515&buildingNos=&areaNos=7&type=list&order=rank' \

complex/ 다음에 나오는 숫자가 apt_id
areaNos= 다음에 나오는 숫자가 area

### Configuration
/config/configuration.yaml에 아래와 같은 센서 추가
sensor 1:
  - platform: naver-land
    apt_id: 111515
    area: 7
    scan_interval: 6000