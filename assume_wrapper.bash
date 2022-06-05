# This is the shell wrapper for assume, it is required to correctly set the shell environment
# variables when using assume.  It does this by being invoked as `source` and setting the 
# environment variables for AWS assumed roles.  In the order of operations for AWS CLI and SDK
# credential use this precedes the `shared_credentials` file, and so the assumed role is used
# instead of what would have been in that file until the shell is closed or the `exit` command
# is sent and the vars set to empty strings.
if [[ $1 == "exit" ]]; then
    export AWS_ACCESS_KEY_ID=""
    export AWS_SECRET_ACCESS_KEY=""
    export AWS_SESSION_TOKEN=""
elif [[ $1 == "whoami" ]]; then
    aws sts get-caller-identity
elif [ $1 ]; then
    assume_response=$(python3 $HOME/.local/bin/assume.py --shell $1) 
    if [[ $assume_response == Alias* ]]; then
        echo "ERROR! Alias not found in YAML file: $1"
    else
        export AWS_ACCESS_KEY_ID=$(echo ${assume_response} | cut -d , -f 1)
        export AWS_SECRET_ACCESS_KEY=$(echo ${assume_response} | cut -d , -f 2)
        export AWS_SESSION_TOKEN=$(echo ${assume_response} | cut -d , -f 3)
    fi

else
    echo 'ERROR!  Assume alias is required as a parameter, such as: `>$ assume ROLE_NAME_ALIAS` '
fi