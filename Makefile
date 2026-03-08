.PHONY: proto deps run

# Variables
HELIOS_PROTO_SOURCE_DIR=helios-protos
HELIOS_PROTO_BUILD_DIR=generated/helios
FALCON_PROTO_SOURCE_DIR=falcon-protos
FALCON_PROTO_BUILD_DIR=generated/falcon

# Find all .proto files in the proto directory and subdirectories
HELIOS_PROTO_SRC := $(wildcard $(HELIOS_PROTO_SOURCE_DIR)/**/*.proto)
FALCON_PROTO_SRC := $(wildcard $(FALCON_PROTO_SOURCE_DIR)/**/*.proto)

# 1=true, 0=false
DOCKER_DISABLED=1
export DOCKER_DISABLED

# Commands
proto: $(HELIOS_PROTO_BUILD_DIR) $(FALCON_PROTO_BUILD_DIR)
	protoc -I=$(HELIOS_PROTO_SOURCE_DIR) --python_out=$(HELIOS_PROTO_BUILD_DIR) $(HELIOS_PROTO_SRC)
	protoc -I=$(FALCON_PROTO_SOURCE_DIR) --python_out=$(FALCON_PROTO_BUILD_DIR) $(FALCON_PROTO_SRC)

# Create the directory if it doesn't exist
$(HELIOS_PROTO_BUILD_DIR):
	mkdir -p $(HELIOS_PROTO_BUILD_DIR)

$(FALCON_PROTO_BUILD_DIR):
	mkdir -p $(FALCON_PROTO_BUILD_DIR)

deps:
	uv run sync

run:
	ifeq ($(wildcard $(HELIOS_PROTO_BUILD_DIR)/.),)
		$(error Helios Protobuf build directory not found. Please run 'make proto')
	else ifeq ($(wildcard $(FALCON_PROTO_BUILD_DIR)/.),)
		$(error Falcon Protobuf build directory not found. Please run 'make proto')
	else
		uv run src/main.py
	endif