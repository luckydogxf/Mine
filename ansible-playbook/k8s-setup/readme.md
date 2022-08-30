# site.yml
```
---
- name: testing...
  hosts: all
  gather_facts: yes
  ignore_errors: yes
  remote_user: ubuntu
  become: yes
  roles:
    - k8s-setup
  environment:
    http_proxy: http://172.16.232.21:8088
    https_proxy: http://172.16.232.21:8088
    no_proxy: no_proxy=10.96.0.0/12,172.16.232.234,172.16.232.21,172.16.215.0/24,172.16.215.81,.pacific-textiles.com,10.244.0.0/16,127.0.0.1
```
# How to use it ?

``` ansible-playbook site.yml -i 172.16.215.162, -u ubuntu -k -b ```

or write your own inventory files.

# What's next ?

1. Go to master nodes, run 

``` kubeadm token create --print-join-command ```

would show the command to join a worker node.

2. what if it is a mater node ?

``` kubeadm init phase upload-certs --upload-certs```

3. run step 1 again.

```
<join command from step 02> --control-plane --certificate-key <key from step 01>

```
4. change logs

Bump version to `1.24.3`. Removed `docker` and enable `containerd` as default.
