FROM python:3.6-alpine

RUN adduser -D brandsafer

WORKDIR /home/api-server

# 기본 인스톨 (gcc, g++ 등), python:3.6-alpine 에 기본포함 되지 않음
# ex) pycryptodome==3.7.3 인스톨시 필요
RUN apk add --no-cache build-base libffi-dev openssl-dev ncurses-dev
# Timezone 데이터, python:3.6-alpine 에 기본포함 되지 않음
RUN apk add tzdata

COPY requirements.txt requirements.txt
# RUN python3.6 -m venv venv
# RUN venv/bin/pip3 install --upgrade pip
# RUN venv/bin/pip3 install -r requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY app app
COPY tests tests
COPY translations translations
COPY api-server.py config.py boot.sh ./

RUN chmod +x boot.sh

# Timezone 설정
ENV TZ Asia/Seoul
ENV FLASK_APP api-server.py
ENV FLASK_ENV prod

RUN chown -R brandsafer:brandsafer ./
USER brandsafer

# AWS Configure 설정
#RUN aws configure set aws_access_key_id AKIAJTXLGJBHF7IIRLCQ \
#&& aws configure set aws_secret_access_key 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 \
#&& aws configure set region ap-northeast-2

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]