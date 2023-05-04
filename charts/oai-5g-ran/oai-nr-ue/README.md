# Helm Chart for OAI New Radio User Equipment (OAI-NR-UE)

This helm-chart is only tested for [RF Simulated oai-nr-ue](https://gitlab.eurecom.fr/oai/openairinterface5g/-/blob/develop/radio/rfsimulator/README.md). You can read about the design of [oai-nr-ue](https://gitlab.eurecom.fr/oai/openairinterface5g/-/blob/develop/doc/nr-ue-design.md) and a non helm-chart based [tutorial](https://gitlab.eurecom.fr/oai/openairinterface5g/-/blob/develop/doc/NR_SA_Tutorial_OAI_nrUE.md#3-oai-gnb-and-oai-nrue) with USRP B210.

**Note**: This chart is tested on [Minikube](https://minikube.sigs.k8s.io/docs/) and [Red Hat Openshift](https://www.redhat.com/fr/technologies/cloud-computing/openshift) 4.10 and 4.12. RFSIM requires minimum 2CPU and 2Gi RAM and [multus-cni](https://github.com/k8snetworkplumbingwg/multus-cni) plugin for multiple interfaces. 
 
## Introduction

To know more about the feature set of OpenAirInterface you can check it [here](https://gitlab.eurecom.fr/oai/openairinterface5g/-/blob/develop/doc/FEATURE_SET.md#openairinterface-5g-nr-feature-set). 

The [codebase](https://gitlab.eurecom.fr/oai/openairinterface5g/-/tree/develop) for NR-UE is same as gNB, CU, DU, CU-CP/CU-UP. Everyweek on [docker-hub](https://hub.docker.com/r/oaisoftwarealliance/oai-gnb) our [Jenkins Platform](https://jenkins-oai.eurecom.fr/view/RAN/) publishes docker-images for `oaisoftwarealliance/oai-nr-ue` 

Each image has develop tag and a dedicated week tag for example `2023.w18`. We only publish Ubuntu 18.04/20.04 images. We do not publish RedHat/UBI images. These images you have to build from the source code on your RedHat systems or Openshift Platform. You can follow this [tutorial](../../../openshift/README.md) for that.

The helm chart of OAI-NR-UE creates multiples Kubernetes resources,

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

[Values.yaml](./values.yaml) contains all the configurable parameters. Below table defines the configurable parameters. You need a dedicated interface for for NR-UE when it will run on a different cluster then gNB/DU.


|Parameter                    |Allowed Values                 |Remark                         |
|-----------------------------|-------------------------------|-------------------------------|
|kubernetesType               |Vanilla/Openshift              |Vanilla Kubernetes or Openshift|
|nfimage.repository           |Image Name                     |                               |
|nfimage.version              |Image tag                      |                               |
|nfimage.pullPolicy           |IfNotPresent or Never or Always|                               |
|imagePullSecrets.name        |String                         |Good to use for docker hub     |
|serviceAccount.create        |true/false                     |                               |
|serviceAccount.annotations   |String                         |                               |
|serviceAccount.name          |String                         |                               |
|podSecurityContext.runAsUser |Integer (0,65534)              |                               |
|podSecurityContext.runAsGroup|Integer (0,65534)              |                               |
|multus.create                |true/false                     |                               |
|multus.iPadd                 |Ip-Address                     |                               |
|multus.netmask               |Netmask                        |                               |
|multus.defaultGateway        |Ip-Address                     |                               |
|multus.hostInterface         |host interface                 |                               |


## Advance Debugging Parameters

Only needed if you are doing advance debugging

|Parameter                        |Allowed Values                 |Remark                                        |
|---------------------------------|-------------------------------|----------------------------------------------|
|start.nrue                      |true/false                     |If true nrue container will go in sleep mode   |
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
helm install oai-nr-ue .
```

## Note

1. If you are using multus then make sure it is properly configured and if you don't have a gateway for your multus interface then avoid using gateway and defaultGateway parameter. Either comment them or leave them empty. Wrong gateway configuration can create issues with pod networking and pod will not be able to resolve service names.