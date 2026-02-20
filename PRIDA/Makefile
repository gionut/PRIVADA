PHONY: compile run run0 run1 test_receive_from_clients prida+_ssl prida+_compute prida+_clients benchmark_prida+ prida+_compute_docker prida+_clients_docker

compile:
	../MP-SPDZ/compile.py $(FILE)

run:
	../MP-SPDZ/Scripts/compile-run.py -E spdz2k $(FILE)

run0:
	../MP-SPDZ/Scripts/../spdz2k-party.x 0 prida -pn 12501 -h localhost -N 2

run1:
	../MP-SPDZ/Scripts/../spdz2k-party.x 1 prida -pn 12501 -h localhost -N 2

test_receive_from_clients:
	../MP-SPDZ/compile.py client_connection_manager
	# ../MP-SPDZ/Scripts/setup-ssl.sh 2
	# ../MP-SPDZ/Scripts/setup-clients.sh 6
	../MP-SPDZ/Scripts/../spdz2k-party.x 0 -pn 12501 client_connection_manager -h localhost -N 2 &
	../MP-SPDZ/Scripts/../spdz2k-party.x 1 -pn 12501 client_connection_manager -h localhost -N 2 &
	../MP-SPDZ/ExternalIO/data_owner.py 0 2 &
	../MP-SPDZ/ExternalIO/data_owner.py 1 2 &
	../MP-SPDZ/ExternalIO/data_owner.py 2 2 &
	../MP-SPDZ/ExternalIO/data_customer.py 3 2 &
	../MP-SPDZ/ExternalIO/data_customer.py 4 2 &
	../MP-SPDZ/ExternalIO/data_customer.py 5 2

N=10000
M=100
prida+_ssl:
	../MP-SPDZ/Scripts/setup-ssl.sh 2
	../MP-SPDZ/Scripts/setup-clients.sh $$(($(N)+$(M))) > /dev/null 2>&1

prida+_compute:
	@../MP-SPDZ/compile.py -l prida+
	@../MP-SPDZ/Scripts/../spdz2k-party.x 1 prida+ -h localhost -N 2 &
	@../MP-SPDZ/Scripts/../spdz2k-party.x 0 prida+ -h localhost -N 2 -v -t 2>&1 | tee ./benchmark/$(N)DO_$(M)DC_$(index).log &

prida+_clients:
	for i in $(shell seq 0 $$(($(N)-1))); do \
		../MP-SPDZ/ExternalIO/data_owner.py $$i 2 $(M) 2>&1 | tee ./do/$(N)DO_$(M)DC_$(index).log & \
	done; \
	for i in $(shell seq 0 $$(($(M)-1))); do \
		../MP-SPDZ/ExternalIO/data_customer.py $$(($(N)+$$i)) 2 2>&1 | tee ./dc/$(N)DO_$(M)DC_$(index).log & \
	done;

benchmark_prida+:
	@for i in $(shell seq 1 1); do \
		echo "Iteration $$i:"; \
		make prida+_compute index=$$i; \
		make prida+_clients index=$$i; \
		while ! grep -q "Program Finished" ./benchmark/$(N)DO_$(M)DC_$$i.log; do \
			echo "Waiting for prida+_compute to finish..."; \
			sleep 1; \
		done; \
		echo "Program Completed!"; \
	done

@for i in $(shell seq 0 1); do \
	output=$$(make prida+_compute); \
	echo $output; \
	make prida+_clients; \
done

	../MP-SPDZ/compile.py -l prida+
	../MP-SPDZ/Scripts/../spdz2k-party.x 1 prida+ -pn 12000 -h localhost -N 2 &
	../MP-SPDZ/Scripts/../spdz2k-party.x 0 prida+ -pn 12001 -h localhost -N 2 -v & 

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
	docker network create pridanet
	docker run -d -it --name pridaservice --network pridanet --mount type=bind,source="$(pwd)"/logs,target=/usr/src/MP-SPDZ/logs --mount type=bind,source="$(pwd)"/Programs/Source,target=/usr/src/MP-SPDZ/Programs/Source --mount type=bind,source="$(pwd)"/Player-Data,target=/usr/src/MP-SPDZ/Player-Data --mount type=bind,source="$(pwd)"/../MP-SPDZ/ExternalIO,target=/usr/src/MP-SPDZ/ExternalIO --mount type=bind,source="$(pwd)"/Programs/Schedules,target=/usr/src/MP-SPDZ/Programs/Schedules --mount type=bind,source="$(pwd)"/Programs/Bytecode,target=/usr/src/MP-SPDZ/Programs/Bytecode mpspdz:spdz2k-party
	docker run -d -it --name doservice --network pridanet --mount type=bind,source="$(pwd)"/logs,target=/usr/src/MP-SPDZ/logs --mount type=bind,source="$(pwd)"/Programs/Source,target=/usr/src/MP-SPDZ/Programs/Source --mount type=bind,source="$(pwd)"/Player-Data,target=/usr/src/MP-SPDZ/Player-Data --mount type=bind,source="$(pwd)"/../MP-SPDZ/ExternalIO,target=/usr/src/MP-SPDZ/ExternalIO --mount type=bind,source="$(pwd)"/Programs/Schedules,target=/usr/src/MP-SPDZ/Programs/Schedules --mount type=bind,source="$(pwd)"/Programs/Bytecode,target=/usr/src/MP-SPDZ/Programs/Bytecode mpspdz:spdz2k-party
	docker run -d -it --name dcservice --network pridanet --mount type=bind,source="$(pwd)"/logs,target=/usr/src/MP-SPDZ/logs --mount type=bind,source="$(pwd)"/Programs/Source,target=/usr/src/MP-SPDZ/Programs/Source --mount type=bind,source="$(pwd)"/Player-Data,target=/usr/src/MP-SPDZ/Player-Data --mount type=bind,source="$(pwd)"/../MP-SPDZ/ExternalIO,target=/usr/src/MP-SPDZ/ExternalIO --mount type=bind,source="$(pwd)"/Programs/Schedules,target=/usr/src/MP-SPDZ/Programs/Schedules --mount type=bind,source="$(pwd)"/Programs/Bytecode,target=/usr/src/MP-SPDZ/Programs/Bytecode mpspdz:spdz2k-party
 	
# Run evaluation in batches
# python Programs/Source/run_batch.py -N 5000 -M 1 --batch-size 500 --n-batch-size 700 --prog prida+_readability --timeout 60 --times 1 --n-threads 13 --log-dir logs/tests