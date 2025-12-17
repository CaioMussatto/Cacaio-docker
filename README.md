# Cacaio Shiny App - Interactive Data Dashboard

A containerized, interactive data dashboard built with Python Shiny and deployed as a scalable, serverless service on Google Cloud Run. This project demonstrates modern application development, containerization, and cloud deployment practices.

- **[Live Application](https://cacaiodocker-407940146224.us-central1.run.app/)**
- **[Source Code](https://github.com/CaioMussatto/Cacaio-docker.git)**
- **[Docker Image](https://hub.docker.com/repository/docker/caiomussatto/cacaio-docker)**

## Table of Contents
- [Cacaio Shiny App - Interactive Data Dashboard](#cacaio-shiny-app---interactive-data-dashboard)
  - [Table of Contents](#table-of-contents)
  - [Project Overview](#project-overview)
  - [Key Features \& Technology Stack](#key-features--technology-stack)
  - [Deployment Journey \& Architecture](#deployment-journey--architecture)
  - [Local Setup \& Development](#local-setup--development)
  - [Data Download Instructions](#data-download-instructions)
    - [For Git Users (Local Development)](#for-git-users-local-development)
    - [For Docker Users](#for-docker-users)
    - [Dataset Information](#dataset-information)
  - [Project Structure](#project-structure)
  - [Contributing](#contributing)
  - [License](#license)

## Project Overview

This project addresses the challenge of deploying a computationally intensive Python Shiny application. The solution involved containerizing the app with Docker to manage its complex dependencies and memory requirements, followed by a serverless deployment on Google Cloud Run. This approach ensures reliability, easy scalability, and eliminates server management overhead.

The dashboard visualizes and allows interactive exploration of biological datasets (`sc_samples.pkl`, `degs.pkl`), utilizing libraries like `gseapy` for gene enrichment analysis.

## Key Features & Technology Stack

**Core Framework & Visualization:**
- **Shiny for Python**: Served as the primary web framework for building the reactive, interactive dashboard.
- **Pandas, NumPy, Scipy**: For robust data manipulation and scientific computing.
- **Plotly & Matplotlib**: Generated interactive and static visualizations.

**Specialized Data Analysis:**
- **GSEApy**: Performed gene set enrichment analysis directly within the app.
- **Scikit-learn & Numba**: Enabled advanced machine learning and performance-optimized computations.

**Containerization & Deployment:**
- **Docker**: Used to create a portable, self-contained image of the application and all its dependencies.
- **Google Cloud Run**: The chosen platform for serverless deployment, offering auto-scaling and pay-per-use billing.
- **Google Container Registry (GCR)**: Hosts the built Docker image for Cloud Run to access.
- **Docker Hub**: The public container image registry where the application image is also available for community use.

**Development & Tooling:**
- **UV**: An extremely fast Python package installer and resolver, used for managing project dependencies.
- **Git**: For version control.

## Deployment Journey & Architecture

Deploying this application involved several key steps that demonstrate important DevOps practices:

1. **Dependency Management**: Defined all Python packages in a `pyproject.toml` file and used `uv` for fast, reproducible dependency resolution.
2. **Containerization**:
   - A multi-stage `Dockerfile` was created to build a lean production image.
   - It copies the application code (`app.py`, `ui.py`, `server.py`), data files, and installs dependencies.
   - The container is configured to run as a non-root user for security and listens on port `8080` as required by Cloud Run.
3. **Cloud Deployment Pipeline**:
   - The Docker image was built and pushed to **Google Container Registry (GCR)** and **Docker Hub**.
   - The image was deployed to **Google Cloud Run** as a serverless service.
   - Configuration included setting memory limits (`1Gi`), CPU allocation, and a generous timeout to accommodate the app's intensive startup process.

---

**Architectural Flow:**
```
Local Code → Docker Build → Image in GCR → Cloud Run Service → Public HTTPS URL
```

## Local Setup & Development

Follow these steps to run a copy of this project on your local machine.

**Prerequisites:**
- [Docker](https://www.docker.com/get-started) installed and running.
- [Git](https://git-scm.com/) for cloning.

**Steps:**

1. **Clone the repository**:
   ```bash
   git clone https://github.com/CaioMussatto/Cacaio-docker.git 
   cd CacaioDocker
   ```

2. **Download and extract the full datasets** (required for local execution):
   ```bash
   # Download the compressed data archive
   wget https://storage.googleapis.com/dados_cacaio/cacaio_data.tar.gz
   
   # Extract to the data directory
   tar -xzf cacaio_data.tar.gz -C data/
   
   # Clean up the downloaded archive
   rm cacaio_data.tar.gz
   
   # Verify the files are present
   ls -lh data/*.pkl
   ```

3. **Build the Docker image locally**:
   ```bash
   docker build -t cacaioshiny-local .
   ```
   
   **Alternative: Pull from Docker Hub**
   ```bash
   docker pull caiomussatto/cacaio-docker:latest
   docker tag caiomussatto/cacaio-docker:latest cacaioshiny-local
   ```

4. **Run the container**:
   ```bash
   docker run --rm -p 8000:8000 cacaioshiny-local
   ```

5. **Access the application**: Open your browser and navigate to `http://localhost:8000`.

## Data Download Instructions

### For Git Users (Local Development)
When cloning this repository, you need to download the complete datasets separately as they are not included in the Git repository due to size constraints:

```bash
# From within the project directory
wget https://storage.googleapis.com/dados_cacaio/cacaio_data.tar.gz
tar -xzf cacaio_data.tar.gz -C data/
rm cacaio_data.tar.gz
```

**Note**: The application requires these data files to function correctly. Ensure they are placed in the `data/` directory before running.

### For Docker Users
The Docker image available on Docker Hub already includes the complete datasets, so no additional download is required when using the pre-built image.

### Dataset Information
- **Complete Dataset Archive**: [cacaio_data.tar.gz](https://storage.googleapis.com/dados_cacaio/cacaio_data.tar.gz)
- **Contents**: 
  - `sc_samples.pkl` (116MB): Single-cell RNA sequencing sample data
  - `degs.pkl` (73MB): Differential gene expression analysis results
- **Total Size**: ~189MB (compressed to ~160MB in tar.gz format)

## Project Structure

```
CacaioDocker/
├── app.py              # Main Shiny application entry point
├── ui.py               # User interface layout and components
├── server.py           # Server-side reactive logic
├── data.py             # Data loading and processing routines
├── functions.py        # Helper and analytical functions
├── pyproject.toml      # Project metadata and dependencies (for UV)
├── uv.lock             # Locked dependency versions
├── Dockerfile          # Multi-stage Docker build instructions
├── .dockerignore       # Files to exclude from Docker build context
├── .gitignore          # Files to exclude from version control
├── data/               # Application datasets (to be downloaded)
│   ├── degs.pkl        # Downloaded from external storage
│   └── sc_samples.pkl  # Downloaded from external storage
└── README.md           # This documentation file
```

## Contributing

Contributions, issues, and feature requests are welcome.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
