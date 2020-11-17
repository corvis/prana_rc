FROM python:3.7

ARG prana_version
ARG release_date
ARG is_beta=False

RUN apt-get update --no-install-recommends \
  && apt-get install -y bluez \
  && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["prana"]
CMD ["http-server"]

RUN pip install prana-rc[server-tornado]==${prana_version}

LABEL x.prana.version="${prana_version}" \
      x.prana.release-date="${release_date}" \
      x.prana.is-beta="${is_beta}"
