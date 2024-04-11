# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: map_reduce.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10map_reduce.proto\"/\n\x0eMapDataRequest\x12\x11\n\tmapper_id\x18\x01 \x02(\x05\x12\n\n\x02ip\x18\x06 \x02(\t\"U\n\x0fMapDataResponse\x12\x13\n\x0binput_split\x18\x01 \x03(\x05\x12\x19\n\tcentroids\x18\x02 \x03(\x0b\x32\x06.Point\x12\x12\n\ninput_path\x18\x03 \x02(\t\"\x1d\n\x05Point\x12\t\n\x01x\x18\x01 \x02(\x02\x12\t\n\x01y\x18\x02 \x02(\x02\"1\n\x11ReduceDataRequest\x12\x10\n\x08reducers\x18\x01 \x01(\x05\x12\n\n\x02ip\x18\x06 \x02(\t\"%\n\x12ReduceDataResponse\x12\x0f\n\x07message\x18\x01 \x01(\t\"2\n\x11MapperDataRequest\x12\x11\n\tmapper_id\x18\x01 \x02(\x05\x12\n\n\x02ip\x18\x06 \x02(\t\")\n\x12MapperDataResponse\x12\x13\n\x0b\x64\x61ta_points\x18\x01 \x03(\x02\"0\n\x0fKeyValueRequest\x12\x11\n\treducerId\x18\x01 \x02(\x05\x12\n\n\x02ip\x18\x06 \x02(\t\"6\n\x10KeyValueResponse\x12\"\n\x0fkey_value_pairs\x18\x01 \x03(\x0b\x32\t.KeyValue\"L\n\x10PartitionRequest\x12\x12\n\nreducer_id\x18\x01 \x02(\x05\x12\x18\n\x05pairs\x18\x02 \x03(\x0b\x32\t.KeyValue\x12\n\n\x02ip\x18\x06 \x02(\t\"$\n\x11PartitionResponse\x12\x0f\n\x07message\x18\x01 \x01(\t\".\n\x08KeyValue\x12\x0b\n\x03key\x18\x01 \x02(\x05\x12\x15\n\x05value\x18\x02 \x02(\x0b\x32\x06.Point2\x83\x01\n\rMasterService\x12\x35\n\x0eSendMapperData\x12\x0f.MapDataRequest\x1a\x10.MapDataResponse\"\x00\x12;\n\x0eInvokeReducers\x12\x12.ReduceDataRequest\x1a\x13.ReduceDataResponse\"\x00\x32J\n\rMapperService\x12\x39\n\x10SendKeyValuePair\x12\x10.KeyValueRequest\x1a\x11.KeyValueResponse\"\x00\x32J\n\x0eReducerService\x12\x38\n\rSendPartition\x12\x11.PartitionRequest\x1a\x12.PartitionResponse\"\x00')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'map_reduce_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_MAPDATAREQUEST']._serialized_start=20
  _globals['_MAPDATAREQUEST']._serialized_end=67
  _globals['_MAPDATARESPONSE']._serialized_start=69
  _globals['_MAPDATARESPONSE']._serialized_end=154
  _globals['_POINT']._serialized_start=156
  _globals['_POINT']._serialized_end=185
  _globals['_REDUCEDATAREQUEST']._serialized_start=187
  _globals['_REDUCEDATAREQUEST']._serialized_end=236
  _globals['_REDUCEDATARESPONSE']._serialized_start=238
  _globals['_REDUCEDATARESPONSE']._serialized_end=275
  _globals['_MAPPERDATAREQUEST']._serialized_start=277
  _globals['_MAPPERDATAREQUEST']._serialized_end=327
  _globals['_MAPPERDATARESPONSE']._serialized_start=329
  _globals['_MAPPERDATARESPONSE']._serialized_end=370
  _globals['_KEYVALUEREQUEST']._serialized_start=372
  _globals['_KEYVALUEREQUEST']._serialized_end=420
  _globals['_KEYVALUERESPONSE']._serialized_start=422
  _globals['_KEYVALUERESPONSE']._serialized_end=476
  _globals['_PARTITIONREQUEST']._serialized_start=478
  _globals['_PARTITIONREQUEST']._serialized_end=554
  _globals['_PARTITIONRESPONSE']._serialized_start=556
  _globals['_PARTITIONRESPONSE']._serialized_end=592
  _globals['_KEYVALUE']._serialized_start=594
  _globals['_KEYVALUE']._serialized_end=640
  _globals['_MASTERSERVICE']._serialized_start=643
  _globals['_MASTERSERVICE']._serialized_end=774
  _globals['_MAPPERSERVICE']._serialized_start=776
  _globals['_MAPPERSERVICE']._serialized_end=850
  _globals['_REDUCERSERVICE']._serialized_start=852
  _globals['_REDUCERSERVICE']._serialized_end=926
# @@protoc_insertion_point(module_scope)
