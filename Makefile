.PHONY: proto deps run

# Variables
PROTO_SOURCE_DIR=helios-protos
PROTO_BUILD_DIR=generated

# Find all .proto files in the proto directory and subdirectories
PROTO_SRC := $(wildcard $(PROTO_SOURCE_DIR)/**/*.proto)

# 1=true, 0=false
DOCKER_DISABLED=1
export DOCKER_DISABLED

# Commands
proto: $(PROTO_BUILD_DIR)
	protoc -I=$(PROTO_SOURCE_DIR) --python_out=$(PROTO_BUILD_DIR) $(PROTO_SRC)

# Create the directory if it doesn't exist
$(PROTO_BUILD_DIR):
	mkdir -p $(PROTO_BUILD_DIR)

deps:
	uv run sync

run:
	ifeq ($(wildcard $(PROTO_BUILD_DIR)/.),)
		$(error Protobuf build directory not found. Please run 'make proto')
	else
		uv run src/main.py
	endif