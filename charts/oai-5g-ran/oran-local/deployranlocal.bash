#!/bin/bash
mkdir -p /tmp/pcap
helm install -f ../oai-gnb-cu-cp/Chart.yaml cucp ../oai-gnb-cu-cp
while [[ $(kubectl get pods -l app=oai-gnb-cu-cp-cp -o 'jsonpath={..status.conditions[?(@.type=="Ready")].status}') != "True" ]]; do echo "waiting for pod oai-gnb-cu-cp" && sleep 1; done
CUCP=`oc get pods -o custom-columns=POD:.metadata.name --no-headers | grep oai-gnb-cu-cp`
echo "CUCP=$CUCP"
oc logs $CUCP -c gnbcucp > cucp-start.log

helm install -f ../oai-gnb-cu-up/Chart.yaml cuup ../oai-gnb-cu-up
while [[ $(kubectl get pods -l app=oai-gnb-cu-up -o 'jsonpath={..status.conditions[?(@.type=="Ready")].status}') != "True" ]]; do echo "waiting for pod oai-gnb-cu-up" && sleep 1; done
CUUP=`oc get pods -o custom-columns=POD:.metadata.name --no-headers | grep oai-gnb-cu-up`
echo "CUUP=$CUUP"
oc logs $CUUP -c gnbcuup > cuup-start.log

helm install -f ../oai-gnb-du/Chart.yaml du ../oai-gnb-du
while [[ $(kubectl get pods -l app=oai-gnb-du -o 'jsonpath={..status.conditions[?(@.type=="Ready")].status}') != "True" ]]; do echo "waiting for pod oai-gnb-du" && sleep 1; done
DU=`oc get pods -o custom-columns=POD:.metadata.name --no-headers | grep oai-gnb-du`
echo "DU=$DU"
oc logs $DU  -c gnbdu > du-start.log

sleep 4

helm install -f ../oai-nr-ue/Chart.yaml ue1 ../oai-nr-ue
while [[ $(kubectl get pods -l app=oai-nr-ue -o 'jsonpath={..status.conditions[?(@.type=="Ready")].status}') != "True" ]]; do echo "waiting for pod oai-nr-ue" && sleep 1; done
UE=`oc get pods -o custom-columns=POD:.metadata.name --no-headers | grep oai-nr-ue`
echo "UE=$UE"
oc logs $UE > ue-start.log

# helm install -f ../oai-nr-ue2/Chart.yaml ue2 ../oai-nr-ue2
# while [[ $(kubectl get pods -l app=oai-nr-ue2 -o 'jsonpath={..status.conditions[?(@.type=="Ready")].status}') != "True" ]]; do echo "waiting for pod oai-nr-ue2" && sleep 1; done
# UE2=`oc get pods -o custom-columns=POD:.metadata.name --no-headers | grep oai-nr-ue2`
# echo "UE2=$UE2"

UPF=`oc get pods -o custom-columns=POD:.metadata.name --no-headers | grep oai-spgwu-tiny`


oc logs $DU -c gnbdu > du1.log
oc logs $CUCP -c gnbcucp > cucp.log
oc logs $CUUP -c gnbcuup > cuup.log
oc logs $UE > ue1.log
sleep 1
oc logs $DU -c gnbdu > du2.log
oc logs $UE > ue2.log
sleep 2
oc logs $UE > ue3.log
sleep 4
oc rsh -c nr-ue $UE ping -c 10 8.8.8.8 -I oaitun_ue1
oc logs $UE > ue4.log


# Get only pod names
oc get pods -o custom-columns=POD:.metadata.name --no-headers
sleep 20
oc rsync -c tcpdump $CUCP:/tmp/pcap .
oc rsync -c tcpdump $CUUP:/tmp/pcap .
oc rsync -c tcpdump $DU:/tmp/pcap .
oc rsync -c tcpdump $UPF:/tmp/pcap .
mv pcap/*.pcap  /tmp/pcap
rmdir pcap

#export NR_UE_POD_NAME=$(kubectl get pods --namespace {{ .Release.Namespace }} -l "app.kubernetes.io/name={{ include "oai-nr-ue.name" . }},app.kubernetes.io/instance={{ .Release.Name }}" -o jsonpath="{.items[0].metadata.name}")
#echo "NR_UE_POD_NAME=$NR_UE_POD_NAME"

# kubectl exec -it $UE -- bash
# ping 8.8.8.8 -I oaitun_ue1 

