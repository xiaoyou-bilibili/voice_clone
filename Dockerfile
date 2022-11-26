FROM registry.xiaoyou.host/pytorch/pytorch:1.9.1-cuda11.1-cudnn8-runtime
USER root
WORKDIR /code
COPY . .
RUN  apt update && apt install -y libsndfile1 && pip3 install -r requirements.txt
EXPOSE 7001
CMD ["python","web.py"]