Methods 목록
===========

- [약관 동의](https://github.com/zaiyou12/brandsafer-api-server/blob/master/docs/methods.md#term-of-service-%EC%95%BD%EA%B4%80-%EB%8F%99%EC%9D%98)
- [정품 인증](https://github.com/zaiyou12/brandsafer-api-server/blob/master/docs/methods.md#authenticity-%EC%A0%95%ED%92%88-%EC%9D%B8%EC%A6%9D)
- [제보 하기](https://github.com/zaiyou12/brandsafer-api-server/blob/master/docs/methods.md#report-fake-%EC%A0%9C%EB%B3%B4-%ED%95%98%EA%B8%B0)
- [문의 하기](https://github.com/zaiyou12/brandsafer-api-server/blob/master/docs/methods.md#contact-us-%EB%AC%B8%EC%9D%98-%ED%95%98%EA%B8%B0)


Term-of-service (약관 동의)
----------

### Method
```bash
POST
```

### URL Path
```bash
/terms-of-service
```

### JSON [요청]
```json
{
    "model": "Device의 모델명",
    "os_type": "android/ios",
    "os_ver": "Device의 OS 버전",
    "app_type": "App 코드",
    "app_ver": "App 버전",
    "language": "Device의 언어 설정 상태",

    "auth": "약관 동의 여부 (bool)"
}
```

### 결과
```json
{
    "status" : 201
}
```

Authenticity (정품 인증)
-----------

### Method

```bash
POST
```

### URL Path

```bash
/authenticity
```

### 요청

```json
{
    "random_num": "난수 문자",
    "photo": "사진 파일 (BSON)",
    "gps_type": "gps 종류 (int)",
    "latitude": "경도 (float)",
    "longitude": "위도 (float)"
}
```

> gps_type: 0. 모바일 gps, 1. wi-fi gps 2. 최근 gps. [안드로이드 참고문서](https://developer.android.com/guide/topics/location/strategies.html)

### 요청 예시

```json
{
    "random_num": "1643",
    "photo": "180401_123.png",
    "gps_type": 1,
    "latitude": 42.222,
    "longitude": 12.222
}
```

### 결과

```json
{
    "status": 201,
    "result": "정품 여부 (bool)",
    "result_msg": "가품일 때의 상세 메시지",
    "date": "인증 시간 (datetime/UTC)"
}
```

### 결과 예시

```json
{
    "status": 201,
    "result": true,
    "result_msg": "여러 번 인증된 가짜 제품입니다.",
    "date": "Sun, 29 Apr 2018 18:32:27 GMT"
}
```

Report-fake (제보 하기)
---------------
### Method

```bash
POST
```

### URL Path

```bash
/report-fake
```

### JSON [요청]

```json
{
    "random_num": "난수 문자 (str)",
    "authenticity_date": "정품 인증 시간 (datetime/UTC)",
    "email": "이메일 (str)",
    "tel": "국가번호-전화번호 (str)",
    "report_content": "문의 내용 기록 (str)"
}
```

> tel: 국가번호와 전화번호를 `-`로 구분하고, 전화번호는 `-`이나 뛰어쓰기 없이 숫자로만 구성.

### Example [예시]

```json
{
    "random_num": "test",
    "authenticity_date": "Sun, 29 Apr 2018 18:32:27 GMT",
    "email": "test@test.com",
    "tel": "82-1012341234",
    "report_content": "문의 내용 기록"
}
```

### 결과

```json
{
    "status": 201,
    "date": "등록 시간 (datetime/UTC)"
}
```

Contact-us (문의 하기)
------------
### Method

```bash
POST
```

### URL Path

```bash
/contact-us
```

### JSON [요청]

```json
{
    "email": "이메일 (str)",
    "tel": "전화번호 (str)",
    "report_type": "리포트 타입 (int)",
    "report_content": "문의 내용 기록 (str)"
}
```

> report_type: 사전 정의한 문의 종류 필요. 예시) 1. 사용 방법 문의 2. 제품 추가 문의 3. 기타 문의

> tel: 국가번호와 전화번호를 `-`로 구분하고, 전화번호는 `-`이나 뛰어쓰기 없이 숫자로만 구성.

### Example [요청]

```json
{
    "email": "test@test.com",
    "tel": "82-1012341234",
    "report_type": 1,
    "report_content": "문의합니다 oooooo이 ooo다."
}
```

### 결과

```json
{
    "status": 201,
    "date": "등록 시간(datetime/UTC)"
}
```
