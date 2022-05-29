# A little different from what we need for a wrapper
if [[ $1 == "exit" ]]; then
    AWS_ACCESS_KEY_ID=""
    AWS_SECRET_ACCESS_KEY=""
    AWS_SESSION_TOKEN=""
elif [ $1 ]; then
    #  assume_response=$(aws sts assume-role --role-arn "arn:aws:iam::123456789012.:role/sudo-create-s3-buckets --role-session-name BucketBoy")
    assume_response=$(python3 $HOME/code/aws_tricks/assume-py/assume.py --shell $1) 
    echo $assume_response
    # AWS_ACCESS_KEY_ID=$(echo ${assume_response} | jq ".Credentials.AccessKeyId" $assume_response | sed 's/"//g')
    # AWS_SECRET_ACCESS_KEY=$(echo ${assume_response} | jq ".Credentials.SecretAccessKey" $assume_response | sed 's/"//g')
    # AWS_SESSION_TOKEN=$(echo ${assume_response} | jq ".Credentials.SessionToken" $assume_response | sed 's/"//g')

else
    echo 'Assume alias is required as a parameter, such as: `>$ assume ROLE_NAME_ALIAS` '
fi