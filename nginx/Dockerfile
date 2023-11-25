FROM nginx

COPY default.conf /etc/nginx/conf.d/default.conf
COPY cert.pem /root/cert.pem
COPY privkey.pem /root/privkey.pem
COPY chain.pem /root/chain.pem
COPY fullchain.pem /root/fullchain.pem


EXPOSE 80
EXPOSE 443
