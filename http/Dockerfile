FROM nginx:1.27-alpine3.19
RUN rm /etc/nginx/conf.d/default.conf
COPY ["./nginx.conf", "/etc/nginx/conf.d/"]
