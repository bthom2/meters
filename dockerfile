# syntax=docker/dockerfile:1

FROM ubuntu
RUN apt update
RUN apt upgrade -y
ARG DEBIAN_FRONTEND=noninteractive
RUN apt install -y git cmake g++ libboost-all-dev libgmp-dev swig python3-numpy python3-mako python3-sphinx python3-lxml doxygen libfftw3-dev libsdl1.2-dev libgsl-dev libqwt-qt5-dev libqt5opengl5-dev python3-pyqt5 liblog4cpp5-dev libzmq3-dev python3-yaml python3-click python3-click-plugins python3-zmq python3-scipy python3-gi python3-gi-cairo gobject-introspection gir1.2-gtk-3.0 xterm
RUN apt install -y liborc-0.4-dev vim nano
RUN apt install -y software-properties-common mosquitto-clients unzip wget
RUN add-apt-repository ppa:gnuradio/gnuradio-releases-3.8
RUN apt update
RUN apt install -y gnuradio
WORKDIR /opt/
RUN mkdir sdr-drivers
WORKDIR /opt/sdr-drivers
RUN apt-get install -y libusb-1.0-0-dev git cmake
RUN apt-get install -y dbus-x11
RUN git clone git://git.osmocom.org/rtl-sdr.git
WORKDIR /opt/sdr-drivers/rtl-sdr/
RUN mkdir build
WORKDIR /opt/sdr-drivers/rtl-sdr/build
RUN cmake ../ -DINSTALL_UDEV_RULES=ON
RUN make
RUN make install
RUN cp ../rtl-sdr.rules /etc/udev/rules.d/
RUN ldconfig
WORKDIR /opt/
RUN git clone git://git.osmocom.org/gr-osmosdr 
WORKDIR /opt/gr-osmosdr/
RUN git checkout gr3.8
RUN mkdir build
WORKDIR /opt/gr-osmosdr/build
RUN cmake ../
RUN make
RUN make install
RUN ldconfig
WORKDIR /opt/gr-osmosdr/
RUN mkdir Utils
WORKDIR /opt/gr-osmosdr/Utils
RUN git clone https://github.com/sandialabs/gr-pdu_utils.git
WORKDIR /opt/gr-osmosdr/Utils/gr-pdu_utils
RUN git checkout maint-3.8
RUN mkdir build
WORKDIR /opt/gr-osmosdr/Utils/gr-pdu_utils/build
RUN cmake ..
RUN make -j8
RUN make install
RUN ldconfig
WORKDIR /opt/gr-osmosdr/Utils
RUN git clone https://github.com/sandialabs/gr-fhss_utils.git
WORKDIR /opt/gr-osmosdr/Utils/gr-fhss_utils/
RUN git checkout maint-3.8
RUN mkdir build
WORKDIR /opt/gr-osmosdr/Utils/gr-fhss_utils/build
RUN cmake ..
RUN make -j8
RUN make install
RUN ldconfig
WORKDIR /opt/gr-osmosdr/Utils
RUN git clone https://github.com/sandialabs/gr-timing_utils.git
WORKDIR /opt/gr-osmosdr/Utils/gr-timing_utils/
RUN git checkout maint-3.8
RUN mkdir build
WORKDIR /opt/gr-osmosdr/Utils/gr-timing_utils/build
RUN cmake ..
RUN make -j8
RUN make install
RUN ldconfig
WORKDIR /opt/gr-osmosdr/Utils
RUN git clone https://github.com/sandialabs/gr-sandia_utils.git
WORKDIR /opt/gr-osmosdr/Utils/gr-sandia_utils/
RUN git checkout maint-3.8
RUN mkdir build
WORKDIR /opt/gr-osmosdr/Utils/gr-sandia_utils/build/
RUN cmake ..
RUN make -j8
RUN make install
RUN ldconfig
WORKDIR /opt/gr-osmosdr/
RUN curl https://bootstrap.pypa.io/pip/2.7/get-pip.py --output get-pip.py
RUN python2 get-pip.py
RUN pip2 install numpy
RUN git clone https://github.com/BitBangingBytes/gr-smart_meters.git
WORKDIR /opt/gr-osmosdr/gr-smart_meters/
RUN git checkout maint-3.8
WORKDIR /opt/gr-osmosdr/gr-smart_meters/build
RUN cmake ..
RUN make -j8
RUN make install
RUN ldconfig
WORKDIR /opt/gr-osmosdr/
RUN mkdir reveng
WORKDIR /opt/gr-osmosdr/reveng/
RUN wget https://downloads.sourceforge.net/project/reveng/3.0.2/reveng-3.0.2.zip
RUN unzip reveng-3.0.2.zip
WORKDIR /opt/gr-osmosdr/reveng/reveng-3.0.2/
RUN sed -i 's/#define BMP_SUB   16/#define BMP_SUB   32/' config.h
RUN sed -i 's/#define BMP_BIT   32/#define BMP_BIT   64/' config.h
RUN make
ENV PYTHONPATH="/usr/local/lib/python3/dist-packages/"
RUN echo 'export PYTHONPATH=/usr/local/lib/python3/dist-packages/' >> /root/.bashrc
RUN apt install -y mosquitto-clients openssh-server
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config
WORKDIR /opt
RUN git clone https://github.com/bthom2/meters.git
RUN mv /opt/meters/.gnuradio /root
WORKDIR /opt/meters/
RUN chmod +x startup.sh
RUN echo 'root:sdr' | chpasswd 
ENTRYPOINT "/opt/meters/startup.sh"