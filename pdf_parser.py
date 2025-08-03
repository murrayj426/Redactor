import pdfplumber
import re
import streamlit as st

# Import pyperclip safely - it may not be available in all environments
try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

def safe_copy_to_clipboard(text):
    """Safely copy text to clipboard, handling cases where clipboard is not available"""
    if not CLIPBOARD_AVAILABLE:
        return False
    try:
        pyperclip.copy(text)
        return True
    except Exception:
        return False

# Compile regex patterns once for better performance
REGEX_PATTERNS = {
    'ip_addresses': re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    'mac_addresses': re.compile(r"(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}"),
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
    
    # Phone numbers - but exclude technical case numbers
    actual_phone_redactions = 0
    def phone_replacer(match):
        nonlocal actual_phone_redactions
        full_match = match.group(0)
        
        # Check if this appears to be a technical case number (preceded by #, case #, ticket #, etc.)
        # Look at the context around each specific match
        start_pos = match.start()
        if start_pos > 0:
            preceding_text = text[max(0, start_pos-25):start_pos].lower()
            # Don't redact if it looks like a case/ticket number
            if any(indicator in preceding_text for indicator in ['#', 'case', 'ticket', 'reference', 'rma', 'tac', 'inc', 'req']):
                return full_match
            # Also check for patterns like "6-555-123-4567" where it's clearly a case number
            if re.search(r'[#\-]\d{1,2}[-\s]*$', preceding_text):
                return full_match
        
        actual_phone_redactions += 1
        return "[REDACTED PHONE]"
    
    # Apply phone number redaction with context checking
    phone_pattern = r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"
    phone_matches = re.findall(phone_pattern, text)
    text = re.sub(phone_pattern, phone_replacer, text)
    redaction_stats['phone_numbers'] = actual_phone_redactions
    
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
    # Names - Much more conservative approach, focus on actual person names only
    name_count = 0
    
    def name_replacer(match):
        nonlocal name_count
        full_match = match.group(0)
        first_word = match.group(1)
        second_word = match.group(0).split()[1]  # Get full second word
        
        # Comprehensive list of business/technical terms to preserve
        business_terms = {
            # Geographic and locations
            'niagara', 'delaware', 'eastern', 'western', 'northern', 'southern', 'central', 
            'melbourne', 'presidio', 'docklands', 'tower', 'wheeling', 'downs', 'gaming',
            'falls', 'stadium', 'island', 'hotel', 'casino', 'racetrack',
            
            # Business/Service terms
            'security', 'service', 'management', 'client', 'customer', 'activity', 'change',
            'incident', 'request', 'access', 'event', 'status', 'pending', 'hold', 'time',
            'integration', 'monitoring', 'network', 'device', 'system', 'server', 'router',
            'switch', 'firewall', 'appliance', 'configuration', 'automation', 'logic',
            'checkpoint', 'verizon', 'logicmonitor', 'datacenter', 'center',
            
            # Company names and business entities
            'companies', 'inc', 'corp', 'ltd', 'llc', 'north', 'services', 'offering',
            'category', 'subcategory', 'carrier', 'vendor', 'circuit', 'wireless',
            
            # Time and process terms
            'daylight', 'standard', 'mountain', 'pacific', 'atlantic', 'worked', 'notes',
            'steps', 'team', 'group', 'resolution', 'escalation', 'priority', 'impact',
            'urgency', 'assignment', 'billing', 'reporting', 'entitlement',
            
            # Technical terms
            'resource', 'offline', 'online', 'critical', 'medium', 'high', 'low',
            'vmware', 'microsoft', 'windows', 'linux', 'cisco', 'meraki', 'unity',
            'ethernet', 'fabric', 'virtual', 'backup', 'restore', 'patch', 'managed',
            'collaboration', 'engineer', 'datacenter', 'storage', 'compute', 'hypervisor',
            
            # ServiceNow and ticket fields
            'caller', 'opened', 'assigned', 'resolved', 'closed', 'updated', 'created',
            'description', 'summary', 'comments', 'worknotes', 'private', 'public',
            'ticket', 'number', 'state', 'reason', 'follow', 'contact', 'business',
            'location', 'impact', 'urgency', 'priority', 'assignment', 'handoff'
        }
        
        # Check if either word is a business/technical term
        if (first_word.lower() in business_terms or 
            second_word.lower() in business_terms):
            return full_match  # Keep original
        
        # Additional check for compound business terms
        compound_lower = full_match.lower()
        compound_terms = {
            'delaware north', 'niagara falls', 'eastern daylight', 'melbourne docklands',
            'network services', 'security device', 'service offering', 'configuration item',
            'time worked', 'activity task', 'incident details', 'work notes',
            'monitoring automation', 'integration user', 'escalation group', 'wheeling downs',
            'gaming location', 'hotel casino', 'casino racetrack', 'system server',
            'device management', 'resource offline', 'vmware center', 'microsoft windows',
            'network circuit', 'ip address', 'mac address', 'backup services',
            'managed services', 'data center', 'patch management', 'collaboration engineer',
            'security engineer', 'network engineer', 'systems engineer'
        }
        
        if compound_lower in compound_terms:
            return full_match  # Keep original
        
        # Check for technical naming patterns (often contain numbers, underscores, or domain-like structures)
        if (re.search(r'\d', full_match) or '_' in full_match or 
            '.' in full_match or any(tech in full_match.lower() 
            for tech in ['vm', 'srv', 'app', 'db', 'fw', 'sw', 'rtr', 'ws'])):
            return full_match  # Keep technical names
            
        # Only redact if it looks like an actual person's name
        # Must be proper case (First Last format) and not match any business patterns
        if (len(first_word) >= 2 and len(second_word) >= 2 and 
            first_word[0].isupper() and first_word[1:].islower() and
            second_word[0].isupper() and second_word[1:].islower()):
            
            # Additional filters for likely person names vs business terms
            # Skip common business word patterns
            business_endings = ['ing', 'tion', 'ment', 'ness', 'ity', 'ics', 'ogy']
            if any(second_word.lower().endswith(ending) for ending in business_endings):
                return full_match  # Keep business terms
            
            # This appears to be a person's name - redact it
            name_count += 1
            return f"{first_word} {second_word[0]}."
        
        # Default: preserve the original text
        return full_match
    
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
    
    # Try to copy to clipboard silently (for local development convenience)
    safe_copy_to_clipboard(redacted_text)
        
    return redacted_text, redaction_stats

def run_redactor_gui():
    st.title("📄 PDF Redactor")
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

    if uploaded_file is not None:
        with pdfplumber.open(uploaded_file) as pdf:
            full_text = "\n".join(
                page.extract_text() for page in pdf.pages if page.extract_text()
            )
        redacted_text, redaction_stats = redact_sensitive(full_text)
        st.text_area("🔒 Redacted Content", redacted_text, height=400)

        # Show clipboard button with appropriate messaging
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("📋 Copy to Clipboard"):
                if safe_copy_to_clipboard(redacted_text):
                    st.success("Redacted content copied to clipboard!")
                else:
                    st.warning("⚠️ Clipboard not available in this environment.")
                    st.info("💡 Tip: Select all text in the box above and use Ctrl+C (or Cmd+C on Mac) to copy.")
        with col2:
            if not CLIPBOARD_AVAILABLE:
                st.caption("ℹ️ Manual copy required")

