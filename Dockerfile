FROM python:3.7

WORKDIR /mnt

# install java (needed for firestore emulator)
RUN \
  apt-get update && \
  apt-get -y install openjdk-11-jdk

# install gcloud cli and firestore emulator
ENV CLOUDSDK_CORE_DISABLE_PROMPTS=1
RUN curl https://sdk.cloud.google.com | bash
RUN echo 'source /root/google-cloud-sdk/path.bash.inc' >> ~/.bashrc
RUN echo 'source /root/google-cloud-sdk/completion.bash.inc' >> ~/.bashrc
RUN /root/google-cloud-sdk/bin/gcloud components install cloud-firestore-emulator
RUN /root/google-cloud-sdk/bin/gcloud components install beta

# install python requirements
COPY requirements-dev.txt ./
COPY src/requirements.txt ./src/
RUN pip install --no-cache-dir -r requirements-dev.txt
