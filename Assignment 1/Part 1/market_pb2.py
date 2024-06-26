# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: market.proto
# Protobuf Python Version: 4.25.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0cmarket.proto\"!\n\x05\x62uyer\x12\x0c\n\x04name\x18\x05 \x01(\t\x12\n\n\x02ip\x18\x06 \x02(\t\"%\n\tregSeller\x12\x0c\n\x04uuid\x18\x07 \x02(\t\x12\n\n\x02ip\x18\x08 \x02(\t\"{\n\x14sellerMarketResponse\x12,\n\x06status\x18\x01 \x02(\x0e\x32\x1c.sellerMarketResponse.Status\x12\x12\n\nproduct_id\x18\x02 \x01(\x05\"!\n\x06Status\x12\x0b\n\x07SUCCESS\x10\x00\x12\n\n\x06\x46\x41ILED\x10\x01\"\xc7\x01\n\x08soldItem\x12\n\n\x02ip\x18\n \x02(\t\x12\x14\n\x0cproduct_name\x18\x0b \x02(\t\x12$\n\x08\x63\x61tegory\x18\x03 \x02(\x0e\x32\x12.soldItem.Category\x12\x10\n\x08quantity\x18\x04 \x02(\x05\x12\x13\n\x0b\x64\x65scription\x18\x0c \x02(\t\x12\x16\n\x0eprice_per_unit\x18\x07 \x02(\x01\"4\n\x08\x43\x61tegory\x12\x0f\n\x0b\x45LECTRONICS\x10\x01\x12\x0b\n\x07\x46\x41SHION\x10\x02\x12\n\n\x06OTHERS\x10\x03\"1\n\x08sellItem\x12\x17\n\x04item\x18\x01 \x02(\x0b\x32\t.soldItem\x12\x0c\n\x04uuid\x18\t \x01(\t\"d\n\nupdateItem\x12\x12\n\nproduct_id\x18\x01 \x02(\x05\x12\x0c\n\x04uuid\x18\t \x02(\t\x12\n\n\x02ip\x18\n \x02(\t\x12\x10\n\x08quantity\x18\x04 \x02(\x05\x12\x16\n\x0eprice_per_unit\x18\x07 \x02(\x01\"6\n\x06\x64\x65lete\x12\x12\n\nproduct_id\x18\x01 \x02(\x05\x12\x0c\n\x04uuid\x18\t \x02(\t\x12\n\n\x02ip\x18\n \x02(\t\"/\n\x13requestDisplayItems\x12\x0c\n\x04uuid\x18\x07 \x01(\t\x12\n\n\x02ip\x18\x08 \x02(\t\"Q\n\x12\x64isplaySellerItems\x12\x17\n\x04item\x18\x05 \x03(\x0b\x32\t.soldItem\x12\x12\n\nproduct_id\x18\x01 \x03(\x05\x12\x0e\n\x06rating\x18\x03 \x03(\x01\"\x7f\n\treqSearch\x12\x0c\n\x04name\x18\t \x01(\t\x12%\n\x08\x63\x61tegory\x18\x04 \x02(\x0e\x32\x13.reqSearch.Category\"=\n\x08\x43\x61tegory\x12\x0f\n\x0b\x45LECTRONICS\x10\x01\x12\x0b\n\x07\x46\x41SHION\x10\x02\x12\n\n\x06OTHERS\x10\x03\x12\x07\n\x03\x41NY\x10\x04\";\n\x07\x42uyItem\x12\x10\n\x08quantity\x18\x02 \x02(\x05\x12\x12\n\nproduct_id\x18\x01 \x02(\x05\x12\n\n\x02ip\x18\x03 \x02(\t\"*\n\x08wishlist\x12\x12\n\nproduct_id\x18\x01 \x02(\x05\x12\n\n\x02ip\x18\x03 \x02(\t\"6\n\x04rate\x12\x0e\n\x06rating\x18\x02 \x02(\x05\x12\x12\n\nproduct_id\x18\x01 \x02(\x05\x12\n\n\x02ip\x18\x03 \x02(\t2\xbd\x03\n\x06Market\x12\x35\n\x0eRegisterSeller\x12\n.regSeller\x1a\x15.sellerMarketResponse\"\x00\x12\x30\n\nAddProdcut\x12\t.sellItem\x1a\x15.sellerMarketResponse\"\x00\x12\x32\n\nUpdateItem\x12\x0b.updateItem\x1a\x15.sellerMarketResponse\"\x00\x12+\n\x07\x44\x65lItem\x12\x07.delete\x1a\x15.sellerMarketResponse\"\x00\x12\x38\n\tShowItems\x12\x14.requestDisplayItems\x1a\x13.displaySellerItems\"\x00\x12+\n\x06Search\x12\n.reqSearch\x1a\x13.displaySellerItems\"\x00\x12(\n\x03\x42uy\x12\x08.BuyItem\x1a\x15.sellerMarketResponse\"\x00\x12.\n\x08Wishlist\x12\t.wishlist\x1a\x15.sellerMarketResponse\"\x00\x12(\n\x06Rating\x12\x05.rate\x1a\x15.sellerMarketResponse\"\x00')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'market_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_BUYER']._serialized_start=16
  _globals['_BUYER']._serialized_end=49
  _globals['_REGSELLER']._serialized_start=51
  _globals['_REGSELLER']._serialized_end=88
  _globals['_SELLERMARKETRESPONSE']._serialized_start=90
  _globals['_SELLERMARKETRESPONSE']._serialized_end=213
  _globals['_SELLERMARKETRESPONSE_STATUS']._serialized_start=180
  _globals['_SELLERMARKETRESPONSE_STATUS']._serialized_end=213
  _globals['_SOLDITEM']._serialized_start=216
  _globals['_SOLDITEM']._serialized_end=415
  _globals['_SOLDITEM_CATEGORY']._serialized_start=363
  _globals['_SOLDITEM_CATEGORY']._serialized_end=415
  _globals['_SELLITEM']._serialized_start=417
  _globals['_SELLITEM']._serialized_end=466
  _globals['_UPDATEITEM']._serialized_start=468
  _globals['_UPDATEITEM']._serialized_end=568
  _globals['_DELETE']._serialized_start=570
  _globals['_DELETE']._serialized_end=624
  _globals['_REQUESTDISPLAYITEMS']._serialized_start=626
  _globals['_REQUESTDISPLAYITEMS']._serialized_end=673
  _globals['_DISPLAYSELLERITEMS']._serialized_start=675
  _globals['_DISPLAYSELLERITEMS']._serialized_end=756
  _globals['_REQSEARCH']._serialized_start=758
  _globals['_REQSEARCH']._serialized_end=885
  _globals['_REQSEARCH_CATEGORY']._serialized_start=824
  _globals['_REQSEARCH_CATEGORY']._serialized_end=885
  _globals['_BUYITEM']._serialized_start=887
  _globals['_BUYITEM']._serialized_end=946
  _globals['_WISHLIST']._serialized_start=948
  _globals['_WISHLIST']._serialized_end=990
  _globals['_RATE']._serialized_start=992
  _globals['_RATE']._serialized_end=1046
  _globals['_MARKET']._serialized_start=1049
  _globals['_MARKET']._serialized_end=1494
# @@protoc_insertion_point(module_scope)
