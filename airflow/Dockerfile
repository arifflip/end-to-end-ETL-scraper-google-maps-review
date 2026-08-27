FROM apache/airflow:2.8.1-python3.10

USER root

# 1. Install dependencies untuk Chrome, Xvfb, dan GPG
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    xvfb \
    libxv1 \
    libxi6 \
    libgconf-2-4 \
    libnss3 \
    libxss1 \
    libasound2 \
    fonts-liberation \
    libappindicator3-1 \
    xdg-utils \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 2. Install Google Chrome Stable (Menggunakan Keyring Modern)
RUN curl -fsSL https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /etc/apt/trusted.gpg.d/google.gpg \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# 3. Buat folder cache UC & beri akses penuh ke user airflow
RUN mkdir -p /home/airflow/.local/share/undetected_chromedriver \
    && chown -R airflow:root /home/airflow/.local

USER airflow

# 4. Install python library
RUN pip install --no-cache-dir undetected-chromedriver pyvirtualdisplay