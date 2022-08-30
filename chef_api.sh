#!/bin/bash
# author:hongquan,2017-07-18
# Chef Server API by bash.
# setup node side first. And then use this script to GET/POST/PUT/DELETE

#  GNU gawk is required.
# verbose mode, for debugging.
#set -x

_chomp () {
  # helper function to remove newlines
  awk '{printf "%s", $0}'
}

chef_api_request() {

  local method path body timestamp chef_server_url client_name hashed_body hashed_path
  local canonical_request headers auth_headers

  chef_server_url="https://ipa.ipa.pthl.hk:9443"
  ca_cert="/root/.chef/trusted_certs/ipa_ipa_pthl_hk.crt"
  client_name="opscode" # from `knife user list`, and the one who is associated with the org when created by `chef-server-ctl org-create`
  method=$1
  endpoint=${2%%\?*}
  path=${chef_server_url}$2
  body=$3

  hashed_path=$(echo -n "$endpoint" | openssl dgst -sha1 -binary | openssl enc -base64)
  hashed_body=$(echo -n "$body" | openssl dgst -sha1 -binary | openssl enc -base64)
  timestamp=$(date -u "+%Y-%m-%dT%H:%M:%SZ")

  canonical_request="Method:$method\nHashed Path:$hashed_path\nX-Ops-Content-Hash:$hashed_body\nX-Ops-Timestamp:$timestamp\nX-Ops-UserId:$client_name"
  headers="-H X-Ops-Timestamp:$timestamp \
    -H X-Ops-Userid:$client_name \
    -H X-Chef-Version:12.15.8 \
    -H Accept:application/json \
    -H X-Ops-Content-Hash:$hashed_body \
    -H X-Ops-Sign:version=1.0"

  auth_headers=$(printf "$canonical_request" | openssl rsautl -sign -inkey \
    "/etc/chef/${client_name}.pem" | openssl enc -base64 | _chomp |  awk '{ll=int(length/60);i=0; \
    # fold -w 60 is much more concise.
    while (i<=ll) {printf " -H X-Ops-Authorization-%s:%s", i+1, substr($0,i*60+1,60);i=i+1}}')

  case $method in
    GET)
    # No "-X", defaults is GET.
      eval "curl --cacert $ca_cert $headers $auth_headers $path"
      ;;
    # Content-Type:application/json is required for POST/PUT.
    POST)
      eval "curl --cacert $ca_cert -H Content-Type:application/json $headers $auth_headers -X POST -d '$body' $path"
      ;;
    PUT)
      eval "curl --cacert $ca_cert -H Content-Type:application/json $headers $auth_headers -X PUT -d '$body' $path"
      ;;
    DELETE)
      eval "curl --cacert $ca_cert $headers $auth_headers -X DELETE $path"
      ;;
    *)
      echo "Unknown Method. " >&2
      exit 1
      ;;
    esac
  }

 chef_api_request "$@"


