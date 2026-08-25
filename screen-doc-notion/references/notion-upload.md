# Notion 이미지 업로드 & 문서 작성

## 이미지 업로드 (3단계)

Notion MCP는 로컬 파일을 직접 못 올린다. **업로드 URL 발급 → curl POST → markdown_source 삽입** 순서.

### 1) 업로드 URL 발급
```
notion-create-file-upload(filename: "01_list.png")
```
응답:
```json
{
  "file_upload_id": "3c64...",
  "upload_url": "https://api.notion.com/v1/mcp/file_uploads/3c64.../send",
  "upload_headers": { "authorization": "Bearer eyJ..." },
  "upload_form_field": "file",
  "expires_at": "..."   ← 수 분 내 만료
}
```

### 2) 파일 전송
```bash
curl -sS -X POST "<upload_url>" \
  -H "authorization: <upload_headers.authorization 값>" \
  -F "file=@/path/to/01_list.png;type=image/png"
```
응답에 `"status":"uploaded"`와 `"markdown_source":"file-upload://<id>"`가 온다.

### 3) 문서에 삽입
```html
<image src="file-upload://<file_upload_id>"></image>
```

### 여러 장 올릴 때
`notion-create-file-upload`를 **한 번에 병렬 호출**해 URL들을 먼저 받고, curl을 순차 실행하면 빠르다. 셸 함수로 묶으면 편하다.

```bash
up() { curl -sS -X POST "https://api.notion.com/v1/mcp/file_uploads/$1/send" \
        -H "authorization: Bearer $2" -F "file=@$3;type=image/png" \
     | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('status'),d.get('markdown_source'))"; }
up "<id>" "<token>" "<파일>"
```

> 업로드 URL이 만료되면 처음부터 다시 발급한다. 발급 후 지체 없이 올릴 것.

## 문서 작성

```
notion-update-page(page_id, command: "replace_content", new_str: "<전체 마크다운>")
```
- `replace_content` — 전체 교체 (빈 페이지에 처음 쓸 때)
- `insert_content` — 뒤에 추가 (기존 내용 유지)
- `update_content` — 부분 치환 (old_str/new_str)

표는 마크다운 표 문법이 Notion 표로 렌더링된다. 인용(`>`), 체크박스, 코드블록도 그대로 동작한다.

## 작성 후 검증 (필수)

```
notion-fetch(page_id)
```
확인할 것:
- 이미지가 `![](https://prod-files-secure.s3...)` 형태로 치환됐는가 (그대로 `file-upload://`면 실패)
- 표가 `<table header-row="true">`로 렌더링됐는가
- 제목 계층(#, ##, ###)이 유지됐는가

## 마무리

페이지 제목과 아이콘을 정리하면 완성도가 올라간다.
```
notion-update-page(page_id, command: "update_properties",
                   properties: {"title": "<문서 제목>"}, icon: "💬")
```

## 주의

- 문서에 **개인정보가 들어간 스크린샷을 올리지 않는다.** Notion은 공유되는 공간이다.
- 페이지가 데이터베이스 하위면 title 외 속성이 있을 수 있으니 `notion-fetch`로 스키마를 먼저 확인한다.
