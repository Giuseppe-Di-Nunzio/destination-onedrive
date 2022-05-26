#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any, Dict, List, Mapping

import pytest
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    Status,
    SyncMode,
    Type,
)
from destination_onedrive import DestinationOnedrive


@pytest.fixture(name="config")
def config_fixture() -> Mapping[str, Any]:
    with open("secrets/config.json", "r") as f:
        return json.loads(f.read())

@pytest.fixture(name="configured_catalog")
def configured_catalog_fixture() -> ConfiguredAirbyteCatalog:
    stream_schema = {"type": "object", "properties": {"string_col": {"type": "str"}, "int_col": {"type": "integer"}}}
    #stream_schema = {"type":"object","properties":{"CORSO":{"type":"string"},"SESSO":{"type":"string"},"FACOLTA":{"type":"string"},"ISCRITTI":{"type":"number"}}}

    append_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name="append_stream", json_schema=stream_schema),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
    )

    overwrite_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name="overwrite_stream", json_schema=stream_schema),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.overwrite,
    )

    return ConfiguredAirbyteCatalog(streams=[append_stream, overwrite_stream])

def test_check_valid_config(config: Mapping):
    outcome = DestinationOnedrive().check(AirbyteLogger(), config)
    assert outcome.status == Status.SUCCEEDED

def test_check_invalid_config():
    outcome = DestinationOnedrive().check(AirbyteLogger(), {"authority": "not_a_real_authority", "client_id": "my_client", "username": "myuser@mail.com", "password": "mypassword", "folder": "my/data/folder"})
    assert outcome.status == Status.FAILED

def _state(data: Dict[str, Any]) -> AirbyteMessage:
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data=data))


def _record(stream: str, str_value: str, int_value: int) -> AirbyteMessage:
    return AirbyteMessage(
        type=Type.RECORD, record=AirbyteRecordMessage(stream=stream, data={"str_col": str_value, "int_col": int_value}, emitted_at=0)
    )

##def test_write(config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]) -> Iterable[AirbyteMessage]:
     
