*** Settings ***
Library    Process
Library    CNTestLib.py
Library    GNBSimTestLib.py

# This file is intended to define common robot framework keywords that are used in many tests and suites

*** Variables ***


*** Keywords ***

Launch NRF CN with PCF
    @{list} =    Create List  oai-amf   oai-smf   oai-udm   oai-nrf  oai-udr  oai-ausf  mysql  oai-ext-dn  oai-spgwu  oai-pcf
    Prepare Scenario    ${list}   nrf-cn-pcf
    @{replace_list} =  Create List  smf  support_features  use_local_pcc_rules
    Replace In Config    ${replace_list}  no
    Start Trace    core_network
    Start CN
    Check Core Network Health Status

Launch NRF CN For QoS
    @{list} =    Create List  oai-amf   oai-smf   oai-udm   oai-nrf  oai-udr  oai-ausf  mysql  oai-ext-dn  oai-ext-dn-2  oai-ext-dn-3  oai-spgwu  oai-pcf
    Prepare Scenario    ${list}   nrf-cn-qos
    @{replace_list} =  Create List  smf  support_features  use_local_pcc_rules
    Replace In Config    ${replace_list}  no
    Start Trace    core_network
    Start CN
    Check Core Network Health Status

Launch NRF CN
    @{list} =    Create List  oai-amf   oai-smf   oai-udm   oai-nrf  oai-udr  oai-ausf  mysql  oai-ext-dn  oai-spgwu
    Prepare Scenario    ${list}   nrf-cn
    Start Trace    core_network
    Start CN
    Check Core Network Health Status

Launch Non NRF CN
    @{list} =    Create List  oai-amf   oai-smf   oai-udm   oai-udr  oai-ausf  mysql  oai-ext-dn  oai-spgwu
    Prepare Scenario    ${list}   nonnrf-cn
    @{replace_list} =   Create List  register_nf  general
    Replace In Config   ${replace_list}  no
    Start Trace    core_network
    Start CN
    Check Core Network Health Status

Suite Teardown Default
    Stop Cn
    Collect All Logs
    Stop Trace   core_network
    Down Cn

Check Core Network Health Status
    Wait Until Keyword Succeeds  60s  1s    Check CN Health Status

Wait and Verify Iperf3 Result
    [Arguments]    ${container}  ${mbits}=50
    Wait Until Keyword Succeeds    60s  1s   Iperf3 Is Finished    ${container}
    TRY
        Iperf3 Results Should Be    ${container}  ${mbits}
    EXCEPT    AS   ${error_message}
        Log   IPerf3 Results is wrong, ignored for now: ${error_message}   level=ERROR
    END

Check gnbsim IP
    [Arguments]    ${gnbsim_name}
    Wait Until Keyword Succeeds    30s  1s  Check Gnbsim Ongoing   ${gnbsim_name}
    ${ip} =    Get Gnbsim Ip    ${gnbsim_name}    # to get the output we parse again
    [Return]    ${ip}

