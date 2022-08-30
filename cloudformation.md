.  CloudFormation 官方啰嗦一大堆，其实就是根据amazon提供的API和规则编写json文件（stack)来实现自动创建各种资源如vpc/ec2/rds等。然后实现 infrastcture as code，
    就是把基础设施用code来实现，当然这是在云时代才可行的哦。BTW, 阿里云也推出了类似的工具叫资源编排(名字好奇怪啊），几乎是个拷贝，估计是方便AWS用户迁移到阿里云上吧，
    兼容性极好，学习起来也是零成本。
 . 好处：非常的方便，当然也包括删除资源，除非你后来手工做了改动比如加了某个Instance到自动创建的subnet,此时delete会报错（有依赖关系），不过当你手动删掉你之前手工创建
    的资源后，再次删除delete stack就可以了。建议既然用CF了，就不要人工的去做了。

. 所有的stack在console能实现的，都有对应的命令行工具。

. 当你创建了stack policy的时候某些资源做了限制。只有满足条件才能update等。

. changeset: 当stack执行完毕，若update,此时无需删除stack重来，只需修改tempalte,然后创建changset后执行即可，比如修改instance的type。但可能会造成中断等。

. stack分组，比如website/database,这样不影响，然后nested stack，比如把loadbalancer单独当做一个stack.如下:

    
```
{
    "AWSTemplateFormatVersion" : "2010-09-09",
    "Resources" : {
        "myStackWithParams" : {
             "Type" : "AWS::CloudFormation::Stack",
           "Properties" : {
               "TemplateURL" : "https://s3.amazonaws.com/xxx/elb.template",
               "Parameters" : {
                   "InstanceType" : "t2.micro",
                   "KeyName" : "mykey"
               }
              }
        }
    }
}
```
##########  一个stack的大致结构  ########################
```
{
  "AWSTemplateFormatVersion" : "version date",

  "Description" : "JSON string",

  "Metadata" : {
    template metadata
  },

  "Parameters" : {  # 输入参数，有参数类型string等，default值，长度，以及[a-zA-Z0-9]来约束，多选，No echo(针对密码）等。还有一些aws-specfic
    set of parameters
  },

  "Mappings" : {    # 映射关系，太长懒得解释了，基本上就类似一个环境变量，多跟Fn::FindInMap结合，看官方文档吧，或者看我的代码。
    set of mappings
  },

  "Conditions" : {  # 比如你有2个环境dev/prod，假如prod的话可能需要多几个ec2，那么可以parameter来指定condition，然后resource来标记，多跟and/equals/if/not/or几个函数一起，不废话，看例子1
    set of conditions
  },

  "Resources" : {   # 这个必须有，不多说了，基本就是各种资源了比如AWS::EC2::Instance这种。
    set of resources
  },

  "Outputs" : {   # 顾名思义
    set of outputs
  }
}
```

. 例1:
```
{
  "AWSTemplateFormatVersion" : "2010-09-09",
  "Parameters" : {
    "EnvType" : {
      "Description" : "Environment type.",
      "Default" : "test",
      "Type" : "String",
      "AllowedValues" : ["prod", "test"],
      "ConstraintDescription" : "must specify prod or test."
    }
  },
 
  "Conditions" : {
    "CreateProdResources" : {"Fn::Equals" : [{"Ref" : "EnvType"}, "prod"]},
     "CreateDevResources" : {"Fn::Not": [{"Fn::Equals" : [{"Ref" : "DBSnapshotName"}, ""]}]}
  },

  },
 
  "Resources" : {
    "EC2Instance" : {
      "Type" : "AWS::EC2::Instance",
      #  省略7788的一堆
    },

  "xxxx":{

       "DBSnapshotIdentifier" : {
          "Fn::If" : [
            ""CreateDevResources" ",                  # 跟资源结合
            {"Ref" : "DBSnapshotName"},
          ]
        }
}
    
    "MountPoint" : {
      "Type" : "AWS::EC2::VolumeAttachment",
      "Condition" : "CreateProdResources",
      "Properties" : {
        "InstanceId" : { "Ref" : "EC2Instance" },
        "Device" : "/dev/sdh"
      }
    }
  }
}
```

故障排除：

用aws cli的时候需要传递一个list，需要转义

```ParameterKey=CIDR,ParameterValue='10.10.0.0/16\,10.10.0.0/24\,10.10.1.0/24'```

现在附上我写的一个,本意是创建一个vpc/2 subnets，若干securitygroup,internet gateway, route table。然后一个opsman和nat box这2个instance在public subnet, private subnet的通过nat box上网，还有ELB等资源。当然我添加了若干注释是没用到的，仅仅是为了做笔记，实际上json不允许有任何注释。
```

{
    "AWSTemplateFormatVersion": "2010-09-09",
    "Description": "Initilize Network infrastructure which hosted OpsManger/natbox for China",
    "Parameters": {
        "KeyName": {
            "Description": "Name of an existing EC2 KeyPair to enable SSH access to the instances",
            "Type": "AWS::EC2::KeyPair::KeyName"
        },
        "SshFrom": {
            "Description": "ip range that could be access OpsManager (default can be accessible anywhere)",
            "Type": "String",
            "MinLength": "9",
            "MaxLength": "18",
            "Default": "0.0.0.0/0",
            "AllowedPattern": "(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})/(\\d{1,2})",
            "ConstraintDescription": "must be a valid CIDR range of the form x.x.x.x/x."
        },
        "RdsDBName": {
            "Type": "String",
            "MinLength": "4",
            "Default": "bosh",
            "Description": "BOSH database name"
        },
        "RdsUsername": {
            "Type": "String",
            "Description": "BOSH database username"
        },
        "RdsPassword": {
            "Type": "String",
            "NoEcho": "true",
            "MinLength": "8",
            "Description": "BOSH database password"
        },
        "SSLCertARN": {
            "Type": "String",
            "Description": "ARN for pre-uploaded SSL certificate"
        },
        "NATInstanceType": {
            "Description": "Nat Box EC2 instance type",
            "Type": "String",
            "Default": "m3.large",
            "AllowedValues": [
                "t2.micro",
                "t2.small",
                "t2.medium",
                "t2.large",
                "m1.small",
                "m1.medium",
                "m1.large",
                "m1.xlarge",
                "m2.xlarge",
                "m2.2xlarge",
                "m2.4xlarge",
                "m3.medium",
                "m3.large",
                "m3.xlarge",
                "m3.2xlarge",
                "m4.large",
                "m4.xlarge",
                "m4.2xlarge",
                "m4.4xlarge",
                "m4.10xlarge",
                "c1.medium",
                "c1.xlarge",
                "c3.large",
                "c3.xlarge",
                "c3.2xlarge",
                "c3.4xlarge",
                "c3.8xlarge",
                "c4.large",
                "c4.xlarge",
                "c4.2xlarge",
                "c4.4xlarge",
                "c4.8xlarge",
                "g2.2xlarge",
                "g2.8xlarge",
                "r3.large",
                "r3.xlarge",
                "r3.2xlarge",
                "r3.4xlarge",
                "r3.8xlarge",
                "i2.xlarge",
                "i2.2xlarge",
                "i2.4xlarge",
                "i2.8xlarge",
                "d2.xlarge",
                "d2.2xlarge",
                "d2.4xlarge",
                "d2.8xlarge",
                "hi1.4xlarge",
                "hs1.8xlarge",
                "cr1.8xlarge",
                "cc2.8xlarge",
                "cg1.4xlarge"
            ],
            "ConstraintDescription": "must be a valid EC2 instance type."
        },
        "OpsmanInstanceType": {
            "Description": "ops manager EC2 instance type",
            "Type": "String",
            "Default": "m3.large",
            "AllowedValues": [
                "t2.micro",
                "t2.small",
                "t2.medium",
                "t2.large",
                "m1.small",
                "m1.medium",
                "m1.large",
                "m1.xlarge",
                "m2.xlarge",
                "m2.2xlarge",
                "m2.4xlarge",
                "m3.medium",
                "m3.large",
                "m3.xlarge",
                "m3.2xlarge",
                "m4.large",
                "m4.xlarge",
                "m4.2xlarge",
                "m4.4xlarge",
                "m4.10xlarge",
                "c1.medium",
                "c1.xlarge",
                "c3.large",
                "c3.xlarge",
                "c3.2xlarge",
                "c3.4xlarge",
                "c3.8xlarge",
                "c4.large",
                "c4.xlarge",
                "c4.2xlarge",
                "c4.4xlarge",
                "c4.8xlarge",
                "g2.2xlarge",
                "g2.8xlarge",
                "r3.large",
                "r3.xlarge",
                "r3.2xlarge",
                "r3.4xlarge",
                "r3.8xlarge",
                "i2.xlarge",
                "i2.2xlarge",
                "i2.4xlarge",
                "i2.8xlarge",
                "d2.xlarge",
                "d2.2xlarge",
                "d2.4xlarge",
                "d2.8xlarge",
                "hi1.4xlarge",
                "hs1.8xlarge",
                "cr1.8xlarge",
                "cc2.8xlarge",
                "cg1.4xlarge"
            ],
            "ConstraintDescription": "must be a valid EC2 instance type."
        }
    },
    "Mappings": {
        "Region2VPC": {
            "us-east-1": {
                "VPC": "10.0.0.0/16",
                "Public": "10.0.10.0/24",
                "Private": "10.0.11.0/24"
            },
            "cn-north-1": {
                "VPC": "10.0.0.0/16",
                "Public": "10.0.10.0/24",
                "Private": "10.0.80.0/20",
                "Rds1": "10.0.3.0/24",
                "Rds2": "10.0.2.0/24"
            }
        },
        "ArnSuffix": {
            "us-east-1": {"Value": "aws"},
            "cn-north-1": {"Value": "aws-cn"}
        },
        "AWSNATAMI": {
            "us-east-1": {
                "AMI": "ami-c6699baf"
            },
            "us-west-2": {
                "AMI": "ami-52ff7262"
            },
            "us-west-1": {
                "AMI": "ami-3bcc9e7e"
            },
            "cn-north-1": {
                "AMI": "ami-1848da21"
            }
        },
        "AWSInstanceType2Arch": {
            "t1.micro": {
                "Arch": "64"
            },
            "m1.small": {
                "Arch": "64"
            },
            "m1.medium": {
                "Arch": "64"
            },
            "m1.large": {
                "Arch": "64"
            },
            "m1.xlarge": {
                "Arch": "64"
            },
            "m2.xlarge": {
                "Arch": "64"
            },
            "m2.2xlarge": {
                "Arch": "64"
            },
            "m2.4xlarge": {
                "Arch": "64"
            },
            "m3.large": {
                "Arch": "64"
            },
            "m3.xlarge": {
                "Arch": "64"
            },
            "m3.2xlarge": {
                "Arch": "64"
            },
            "c1.medium": {
                "Arch": "64"
            },
            "c1.xlarge": {
                "Arch": "64"
            },
            "cc1.4xlarge": {
                "Arch": "64Cluster"
            },
            "cc2.8xlarge": {
                "Arch": "64Cluster"
            },
            "cg1.4xlarge": {
                "Arch": "64GPU"
            }
        },
        "AWSRegionArch2AMI": {
            "us-east-1": {
                "32": "ami-a0cd60c9",
                "64": "ami-aecd60c7"
            },
            "us-west-2": {
                "32": "ami-46da5576",
                "64": "ami-48da5578"
            },
            "us-west-1": {
                "32": "ami-7d4c6938",
                "64": "ami-734c6936"
            },
            "cn-north-1": {
                "32": "N/A",
                "64": "ami-2e02c843"
            }
        }
    },
    "Resources": {
        "VPC": {
            "Type": "AWS::EC2::VPC",
            "Properties": {
                "CidrBlock": {
                    "Fn::FindInMap": [
                        "Region2VPC",
                        {
                            "Ref": "AWS::Region"
                        },
                        "VPC"
                    ]
                },
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": {
                            "Ref": "AWS::StackName"
                        }
                    }
                ]
            }
        },
        "PublicSubnet": {
            "Type": "AWS::EC2::Subnet",
            "Properties": {
                "VpcId": {
                    "Ref": "VPC"
                },
                "CidrBlock": {
                    "Fn::FindInMap": [
                        "Region2VPC",
                        {
                            "Ref": "AWS::Region"
                        },
                        "Public"
                    ]
                },
                "AvailabilityZone": {
                    "Fn::Select": [
                        "0",
                        {
                            "Fn::GetAZs": {
                                "Ref": "AWS::Region"
                            }
                        }
                    ]
                },
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": {
                            "Ref": "AWS::StackName"
                        }
                    },
                    {
                        "Key": "Network",
                        "Value": "Public"
                    }
                ]
            }
        },
        "InternetGateway": {
            "Type": "AWS::EC2::InternetGateway",
            "Properties": {
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": {
                            "Ref": "AWS::StackName"
                        }
                    },
                    {
                        "Key": "Network",
                        "Value": "Public"
                    }
                ]
            }
        },
        "GatewayToInternet": {
            "Type": "AWS::EC2::VPCGatewayAttachment",
            "Properties": {
                "VpcId": {
                    "Ref": "VPC"
                },
                "InternetGatewayId": {
                    "Ref": "InternetGateway"
                }
            }
        },
        "PublicRouteTable": {
            "Type": "AWS::EC2::RouteTable",
            "Properties": {
                "VpcId": {
                    "Ref": "VPC"
                },
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": {
                            "Ref": "AWS::StackName"
                        }
                    },
                    {
                        "Key": "Network",
                        "Value": "Public"
                    }
                ]
            }
        },
        "PublicRoute": {
            "Type": "AWS::EC2::Route",
            "DependsOn": "GatewayToInternet",
            "Properties": {
                "RouteTableId": {
                    "Ref": "PublicRouteTable"
                },
                "DestinationCidrBlock": "0.0.0.0/0",
                "GatewayId": {
                    "Ref": "InternetGateway"
                }
            }
        },
        "PublicSubnetRouteTableAssociation": {
            "Type": "AWS::EC2::SubnetRouteTableAssociation",
            "Properties": {
                "SubnetId": {
                    "Ref": "PublicSubnet"
                },
                "RouteTableId": {
                    "Ref": "PublicRouteTable"
                }
            }
        },
        "PrivateSubnet": {
            "Type": "AWS::EC2::Subnet",
            "Properties": {
                "VpcId": {
                    "Ref": "VPC"
                },
                "CidrBlock": {
                    "Fn::FindInMap": [
                        "Region2VPC",
                        {
                            "Ref": "AWS::Region"
                        },
                        "Private"
                    ]
                },
                "AvailabilityZone": {
                    "Fn::Select": [
                        "1",
                        {
                            "Fn::GetAZs": {
                                "Ref": "AWS::Region"
                            }
                        }
                    ]
                },
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": {
                            "Ref": "AWS::StackName"
                        }
                    },
                    {
                        "Key": "Network",
                        "Value": "Private"
                    }
                ]
            }
        },
        "PrivateRouteTable": {
            "Type": "AWS::EC2::RouteTable",
            "Properties": {
                "VpcId": {
                    "Ref": "VPC"
                },
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": {
                            "Ref": "AWS::StackName"
                        }
                    },
                    {
                        "Key": "Network",
                        "Value": "Private"
                    }
                ]
            }
        },
        "PrivateSubnetRouteTableAssociation": {
            "Type": "AWS::EC2::SubnetRouteTableAssociation",
            "Properties": {
                "SubnetId": {
                    "Ref": "PrivateSubnet"
                },
                "RouteTableId": {
                    "Ref": "PrivateRouteTable"
                }
            }
        },
        "PrivateRoute": {
            "Type": "AWS::EC2::Route",
            "Properties": {
                "RouteTableId": {
                    "Ref": "PrivateRouteTable"
                },
                "DestinationCidrBlock": "0.0.0.0/0",
                "InstanceId": {
                    "Ref": "NatBox"
                }
            }
        },
        "NATIPAddress": {
            "Type": "AWS::EC2::EIP",
            "DependsOn": "GatewayToInternet",
            "Properties": {
                "Domain": "vpc",
                "InstanceId": {
                    "Ref": "NatBox"
                }
            }
        },
        "NatBox": {
            "Type": "AWS::EC2::Instance",
            "Properties": {
                "InstanceType": {
                    "Ref": "NATInstanceType"
                },
                "KeyName": {
                    "Ref": "KeyName"
                },
                "SubnetId": {
                    "Ref": "PublicSubnet"
                },
                "SourceDestCheck": "false",
                "ImageId": {
                    "Fn::FindInMap": [
                        "AWSNATAMI",
                        {
                            "Ref": "AWS::Region"
                        },
                        "AMI"
                    ]
                },
                "SecurityGroupIds": [
                    {
                        "Ref": "NATSecurityGroup"
                    }
                ],
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": "Nat-Box-CN"
                    }
                ]
            }
        },
        "NATSecurityGroup": {
            "Type": "AWS::EC2::SecurityGroup",
            "Properties": {
                "GroupDescription": "Enable internal access to the NAT Box",
                "VpcId": {
                    "Ref": "VPC"
                },
                "SecurityGroupIngress": [
                    {
                        "CidrIp": {
                            "Fn::FindInMap": [
                                "Region2VPC",
                                {
                                    "Ref": "AWS::Region"
                                },
                                "VPC"
                            ]
                        },
                        "IpProtocol": "-1"
                    }
                ]
            }
        },
        "OpsManagerIPAddress": {
            "Type": "AWS::EC2::EIP",
            "DependsOn": "GatewayToInternet",
            "Properties": {
                "Domain": "vpc",
                "InstanceId": {
                    "Ref": "OpsMananger"
                }
            }
        },
        "OpsMananger": {
            "Type": "AWS::EC2::Instance",
######################################################### Metadata 被cfn-init 调用 #######################
    "Metadata": {
      "AWS::CloudFormation::Init": {
        "configSets": {
          "MyConfigSet": [
            "Set1",
            "Set2"
          ]
        },
        "Set1": {
          "packages": {
            "yum": {
              "php": [],
              "mysql": []
            }
          },
          "commands": {
            "01command": {
              "command": {
                "Fn::Join": [
                  "",
                  [
                    {
                      "Ref": "xxxxx"
                    },
                    "abcd"
                  ]
                ]
              },
              "test": {}
            }
          },
          "files": {
            "File1": {
              "content": {
                "Fn::Join": [
                  "",
                  [
                    "ABC\n"
                  ]
                ]
              },
              "mode": "000400",
              "owner": "root",
              "group": "root"
            },
            "File2": {
     "source": {
              "Fn::Join": [
                "",
                [
                  "https://s3.amazonaws.com/",
                  {
                    "Ref": "PrivateBucket"
                  },
                  "/id_rsa.pub"
                ]
              ]
            },
            "mode": "000500",
            "owner": "root",
            "group": "root",
            "authentication": "S3AccessCreds"}
          },
          "services": {
            "sysvinit": {
              "Service1": {
                "enable": "true",
                "ensureRunning": "true",
                "files": [
                  "file_confg"
                ]
              }
            }
          }
        },
        "Set2": {},
                    "AWS::CloudFormation::Authentication": {
                        "S3AccessCreds": {
                            "type": "S3",
                            "accessKeyId": {
                                "Ref": "IamUserAccessKey"
                            },
                            "secretKey": {
                                "Fn::GetAtt": [
                                    "IamUserAccessKey",
                                    "SecretAccessKey"
                                ]
                            },
                            "buckets": [
                                {
                                    "Ref": "PrivateBucket"
                                },
                                {
                                    "Ref": "PublicBucket"
                                }
                            ]
                        }
                    }
      },
      "Propterties": {
        "KeyName": {
          "Ref": "YourKeyName"
        }
      },
    }
######################################################
            "Properties": {
                "InstanceType": {
                    "Ref": "OpsmanInstanceType"
                },
                "KeyName": {
                    "Ref": "KeyName"
                },
###################################################
        "UserData": {
          "Fn::Base64": {
            "Fn::Join": [
              "",
              [
                "#!/bin/bash -ex\n",
                "yum update -y aws-cfn-bootstrap\n",
                "/opt/aws/bin/cfn-init -v ",
                " --stack ",
                {
                  "Ref": "AWS::StackName"
                },
                " --resource OpsMananger",
                " --configsets MyconfigSet",
                " --region ",
                {
                  "Ref": "AWS::Region"
                },
                "\n",
                "/opt/aws/bin/cfn-signal -e $? ",
                " --stack ",
                {
                  "Ref": "AWS::StackName"
                },
                " --resource OpsMananger",
                " --region ",
                {
                  "Ref": "AWS::Region"
                },
                "\n"
              ]
            ]
          }
        }
####################################
 cfn-init专门来安装、配置，启动服务等，定义在上面的metadata里面，详细的介绍看http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-init.html#aws-resource-init-sources
### createpolicy接受cf-signal的信号，或者timeout,可以确保资源成功创建。目前 AWS::AutoScaling::AutoScalingGroup, AWS::EC2::Instance, and AWS::CloudFormation::WaitCondition支持。
EC2/Auto Scaling建议使用。还有个waitcondition跟这个类似，但具体区别看不明白，看文档官方以后要去掉waitcondition了吧。
      "CreatePolicy": {
        "ResourceSignal": {
          "Timeout": "PT15M"
        }
      }
####################################
                "SubnetId": {
                    "Ref": "PublicSubnet"
                },
                "ImageId": {
                    "Fn::FindInMap": [
                        "AWSRegionArch2AMI",
                        {
                            "Ref": "AWS::Region"
                        },
                        {
                            "Fn::FindInMap": [
                                "AWSInstanceType2Arch",
                                {
                                    "Ref": "OpsmanInstanceType"
                                },
                                "Arch"
                            ]
                        }
                    ]
                },
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": "OpsManager"
                    }
                ],
                "SecurityGroupIds": [
                    {
                        "Ref": "OpsManSecurityGroup"
                    }
                ]
            }
        },
######################################## Auto Scaling ######################
  "WebServerGroup": {
    "Type": "AWS::AutoScaling::AutoScalingGroup",
    "Properties": {
      "AvailabilityZones": {
        "Fn::GetAZs": ""
      },
      "LaunchConfigurationName": {
        "Ref": "LaunchConfig"
      },
      "MinSize": "1",
      "MaxSize": "5",
      "DesiredCapacity": {
        "Ref": "WebServerCapacity"
      },
      "LoadBalancerNames": [
        {
          "Ref": "PublicElasticLoadBalancer"
        }
      ]
    },
    "CreationPolicy": {
      "ResourceSignal": {
        "Timeout": "PT30M"
      }
    },
    "UpdatePolicy": {
      "AutoScalingRollingUpdate": {
        "MinInstancesInService": "1",
        "MaxBatchSize": "1",
        "PauseTime": "PT30M",
        "WaitOnResourceSignals": "true"
      }
    }
  },
  "LaunchConfig": {
    "Type": "AWS::AutoScaling::LaunchConfiguration",
    "Metadata": {
      "AWS::CloudFormation::Init": { #也可以设置 metadata来初始化
        "configSets": {
          "xxxx": []
        },
        "xxx": {
          "files": {}
        }
      }
    },
"Properties":{
  "ImageId": {},
  "InstanceType": {},
  "SecurityGroups": [
    {}
  ],
  "KeyName": {},
  "UserData": {
    "Fn::Base64": {
      "Fn::Join": [
        "",
        [
          "#!/bin/bash -xe\n",
          "yum update -y aws-cfn-bootstrap\n",
          "/opt/aws/bin/cfn-init -v ",
          " --stack ",
          {
            "Ref": "AWS::StackId"
          },
          " --resource LaunchConfig ",
          " --configsets full_install ",
          " --region ",
          {
            "Ref": "AWS::Region"
          },
          "\n",
          "/opt/aws/bin/cfn-signal -e $? ",
          " --stack ",
          {
            "Ref": "AWS::StackId"
          },
          " --resource WebServerGroup ",
          " --region ",
          {
            "Ref": "AWS::Region"
          },
          "\n"
        ]
      ]
    }
  }
}
  }
##################### Auto Scaling ##############
        "OpsManSecurityGroup": {
            "Type": "AWS::EC2::SecurityGroup",
            "Properties": {
                "GroupDescription": "Enable access to the OpsManager ",
                "VpcId": {
                    "Ref": "VPC"
                },
                "SecurityGroupIngress": [
                    {
                        "IpProtocol": "tcp",
                        "FromPort": "22",
                        "ToPort": "22",
                        "CidrIp": {
                            "Ref": "SshFrom"
                        }
                    },
                    {
                        "IpProtocol": "tcp",
                        "FromPort": "80",
                        "ToPort": "80",
                        "CidrIp": {
                            "Ref": "SshFrom"
                        }
                    },
                    {
                        "IpProtocol": "tcp",
                        "FromPort": "443",
                        "ToPort": "443",
                        "CidrIp": {
                            "Ref": "SshFrom"
                        }
                    },
                    {
                        "IpProtocol": "tcp",
                        "FromPort": "25555",
                        "ToPort": "25555",
                        "CidrIp": {
                            "Fn::FindInMap": [
                                "Region2VPC",
                                {
                                    "Ref": "AWS::Region"
                                },
                                "VPC"
                            ]
                        }
                    },
                    {
                        "IpProtocol": "tcp",
                        "FromPort": "6868",
                        "ToPort": "6868",
                        "CidrIp": {
                            "Fn::FindInMap": [
                                "Region2VPC",
                                {
                                    "Ref": "AWS::Region"
                                },
                                "VPC"
                            ]
                        }
                    }
                ]
            }
        },
        "VmsSecurityGroup": {
            "Type": "AWS::EC2::SecurityGroup",
            "Properties": {
                "GroupDescription": "PCF VMs Security Group",
                "VpcId": {
                    "Ref": "VPC"
                },
                "SecurityGroupIngress": [
                    {
                        "IpProtocol": "-1",
                        "CidrIp": {
                            "Fn::FindInMap": [
                                "Region2VPC",
                                {
                                    "Ref": "AWS::Region"
                                },
                                "VPC"
                            ]
                        }
                    }
                ]
            }
        },
        "MysqlSecurityGroup": {
            "Type": "AWS::EC2::SecurityGroup",
            "Properties": {
                "GroupDescription": "PCF MySQL Security Group",
                "VpcId": {
                    "Ref": "VPC"
                },
                "SecurityGroupIngress": [
                    {
                        "IpProtocol": "tcp",
                        "FromPort": "3306",
                        "ToPort": "3306",
                        "CidrIp": {
                            "Fn::FindInMap": [
                                "Region2VPC",
                                {
                                    "Ref": "AWS::Region"
                                },
                                "VPC"
                            ]
                        }
                    }
                ]
            }
        },
        "PublicElasticLoadBalancer": {
            "Type": "AWS::ElasticLoadBalancing::LoadBalancer",
            "Properties": {
                "LoadBalancerName": "pcf-china",
                "CrossZone": true,
                "ConnectionSettings": {
                    "IdleTimeout": 3600
                },
                "SecurityGroups": [
                    {
                        "Ref": "PublicLoadBalancerSecurityGroup"
                    }
                ],
                "Subnets": [
                    {
                        "Ref": "PrivateSubnet"
                    }
                ],
                "Listeners": [
                    {
                        "LoadBalancerPort": "80",
                        "InstancePort": "80",
                        "Protocol": "HTTP"
                    },
                    {
                        "LoadBalancerPort": "443",
                        "InstancePort": "80",
                        "Protocol": "HTTPS",
                        "SSLCertificateId": {
                            "Ref": "SSLCertARN"
                        }
                    },
                    {
                        "LoadBalancerPort": "4443",
                        "InstancePort": "443",
                        "Protocol": "SSL",
                        "SSLCertificateId": {
                            "Ref": "SSLCertARN"
                        }
                    }
                ],
                "HealthCheck": {
                    "Target": "TCP:80",
                    "HealthyThreshold": "10",
                    "UnhealthyThreshold": "2",
                    "Interval": "30",
                    "Timeout": "6"
                }
            }
        },
        "PublicLoadBalancerSecurityGroup": {
            "Type": "AWS::EC2::SecurityGroup",
            "Properties": {
                "GroupDescription": "Public ELB Security Group with HTTP access on port 80 from the internet",
                "VpcId": {
                    "Ref": "VPC"
                },
                "SecurityGroupIngress": [
                    {
                        "IpProtocol": "tcp",
                        "FromPort": "80",
                        "ToPort": "80",
                        "CidrIp": "0.0.0.0/0"
                    },
                    {
                        "IpProtocol": "tcp",
                        "FromPort": "443",
                        "ToPort": "443",
                        "CidrIp": "0.0.0.0/0"
                    },
                    {
                        "IpProtocol": "tcp",
                        "FromPort": "4443",
                        "ToPort": "4443",
                        "CidrIp": "0.0.0.0/0"
                    }
                ]
            }
        },
        "SSHElasticLoadBalancer": {
            "Type": "AWS::ElasticLoadBalancing::LoadBalancer",
            "Properties": {
                "LoadBalancerName": "ssh-elb",
                "CrossZone": true,
                "ConnectionSettings": {
                    "IdleTimeout": 3600
                },
                "SecurityGroups": [
                    {
                        "Ref": "SSHLoadBalancerSecurityGroup"
                    }
                ],
                "Subnets": [
                    {
                        "Ref": "PrivateSubnet"
                    }
                ],
                "Listeners": [
                    {
                        "LoadBalancerPort": "2222",
                        "InstancePort": "2222",
                        "Protocol": "tcp"
                    }
                ],
                "HealthCheck": {
                    "Target": "TCP:2222",
                    "HealthyThreshold": "10",
                    "UnhealthyThreshold": "2",
                    "Interval": "30",
                    "Timeout": "6"
                }
            }
        },
        "SSHLoadBalancerSecurityGroup": {
            "Type": "AWS::EC2::SecurityGroup",
            "Properties": {
                "GroupDescription": "ssh ELB Security Group",
                "VpcId": {
                    "Ref": "VPC"
                },
                "SecurityGroupIngress": [
                    {
                        "IpProtocol": "tcp",
                        "FromPort": "2222",
                        "ToPort": "2222",
                        "CidrIp": "0.0.0.0/0"
                    }
                ]
            }
        },
        "RdsSubnet1": {
            "Type": "AWS::EC2::Subnet",
            "Properties": {
                "AvailabilityZone": {
                    "Fn::Select": [
                        "0",
                        {
                            "Fn::GetAZs": {
                                "Ref": "AWS::Region"
                            }
                        }
                    ]
                },
                "CidrBlock": {
                    "Fn::FindInMap": [
                        "Region2VPC",
                        {
                            "Ref": "AWS::Region"
                        },
                        "Rds1"
                    ]
                },
                "VpcId": {
                    "Ref": "VPC"
                },
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": "rds-subnet-1"
                    }
                ]
            }
        },
        "RdsSubnet2": {
            "Type": "AWS::EC2::Subnet",
            "Properties": {
                "AvailabilityZone": {
                    "Fn::Select": [
                        "1",
                        {
                            "Fn::GetAZs": {
                                "Ref": "AWS::Region"
                            }
                        }
                    ]
                },
                "CidrBlock": {
                    "Fn::FindInMap": [
                        "Region2VPC",
                        {
                            "Ref": "AWS::Region"
                        },
                        "Rds2"
                    ]
                },
                "VpcId": {
                    "Ref": "VPC"
                },
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": "rds-subnet-2"
                    }
                ]
            }
        },
        "RdsSubnet1tRouteTableAssociation": {
            "Type": "AWS::EC2::SubnetRouteTableAssociation",
            "Properties": {
                "SubnetId": {
                    "Ref": "RdsSubnet1"
                },
                "RouteTableId": {
                    "Ref": "PublicRouteTable"
                }
            }
        },
        "RdsSubnet2tRouteTableAssociation": {
            "Type": "AWS::EC2::SubnetRouteTableAssociation",
            "Properties": {
                "SubnetId": {
                    "Ref": "RdsSubnet2"
                },
                "RouteTableId": {
                    "Ref": "PublicRouteTable"
                }
            }
        },
        "OpsManS3Bucket": {
            "Type": "AWS::S3::Bucket",
            "Properties": {
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": "PCF Ops Manager S3 Bucket"
                    }
                ]
            }
        },
        "IamUser": {
            "Type": "AWS::IAM::User",
            "DependsOn": [
                "OpsManS3Bucket"
            ],
            "Properties": {
                "Policies": [
                    {
                        "PolicyName": "Policy",
                        "PolicyDocument": {
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Effect": "Deny",
                                    "Action": [
                                        "iam:*"
                                    ],
                                    "Resource": [
                                        "*"
                                    ]
                                },
                                {
                                    "Sid": "OpsManS3Permissions",
                                    "Effect": "Allow",
                                    "Action": [
                                        "s3:*"
                                    ],
                                    "Resource": [
                                        {
                                            "Fn::Join": [
                                                "",
                                                [
                                                    "arn:",
                                                    {
                                                        "Fn::FindInMap": [
                                                            "ArnSuffix",
                                                            {"Ref": "AWS::Region"
                                                            },
                                                            "Value"
                                                        ]
                                                    },
                                                    ":s3:::",
                                                    {
                                                        "Ref": "OpsManS3Bucket"
                                                    }
                                                ]
                                            ]
                                        },
                                        {
                                            "Fn::Join": [
                                                "",
                                                [
                                                    "arn:",
                                                    {
                                                        "Fn::FindInMap": [
                                                            "ArnSuffix",
                                                            {"Ref": "AWS::Region"
                                                            },
                                                            "Value"
                                                        ]
                                                    },
                                                    ":s3:::",
                                                    {
                                                        "Ref": "OpsManS3Bucket"
                                                    },
                                                    "/*"
                                                ]
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "Sid": "OpsManEc2Permissions",
                                    "Effect": "Allow",
                                    "Action": [
                                        "ec2:DescribeAccountAttributes",
                                        "ec2:DescribeAddresses",
                                        "ec2:AssociateAddress",
                                        "ec2:DisassociateAddress",
                                        "ec2:DescribeAvailabilityZones",
                                        "ec2:DescribeImages",
                                        "ec2:DescribeInstances",
                                        "ec2:RunInstances",
                                        "ec2:RebootInstances",
                                        "ec2:TerminateInstances",
                                        "ec2:DescribeKeypairs",
                                        "ec2:DescribeRegions",
                                        "ec2:DescribeSnapshots",
                                        "ec2:CreateSnapshot",
                                        "ec2:DeleteSnapshot",
                                        "ec2:DescribeSecurityGroups",
                                        "ec2:DescribeSubnets",
                                        "ec2:DescribeVpcs",
                                        "ec2:CreateTags",
                                        "ec2:DescribeVolumes",
                                        "ec2:CreateVolume",
                                        "ec2:AttachVolume",
                                        "ec2:DeleteVolume",
                                        "ec2:DetachVolume"
                                    ],
                                    "Resource": [
                                        "*"
                                    ]
                                },
                                {
                                    "Sid": "OpsManElbPermissions",
                                    "Effect": "Allow",
                                    "Action": [
                                        "elasticloadbalancing:DescribeLoadBalancers",
                                        "elasticloadbalancing:DeregisterInstancesFromLoadBalancer",
                                        "elasticloadbalancing:RegisterInstancesWithLoadBalancer"
                                    ],
                                    "Resource": [
                                        "*"
                                    ]
                                }
                            ]
                        }
                    }
                ]
            }
        },
        "IamUserAccessKey": {
            "Type": "AWS::IAM::AccessKey",
            "DependsOn": "IamUser",
            "Properties": {
                "UserName": {
                    "Ref": "IamUser"
                }
            }
        },
        "RdsSubnetGroup": {
            "Type": "AWS::RDS::DBSubnetGroup",
            "Properties": {
                "DBSubnetGroupDescription": "PCF RDS Subnet Group",
                "SubnetIds": [
                    {
                        "Ref": "RdsSubnet1"
                    },
                    {
                        "Ref": "RdsSubnet2"
                    }
                ]
            }
        },
        "Rds": {
            "Type": "AWS::RDS::DBInstance",
            "Properties": {
                "AllocatedStorage": "100",
                "DBInstanceClass": "db.m3.large",
                "Engine": "MySQL",
                "EngineVersion": "5.6.22",
                "MultiAZ": "True",
                "DBName": {
                    "Ref": "RdsDBName"
                },
                "Iops": "1000",
                "MasterUsername": {
                    "Ref": "RdsUsername"
                },
                "MasterUserPassword": {
                    "Ref": "RdsPassword"
                },
                "PubliclyAccessible": "False",
                "VPCSecurityGroups": [
                    {
                        "Ref": "MysqlSecurityGroup"
                    }
                ],
                "DBSubnetGroupName": {
                    "Ref": "RdsSubnetGroup"
                }
            }
        }
    },
    "Outputs": {
        "OpsManager": {
            "Description": "IP Address of the OpsManager host",
            "Value": {
                "Ref": "OpsManagerIPAddress"
            }
        },
        "VmsSecurityGroup": {
            "Value": {
                "Ref": "VmsSecurityGroup"
            }
        },
        "VPCId": {
            "Value": {
                "Ref": "VPC"
            }
        },
        "PublicSubnet": {
            "Value": {
                "Ref": "PublicSubnet"
            }
        },
        "IamUserName": {
            "Value": {
                "Ref": "IamUser"
            }
        },
        "IamUserAccessKey": {
            "Value": {
                "Ref": "IamUserAccessKey"
            }
        },
        "IamUserSecretAccessKey": {
            "Value": {
                "Fn::GetAtt": [
                    "IamUserAccessKey",
                    "SecretAccessKey"
                ]
            }
        },
        "S3Bucket": {
            "Value": {
                "Ref": "OpsManS3Bucket"
            }
        },
        "PrivateSubnet": {
            "Value": {
                "Ref": "PrivateSubnet"
            }
        },
        "PrivateSubnetAvailabilityZone": {
            "Value": {
                "Fn::GetAtt": [
                    "PrivateSubnet",
                    "AvailabilityZone"
                ]
            }
        },
        "PublicSubnetAvailabilityZone": {
            "Value": {
                "Fn::GetAtt": [
                    "PublicSubnet",
                    "AvailabilityZone"
                ]
            }
        },
        "RdsAddress": {
            "Value": {
                "Fn::GetAtt": [
                    "Rds",
                    "Endpoint.Address"
                ]
            }
        },
        "RdsPort": {
            "Value": {
                "Fn::GetAtt": [
                    "Rds",
                    "Endpoint.Port"
                ]
            }
        },
        "RdsUsername": {
            "Value": {
                "Ref": "RdsUsername"
            }
        },
        "RdsPassword": {
            "Value": {
                "Ref": "RdsPassword"
            }
        },
        "RdsDBName": {
            "Value": {
                "Ref": "RdsDBName"
            }
        },
        "CidrBlock": {
            "Value": {
                "Fn::FindInMap": [
                    "Region2VPC",
                    {
                        "Ref": "AWS::Region"
                    },
                    "Private"
                ]
            }
        },
        "KeyPairName": {
            "Value": {
                "Ref": "KeyName"
            }
        }
    }
}
以下是跟DNS操作有关的，未验证，因为route53我没用到，拷贝为了参考备忘。
"HostedZone": {
            "Type": "AWS::Route53::HostedZone",
            "Properties": {
                "HostedZoneConfig": {
                    "Comment": "Hosted zone for example.com"
                },
                "Name": "example.com",
                "VPCs": [
                    {
                        "VPCId": {
                            "Ref": "VPC"
                        },
                        "VPCRegion": {
                            "Ref": "AWS::Region"
                        }
                    }
                ]
            }
        },
        "PuppetMasterDNSRecord": {
            "Type": "AWS::Route53::RecordSet",
            "DependsOn": "HostedZone",
            "Properties": {
                "HostedZoneId": {
                    "Fn::Join": [
                        "",
                        [
                            "/hostedzone/",
                            {
                                "Ref": "HostedZone"
                            }
                        ]
                    ]
                },
                "Name": "puppet.example.com",
                "Type": "A",
                "TTL": "900",
                "ResourceRecords": [
                    {
                        "Ref": "PuppetMasterIP"
                    }
                ]
            }
        },
        "PuppetAgentLinuxDNSRecord": {
            "Type": "AWS::Route53::RecordSet",
            "Properties": {
                "HostedZoneId": {
                    "Fn::Join": [
                        "",
                        [
                            "/hostedzone/",
                            {
                                "Ref": "HostedZone"
                            }
                        ]
                    ]
                },
                "Name": "linuxagent.example.com",
                "Type": "A",
                "TTL": "900",
                "ResourceRecords": [
                    {
                        "Ref": "PuppetAgentLinuxIP"
                    }
                ]
            }
        },
        "PuppetAgentWindowsDNSRecord": {
            "Type": "AWS::Route53::RecordSet",
            "Properties": {
                "HostedZoneId": {
                    "Fn::Join": [
                        "",
                        [
                            "/hostedzone/",
                            {
                                "Ref": "HostedZone"
                            }
                        ]
                    ]
                },
                "Name": "windowsagent.example.com",
                "Type": "A",
                "TTL": "900",
                "ResourceRecords": [
                    {
                        "Ref": "PuppetAgentWindowsIP"
                    }
                ]
            }
        }
```
