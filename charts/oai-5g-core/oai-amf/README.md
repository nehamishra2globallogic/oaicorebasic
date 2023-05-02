# Helm Chart for OAI Access and Mobility Function (AMF)

The helm-charts are tested on [Minikube](https://minikube.sigs.k8s.io/docs/) and [Red Hat Openshift](https://www.redhat.com/fr/technologies/cloud-computing/openshift) 4.10 and 4.12. There are no special resource requires for AMF. 

## Introduction

OAI-AMF follows release 16 more detail about its funtioning can be found on [AMFs WiKi page](https://gitlab.eurecom.fr/oai/cn5g/oai-cn5g-amf/-/wikis/home). The source code be downloaded from [GitLab](https://gitlab.eurecom.fr/oai/cn5g/oai-cn5g-amf)

OAI [Jenkins Platform](https://jenkins-oai.eurecom.fr/job/OAI-CN5G-AMF/) publish every `develop` and `master` branch image of AMF on [docker-hub](https://hub.docker.com/r/oaisoftwarealliance/oai-amf) with tag `develop` and `latest` respectively. Apart from that you can find tags for every release `VX.X.X` 

The helm chart of OAI-AMF creates multiples Kubernetes resources

1. Service
2. Role Base Access Control (RBAC) (role and role bindings)
3. Deployment
4. Configmap (Contains the configuration file for AMF)
5. Service account
6. Network-attachment-defination (Optional only when multus is used)

The directory structure

```
├── Chart.yaml
├── README.md
├── templates
│   ├── configmap.yaml
│   ├── deployment.yaml
│   ├── _helpers.tpl
│   ├── multus.yaml
│   ├── NOTES.txt
│   ├── rbac.yaml
│   ├── serviceaccount.yaml
│   └── service.yaml
└── values.yaml (Parent file contains all the configurable parameters)
```

## Parameters

[Values.yaml](./values.yaml) contains all the configurable parameters. Below table defines the configurable parameters. 


|Parameter                        |Allowed Values                 |Remark                         |
|---------------------------------|-------------------------------|-------------------------------|
|kubernetesType                   |Vanilla/Openshift              |Vanilla Kubernetes or Openshift|
|nfimage.repository               |Image Name                     |                               |
|nfimage.version                  |Image Version                  |                               |
|nfimage.pullPolicy               |IfNotPresent or Never or Always|                               |
|imagePullSecrets.name            |String                         |Good to use for docker hub     |
|serviceAccount.create            |true/false                     |                               |
|serviceAccount.annotations       |String                         |                               |
|serviceAccount.name              |String                         |                               |
|podSecurityContext.runAsUser     |Integer (0,65534)              |Mandatory to use 0             |
|podSecurityContext.runAsGroup    |Integer (0,65534)              |Mandatory to use 0             |
|multus.create                    |true/false                     |false                          |
|multus.n2IPadd                   |IpAddress                      |NA                             |
|multus.n2Netmask                 |Netmask                        |NA                             |
|multus.n2Gateway                 |Gateway                        |NA                             |
|multus.hostInterface             |HostInterface Name             |NA                             |



|Parameter                      |Mandatory/Optional          |Remark                                      |
|-------------------------------|----------------------------|--------------------------------------------|
|config.mcc                     |Mandatory                   |Mobile Country Code                         |
|config.mnc                     |Mandatory                   |Mobile Network Code                         |
|config.regionId                |Mandatory                   |                                            |
|config.amfSetId                |Mandatory                   |                                            |
|config.tac                     |Hexadecimal/Mandatory       |                                            |
|config.sst0                    |Integer 1-256/Mandatory     |                                            |
|config.sd0                     |Integer/Hexadecimal/Optional|                                            |
|config.sst1                    |Optional                    |                                            |
|config.sd1                     |Optional                    |                                            |
|config.amfInterfaceNameForNGAP |eth0/net1/Mandatory         |net1 when multus is used                    |
|config.amfInterfaceNameForSBI  |eth0/Mandatory              |                                            |
|config.amfInterfaceSBIHTTPPort |Integer/Mandatory           |Standard port 80                            |
|config.amfInterfaceSBIHTTP2Port|Integer/Mandatory           |8080 if 80 is already inused                |
|config.smfFqdn                 |Mandatory                   |SMF ip-address/FQDN                         |
|config.nrfFqdn                 |Mandatory                   |NRF ip-address/FQDN                         |
|config.ausfFqdn                |Mandatory                   |AUSF ip-address/FQDN                        |
|config.nfRegistration          |Mandatory                   |yes/no                                      |
|config.nrfSelection            |Optional                    |yes/no                                      |
|config.smfSelection            |Mandatory                   |It helps in selecting the SMF via NRF       |
|config.externalAusf            |Mandatory                   |Always yes when using AUSF                  |
|config.useHttp2                |Mandatory (yes/no)          |if using HTTP/2 change the port for HTTP/1.1|
|config.mySqlServer             |Optional                    |if not using AUSF                           |
|config.mySqlUser               |Optional                    |if not using AUSF                           |
|config.externalNssf            |Optional                    |if not using AUSF                           |
|config.mySqlPass               |Optional                    |if not using AUSF                           |

Only needed if you are doing advance debugging

|Parameter                        |Allowed Values                 |Remark                         |
|---------------------------------|-------------------------------|-------------------------------|
|start.amf                        |                               |                               |
|start.tcpdump                    |                               |                               |
|includeTcpDumpContainer          |                               |                               |
|tcpdumpimage.repository          |                               |                               |
|tcpdumpimage.version             |                               |                               |
|tcpdumpimage.pullPolicy          |                               |                               |
|persistent.sharedvolume          |                               |                               |
|resources.define                 |                               |                               |
|resources.limits.tcpdump.cpu     |                               |                               |
|resources.limits.tcpdump.memory  |                               |                               |
|resources.limits.nf.cpu          |                               |                               |
|resources.limits.nf.memory       |                               |                               |
|resources.requests.tcpdump.cpu   |                               |                               |
|resources.requests.tcpdump.memory|                               |                               |
|resources.requests.nf.cpu        |                               |                               |
|readinessProbe                   |true/false                     |                               |
|livenessProbe                    |true/false                     |                               |
|terminationGracePeriodSeconds    |                               |                               |
|nodeSelector                     |Vanilla/Openshift              |                               |
|nodeName                         |Vanilla/Openshift              |                               |


