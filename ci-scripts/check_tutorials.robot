*** Settings ***
Library     CheckTutorial.py
Library     Process

*** Variables ***
${BASIC_STATIC_UE_TUTORIAL_PATH}  ${CURDIR}/../docs/DEPLOY_SA5G_BASIC_STATIC_UE_IP.md
${WITH_VPP_UPF_TUTORIAL_PATH}      ${CURDIR}/../docs/DEPLOY_SA5G_WITH_VPP_UPF.md

${CMD_TIMEOUT}      60s

*** Test Cases ***

Test Static IP Tutorial
    Prepare Tutorial    ${BASIC_STATIC_UE_TUTORIAL_PATH}
    Execute All Tutorial Commands

Test VPP UPF Tutorial
    Prepare Tutorial    ${WITH_VPP_UPF_TUTORIAL_PATH}
    Execute All Tutorial Commands