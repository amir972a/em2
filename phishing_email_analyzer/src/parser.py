import email
from email.policy import default
import re
import hashlib
from typing import Dict, Any, List

def parse_eml(file_path: str) -> Dict[str, Any]:
    """Parses an EML file and extracts required information."""
    try:
        with open(file_path, 'rb') as f:
            msg = email.message_from_binary_file(f, policy=default)
    except Exception as e:
        raise ValueError(f"Error reading EML file: {e}")

    result = {
        'Date': msg.get('Date', ''),
        'Subject': msg.get('Subject', ''),
        'To': msg.get('To', ''),
        'From': msg.get('From', ''),
        'Reply-To': msg.get('Reply-To', ''),
        'Return-Path': msg.get('Return-Path', ''),
        'Message-ID': msg.get('Message-ID', ''),
        'Sender IP': '',
        'Resolve Host': '',
        'Authentication-Results': msg.get('Authentication-Results', ''),
        'URLs': [],
        'Attachments': [],
        '_Source_Filename': file_path
    }

    # Process Received headers to try and find Sender IP
    received_headers = msg.get_all('Received', [])
    for header in received_headers:
        # Looking for IPv4 in Received
        ip_match = re.search(r'\[(\d{1,3}(?:\.\d{1,3}){3})\]', header)
        if ip_match and not result['Sender IP']:
            result['Sender IP'] = f"{ip_match.group(1)} (Unverified from Received)"

        # Try to find a hostname
        host_match = re.search(r'from\s+([a-zA-Z0-9.-]+)\s+', header)
        if host_match and not result['Resolve Host']:
            result['Resolve Host'] = f"{host_match.group(1)} (Unverified from Received)"

    urls = set()

    # Process parts
    for part in msg.walk():
        if part.is_multipart():
            continue

        content_type = part.get_content_type()
        content_disposition = str(part.get('Content-Disposition'))

        # Attachments
        if 'attachment' in content_disposition or part.get_filename():
            filename = part.get_filename()
            if filename:
                payload = part.get_payload(decode=True)
                if payload:
                    md5_hash = hashlib.md5(payload).hexdigest()
                    sha1_hash = hashlib.sha1(payload).hexdigest()
                    sha256_hash = hashlib.sha256(payload).hexdigest()

                    result['Attachments'].append({
                        'Attachment Name': filename,
                        'MD5': md5_hash,
                        'SHA1': sha1_hash,
                        'SHA256': sha256_hash
                    })

        # Body (for URLs)
        elif content_type in ('text/plain', 'text/html'):
            try:
                body = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8', errors='ignore')
                # Simple URL regex extraction
                extracted_urls = re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s"\'<>]*', body)
                urls.update(extracted_urls)
            except Exception:
                pass

    result['URLs'] = list(urls)
    return result
