export WINEGUARD_IP=10.11.12.1
export WGO_LOCAL=$1


ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -L 8080:$WINEGUARD_IP:80 $WGO_LOCAL
