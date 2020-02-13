# Pilot Project: Crawler

## Web Spider

### Obey robots.txt

- https://developers.google.com/search/reference/robots_txt

### Crawl documents

- Support HTTP/HTTPS
    - https://multifrontgarden.tistory.com/219
- Dequeue and crawl URL
- remove duplicated site (bfs처럼)
- limit by depth (예시)

### Parse HTML

- Retrieve `<a href>` attribute

### Follow link

- Enqueue the URL to be crawled

## Search OpenAPI

### Search web documents

- Query inputed keyword
- Enqueue URLs searched

## User Interface

- by Web browser
- Input search keyword
- List og: objects of crawled documents


### Planning
 - use db?
 - on demand?
 - https://developers.facebook.com/tools/debug/sharing/?q=https%3A%2F%2Fsupport.google.com%2Fwebmasters%2Fanswer%2F6062608%3Fhl%3Dko
 - 얼마나 크롤링할지
 - 얼마나 보여줄지
 - nested한 링크 어떻게 처리
 - search api와 크롤러의 역할

### naver openapi
 - Client ID: XI45JOPUhLNDIiOBlooN
 - Client Secret: XnY40nbqyJ


### 정리
 - open api로 키워드 검색
 1. Pick a URL from the frontier
 2. Fetch the HTML code
 3. Parse the HTML to extract links to other URLs
 4. Check if you have already crawled the URLs and/or if you have seen the same content before
    - If not add it to the index
 5. For each extracted URL
    - Confirm that it agrees to be checked (robots.txt, crawling frequency)

