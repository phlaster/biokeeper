#!/bin/bash

SPECIAL_CHARS="\'\"@?^&*()\`:~?;:[]{}.,\/|<>!$:"

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

RED='\033[0;31m'
NC='\033[0m' # No Color
# Function to check if a file exists and print a warning
check_file_exists() {
    if [ -f "$1" ]; then
        printf "${RED}: $1 already exists.${NC}\n"
        return 0
    else
        return 1
    fi
}

# JWT KEYS GENERATION
echo "Generating new JWT keys will result in loss of access to existing data stored with the old keys."
check_file_exists jwt_keys/.jwt.public.env
check_file_exists jwt_keys/.jwt.private.env
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

    printf "JWT keys generated successfully in jwt_keys/ directory.\n\n"
else
    printf "Operation canceled.\n\n"
fi




# AUTH DB ENV VARIABLES
filename=biokeeper-auth/.db.env
echo "Generating $filename"
check_file_exists $filename
if confirm "Do you want to proceed? [y/N]"; then
    echo "POSTGRES_USER=biokeeper_auth" > $filename
    echo POSTGRES_PASSWORD=\"$(pwgen 32 1 -y -s -r $SPECIAL_CHARS)\" >> $filename
    echo POSTGRES_DB=auth_db >> $filename

    printf "$filename generated successfully\n\n"
else
    printf "Operation canceled.\n\n"
fi


# AUTH RTOKEN SALT
filename=biokeeper-auth/.rtoken.salt.env
echo "Generating $filename"
check_file_exists $filename
if confirm "Do you want to proceed? [y/N]"; then
    echo REFRESH_TOKEN_HASH_SALT=\"$(pwgen 32 1 -y -s -r $SPECIAL_CHARS)\" > $filename
    printf "$filename generated successfully\n\n"
else
    printf "Operation canceled.\n\n"
fi


filename=./biokeeper-mq/env_files/.auth_user.env
echo "Generating $filename"
check_file_exists $filename
if confirm "Do you want to proceed? [y/N]"; then
	echo RABBITMQ_AUTH_USER=biokeeper_auth > $filename
    echo RABBITMQ_AUTH_PASS=\"$(pwgen 32 1 -y -s -r $SPECIAL_CHARS)\" >> $filename
    printf "$filename generated successfully\n\n"
else
    printf "Operation canceled.\n\n"
fi


filename=./biokeeper-mq/env_files/.core_user.env
echo "Generating $filename"
check_file_exists $filename
if confirm "Do you want to proceed? [y/N]"; then
	echo RABBITMQ_CORE_USER=biokeeper_core > $filename
    echo RABBITMQ_CORE_PASS=\"$(pwgen 32 1 -y -s -r $SPECIAL_CHARS)\" >> $filename
    printf "$filename generated successfully\n\n"
else
    printf "Operation canceled.\n\n"
fi


filename=./biokeeper-mq/env_files/.default_user.env
echo "Generating $filename"
check_file_exists $filename
if confirm "Do you want to proceed? [y/N]"; then
	echo RABBITMQ_DEFAULT_USER=biokeeper_mq > $filename
    echo RABBITMQ_DEFAULT_PASS=\"$(pwgen 32 1 -y -s -r $SPECIAL_CHARS)\" >> $filename
    printf "$filename generated successfully\n\n"
else
    printf "Operation canceled.\n\n"
fi


filename=./.docs.password.env
echo "Generating $filename"
check_file_exists $filename
if confirm "Do you want to proceed? [y/N]"; then
    echo PASSWORD_FOR_FASTAPI_DOCS=\"$(pwgen 32 1 -y -s -r $SPECIAL_CHARS)\" > $filename
    printf "$filename generated successfully\n\n"
else
    printf "Operation canceled.\n\n"
fi