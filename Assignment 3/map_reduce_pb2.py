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




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10map_reduce.proto\"\x07\n\x05\x45mpty\"C\n\x0fMapDataResponse\x12\x11\n\tmapper_id\x18\x01 \x02(\x05\x12\x0e\n\x06status\x18\x02 \x02(\t\x12\r\n\x05stage\x18\x03 \x02(\t\"T\n\x0eMapDataRequest\x12\x13\n\x0binput_split\x18\x01 \x03(\x05\x12\x19\n\tcentroids\x18\x02 \x03(\x0b\x32\x06.Point\x12\x12\n\ninput_path\x18\x03 \x02(\t\"\x1d\n\x05Point\x12\t\n\x01x\x18\x01 \x02(\x02\x12\t\n\x01y\x18\x02 \x02(\x02\"1\n\x11ReduceDataRequest\x12\x10\n\x08reducers\x18\x01 \x01(\x05\x12\n\n\x02ip\x18\x06 \x02(\t\"G\n\x12ReduceDataResponse\x12\x12\n\nreducer_id\x18\x01 \x02(\x05\x12\x0e\n\x06status\x18\x02 \x02(\t\x12\r\n\x05stage\x18\x03 \x02(\t\"2\n\x11MapperDataRequest\x12\x11\n\tmapper_id\x18\x01 \x02(\x05\x12\n\n\x02ip\x18\x06 \x02(\t\")\n\x12MapperDataResponse\x12\x13\n\x0b\x64\x61ta_points\x18\x01 \x03(\x02\"0\n\x0fKeyValueRequest\x12\x11\n\treducerId\x18\x01 \x02(\x05\x12\n\n\x02ip\x18\x06 \x02(\t\"F\n\x10KeyValueResponse\x12\"\n\x0fkey_value_pairs\x18\x01 \x03(\x0b\x32\t.KeyValue\x12\x0e\n\x06status\x18\x02 \x02(\t\"!\n\x0f\x43\x65ntroidRequest\x12\x0e\n\x06portNo\x18\x06 \x02(\t\"@\n\x10\x43\x65ntroidResponse\x12\x1c\n\tkey_value\x18\x01 \x03(\x0b\x32\t.KeyValue\x12\x0e\n\x06status\x18\x02 \x02(\t\".\n\x08KeyValue\x12\x0b\n\x03key\x18\x01 \x02(\x05\x12\x15\n\x05value\x18\x02 \x02(\x0b\x32\x06.Point2F\n\rMasterService\x12\x35\n\x0eSendMapperData\x12\x0f.MapDataRequest\x1a\x10.MapDataResponse\"\x00\x32\xfc\x01\n\rMapperService\x12\'\n\tHeartbeat\x12\x06.Empty\x1a\x10.MapDataResponse\"\x00\x12*\n\x0cPartitioning\x12\x06.Empty\x1a\x10.MapDataResponse\"\x00\x12%\n\x07Mapping\x12\x06.Empty\x1a\x10.MapDataResponse\"\x00\x12\x34\n\rGetMapperData\x12\x0f.MapDataRequest\x1a\x10.MapDataResponse\"\x00\x12\x39\n\x10SendKeyValuePair\x12\x10.KeyValueRequest\x1a\x11.KeyValueResponse\"\x00\x32\x83\x02\n\x0eReducerService\x12*\n\tHeartbeat\x12\x06.Empty\x1a\x13.ReduceDataResponse\"\x00\x12)\n\x08Reducing\x12\x06.Empty\x1a\x13.ReduceDataResponse\"\x00\x12/\n\x0eShuffleSorting\x12\x06.Empty\x1a\x13.ReduceDataResponse\"\x00\x12.\n\rGetMapperData\x12\x06.Empty\x1a\x13.ReduceDataResponse\"\x00\x12\x39\n\x10SendNewCentroids\x12\x10.CentroidRequest\x1a\x11.CentroidResponse\"\x00')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'map_reduce_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_EMPTY']._serialized_start=20
  _globals['_EMPTY']._serialized_end=27
  _globals['_MAPDATARESPONSE']._serialized_start=29
  _globals['_MAPDATARESPONSE']._serialized_end=96
  _globals['_MAPDATAREQUEST']._serialized_start=98
  _globals['_MAPDATAREQUEST']._serialized_end=182
  _globals['_POINT']._serialized_start=184
  _globals['_POINT']._serialized_end=213
  _globals['_REDUCEDATAREQUEST']._serialized_start=215
  _globals['_REDUCEDATAREQUEST']._serialized_end=264
  _globals['_REDUCEDATARESPONSE']._serialized_start=266
  _globals['_REDUCEDATARESPONSE']._serialized_end=337
  _globals['_MAPPERDATAREQUEST']._serialized_start=339
  _globals['_MAPPERDATAREQUEST']._serialized_end=389
  _globals['_MAPPERDATARESPONSE']._serialized_start=391
  _globals['_MAPPERDATARESPONSE']._serialized_end=432
  _globals['_KEYVALUEREQUEST']._serialized_start=434
  _globals['_KEYVALUEREQUEST']._serialized_end=482
  _globals['_KEYVALUERESPONSE']._serialized_start=484
  _globals['_KEYVALUERESPONSE']._serialized_end=554
  _globals['_CENTROIDREQUEST']._serialized_start=556
  _globals['_CENTROIDREQUEST']._serialized_end=589
  _globals['_CENTROIDRESPONSE']._serialized_start=591
  _globals['_CENTROIDRESPONSE']._serialized_end=655
  _globals['_KEYVALUE']._serialized_start=657
  _globals['_KEYVALUE']._serialized_end=703
  _globals['_MASTERSERVICE']._serialized_start=705
  _globals['_MASTERSERVICE']._serialized_end=775
  _globals['_MAPPERSERVICE']._serialized_start=778
  _globals['_MAPPERSERVICE']._serialized_end=1030
  _globals['_REDUCERSERVICE']._serialized_start=1033
  _globals['_REDUCERSERVICE']._serialized_end=1292
# @@protoc_insertion_point(module_scope)
