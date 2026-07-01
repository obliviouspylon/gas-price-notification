# Gas Price Notification Service

A microservice that provides SMS notifications about tomorrow's predicted gas prices, powered by the Gas Wizard API and 680 News Enpro Gas Price.

---

## Getting Started (Docker)

This project is designed to be deployed easily and consistently using Docker.

### Prerequisites
Before you begin, ensure you have the following installed on your system:

*   [Docker](https://www.docker.com/)
*   [Docker Compose](https://docs.docker.com/compose/)

### Installation Steps

Follow these steps to build and run the service:

1.  **Clone the repository and navigate to the directory:**
    ```bash
    git clone https://github.com/obliviouspylon/gas-price-notification
    cd gas_price-notification
    ```

2.  **Build and Run the Service:**
    This command builds the Docker image (if necessary) and starts the service in detached mode (`-d`).
    ```bash
    sudo docker compose up --build -d
    ```

3.  **View Logs and Status:**
    To check if the container is running correctly and view its output:
    ```bash
    sudo docker compose logs -f
    ```

4.  **Restart the Service:**
    If you make code changes and need to gracefully restart the container:
    ```bash
    sudo docker compose restart
    ```

---

## 📂 Project Structure

The repository contains the necessary files to run the service:
gas-price-notification/
├── server.py           # Main application entry point
├── Dockerfile          # Instructions for building the Docker image
├── docker-compose.yml  # Defines services, volumes, and ports
├── requirements.txt    # Python dependencies