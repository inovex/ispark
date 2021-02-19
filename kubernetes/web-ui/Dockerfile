#base-image
FROM python:3.7.2-slim

WORKDIR /usr/src/app

COPY app/requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# install necessary dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    apt-transport-https \
    curl \
    gnupg \
    ca-certificates \
    lsb-release \
    unzip \
    git \
    jq \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*


# install kubectl
RUN export CLOUD_SDK_REPO="cloud-sdk-$(lsb_release -c -s)" && \
    echo "deb https://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" > /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
    apt-get update && \
    apt-get install -y google-cloud-sdk kubectl



#5000 for flask
EXPOSE 5000

COPY app /usr/src/app/

RUN chmod +x start.sh

CMD ./start.sh
