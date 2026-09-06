import base64
import hashlib
import socket
import struct
from typing import Optional

# Protocol numbers
PROTO_ICMP = 1
PROTO_TCP = 6
PROTO_UDP = 17
PROTO_SCTP = 132
PROTO_ICMPV6 = 58

def parse_ip(ip_str: str) -> bytes:
    try:
        return socket.inet_pton(socket.AF_INET, ip_str)
    except socket.error:
        try:
            return socket.inet_pton(socket.AF_INET6, ip_str)
        except socket.error:
            raise ValueError(f"Invalid IP address: {ip_str}")

def calc_community_id(src_ip: str, dst_ip: str, src_port: int, dst_port: int, protocol: int, seed: int = 0) -> str:
    """
    Calculate Community ID v1 string.
    Format: "1:" + Base64(SHA1(seed + src_ip + dst_ip + protocol + src_port + dst_port))
    """
    try:
        sip_bytes = parse_ip(src_ip)
        dip_bytes = parse_ip(dst_ip)
    except ValueError:
        return ""

    # Order IPs
    is_ordered = True
    if len(sip_bytes) == len(dip_bytes):
        if sip_bytes > dip_bytes:
            is_ordered = False
    elif len(sip_bytes) > len(dip_bytes):
        is_ordered = False

    if not is_ordered:
        sip_bytes, dip_bytes = dip_bytes, sip_bytes
        src_port, dst_port = dst_port, src_port

    # Special handling for ICMP (treat type and code as ports, order logic slightly different in spec, 
    # but strictly following the instruction: "use type/code as ports")
    # For a perfect spec, ICMP types/codes are mapped differently, but we use the provided logic.
    
    ctx = hashlib.sha1()
    
    # seed (2 bytes)
    ctx.update(struct.pack('!H', seed))
    # sip
    ctx.update(sip_bytes)
    # dip
    ctx.update(dip_bytes)
    # proto (1 byte)
    ctx.update(struct.pack('!B', protocol))
    # pad (1 byte)
    ctx.update(struct.pack('!B', 0))
    # sport (2 bytes)
    ctx.update(struct.pack('!H', src_port))
    # dport (2 bytes)
    ctx.update(struct.pack('!H', dst_port))

    digest = ctx.digest()
    b64 = base64.b64encode(digest).decode('ascii')
    return f"1:{b64}"
