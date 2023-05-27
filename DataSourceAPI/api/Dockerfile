FROM python:3.11-slim-bullseye
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
RUN pip install fastapi uvicorn
RUN pip install requests
RUN pip install openai
RUN pip install aiohttp
RUN pip install six
RUN pip install pandas-datareader
RUN pip install oandapyV20


RUN mkdir /app
COPY ./ /app
WORKDIR /app

ENTRYPOINT ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8002"]

EXPOSE 8002