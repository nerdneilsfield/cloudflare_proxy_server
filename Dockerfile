FROM python:3-alpine
LABEL Author="nerdneilsfield<dengqi935@gmail.com>"
WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8888

CMD [ "python", "./server.py" ]