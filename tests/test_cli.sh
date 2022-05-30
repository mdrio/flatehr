#!/usr/bin/env bash
set -e

xml_comp=$(flatehr generate from-file -t tests/resources/web_template.json -c tests/resources/xml_conf.yaml --skip-ehr-id tests/resources/source.xml)
json_comp=$(flatehr generate from-file -t tests/resources/web_template.json -c tests/resources/json_conf.yaml --skip-ehr-id tests/resources/source.json)

expected='{"test/patient_data/primary_diagnosis/primary_diagnosis/_null_flavour|code": "253", "test/patient_data/primary_diagnosis/primary_diagnosis/_null_flavour|terminology": "openehr", "test/patient_data/primary_diagnosis/primary_diagnosis/_null_flavour|value": "unknown", "test/patient_data/primary_diagnosis/diagnosis_timing/primary_diagnosis:0/age_at_diagnosis": "P63Y", "test/patient_data/gender/biological_sex|code": "8507", "test/patient_data/gender/biological_sex|value": "MALE", "test/patient_data/gender/biological_sex|terminology": "omop_vocabulary", "test/histopathology/result_group/laboratory_test_result/any_event:0/test_name": "Histopathology", "test/histopathology/result_group/laboratory_test_result/any_event:1/test_name": "Histopathology", "ctx/language": "en", "ctx/composer_name": "test", "ctx/subject|name": "42112", "ctx/encoding|code": "UTF-8", "ctx/encoding|terminology": "IANA_character-sets", "ctx/territory|code": "IT", "ctx/territory|terminology": "ISO_3166-1", "ctx/time": "2011-11-11T00:00:00"}'
[[  "$xml_comp" == "$expected" ]]
[[  "$json_comp" == "$expected" ]]
