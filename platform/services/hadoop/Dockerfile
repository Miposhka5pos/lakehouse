
FROM apache/hadoop:3.4.3

USER root

# Python 3.10 для Spark на YARN
RUN curl -fL \
    https://repo.anaconda.com/miniconda/Miniconda3-py310_24.3.0-0-Linux-x86_64.sh \
    -o /tmp/miniconda.sh \
    && bash /tmp/miniconda.sh -b -p /opt/conda \
    && ln -s /opt/conda/bin/python3 /usr/local/bin/python3 \
    && rm -f /tmp/miniconda.sh

ENV PATH="/opt/conda/bin:${PATH}"

RUN mkdir -p \
    /data/dfs/name \
    /data/dfs/data \
    /data/yarn/local \
    /data/yarn/logs \
    && chown -R hadoop:users /data \
    && chmod 755 /data \
    && chmod 700 /data/dfs/name /data/dfs/data \
    && chmod 755 /data/yarn \
    && chmod 755 /data/yarn/local /data/yarn/logs

USER hadoop
