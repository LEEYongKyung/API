DB 테이블
===============

Table 목록
------------
테이블 명 | 설명 | DB 종류
--------|-----|------
[users](https://github.com/zaiyou12/brandsafer-api-server/blob/master/docs/db.md#users)|사용자 정보 | MongoDB
[company](https://github.com/zaiyou12/brandsafer-api-server/blob/master/docs/db.md#company)| 회사 코드 | MongoDB
[certifications](https://github.com/zaiyou12/brandsafer-api-server/blob/master/docs/db.md#certifications) | 인증 정보 | MongoDB
[reports](https://github.com/zaiyou12/brandsafer-api-server/blob/master/docs/db.md#reports) | 제보하기 | MongoDB
[contact_us](https://github.com/zaiyou12/brandsafer-api-server/blob/master/docs/db.md#contact_us) | 문의하기 | MongoDB
[statics](https://github.com/zaiyou12/brandsafer-api-server/blob/master/docs/db.md#statics) | 통계 | MongoDB

Users
------------
```json
{
  "model": "Device의 모델명",
  "os_type": "android/ios",
  "os_ver": "Device의 OS 버전",
  "app_type": "App 코드",
  "app_ver": "App 버전",
  "language": "Device의 언어 설정 상태",
  "token": "모바일 고유 토큰 (Char 152)",

  "tos": "이용약관 동의 여부 (bool) | default = false",
  "is_black": "블랙리스트 여부 (bool) | default = false",
  "certifications": ["ObjectID('AAAA')", "ObjectID('F17C')"],
  "reports": ["ObjectID('AAAA')", "ObjectID('F17C')"],
  "contacts": ["ObjectID('AAAA')", "ObjectID('F17C')"]
}
```

> 유저 기본정보 예시: iPhone6S;iOS;9.7.2;ARCI199999;01.00.01;KO;129874643786

Company
------------
```json
{
  "name": "회사 이름",
  "code": "회사 코드"
}
```

Certifications
------------
```json
{
  "random_num": "난수 번호 (int)",
  "count": "난수 총 인증 횟수 (int)",
  "list": [{
    "company": "회사 이름 (string)",
    "token": "Device token (char 152)",
    "result": "인증 결과 (int)",
    "photo_url": "사진 (url)",
    "gps_type": "gps 종류 (int)",
    "latitude": "경도 (float)",
    "longitude": "위도 (float)",
    "address": "주소지 (string)",
    "data": "인증 날짜(Date)"
  }]
}
```

> 'random_num': 난수 번호/Integer, 'datetime': 인증 시간/datetime

Reports
------------
```json
{
    "random_num": "난수 번호 (int)",
    "auth_date": "인증 날짜 (Date)",
    "company": "회사 이름 (string)",
    "token": "Device token (char 152)",
    "result": "인증 결과 (int)",
    "photo_url": "사진 (url)",
    "gps_type": "gps 종류 (int)",
    "latitude": "경도 (float)",
    "longitude": "위도 (float)",
    "email": "test@test.com",
    "tel": "01012341234",
    "report_content": "문의 내용 기록(text)",
    "confirm": "확인 여부(boolean) | default = false",
    "date": "제보 날짜(Date)"
}
```

> 제보하기 데이터의 빠른 호출 및 처리를 위해, 인증하기 파트와 데이터 중복을 감수하고 데이터 구조 평면화, 추후 빅데이터 분석에 용이.

Contact_us
------------
```json
{
    "token": "Device token (char 152)",
    "email": "test@test.com",
    "tel": "01012341234",
    "report_type": "문의 하기 유형 (string)",
    "report_content": "문의 내용 기록 (text)",
    "confirm": "확인 여부(boolean) | default = false",
    "date": "문의 날짜(Date)"
}
```

Statics
------------
```json
{
  "admin": {
    "certification_count": "인증 총합",
    "report_count": "제보하기 총합",
    "contact_us_count": "문의하기 총합"
  },

  "total": {
    "genuine_count": "정품 총합",
    "fake_count": "가품 총합",

    "206": "블랙리스트 총합",
    "208": "DB에 존재하지 않는 총합"
  },
  "company_name_1": {
    "genuine_count": "정품 총합",
    "fake_count": "가품 총합",

    "206": "블랙리스트 총합",
    "208": "DB에 존재하지 않는 총합"
  },
  "company_name_2": {
    "genuine_count": "정품 총합",
    "fake_count": "가품 총합",

    "206": "블랙리스트 총합",
    "208": "DB에 존재하지 않는 총합"
  },

  "address": {
    "XiangGang": "지역별 총합",
    "GuangDongSheng": "지역별 총합",
    "LiaoNingSheng": "지역별 총합"
  }
}
```