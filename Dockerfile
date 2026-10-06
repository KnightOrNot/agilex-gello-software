FROM nvidia/cuda:11.8.0-devel-ubuntu22.04

WORKDIR /agilex-gello-software

# Set environment variables first (less likely to change)
ENV PYTHONPATH=/agilex-gello-software/src

# Group apt updates and installs together
RUN apt update && apt install -y \
    libhidapi-dev \
    python3-pip \
    android-tools-adb \
    libegl1-mesa-dev && \
    rm -rf /var/lib/apt/lists/* 


# Python alias setup
RUN echo "alias python=python3" >> ~/.bashrc

# Install Python dependencies
COPY pyproject.toml uv.lock README.md LICENSE /agilex-gello-software/
RUN pip install uv && uv sync --frozen --no-dev --no-install-project
COPY src /agilex-gello-software/src
RUN uv sync --frozen --no-dev
