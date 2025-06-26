#declare what image to use
#from codingforentpreneurs/cfe-nginx:latest
#from image_name:latest

FROM python:3.13.3-slim-bullseye
WORKDIR /app
#react static pp
#vue static
# COPY local_folder container_folder
#RUN mkdir -p /static_folder
#COPY ./static_html /static_folder

#same destination is app
#COPY ./static_html /app
COPY . .

#RUN echo "hello" > index.html


#docker build -f Dockerfile -t pyapp .
#docker run -it pyapp

#docker build -f Dockerfile -t codingforentrepreneurs/ai-py-app-test:latest .
#docker push codingforentrepreneurs/ai-py-app-test:latest

#docker build -f Dockerfile -t codingforentrepreneurs/ai-py-app-test:v1 .
#docker push codingforentrepreneurs/ai-py-app-test:v1

#python -m http.server 8000
#docker run -it -p 3000:8000 pyapp
#docker run -it -p 8000:8000 pyapp
CMD ["python","-m","http.server","8000"]
