#!/bin/bash
mkdir -p /tmp/pcap
cd ../../oai-5g-core/oai-5g-basic && helm dependency update && helm spray .
