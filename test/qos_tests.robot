*** Settings ***
Library    Process
Library    CNTestLib.py

Test Setup    Test Setup Default
Test Teardown    Test Teardown Default

*** Variables ***
${DOCKER_COMPOSE_FILE}          ${CURDIR}/docker-compose-qos-tests.yaml
${GNBSIM_DOCKER_COMPOSE_FILE}   ${CURDIR}/docker-compose-gnbsim-vpp.yaml
${CN_HEALTHY_NFs}               11

${EXT_DN1_IP}                   192.168.73.135
${EXT_DN2_IP}                   192.168.73.136
${EXT_DN3_IP}                   192.168.73.137

${LOG_DIR}                      ${CURDIR}/logs/

*** Test Cases ***

Default QoS Session AMBR
    Configure Default Qos  5qi=9  session_ambr=50  # TODO
    Start GnbSIM
    ${ip} =  Check Gnbsim IP
    # UPLINK
    Start Iperf3 Server     oai-ext-dn-1
    Start Iperf3 Client     gnbsim-vpp  ${ip}  ${EXT_DN1_IP}  bandwidth=40
    Wait and Verify Iperf3 Result   gnbsim-vpp  40

    Start Iperf3 Client    gnbsim-vpp   ${ip}  ${EXT_DN1_IP}  bandwidth=60
    Wait And Verify Iperf3 Result    gnbsim-vpp    50
    Stop Iperf3 Server    oai-ext-dn-1

    # DOWNLINK
    Start Iperf3 Server     gnbsim-vpp   bind_ip=${ip}
    Start Iperf3 Client     oai-ext-dn-1  ${EXT_DN1_IP}  ${ip}   bandwidth=40
    Wait And Verify Iperf3 Result    oai-ext-dn-1    40

    Start Iperf3 Client     oai-ext-dn-1  ${EXT_DN1_IP}  ${ip}   bandwidth=60
    Wait And Verify Iperf3 Result    oai-ext-dn-1    50
    Stop Iperf3 Server      gnbsim-vpp


QoS Flow Session AMBR
    Configure Default Qos  five_qi=9  session_ambr=50  # TODO
    Add Qos Flow On Pcf    five_qi=5  match=${EXT_DN2_IP}
    Start GnbSIM
    ${ip} =  Check Gnbsim IP
    Start Iperf3 Server     gnbsim-vpp   39265   bind_ip=${ip}
    Start Iperf3 Client     oai-ext-dn-1   ${EXT_DN1_IP}  ${ip}

    Start Iperf3 Server    gnbsim-vpp    39266   bind_ip=${ip}
    Start Iperf3 Client    oai-ext-dn-2   ${EXT_DN2_IP}  ${ip}   port=39266   bandwidth=10

    Wait And Verify Iperf3 Result    oai-ext-dn-1    40
    Wait And Verify Iperf3 Result    oai-ext-dn-2    10


QoS Flow GBR Session AMBR
    Configure Default Qos  5qi=9  session_ambr=50  # TODO
    Add Qos Flow On Pcf    five_qi=1   gfbr=10   mfbr=11   match=${EXT_DN_2_IP}
    Start GnbSIM
    ${ip} =  Check Gnbsim IP
    Start Iperf3 Server     gnbsim-vpp   39265   bind_ip=${ip}
    Start Iperf3 Client     oai-ext-dn-1   ${EXT_DN1_IP}  ${ip}

    Start Iperf3 Server    gnbsim-vpp    39266   bind_ip=${ip}
    Start Iperf3 Client    oai-ext-dn-2   ${EXT_DN2_IP}  ${ip}   port=39266   bandwidth=10

    Wait And Verify Iperf3 Result    oai-ext-dn-1    40
    Wait And Verify Iperf3 Result    oai-ext-dn-2    10

QoS Flow GBR Session AMBR 2
    Configure Default Qos  5qi=9  session_ambr=50  # TODO
    Add Qos Flow On Pcf    five_qi=5    match=${EXT_DN_2_IP}
    Add Qos Flow On Pcf    five_qi=1   gfbr=10   mfbr=11   match=${EXT_DN_3_IP}
    Start GnbSIM
    ${ip} =  Check Gnbsim IP
    Start Iperf3 Server     gnbsim-vpp   39265   bind_ip=${ip}
    Start Iperf3 Client     oai-ext-dn-1   ${EXT_DN1_IP}  ${ip}

    Start Iperf3 Server    gnbsim-vpp    39266   bind_ip=${ip}
    Start Iperf3 Client    oai-ext-dn-2   ${EXT_DN2_IP}  ${ip}   port=39266   bandwidth=10

    Start Iperf3 Server    gnbsim-vpp    39267   bind_ip=${ip}
    Start Iperf3 Client    oai-ext-dn-3   ${EXT_DN3_IP}  ${ip}   port=39267   bandwidth=10

    Wait And Verify Iperf3 Result    oai-ext-dn-1    0
    Wait And Verify Iperf3 Result    oai-ext-dn-2    5
    Wait And Verify Iperf3 Result    oai-ext-dn-3    10

*** Keywords ***

Test Setup Default
    # To make sure there is nothing left from other (manual) tests
    Down Docker Compose    ${DOCKER_COMPOSE_FILE}
    Down Docker Compose    ${GNBSIM_DOCKER_COMPOSE_FILE}
    Start Docker Compose    ${DOCKER_COMPOSE_FILE}
    Check Core Network Health Status    ${DOCKER_COMPOSE_FILE}

Test Teardown Default
    Stop Docker Compose   ${DOCKER_COMPOSE_FILE}
    Stop Docker Compose    ${GNBSIM_DOCKER_COMPOSE_FILE}
    Collect All Logs    ${LOG_DIR}${TEST NAME}   ${DOCKER_COMPOSE_FILE}
    Collect All Logs    ${LOG_DIR}${TEST NAME}   ${GNBSIM_DOCKER_COMPOSE_FILE}
    Down Docker Compose    ${DOCKER_COMPOSE_FILE}
    Down Docker Compose    ${GNBSIM_DOCKER_COMPOSE_FILE}

Start Docker Compose
    [Arguments]    ${docker-compose-file}
    ${res} =  Run Process    docker-compose   -f   ${docker-compose-file}   up   -d   timeout=10s
    Check Process Result    ${res}

Stop Docker Compose
    [Arguments]    ${docker-compose-file}
    ${res} =  Run Process    docker-compose   -f   ${docker-compose-file}   stop   timeout=20s
    Check Process Result    ${res}

Down Docker Compose
    [Arguments]    ${docker-compose-file}
    ${res} =  Run Process    docker-compose   -f   ${docker-compose-file}   down   timeout=20s
    Check Process Result    ${res}

Start gnbSIM
    Start Docker Compose    ${GNBSIM_DOCKER_COMPOSE_FILE}

Check Core Network Health Status
    [Arguments]    ${docker-compose-file}
    Wait Until Keyword Succeeds  60s  1s    Check CN Health Status   ${docker-compose-file}

Wait and Verify Iperf3 Result
    [Arguments]    ${container}  ${mbits}=50
    Wait Until Keyword Succeeds    60s  1s   Iperf3 Is Finished    ${container}
    TRY
        Iperf3 Results Should Be    ${container}  ${mbits}
    EXCEPT
        Log   IPerf3 Results is wrong, ignored for now   level=ERROR
    END

Check gnbsim IP
    Wait Until Keyword Succeeds    30s  1s  Get Gnbsim Ip    gnbsim-vpp
    ${ip} =    Get Gnbsim Ip    gnbsim-vpp    # to get the output we parse again
    [Return]    ${ip}

Check Process Result
    [Arguments]    ${res}
    IF  ${res.rc}!=0
        Log    ${res.stdout}   level=ERROR
        Log    ${res.stderr}   level=ERROR
        Fail   Return Code != 0
    END
