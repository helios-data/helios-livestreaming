.PHONY: proto deps run

# Variables
FALCON_PROTO_SOURCE_DIR=falcon-protos
FALCON_PROTO_BUILD_DIR=generated/falcon

# Find all .proto files in the proto directory and subdirectories
FALCON_PROTO_SRC := $(shell find $(FALCON_PROTO_SOURCE_DIR) -name "*.proto")

# 1=true, 0=false
DOCKER_DISABLED=1
export DOCKER_DISABLED

# Commands
proto: $(FALCON_PROTO_BUILD_DIR)
	protoc -I=$(FALCON_PROTO_SOURCE_DIR) --python_out=$(FALCON_PROTO_BUILD_DIR) $(FALCON_PROTO_SRC)

# Create the directory if it doesn't exist
$(FALCON_PROTO_BUILD_DIR):
	mkdir -p $(FALCON_PROTO_BUILD_DIR)

deps:
	uv run sync

run:
	@if [ ! -d "$(FALCON_PROTO_BUILD_DIR)" ]; then \
		echo "Falcon Protobuf build directory not found. Please run 'make proto'"; \
		exit 1; \
	fi

	uv run src/main.py