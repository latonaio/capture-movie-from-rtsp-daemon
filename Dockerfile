FROM l4t-ds-opencv-6.2

RUN apt-get update && apt-get install -y \
    libgstrtspserver-1.0-dev \
    gstreamer1.0-rtsp \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
# Definition of a Device & Service
ENV POSITION=Runtime \
    SERVICE=capture-movie-from-rtsp-daemon \
    AION_HOME=/var/lib/aion

RUN mkdir ${AION_HOME}
WORKDIR ${AION_HOME}
# Setup Directoties
RUN mkdir -p \
    $POSITION/$SERVICE
WORKDIR ${AION_HOME}/$POSITION/$SERVICE/

ADD . . 
# RUN python3 setup.py install
# RUN sed -i "s/127.0.0.1:8554/stream-usb-video-by-rtsp-001-srv:8555/g" ./main.py

CMD ["sh", "entrypoint.sh"]
