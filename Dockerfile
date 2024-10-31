FROM amazoncorretto:21-al2023-headless

ARG TARNAME=mytest1-0.1.tar

#findutils is required for the 'xargs' command
RUN dnf install -y tar findutils \
      	&& dnf clean all \
      	&& rm -rf /var/cache/yum

RUN mkdir -p /app
COPY ./build/distributions/$TARNAME /app
RUN cd /app && tar -xvf $TARNAME && rm $TARNAME
