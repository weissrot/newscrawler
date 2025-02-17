# Start with a base Ubuntu image
FROM ubuntu:20.04

# Avoid interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    ca-certificates \
    libx11-dev \
    libxkbfile-dev \
    libsecret-1-dev \
    xdg-utils \
    wget \
    && apt-get clean

# Add Google Chrome's signing key
RUN curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | tee /usr/share/keyrings/google-chrome-keyring.gpg

# Add Google's Chrome repository to the list of apt sources
RUN echo "deb [signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list

# Install Google Chrome
RUN apt-get update && apt-get install -y google-chrome-stable && apt-get clean

# Install Xvfb for headless mode (necessary for running Chrome headlessly)
RUN apt-get install -y xvfb

# Set default command to run Chrome in headless mode
CMD ["google-chrome-stable", "--headless", "--disable-gpu", "--no-sandbox", "--remote-debugging-port=9222"]
