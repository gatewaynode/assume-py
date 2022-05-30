# A little different from what we need for a wrapper
if [[ $1 == "exit" ]]; then
    AWS_ACCESS_KEY_ID=""
    AWS_SECRET_ACCESS_KEY=""
    AWS_SESSION_TOKEN=""
elif [ $1 ]; then
    #  assume_response=$(aws sts assume-role --role-arn "arn:aws:iam::123456789012.:role/sudo-create-s3-buckets --role-session-name BucketBoy")
    assume_response=$(python3 $HOME/code/aws_tricks/assume-py/assume.py --shell $1) 
    if [[ $assume_response == Alias* ]]; then
        echo "ERROR! Alias not found in YAML file: $1"
    else
        export AWS_ACCESS_KEY_ID=$(echo ${assume_response} | jq ".Credentials.AccessKeyId" | sed 's/"//g')
        export AWS_SECRET_ACCESS_KEY=$(echo ${assume_response} | jq ".Credentials.SecretAccessKey" | sed 's/"//g')
        export AWS_SESSION_TOKEN=$(echo ${assume_response} | jq ".Credentials.SessionToken" | sed 's/"//g')
        echo "Assumed role: $(echo ${assume_response} | jq '.AssumedRoleUser.Arn')"
    fi

else
    echo 'ERROR!  Assume alias is required as a parameter, such as: `>$ assume ROLE_NAME_ALIAS` '
fi