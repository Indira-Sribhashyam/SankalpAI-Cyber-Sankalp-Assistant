# prepare_rag_docs.py
# Reads the devices_scan 2.csv and creates rag_docs_devices.jsonl for RAG indexing.
import pandas as pd, json
df = pd.read_csv('devices_scan 2.csv')   
docs=[]
for i,row in df.iterrows():
    device = str(row.get('device_id') or f'device-{i}')
    ports = row.get('port_list') or row.get('open_ports_list') or row.get('port_list_str') or ''
    vuln_count = row.get('known_cve_count') or row.get('vuln_count') or ''
    summary = (
        f"Device {device} | IP: {row.get('ip_address')} | ports: {ports} | "
        f"vuln_count: {vuln_count} | weak_password: {row.get('weak_password_detected')} | "
        f"external_access: {row.get('external_ip_detected')}"
    )
    docs.append({
        "id": device,
        "metadata": {
            "doc_type": "device_report",
            "device_id": device,
            "scan_ts": str(row.get('last_scan_time') or row.get('scan_date') or ''),
            "source": row.get('scan_source') or 'uploaded'
        },
        "content": summary,
        "raw": row.fillna('').to_dict()
    })
out_path = 'rag_docs_devices.jsonl'
with open(out_path,'w',encoding='utf-8') as f:
    for d in docs: f.write(json.dumps(d) + '\n')
print(f"Created {out_path} with {len(docs)} documents")
