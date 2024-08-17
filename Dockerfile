FROM python:3.11-slim
# Create user, we need $HOME/.config
RUN useradd --create-home --shell /bin/bash synapseadmin
# Create app dir and switch context (irrelevant on pypi inst)
RUN mkdir /synadm_app
WORKDIR /synadm_app
COPY . .

WORKDIR /home/synapseadmin
RUN \
    chown -R synapseadmin:synapseadmin /home/synapseadmin && \
    chmod -R 755 /home/synapseadmin
# User home on volume (will be prepoluated on first init)
VOLUME /home/synapseadmin
# Run as non-root user from here
USER synapseadmin
# Add user bin to path
ENV PATH="/home/synapseadmin/.local/bin:$PATH"
# Install synadm from pypi
RUN pip install --upgrade pip && \
    pip install --no-cache-dir synadm && \
    chown -R synapseadmin:synapseadmin /home/synapseadmin && \
    chmod -R 755 /home/synapseadmin

