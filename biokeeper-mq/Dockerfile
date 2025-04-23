FROM rabbitmq:management-alpine

ADD scripts/ /scripts

RUN chmod +x /scripts/*.sh

CMD ["/scripts/run.sh"]