
# ------------------------------------------------------------
# Stage 1: Build MinIO from pinned source code
# ------------------------------------------------------------
FROM --platform=$BUILDPLATFORM golang:1.24.8-alpine3.22 AS build

ARG TARGETOS
ARG TARGETARCH
ARG MINIO_COMMIT
ARG MINIO_COMMIT_TIME

RUN apk add --no-cache \
    bash \
    git \
    make \
    perl \
    ca-certificates

WORKDIR /src

COPY . .

# Normalize Windows CRLF to Linux LF in shell scripts.
RUN find . -type f \( -name '*.sh' -o -name '*.bash' \) \
    -exec sed -i 's/\r$//' {} +

# Validate pinned metadata.
RUN test -n "$MINIO_COMMIT" \
    && test -n "$MINIO_COMMIT_TIME"

# Use the pinned commit ID instead of querying Git history.
# This modification exists only inside the temporary build image.
RUN perl -0pi -e 's/func commitID\(\) string \{/func commitID() string {\n\tif id := os.Getenv("MINIO_COMMIT"); id != "" { return id }\n/' \
    buildscripts/gen-ldflags.go

# Generate linker flags and run the official MinIO build target.
RUN export MINIO_COMMIT="$MINIO_COMMIT" \
    && LDFLAGS="$(MINIO_RELEASE=RELEASE go run buildscripts/gen-ldflags.go "$MINIO_COMMIT_TIME")" \
    && make build \
        GOOS="$TARGETOS" \
        GOARCH="$TARGETARCH" \
        LDFLAGS="$LDFLAGS"

# ------------------------------------------------------------
# Stage 2: Minimal runtime image
# ------------------------------------------------------------
FROM alpine:3.22 AS runtime

ARG MINIO_COMMIT

LABEL org.opencontainers.image.revision="${MINIO_COMMIT}"

RUN apk add --no-cache ca-certificates \
    && command -v chroot

COPY --from=build /src/minio /usr/bin/minio
COPY --from=build /src/dockerscripts/docker-entrypoint.sh /usr/bin/docker-entrypoint.sh

RUN chmod +x /usr/bin/minio /usr/bin/docker-entrypoint.sh

EXPOSE 9000
VOLUME ["/data"]

ENTRYPOINT ["/usr/bin/docker-entrypoint.sh"]
CMD ["minio"]
