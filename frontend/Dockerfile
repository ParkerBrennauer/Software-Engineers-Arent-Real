#Switch to node.js docker template once frontend is implemented
FROM alpine:latest
LABEL Name=softwareengineersarentreal Version=0.0.1
RUN apk add --no-cache fortune
ENTRYPOINT ["sh", "-c", "fortune -a | cat"]
