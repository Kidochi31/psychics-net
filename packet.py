from enum import Enum
from typing import Any

class PacketType(Enum):
    REQUEST = 0b10000000
    ACCEPT = 0b01000000
    DATA = 0b00100000
    NAK = 0b00010000

class FieldType(Enum):
    PAD16 = -2
    PAD8 = -1
    INT8 = 0
    INT16 = 1
    INT24 = 2
    INT32 = 3
    INT64 = 4
    VARCHAR = 5
    ENDVARINT16 = 6
    ENDDATA = 7
    SINT16 = 8


PACKET_FIELDS :dict[PacketType, list[tuple[str, FieldType]]] = ({
    PacketType.REQUEST: [("vers", FieldType.INT8), ("version", FieldType.INT16), ("name", FieldType.VARCHAR), ("data", FieldType.ENDDATA)],
    PacketType.ACCEPT: [("vers", FieldType.INT8), ("version", FieldType.INT16), ("timestep0", FieldType.INT64), ("lentimestep", FieldType.INT16), ("pad", FieldType.PAD16), ("timestamp", FieldType.INT32), ("data", FieldType.ENDDATA)],
    PacketType.DATA: [("timestep", FieldType.INT24), ("timestamp", FieldType.INT16), ("delay", FieldType.SINT16), ("seg", FieldType.INT16), ("totalsegs", FieldType.INT16), ("data", FieldType.ENDDATA)],
    PacketType.NAK: [("timestep", FieldType.INT24), ("segs", FieldType.ENDVARINT16)]
    })

def create_request_packet(vers: int, version: int, name: str, data: bytes) -> bytes | None:
    result : dict[str, Any] = {}
    result["vers"] = vers
    result["version"] = version
    result["name"] = name
    result["data"] = data
    return create_packet_safe(PacketType.REQUEST, result)

def create_accept_packet(vers: int, version: int, timestep0: int, lentimestep: int, timestamp: int, data: bytes) -> bytes | None:
    result : dict[str, Any] = {}
    result["vers"] = vers
    result["version"] = version
    result["timestep0"] = timestep0
    result["lentimestep"] = lentimestep
    result["timestamp"] = timestamp
    result["data"] = data
    return create_packet_safe(PacketType.ACCEPT, result)

def create_data_packet(timestep: int, timestamp: int, delay: int, seg: int, totalsegs: int, data: bytes) -> bytes | None:
    result : dict[str, Any] = {}
    result["timestep"] = timestep
    result["timestamp"] = timestamp
    result["delay"] = delay
    result["seg"] = seg
    result["totalsegs"] = totalsegs
    result["data"] = data
    return create_packet_safe(PacketType.DATA, result)

def create_nak_packet(timestep: int, segs: list[int]) -> bytes | None:
    result : dict[str, Any] = {}
    result["timestep"] = timestep
    result["segs"] = segs
    return create_packet_safe(PacketType.NAK, result)

def create_packet_safe(type: PacketType, data: dict[str, Any]) -> bytes | None:
    try:
        return create_packet(type, data)
    except:
        return None

def create_packet(type: PacketType, data: dict[str, Any]) -> bytes:
    fields = PACKET_FIELDS[type]
    packet_data = create_bytes(type.value, FieldType.INT8)
    for field, field_type in fields:
        if field in data:
            try:
                packet_data += create_bytes(data[field], field_type)
            except:
                print(f"Error in creating packet field of type {field_type} with value {data[field]} for field {field} in packet of type {type}.")
                raise
        else:
            try:
                packet_data += create_bytes(None, field_type)
            except:
                print(f"Error in creating packet field of type {field_type} with no value for field {field} in packet of type {type}.")
                raise
    return packet_data

def create_bytes(data: Any, type: FieldType) -> bytes:
    match type:
        case FieldType.PAD16:
            return b'\0\0'
        case FieldType.PAD8:
            return b'\0'
        case FieldType.INT8:
            return int(data).to_bytes(1, byteorder="big")
        case FieldType.INT16:
            return int(data).to_bytes(2, byteorder="big")
        case FieldType.SINT16:
            return int(data).to_bytes(2, byteorder="big", signed=True)
        case FieldType.INT24:
            return int(data).to_bytes(3, byteorder="big")
        case FieldType.INT32:
            return int(data).to_bytes(4, byteorder="big")
        case FieldType.INT64:
            return int(data).to_bytes(8, byteorder="big")
        case FieldType.VARCHAR:
            data_string = str(data).encode()
            if len(data_string) > 255:
                data_string = data_string[0:256]
            length = len(data_string)
            return int(length).to_bytes(1, byteorder="big") + data_string
        case FieldType.ENDVARINT16:
            result = b''
            for value in data:
                result += int(value).to_bytes(2, byteorder="big")
            return result
        case FieldType.ENDDATA:
            return data

def interpret_packet_safe(data: bytes) -> tuple[PacketType, dict[str, Any]] | None:
    try:
        return interpret_packet(data)
    except:
        return None

def interpret_packet(data: bytes) -> tuple[PacketType, dict[str, Any]]:
    int_type, size = interpret_bytes(data, FieldType.INT8)
    type = PacketType(int_type)
    data = data[size:]
    fields = PACKET_FIELDS[type]
    result: dict[str, Any] = {}
    for field, field_type in fields:
        try:
            interpret_result, size = interpret_bytes(data, field_type)
            if interpret_result is not None:
                result[field] = interpret_result
            data = data[size:]
        except:
            print(f"Error in interpreting packet field of type {field_type} with value {data} for field {field} in packet of type {type}.")
            raise
    return (type, result)

def interpret_bytes(data: bytes, type: FieldType) -> tuple[Any | None, int]:
    match type:
        case FieldType.PAD16:
            return (None, 2)
        case FieldType.PAD8:
            return (None, 1)
        case FieldType.INT8:
            return (int.from_bytes(data[0:1], byteorder="big"), 1)
        case FieldType.INT16:
            return (int.from_bytes(data[0:2], byteorder="big"), 2)
        case FieldType.SINT16:
             return (int.from_bytes(data[0:2], byteorder="big", signed=True), 2)
        case FieldType.INT24:
            return (int.from_bytes(data[0:3], byteorder="big"), 3)
        case FieldType.INT32:
            return (int.from_bytes(data[0:4], byteorder="big"), 4)
        case FieldType.INT64:
            return (int.from_bytes(data[0:8], byteorder="big"), 8)
        case FieldType.VARCHAR:
            length = int.from_bytes(data[0:1], byteorder="big")
            data = data[1:]
            length = min(length, len(data))
            data_string = data[0:length].decode()
            return (data_string, length + 1)
        case FieldType.ENDVARINT16:
            length = len(data)
            result: list[int] = []
            while len(data) >= 2:
                result.append(int.from_bytes(data[0:2], byteorder="big"))
                data = data[2:]
            return (result, length)
        case FieldType.ENDDATA:
            length = len(data)
            return (data, length)