PHONY: prida+_ssl prida+_compute prida+_clients benchmark_prida+ prida+_compute_docker prida+_clients_docker

# clone the repo including the submodules
# git submodule update --init --recursive
# cd PRIDA
# make prida+_ssl // This will create certificates for the communication between clients and parties
# cp Programs/Source/data_owner.py ../MP-SPDZ/ExternalIO/data_owner.py
# cp Programs/Source/data_customers.py ../MP-SPDZ/ExternalIO/data_customer.py
# make create_containers // Makes sure docker deamon is on
# // Run evaluation in batches
# python Programs/Source/run_batch.py -N 100 -M 1 --batch-size 500 --n-batch-size 700 --prog prida+_readability --timeout 10 --times 1 --n-threads 1 --log-dir logs

N=15000
M=1000
prida+_ssl:
	../MP-SPDZ/Scripts/setup-ssl.sh 2
	../MP-SPDZ/Scripts/setup-clients.sh $$(($(N)+$(M))) > /dev/null 2>&1

prida+_compute_docker:
	docker exec prida_plus sh -c "./compile.py prida+ 10 1"
	docker exec prida_plus sh -c "spdz2k-party.x 1 prida+ -h localhost -N 2 -v " > logs_1.txt 2>&1 &
	docker exec prida_plus sh -c "spdz2k-party.x 0 prida+ -h localhost -N 2 -v " > logs_0.txt 2>&1 &

run_service:
	docker exec pridaservice sh -c "./compile.py prida+_readability -M -E spdz2k 1 1 1 1"
	docker exec pridaservice sh -c "spdz2k-party.x 1 prida+_readability-1-1-1-1  -h localhost -N 2 -v " > logs_1.txt 2>&1 &
	docker exec pridaservice sh -c "spdz2k-party.x 0 prida+_readability-1-1-1-1  -h localhost -N 2 -v " > logs_0.txt 2>&1 &

run_clients:
	for i in $(shell seq 0 $$(($(N)-1))); do \
		docker exec doservice sh -c "./ExternalIO/data_owner.py $$i 2 $(M)" & \
	done; \
	for i in $(shell seq 0 $$(($(M)-1))); do \
		docker exec dcservice sh -c "./ExternalIO/data_customer.py $$(($(N)+$$i)) 2" & \
	done;

pwd := $(CURDIR)
create_containers:
# 	mkdir logs
# 	docker network create pridanet
	docker run -d -it --name pridaservice --network pridanet --mount type=bind,source="$(pwd)"/logs,target=/usr/src/MP-SPDZ/logs --mount type=bind,source="$(pwd)"/Programs/Source,target=/usr/src/MP-SPDZ/Programs/Source --mount type=bind,source="$(pwd)"/Player-Data,target=/usr/src/MP-SPDZ/Player-Data --mount type=bind,source="$(pwd)"/../MP-SPDZ/ExternalIO,target=/usr/src/MP-SPDZ/ExternalIO --mount type=bind,source="$(pwd)"/Programs/Schedules,target=/usr/src/MP-SPDZ/Programs/Schedules --mount type=bind,source="$(pwd)"/Programs/Bytecode,target=/usr/src/MP-SPDZ/Programs/Bytecode mpspdz:spdz2k-party
	docker run -d -it --name doservice --network pridanet --mount type=bind,source="$(pwd)"/logs,target=/usr/src/MP-SPDZ/logs --mount type=bind,source="$(pwd)"/Programs/Source,target=/usr/src/MP-SPDZ/Programs/Source --mount type=bind,source="$(pwd)"/Player-Data,target=/usr/src/MP-SPDZ/Player-Data --mount type=bind,source="$(pwd)"/../MP-SPDZ/ExternalIO,target=/usr/src/MP-SPDZ/ExternalIO --mount type=bind,source="$(pwd)"/Programs/Schedules,target=/usr/src/MP-SPDZ/Programs/Schedules --mount type=bind,source="$(pwd)"/Programs/Bytecode,target=/usr/src/MP-SPDZ/Programs/Bytecode mpspdz:spdz2k-party
	docker run -d -it --name dcservice --network pridanet --mount type=bind,source="$(pwd)"/logs,target=/usr/src/MP-SPDZ/logs --mount type=bind,source="$(pwd)"/Programs/Source,target=/usr/src/MP-SPDZ/Programs/Source --mount type=bind,source="$(pwd)"/Player-Data,target=/usr/src/MP-SPDZ/Player-Data --mount type=bind,source="$(pwd)"/../MP-SPDZ/ExternalIO,target=/usr/src/MP-SPDZ/ExternalIO --mount type=bind,source="$(pwd)"/Programs/Schedules,target=/usr/src/MP-SPDZ/Programs/Schedules --mount type=bind,source="$(pwd)"/Programs/Bytecode,target=/usr/src/MP-SPDZ/Programs/Bytecode mpspdz:spdz2k-party


# python parse_mem_files.py
# python average.py
# python plotting_mem.py