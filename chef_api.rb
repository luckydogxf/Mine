#!/usr/bin/env ruby

# By hongquan
# A pure ruby for Chef Server APIs, see https://docs.chef.io/api_chef_server.html#
# Best practice:
# 1.) register nodes via kickstart/autoyast(%post section of kickstart, while scripts(init-script) in autoyast)
#     or scripts. (To run `chef-client`).
# 2.) assign roles/recipes to the nodes.

require 'base64'
require 'time'
require 'digest/sha1'
require 'openssl'
require 'json'
require 'net/https'
=begin
if ARGV.size != 2

 puts "insufficient parameters"
 puts "USAGE: ruby #{$0} <ENDPOINT>  <JSON>"
 exit 1

end

endpoint = ARGV[0]
json_data = ARGV[1]

=end

class ChefAPI

  # WHY? http://kaochenlong.com/2015/03/21/attr_accessor/
  # Ruby cannot access its properties directly, unless through attr_accessor

  attr_accessor :http, :path, :http_cert, :http_key
  attr_accessor :client_name, :key_file,  :ca_file

  def initialize(opts={})
    # local variables, begin with a lowercase letter or _. Only available inside the method.
    server            = opts[:server]
    port              = opts.fetch(:port, 443)
    use_ssl           = opts.fetch(:use_ssl, true)
    ca_file           = opts[:ca_file] 
    ssl_insecure      = opts[:ssl_insecure] ? OpenSSL::SSL::VERIFY_NONE :  OpenSSL::SSL::VERIFY_PEER

    # instance variables(begin with @) are available across methods for any particular instance or object. That means
    # that instance variables change from object to object
    # And there also are Global var( $VAR_NAME, across classes.
    # And Class variables are available across different objects( @@VAR).
    @client_name      = opts[:client_name]
    @key_file         = opts[:key_file]
    @http             = Net::HTTP.new(server, port)
    @http.use_ssl     = use_ssl
    @http.ca_file     = ca_file
    @http.verify_mode = ssl_insecure

  end


  private def headers(body,method)
    timestamp = Time.now.utc.iso8601
    key       = OpenSSL::PKey::RSA.new(File.read(key_file))
    canonical = "Method:#{method}\nHashed Path:#{encode(path)}\nX-Ops-Content-Hash:#{encode(body)}\nX-Ops-Timestamp:#{timestamp}\nX-Ops-UserId:#{client_name}"

    header_hash = {
      'Accept'             => 'application/json',
      'X-Ops-Sign'         => 'version=1.0',
      'X-Chef-Version'     => '12.15.8',   # Chef Server version.
      'X-Ops-Userid'       => client_name,
      'X-Ops-Timestamp'    => timestamp,
      'X-Ops-Content-Hash' => encode(body),
    }

    # ONLY APPLY TO `POST` and `PUT`.
    if ['POST', 'PUT'].include?method
      header_hash['Content-Type'] = 'application/json'

    end

    signature = Base64.encode64(key.private_encrypt(canonical))
    # break into X-Ops-Authorization-N, each line is no more than 6o chars.
    signature_lines = signature.split(/\n/)
    signature_lines.each_index do |index|
      key = "X-Ops-Authorization-#{index + 1}"
      header_hash[key] = signature_lines[index]
    end

    header_hash

  end

  private def encode(string)
    ::Base64.encode64(Digest::SHA1.digest(string)).chomp
  end

  def get_request(req_path, body)
    @path = req_path

    begin

      request  = Net::HTTP::Get.new(path, headers(body,"GET"))
      response = http.request(request)
      puts JSON.parse(response.body).keys

    rescue Exception => e
      raise "error: #{e.message}."
    end

  end

  def post_request(req_path, body)
    @path = req_path

    begin

      request  = Net::HTTP::Post.new(path, headers(body,"POST"))
      request.body = body
      response = http.request(request)
      puts JSON.parse(response.body)

    rescue Exception => e

      raise "error: #{e.message}."
    end

  end

  def put_request(req_path, body)
    @path = req_path

    begin
     # puts headers(body, "PUT")
      request  = Net::HTTP::Put.new(path, headers(body,"PUT"))
      request.body = body
      response = http.request(request)
      puts JSON.parse(response.body)

    rescue Exception => e
      raise "error: #{e.message}."
    end

  end

  def delete_request(req_path, body)
    @path = req_path

    begin

      request  = Net::HTTP::Delete.new(path, headers(body,"DELETE"))
      response = http.request(request)
      puts JSON.parse(response.body)

    rescue Exception => e
      raise "error: #{e.message}."
    end

  end

end

#
chef = ChefAPI.new(
  :server       => 'ipa.ipa.pthl.hk',
  :port         => 9443,
  :ca_file      => '/root/.chef/trusted_certs/ipa_ipa_pthl_hk.crt',
  :client_name  => 'opscode',
  :key_file     => '/etc/chef/opscode.pem',
  :ssl_insecure => false # enable SSL
)

=begin 
role ='{
  "name": "ipa_client",
  "description": "configure ipa-client, test passed on SLES12-sp2",
  "json_class": "Chef::Role",
  "default_attributes": {

  },
  "override_attributes": {

  },
  "chef_type": "role",
  "run_list": [
   "recipe[base]",
   "recipe[krb5]",
   "recipe[sssd]"

  ],
  "env_run_lists": {

  }
}'
=end

node ='
{
  "name": "acs03z",
  "chef_environment": "_default",
  "run_list": [
  "role[ipa_client]"
]
,
  "normal": {
    "tags": [
      "sssd_client"
    ]
  }
}
'


puts chef.put_request("/organizations/pacific-textiles/nodes/acs03z", node)

