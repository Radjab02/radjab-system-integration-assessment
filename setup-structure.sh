#!/bin/bash

# Create Java producers project structure
mkdir -p java-producers/src/main/java/com/ecommerce/integration/{config,controller,model,service,producer}
mkdir -p java-producers/src/main/resources
mkdir -p java-producers/src/test/java/com/ecommerce/integration

# Create mock APIs project structure
mkdir -p mock-apis/src/main/java/com/ecommerce/mock/{config,controller,model,repository,service,soap}
mkdir -p mock-apis/src/main/resources/{wsdl,schema}
mkdir -p mock-apis/src/test/java/com/ecommerce/mock

# Create Python consumers project structure
mkdir -p python-consumers/src/{consumers,services,models,config}
mkdir -p python-consumers/tests

# Create infrastructure directory
mkdir -p infrastructure/{kafka,localstack}

# Create docs directory
mkdir -p docs/{diagrams,api-specs}

echo "Project structure created successfully!"
