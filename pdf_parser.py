import pdfplumber
import re
import pyperclip
import streamlit as st

# Compile regex patterns once for better performance
REGEX_PATTERNS = {
    'ip_addresses': re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    'mac_addresses': re.compile(r"(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}"),
    'phone_numbers': re.compile(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    'email_addresses': re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    'employee_ids': re.compile(r"EVE\d{8}"),
    'imei_numbers': re.compile(r"IMEI[#\s]*\d+"),
    'account_numbers': re.compile(r"Account\s+\d{8,}(-\d+)?"),
    'urls': re.compile(r"https?://\S+"),
    'names': re.compile(r"\b([A-Z][a-z]+)\s+([A-Z])[a-z]+\b")
}

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
    
    # Use pre-compiled regex patterns for better performance
    ip_matches = REGEX_PATTERNS['ip_addresses'].findall(text)
    redaction_stats['ip_addresses'] = len(ip_matches)
    text = REGEX_PATTERNS['ip_addresses'].sub("[REDACTED IP]", text)
    
    mac_matches = REGEX_PATTERNS['mac_addresses'].findall(text)
    redaction_stats['mac_addresses'] = len(mac_matches)
    text = REGEX_PATTERNS['mac_addresses'].sub("[REDACTED MAC]", text)
    
    phone_matches = REGEX_PATTERNS['phone_numbers'].findall(text)
    redaction_stats['phone_numbers'] = len(phone_matches)
    text = REGEX_PATTERNS['phone_numbers'].sub("[REDACTED PHONE]", text)
    
    email_matches = REGEX_PATTERNS['email_addresses'].findall(text)
    redaction_stats['email_addresses'] = len(email_matches)
    text = REGEX_PATTERNS['email_addresses'].sub("[REDACTED EMAIL]", text)
    
    employee_matches = REGEX_PATTERNS['employee_ids'].findall(text)
    redaction_stats['employee_ids'] = len(employee_matches)
    text = REGEX_PATTERNS['employee_ids'].sub("[REDACTED EMPLOYEE ID]", text)
    
    imei_matches = REGEX_PATTERNS['imei_numbers'].findall(text)
    redaction_stats['imei_numbers'] = len(imei_matches)
    text = REGEX_PATTERNS['imei_numbers'].sub("IMEI#[REDACTED]", text)
    
    account_matches = REGEX_PATTERNS['account_numbers'].findall(text)
    redaction_stats['account_numbers'] = len(account_matches)
    text = REGEX_PATTERNS['account_numbers'].sub("Account [REDACTED]", text)
    
    url_matches = REGEX_PATTERNS['urls'].findall(text)
    redaction_stats['urls'] = len(url_matches)
    text = REGEX_PATTERNS['urls'].sub("[REDACTED URL]", text)
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
    
    text = REGEX_PATTERNS['names'].sub(name_replacer, text)
    redaction_stats['names_truncated'] = name_count
    
    # Calculate total redactions
    redaction_stats['total_redactions'] = sum(redaction_stats.values()) - redaction_stats['total_redactions']
    
    return text, redaction_stats

def extract_text_from_pdf(file_path, max_pages=None):
    """Extract text from PDF and apply redaction with statistics"""
    with pdfplumber.open(file_path) as pdf:
        # Process pages in batches for memory efficiency
        pages_to_process = pdf.pages[:max_pages] if max_pages else pdf.pages
        
        # Stream processing for large files
        text_chunks = []
        for i, page in enumerate(pages_to_process):
            page_text = page.extract_text()
            if page_text:
                text_chunks.append(page_text)
            
            # Memory management for very large files
            if len(text_chunks) > 50:  # Process every 50 pages
                partial_text = "\n".join(text_chunks)
                text_chunks = [partial_text]
        
        full_text = "\n".join(text_chunks)
    
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

