FROM ubuntu:latest
# Install Java JRE.
RUN apt-get update && \
    apt-get install openjdk-8-jdk python -y

# Install HBase
RUN apt-get update && \
    apt-get install wget && \
    mkdir -p /data/zookeeper && \
    mkdir -p /opt/hbase && \
    cd /tmp && \
    wget -O hbase.tar.gz http://ftp.tudelft.nl/apache/hbase/stable/hbase-1.2.5-bin.tar.gz && \
    tar xf hbase.tar.gz && \
    mv hbase*/* /opt/hbase && \
    rm /tmp/hbase.tar.gz && \
    rmdir /tmp/hbase* && \
    echo 'export JAVA_HOME=/usr' >> /opt/hbase/conf/hbase-env.sh
ADD conf/hbase-site.xml /opt/hbase/conf/hbase-site.xml
ADD conf/starthbase.sh /starthbase.sh
RUN chmod +x /starthbase.sh

# Install OpenTSDB
RUN cd /tmp && \
    wget https://github.com/OpenTSDB/opentsdb/releases/download/v2.3.0/opentsdb-2.3.0_all.deb && \
    apt-get install /tmp/opentsdb-2.3.0_all.deb
RUN /starthbase.sh & proc=$! && sleep 10 && \
    env COMPRESSION=NONE HBASE_HOME=/opt/hbase /usr/share/opentsdb/tools/create_table.sh && \
    kill -INT $proc
EXPOSE 4242

# Install and setup supervisord
RUN apt-get update && \
    apt-get install supervisor -y
ADD conf/supervisord.conf /etc/supervisord.conf
CMD supervisord -c /etc/supervisord.conf
