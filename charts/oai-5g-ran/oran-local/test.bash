#!/bin/bash
./endran.bash
./endcn.bash
sleep 3
./deploycn.bash
sleep 3
./deployran.bash
oc get pods -o custom-columns=POD:.metadata.name --no-headers
CUCP=`oc get pods -o custom-columns=POD:.metadata.name --no-headers | grep oai-gnb-cu-cp`
CUUP=`oc get pods -o custom-columns=POD:.metadata.name --no-headers | grep oai-gnb-cu-up`
DU=`oc get pods -o custom-columns=POD:.metadata.name --no-headers | grep oai-gnb-du`
UE=`oc get pods -o custom-columns=POD:.metadata.name --no-headers | grep oai-nr-ue`
UPF=`oc get pods -o custom-columns=POD:.metadata.name --no-headers | grep oai-upf`
AMF=`oc get pods -o custom-columns=POD:.metadata.name --no-headers | grep oai-amf`
SMF=`oc get pods -o custom-columns=POD:.metadata.name --no-headers | grep oai-smf`

echo "AMF=$AMF"
echo "SMF=$SMF"
echo "UPF=$UPF"

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

sleep 20
oc rsync -c tcpdump $AMF:/tmp/pcap .
oc rsync -c tcpdump $CUCP:/tmp/pcap .
oc rsync -c tcpdump $CUUP:/tmp/pcap .
oc rsync -c tcpdump $DU:/tmp/pcap .
oc rsync -c tcpdump $UPF:/tmp/pcap .
mv pcap/*.pcap  /tmp/pcap
rmdir pcap


oc logs $AMF -c amf > amf.log
oc logs $SMF -c smf > smf.log
oc logs $UPF -c upf > upf.log


