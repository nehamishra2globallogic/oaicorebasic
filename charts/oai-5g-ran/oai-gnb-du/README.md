# Helm Chart for OAI Distributed Unit (OAI-DU)

This helm-chart is only tested for [RF Simulated oai-du](https://gitlab.eurecom.fr/oai/openairinterface5g/-/blob/develop/radio/rfsimulator/README.md). Though it is designed to work with split 8 radio units or USRPs. In `template/deployment.yaml` there is a section to use it with USB based USRPs. The option to use RFSIM, USRPs or Radio Units is decided via configuration file. The container image always remains the same. 

We are in the process of testing the helm-chart with different USRPs, Radio Units and extend it for O-RAN 7.2 interface. We have already implemented 7.2 interface in OAI codebase.

Before using this helm-chart we recommend you read about OAI codebase and its working from the documents listed on [OAI gitlab](https://gitlab.eurecom.fr/oai/openairinterface5g/-/tree/develop/doc)

**Note**: This chart is tested on [Minikube](https://minikube.sigs.k8s.io/docs/) and [Red Hat Openshift](https://www.redhat.com/fr/technologies/cloud-computing/openshift) 4.10 and 4.12. RFSIM requires minimum 2CPU and 2Gi RAM. 

## Introduction

To know more about the feature set of OpenAirInterface you can check it [here](https://gitlab.eurecom.fr/oai/openairinterface5g/-/blob/develop/doc/FEATURE_SET.md#openairinterface-5g-nr-feature-set). 

The [codebase](https://gitlab.eurecom.fr/oai/openairinterface5g/-/tree/develop) for gNB, CU, DU, CU-CP/CU-UP, NR-UE is the same. Everyweek on [docker-hub](https://hub.docker.com/r/oaisoftwarealliance/oai-gnb) our [Jenkins Platform](https://jenkins-oai.eurecom.fr/view/RAN/) publishes two docker-images 

1. `oaisoftwarealliance/oai-gnb` for monolithic gNB, DU, CU, CU-CP 
2. `oaisoftwarealliance/oai-nr-cuup` for CU-UP. 

Each image has develop tag and a dedicated week tag for example `2023.w18`. We only publish Ubuntu 18.04/20.04 images. We do not publish RedHat/UBI images. These images you have to build from the source code on your RedHat systems or Openshift Platform. You can follow this [tutorial](../../../openshift/README.md) for that.

The helm chart of OAI-DU creates multiples Kubernetes resources,

1. Service
2. Role Base Access Control (RBAC) (role and role bindings)
3. Deployment
4. Configmap
5. Service account
6. Network-attachment-defination (Optional only when multus is used)

The directory structure

```
.
├── Chart.yaml
├── templates
│   ├── configmap.yaml
│   ├── deployment.yaml
│   ├── _helpers.tpl
│   ├── multus.yaml
│   ├── NOTES.txt
│   ├── rbac.yaml
│   ├── serviceaccount.yaml
│   └── service.yaml
└── values.yaml
```

## Parameters

[Values.yaml](./values.yaml) contains all the configurable parameters. Below table defines the configurable parameters. You need a dedicated interface for Fronthaul.


|Parameter                       |Allowed Values                 |Remark                          |
|--------------------------------|-------------------------------|--------------------------------|
|kubernetesType                  |Vanilla/Openshift              |Vanilla Kubernetes or Openshift |
|nfimage.repository              |Image Name                     |                                |
|nfimage.version                 |Image tag                      |                                |
|nfimage.pullPolicy              |IfNotPresent or Never or Always|                                |
|imagePullSecrets.name           |String                         |Good to use for docker hub      |
|serviceAccount.create           |true/false                     |                                |
|serviceAccount.annotations      |String                         |                                |
|serviceAccount.name             |String                         |                                |
|podSecurityContext.runAsUser    |Integer (0,65534)              |                                |
|podSecurityContext.runAsGroup   |Integer (0,65534)              |                                |
|multus.defaultGateway           |Ip-Address                     |default route in the pod        |
|multus.f1Interface.create       |true/false                     |                                |
|multus.f1Interface.IPadd        |Ip-Address                     |                                |
|multus.f1Interface.Netmask      |Netmask                        |                                |
|multus.f1Interface.Gateway      |Ip-Address                     |                                |
|multus.f1Interface.hostInterface|host interface                 |                                |
|multus.ruInterface.create       |true/false                     |                                |
|multus.ruInterface.IPadd        |Ip-Address                     |                                |
|multus.ruInterface.Netmask      |Netmask                        |                                |
|multus.ruInterface.Gateway      |Ip-Address                     |                                |
|multus.ruInterface.hostInterface|host interface                 |                                |
|multus.ruInterface.mtu          |Integer                        ||Range [0, Parent interface MTU]|


The config parameters mentioned in `config` block of `values.yaml` are limited on purpose to maintain simplicity. They do not allow changing a lot of parameters of oai-gnb. If you want to use your own configuration file for oai-gnb-du. It is recommended to copy it in `templates/configmap.yaml` and set `config.mountConfig` as `true`. The command line for gnb is provided in `config.useAdditionalOptions`.

The charts are configured to be used with primary CNI of Kubernetes. When you will mount the configuration file you have to define static ip-addresses for F1 and RU. Most of the primary CNIs do not allow static ip-address allocation. To overcome this we are using multus-cni with static ip-address allocation. At minimum you have to create one multus interface which you can use for F1 and RU. If you want you can create dedicated interfaces. 

You can find [here](https://gitlab.eurecom.fr/oai/openairinterface5g/-/tree/develop/targets/PROJECTS/GENERIC-NR-5GC/CONF) different sample configuration files for different bandwidths and frequencies. The binary of oai-gnb is called as `nr-softmodem`. To know more about its functioning and command line parameters you can visit this [page](https://gitlab.eurecom.fr/oai/openairinterface5g/-/blob/develop/doc/RUNMODEM.md)

## Advance Debugging Parameters

Only needed if you are doing advance debugging

|Parameter                        |Allowed Values                 |Remark                                        |
|---------------------------------|-------------------------------|----------------------------------------------|
|start.gnbdu                      |true/false                     |If true gnbdu container will go in sleep mode   |
|start.tcpdump                    |true/false                     |If true tcpdump container will go in sleepmode|
|includeTcpDumpContainer          |true/false                     |If false no tcpdump container will be there   |
|tcpdumpimage.repository          |Image Name                     |                                              |
|tcpdumpimage.version             |Image tag                      |                                              |
|tcpdumpimage.pullPolicy          |IfNotPresent or Never or Always|                                              |
|persistent.sharedvolume          |true/false                     |Save the pcaps in a shared volume with NRF    |
|resources.define                 |true/false                     |                                              |
|resources.limits.tcpdump.cpu     |string                         |Unit m for milicpu or cpu                     |
|resources.limits.tcpdump.memory  |string                         |Unit Mi/Gi/MB/GB                              |
|resources.limits.nf.cpu          |string                         |Unit m for milicpu or cpu                     |
|resources.limits.nf.memory       |string                         |Unit Mi/Gi/MB/GB                              |
|resources.requests.tcpdump.cpu   |string                         |Unit m for milicpu or cpu                     |
|resources.requests.tcpdump.memory|string                         |Unit Mi/Gi/MB/GB                              |
|resources.requests.nf.cpu        |string                         |Unit m for milicpu or cpu                     |
|resources.requests.nf.memory     |string                         |Unit Mi/Gi/MB/GB                              |
|readinessProbe                   |true/false                     |default true                                  |
|livenessProbe                    |true/false                     |default false                                 |
|terminationGracePeriodSeconds    |5                              |In seconds (default 5)                        |
|nodeSelector                     |Node label                     |                                              |
|nodeName                         |Node Name                      |                                              |

## How to use

```bash
helm install oai-gnb-du .
```

## Note

1. If you are using multus then make sure it is properly configured and if you don't have a gateway for your multus interface then avoid using gateway and defaultGateway parameter. Either comment them or leave them empty. Wrong gateway configuration can create issues with pod networking and pod will not be able to resolve service names.