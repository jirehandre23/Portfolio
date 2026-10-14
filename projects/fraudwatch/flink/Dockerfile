FROM flink:1.20.1-scala_2.12-java17
USER root
RUN wget -q https://repo.maven.apache.org/maven2/org/apache/flink/flink-sql-connector-kafka/3.3.0-1.20/flink-sql-connector-kafka-3.3.0-1.20.jar -O /opt/flink/lib/flink-sql-connector-kafka.jar
USER flink
COPY pipeline.sql /opt/flink/pipeline.sql
