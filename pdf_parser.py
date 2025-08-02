import pdfplumber
import re
import pyperclip
import streamlit as st

def redact_sensitive(text):
    """Redact sensitive information and track statistics"""
    redaction_stats = {
        'ip_addresses': 0,
        'mac_addresses': 0,
        'phone_numbers': 0,
        'email_addresses': 0,
        'employee_ids': 0,
        'imei_numbers': 0,
        'account_numbers': 0,
        'urls': 0,
        'names_truncated': 0,
        'total_redactions': 0
    }
    
    # Track each type of redaction
    ip_matches = re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", text)
    redaction_stats['ip_addresses'] = len(ip_matches)
    text = re.sub(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "[REDACTED IP]", text)
    
    mac_matches = re.findall(r"(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}", text)
    redaction_stats['mac_addresses'] = len(mac_matches)
    text = re.sub(r"(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}", "[REDACTED MAC]", text)
    
    phone_matches = re.findall(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b", text)
    redaction_stats['phone_numbers'] = len(phone_matches)
    text = re.sub(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b", "[REDACTED PHONE]", text)
    
    email_matches = re.findall(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text)
    redaction_stats['email_addresses'] = len(email_matches)
    text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[REDACTED EMAIL]", text)
    
    employee_matches = re.findall(r"EVE\d{8}", text)
    redaction_stats['employee_ids'] = len(employee_matches)
    text = re.sub(r"EVE\d{8}", "[REDACTED EMPLOYEE ID]", text)
    
    imei_matches = re.findall(r"IMEI[#\s]*\d+", text)
    redaction_stats['imei_numbers'] = len(imei_matches)
    text = re.sub(r"IMEI[#\s]*\d+", "IMEI#[REDACTED]", text)
    
    account_matches = re.findall(r"Account\s+\d{8,}(-\d+)?", text)
    redaction_stats['account_numbers'] = len(account_matches)
    text = re.sub(r"Account\s+\d{8,}(-\d+)?", "Account [REDACTED]", text)
    
    url_matches = re.findall(r"https?://\S+", text)
    redaction_stats['urls'] = len(url_matches)
    text = re.sub(r"https?://\S+", "[REDACTED URL]", text)
    # Names - Use a smarter approach to identify actual person names vs business terms
    name_count = 0
    
    def name_replacer(match):
        nonlocal name_count
        full_match = match.group(0)
        first_word = match.group(1)
        second_word = match.group(2) + match.group(0).split()[1][1:]  # Get full second word
        
        # Skip if it's clearly technical/business terminology
        technical_indicators = [
            # Infrastructure terms
            r'(?i)\b\w*(?:fw|server|router|switch|tower|device|system|network|config)\w*\b',
            # Business process terms  
            r'(?i)\b(?:security|service|management|client|customer|activity|change|incident|request|access|event|status|pending|hold)\b',
            # Common business phrases
            r'(?i)\b(?:dear|first|next|current|event|follow|time|close)\s+(?:team|access|steps|status|date|up|worked|notes)\b'
        ]
        
        # Check if this matches technical/business patterns
        for pattern in technical_indicators:
            if re.search(pattern, full_match):
                return full_match  # Keep original
        
        # Check if second word looks like a common business term
        business_suffixes = ['management', 'services', 'access', 'hold', 'team', 'client', 'device', 'tower', 'offering', 'request', 'task', 'notes', 'steps', 'status', 'date', 'worked']
        if any(second_word.lower().endswith(suffix) for suffix in business_suffixes):
            return full_match  # Keep original
            
        # Check if it contains common business prefixes
        business_prefixes = ['security', 'network', 'service', 'system', 'device', 'client', 'customer', 'activity', 'change', 'incident', 'configuration', 'first', 'dear', 'event', 'current', 'next', 'time', 'close']
        if any(first_word.lower().startswith(prefix) or first_word.lower() in business_prefixes for prefix in business_prefixes):
            return full_match  # Keep original
            
        # Check if words appear in common business combinations
        common_pairs = [
            ('dear', 'team'), ('first', 'access'), ('client', 'hold'), 
            ('security', 'device'), ('device', 'management'), ('network', 'services'),
            ('service', 'offering'), ('activity', 'task'), ('change', 'request'),
            ('event', 'date'), ('current', 'status'), ('next', 'steps'),
            ('time', 'worked'), ('close', 'notes')
        ]
        
        first_lower = first_word.lower()
        second_lower = second_word.lower()
        
        for pair in common_pairs:
            if (first_lower == pair[0] and second_lower.startswith(pair[1])) or \
               (first_lower.startswith(pair[0]) and second_lower == pair[1]):
                return full_match  # Keep original
        
        # If we get here, it's likely a person's name
        name_count += 1
        return f"{first_word} {second_word[0]}."
    
    text = re.sub(r"\b([A-Z][a-z]+)\s+([A-Z])[a-z]+\b", name_replacer, text)
    redaction_stats['names_truncated'] = name_count
    
    # Calculate total redactions
    redaction_stats['total_redactions'] = sum(redaction_stats.values()) - redaction_stats['total_redactions']
    
    return text, redaction_stats

def extract_text_from_pdf(file_path):
    """Extract text from PDF and apply redaction with statistics"""
    with pdfplumber.open(file_path) as pdf:
        full_text = "\n".join(
            page.extract_text() for page in pdf.pages if page.extract_text()
        )
    redacted_text, redaction_stats = redact_sensitive(full_text)
    pyperclip.copy(redacted_text)
    return redacted_text, redaction_stats

def run_redactor_gui():
    st.title("📄 PDF Redactor")
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

    if uploaded_file is not None:
        with pdfplumber.open(uploaded_file) as pdf:
            full_text = "\n".join(
                page.extract_text() for page in pdf.pages if page.extract_text()
            )
        redacted = redact_sensitive(full_text)
        st.text_area("🔒 Redacted Content", redacted, height=400)

        if st.button("📋 Copy to Clipboard"):
            pyperclip.copy(redacted)
            st.success("Redacted content copied to clipboard!")

