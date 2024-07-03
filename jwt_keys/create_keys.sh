#!/bin/bash

# Function to prompt the user
confirm() {
    read -r -p "${1:-Are you sure? [y/N]} " response
    case "$response" in
        [yY][eE][sS]|[yY])
            true
            ;;
        *)
            false
            ;;
    esac
}

# Prompt user before proceeding
echo "Generating new JWT keys will result in loss of access to existing data stored with the old keys."
if confirm "Do you want to proceed? [y/N]"; then
    # Ensure jwt_keys directory exists
    mkdir -p jwt_keys

    # Generate private key
    openssl genpkey -algorithm RSA -out jwt_keys/private_key.pem
    echo 'JWT_PRIVATE_KEY="' > jwt_keys/.jwt.private.env
    sed ':a;N;$!ba;s/\n/\\n/g' jwt_keys/private_key.pem | awk '{print $0 "\\n"}' >> jwt_keys/.jwt.private.env
    echo '"' >> jwt_keys/.jwt.private.env

    tr -d '\n' < jwt_keys/.jwt.private.env > jwt_keys/.jwt.private.env.tmp && mv jwt_keys/.jwt.private.env.tmp jwt_keys/.jwt.private.env

    # Generate public key
    openssl rsa -pubout -in jwt_keys/private_key.pem -out jwt_keys/public_key.pem
    echo 'JWT_PUBLIC_KEY="' > jwt_keys/.jwt.public.env
    sed ':a;N;$!ba;s/\n/\\n/g' jwt_keys/public_key.pem | awk '{print $0 "\\n"}' >> jwt_keys/.jwt.public.env
    echo '"' >> jwt_keys/.jwt.public.env

    tr -d '\n' < jwt_keys/.jwt.public.env > jwt_keys/.jwt.public.env.tmp && mv jwt_keys/.jwt.public.env.tmp jwt_keys/.jwt.public.env

    # Remove temp files
    rm jwt_keys/private_key.pem jwt_keys/public_key.pem

    echo "JWT keys generated successfully in jwt_keys/ directory."
else
    echo "Operation canceled."
fi
