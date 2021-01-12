FROM ubuntu
RUN apt-get update && \
    apt-get install python3 python3-pip git vim curl -y && \
    pip3 install numpy netCDF4 matplotlib Flask && \
    git clone https://github.com/aayushgandhi/ScaaS.git && \
    chmod +x /ScaaS/app.sh
EXPOSE 5000
EXPOSE 8888
CMD '/ScaaS/app.sh'