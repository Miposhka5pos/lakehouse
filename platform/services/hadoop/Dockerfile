
FROM apache/hadoop:3.3.6

USER root

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
