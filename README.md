# naver_land
![HACS][hacs-shield]
네이버 부동산에서 아파트 호가 추적 Component입니다.

## 사용자 구성요소를 HA에 설치하는 방법
### HACS
- HACS > Integrations > 우측상단 메뉴 > `Custom repositories` 선택
- `Add custom repository URL`에 `https://github.com/chongjae/naver_land` 입력
- Category 는 `Integration` 선택 후 `ADD` 클릭
- HACS > Integrations 에서 `네이버부동산시` 찾아서 설치
- HomeAssistant 재시작

### 수동설치
- `https://github.com/chongjae/naver_land` 에서 `코드 -> 소스 코드 다운로드(zip)` 을 눌러 파일을 다운로드, 내부의 `naver_land` 폴더 확인
- HomeAssistant 설정폴더 `/config` 내부에 `custom_components` 폴더를 생성(이미 있으면 다음 단계)<br/>설정폴더는 `configuration.yaml` 파일이 있는 폴더를 의미합니다.
- `/config/custom_components`에 위에서 다운받은 `naver_land` 폴더를 넣기
- HomeAssistant 재시작


## 사용법
### apt_id 및 area 취득 방법
https://new.land.naver.com/complexes
Chrome에서 위 사이트 진입 후, 원하는 아파트 선택 후, 거래방식 / 면적 선택
개발자모드 On시킨 후, 네트워크 탭 -> Fetch/XHR 탭으로 이동
매물 드래그해서 나오는 URL확인
<img src="https://github.com/chongjae/naver_land/blob/master/images/get_id.png?raw=true" title="Get APT Id" alt="Get APT Id" />


복사 하면 아래와 같은 URL이 나옴
curl 'https://new.land.naver.com/api/articles/complex/111515?realEstateType=APT%3AABYG%3AJGC%3APRE&tradeType=&tag=%3A%3A%3A%3A%3A%3A%3A%3A&rentPriceMin=0&rentPriceMax=900000000&priceMin=0&priceMax=900000000&areaMin=0&areaMax=900000000&oldBuildYears&recentlyBuildYears&minHouseHoldCount&maxHouseHoldCount&showArticle=false&sameAddressGroup=false&minMaintenanceCost&maxMaintenanceCost&priceType=RETAIL&directions=&page=2&complexNo=111515&buildingNos=&areaNos=7&type=list&order=rank' \

complex/ 다음에 나오는 숫자가 apt_id
areaNos= 다음에 나오는 숫자가 area

### Configuration
통합 구성요소에서 naver_land 검색하여 추가
위에서 찾은 apt_id와 원하는 평형 추가(평형이 단순 숫자가 아니라 18%3A21%3A20%3A19%3A23%3A24%3A22 이런식이 될 수도 있음.)
Ex,
apt_id : 111515
area : 7

3개의 Entity가 추가되며, min,max의 attributes는 아래와 같이 추가됨.
**ArticleName**
헬리오시티
**FloorInfo**
저/23
**DealOrWarrantPrc**
18억 9,000
**AreaName**
84A
**Direction**
남향
**ArticleConfirmYmd**
20250114
**ArticleFeatureDesc**
입주협의 로얄타입 내부풀옵션 매물
**TagList**
10년이내, 대단지, 방세개, 화장실두개
**BuildingName**
214동
**CpName**
선방
**CpPcArticleUrl**
http://homesdid.co.kr/rd.asp?UID=2502579792

<img src="https://github.com/chongjae/naver_land/blob/master/images/info.png?raw=true" title="Get APT Id" alt="Get APT Id" />


distribution을 이용하여 apexchart를 그릴 수 있음.
아래 예시는 각 날짜의 중앙값 데이터를 Y축에 찍어주는 그래프

<img src="https://github.com/chongjae/naver_land/blob/master/images/chart.png?raw=true" title="Get APT Id" alt="Get APT Id" />


type: custom:apexcharts-card
graph_span: 21d
header:
  show: true
  title: 아파트 호가
series:
  - entity: sensor.111515_price_distribution
    name: 헬리오시티
    type: line
    data_generator: |
      const groupedData = {};  

      // 데이터 그룹화  
      Object.entries(entity.attributes)  
        .filter(([key]) => !key.includes('device_class') && !key.includes('friendly_name'))  
        .forEach(([dateKey, values]) => {  
          if (!groupedData[dateKey]) {  
            groupedData[dateKey] = [];  
          }  
          groupedData[dateKey].push(...values.map(Number)); // 숫자로 변환하여 추가  
        });  

      // 중앙값 계산  
      const data = Object.entries(groupedData)  
        .map(([dateKey, values]) => {  
          values.sort((a, b) => a - b); // 오름차순 정렬  
          const mid = Math.floor(values.length / 2);  
          const median = values.length % 2 !== 0 ?   
            values[mid] :   
            (values[mid - 1] + values[mid]) / 2; // 중앙값 계산  

          return {  
            x: new Date(dateKey).getTime(),  // X축에 타임스탬프 설정  
            y: median // 중앙값을 Y축 값으로 설정  
          };  
        })  
        .sort((a, b) => a.x - b.x); // 날짜순으로 정렬  

      return data;  
