#!/bin/bash
mkdir -p /tmp/pcap
while [[ $(kubectl get pods -l app=oai-amf -o 'jsonpath={..status.conditions[?(@.type=="Ready")].status}') != "True" ]]; do echo "waiting for pod oai-amf" && sleep 1; done
while [[ $(kubectl get pods -l app=oai-smf -o 'jsonpath={..status.conditions[?(@.type=="Ready")].status}') != "True" ]]; do echo "waiting for pod oai-smf" && sleep 1; done
while [[ $(kubectl get pods -l app=oai-upf -o 'jsonpath={..status.conditions[?(@.type=="Ready")].status}') != "True" ]]; do echo "waiting for pod oai-upf" && sleep 1; done
sleep 5

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

sleep 5

helm install -f ../oai-nr-ue/Chart.yaml ue1 ../oai-nr-ue
while [[ $(kubectl get pods -l app=oai-nr-ue -o 'jsonpath={..status.conditions[?(@.type=="Ready")].status}') != "True" ]]; do echo "waiting for pod oai-nr-ue" && sleep 1; done
UE=`oc get pods -o custom-columns=POD:.metadata.name --no-headers | grep oai-nr-ue`
echo "UE=$UE"
oc logs $UE > ue-start.log

