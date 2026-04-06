# prepare_rag_docs.py
# Reads devices_scan 2.csv and cve_data_ext.csv and creates rag_docs_devices.jsonl for RAG indexing.
import pandas as pd, json
import os
import hashlib
from langchain_text_splitters import RecursiveCharacterTextSplitter

state_file = "ingestion_state.json"
processed_state = {}
if os.path.exists(state_file):
    try:
        with open(state_file, "r", encoding="utf-8") as f:
            processed_state = json.load(f)
    except Exception:
        pass

docs = []

# 1) Load Device Scan Data
if os.path.exists('devices_scan 2.csv'):
    df_devices = pd.read_csv('devices_scan 2.csv')   
    for i, row in df_devices.iterrows():
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

# 2) Load External CVE Data
if os.path.exists('cve_data_ext.csv'):
    df_cves = pd.read_csv('cve_data_ext.csv')
    
    # Initialize text splitter for chunking long descriptions & remediations
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    
    for i, row in df_cves.iterrows():
        cve_id = str(row.get('cve_id'))
        row_dict = row.fillna('').to_dict()
        
        # Hash check to avoid re-chunking
        row_str = json.dumps(row_dict, sort_keys=True)
        row_hash = hashlib.md5(row_str.encode('utf-8')).hexdigest()
        
        if cve_id in processed_state and processed_state[cve_id].get("hash") == row_hash:
            docs.extend(processed_state[cve_id]["chunks"])
            continue

        base_summary = (
            f"CVE Details | ID: {cve_id} | Severity: {row.get('severity')} | "
            f"Component: {row.get('affected_component')} | Description: "
        )
        
        full_text = str(row.get('description', '')) + " | Remediation: " + str(row.get('remediation', ''))
        
        chunks = splitter.split_text(full_text)
        if not chunks:
            chunks = ["No description or remediation provided."]
            
        new_chunks = []
        for idx, chunk in enumerate(chunks):
            doc_item = {
                "id": f"{cve_id}_chunk_{idx}",
                "metadata": {
                    "doc_type": "cve_report",
                    "cve_id": cve_id,
                    "severity": row.get('severity'),
                    "published": str(row.get('published_date')),
                    "chunk": idx
                },
                "content": base_summary + chunk,
                "raw": row_dict
            }
            docs.append(doc_item)
            new_chunks.append(doc_item)
            
        # Save to state
        processed_state[cve_id] = {"hash": row_hash, "chunks": new_chunks}

# Write ingestion state map
with open(state_file, 'w', encoding='utf-8') as f:
    json.dump(processed_state, f)

out_path = 'rag_docs_devices.jsonl'
with open(out_path, 'w', encoding='utf-8') as f:
    for d in docs:
        f.write(json.dumps(d) + '\n')

print(f"Created {out_path} with {len(docs)} documents")
