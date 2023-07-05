# python 3.10.6버전 이미지를 사용해 빌드
FROM python:3.10.6-slim

# .pyc 파일을 생성하지 않도록 설정합니다.
ENV PYTHONDONTWRITEBYTECODE 1

# 파이썬 로그가 버퍼링 없이 즉각적으로 출력하도록 설정합니다.
ENV PYTHONUNBUFFERED 1

# /app/ 디렉토리를 생성합니다.
RUN mkdir /app/

# /app/ 경로를 작업 디렉토리로 설정합니다.
WORKDIR /app/

# pip를 최신 버전으로 업그레이드합니다.
RUN pip install --upgrade pip

# requirments.txt를 작업 디렉토리(/app/) 경로로 복사합니다.
COPY ./requirements.txt .

# slim 이미지에서 postgresql 패키지를 설치하기 위해 필요 명령어 추가 + ffmpeg
RUN apt update && apt install libpq-dev gcc ffmpeg -y

# 프로젝트 실행에 필요한 패키지들을 설치합니다.
RUN pip install tensorflow-cpu
RUN pip install --no-deps spleeter
RUN pip install --no-cache-dir -r requirements.txt

# gunicorn을 사용하기 위한 패키지를 설치합니다.
RUN pip install gunicorn psycopg2
