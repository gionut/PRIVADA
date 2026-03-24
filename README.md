
# PRIVADA: Private user-centric Data Aggregation

Keywords: Data Aggregation, User Privacy, Multiple Data Customers, Secure Two-party Computation, SPDZ.

## Abstract
<details>
<summary> Privacy-preserving data aggregation has become a fundamental tool for large-scale analytics in AI-driven and
cloud-based systems. While existing solutions provide the default privacy guarantee, i.e., input confidential-
ity, most assure a semi-honest adversary model and fail to simultaneously ensure user anonymity, selective
disclosure, and result privacy in the multiple data customers environment. In this work, we introduce PRI-
VADA, a maliciously secure data aggregation solution that uses MPC in the SPDZ framework. Unlike prior
data aggregation schemes using MPC with/without SPDZ, PRIVADA supports multiple data customers while
preventing inference of user participation and resisting collusions in real-world data aggregation applications. </summary>
Moreover, our work guarantees user privacy and result privacy, in addition to input privacy. PRIVADA out-
performs the state-of-the-art solutions by providing security against participating parties, including malicious
data owners, aggregators, and data customers. Our proof-of-concept implementation also supports the new
privacy-preserving data aggregation by combining malicious security, being available for multiple data cus-
tomers, and ensuring strong privacy guarantees in large-scale deployments. The aggregation operation on
the aggregator side becomes simpler with PRIVADA, and experimental results show a 12–15 times speedup
compared to the state-of-the-art. This confirms that malicious security and strong privacy guarantees can be
achievable without sacrificing practicality.
</details>

## Setup and Installation

### 1. Clone Repository with Submodules
Clone the repository including all submodules:

```bash
git submodule update --init --recursive
```

### 2. Build Docker Image
Follow the MP-SPDZ documentation to build the `mpspdz:spdz2k-party` docker image:

```bash
docker build --tag mpspdz:spdz2k-party --build-arg machine=spdz2k-party.x .
```

## Configuration and Preparation

### 3. Navigate to PRIVADA Directory
```bash
cd PRIVADA
```

### 4. Create SSL Certificates
Generate certificates for communication between clients and parties:

```bash
make prida+_ssl
```

> **⚠️ Warning:** For N=15000, this step may take a considerable amount of time. Proceed with caution.

### 5. Copy Data Scripts
Copy the data owner and customer scripts to the MP-SPDZ external I/O directory:

```bash
cp Programs/Source/data_owner.py ../MP-SPDZ/ExternalIO/data_owner.py
cp Programs/Source/data_customer.py ../MP-SPDZ/ExternalIO/data_customer.py
```

### 6. Create Docker Containers
Set up the necessary docker containers (ensure docker daemon is running):

```bash
make create_containers
```

> **Note:** Make sure the docker daemon is running before executing this command.

## Running Evaluation

### 7. Run Batch Evaluation
Execute batch evaluation with the specified parameters:

```bash
python Programs/Source/run_batch.py \
  -N 100 \
  -M 1 \
  --batch-size 500 \
  --n-batch-size 700 \
  --prog prida+_readability \
  --timeout 10 \
  --times 1 \
  --n-threads 1 \
  --log-dir logs
```

**Parameter Description:**
- `-N 100`: Number of participants (N)
- `-M 1`: Number of machines (M)
- `--batch-size 500`: Batch size for processing
- `--n-batch-size 700`: Batch size for N processing
- `--prog prida+_readability`: Program to run
- `--timeout 10`: Timeout in seconds
- `--times 1`: Number of iterations
- `--n-threads 1`: Number of threads
- `--log-dir logs`: Directory for logs output