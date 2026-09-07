from pathlib import Path
from uuid import uuid4
import hashlib

from fastapi.testclient import TestClient
from scapy.layers.inet import IP, TCP
from scapy.layers.l2 import Ether
from scapy.utils import wrpcap
from app.main import create_app


def test_actual_pcap_import_pivot_duplicate_and_integrity(monkeypatch):
    directory = Path('.test-artifacts') / uuid4().hex
    directory.mkdir(parents=True)
    monkeypatch.setenv('NETRA_EVIDENCE_DIR', str(directory / 'evidence'))
    packet = Ether()/IP(src='10.0.0.1',dst='10.0.0.2')/TCP(sport=44000,dport=443)
    packet.time = 1770000000
    path = directory / 'source.pcap'
    wrpcap(str(path),[packet])
    content=path.read_bytes()
    with TestClient(create_app(':memory:',False)) as client:
        response=client.post('/api/v1/evidence/pcap',content=content,headers={'X-Filename':'source.pcap'})
        assert response.status_code == 201,response.text
        manifest=response.json()
        assert manifest['sha256'] == hashlib.sha256(content).hexdigest()
        assert manifest['packetCount'] == 1
        rows=client.get('/api/v1/packets').json()['data']
        assert rows[0]['srcIp']=='10.0.0.1'
        assert rows[0]['flowId']
        detail=client.get('/api/v1/packets/'+rows[0]['id']).json()
        assert detail['rawHex']==bytes(packet).hex()
        assert client.get('/api/v1/flows/'+rows[0]['flowId']).json()['evidenceId']==manifest['id']
        assert client.get('/api/v1/evidence/'+manifest['id']+'/download').content==content
        assert client.post('/api/v1/evidence/pcap',content=content).json()['duplicate'] is True
        assert client.get('/api/v1/dashboard/summary').json()['totalFlows']==1
        stored=directory/'evidence'/(manifest['id']+'.pcap')
        stored.write_bytes(b'corrupt')
        assert client.get('/api/v1/evidence/'+manifest['id']+'/download').status_code==409


def test_invalid_capture_does_not_create_telemetry():
    with TestClient(create_app(':memory:',False)) as client:
        assert client.post('/api/v1/evidence/pcap',content=b'not a capture').status_code==422
        assert client.get('/api/v1/dashboard/summary').json()['totalFlows']==0
