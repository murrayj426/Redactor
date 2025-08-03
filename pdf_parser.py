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
        'run_by_fields': 0,
        'names_truncated': 0,
        'total_redactions': 0
    }
    
    # First, improve ServiceNow field formatting for better readability
    # Add line breaks before common ServiceNow field labels when they're concatenated
    servicenow_fields = [
        'Impact:', 'Urgency:', 'Priority:', 'Responsible party:', 'Assignment group:',
        'Customer Assignment Group:', 'Assigned to:', 'Opened by:', 'Resolved by:',
        'Company:', 'Location:', 'Configuration item:', 'Service Offering:',
        'Category:', 'Subcategory:', 'Application:', 'Business service:',
        'Service offering:', 'Contact type:', 'Caller name:', 'Caller email:',
        'Caller phone:', 'Caller:', 'Vendor:', 'Carrier:', 'Follow up by:',
        'Event date:', 'Primary agreement:', 'Pending reason:', 'Handoff:',
        'Last Reoccurrence:', 'Last Touched:', 'Sync Ticket with Customer:',
        'Service Restored:', 'Alert Cleared:', 'Short description:', 'Notes:',
        'Watch list:', 'Time worked:', 'Customer watch list:', 'Current status:',
        'Next steps:', 'Additional comments:', 'Close code:', 'Cause code:',
        'Close notes:', 'Root cause:'
    ]
    
    # Add line breaks before field labels that are incorrectly concatenated
    for field in servicenow_fields:
        # Look for patterns where a field appears after text without proper line break
        # But avoid breaking up legitimate sentences
        pattern = r'(\w+)\s+(' + re.escape(field) + ')'
        replacement = r'\1\n\2'
        
        # Only apply if the preceding word doesn't end with common sentence endings
        def field_replacer(match):
            preceding_word = match.group(1)
            field_label = match.group(2)
            
            # Don't break if it looks like part of a sentence
            if preceding_word.lower() in ['high', 'medium', 'low', 'critical', 'the', 'and', 'or', 'but', 'with', 'from', 'to']:
                return f'{preceding_word}\n{field_label}'
            return match.group(0)
        
        text = re.sub(pattern, field_replacer, text)
    
    # Also handle common ServiceNow value-to-field patterns
    value_field_patterns = [
        (r'(High|Medium|Low|Critical)\s+(Responsible party:)', r'\1\n\2'),
        (r'(Presidio|Delaware North[^:]*)\s+(Urgency:)', r'\1\n\2'),
        (r'(\d+\s*-\s*(?:High|Medium|Low|Critical))\s+(Assignment group:)', r'\1\n\2'),
        (r'(MSC Network Engineer|[A-Z][a-z]+ [A-Z][a-z]+)\s+(Customer Assignment Group:)', r'\1\n\2'),
        (r'(true|false)\s+(Service Offering:)', r'\1\n\2'),
        (r'(Network Services|[A-Z][a-z]+ [A-Z][a-z]+)\s+(Category:)', r'\1\n\2'),
    ]
    
    for pattern, replacement in value_field_patterns:
        text = re.sub(pattern, replacement, text)
    
    # IP address redaction with business logic - preserve internal ranges for operational context
    def ip_replacer(match):
        ip = match.group(0)
        # Preserve common internal IP ranges that are needed for operational context
        # Keep 10.x.x.x, 172.16-31.x.x, and 192.168.x.x ranges
        parts = ip.split('.')
        if len(parts) == 4:
            try:
                first_octet = int(parts[0])
                second_octet = int(parts[1])
                # Keep internal/private IP ranges for operational context
                if (first_octet == 10 or 
                    (first_octet == 172 and 16 <= second_octet <= 31) or
                    (first_octet == 192 and second_octet == 168)):
                    return ip  # Keep internal IPs
            except ValueError:
                pass
        # Redact public IPs
        return "[REDACTED IP]"
    
    ip_matches = REGEX_PATTERNS['ip_addresses'].findall(text)
    actual_ip_redactions = len([ip for ip in ip_matches if not ip.startswith(('10.', '172.', '192.168.'))])
    text = REGEX_PATTERNS['ip_addresses'].sub(ip_replacer, text)
    redaction_stats['ip_addresses'] = actual_ip_redactions
    
    mac_matches = REGEX_PATTERNS['mac_addresses'].findall(text)
    redaction_stats['mac_addresses'] = len(mac_matches)
    text = REGEX_PATTERNS['mac_addresses'].sub("[REDACTED MAC]", text)
    
    # Phone numbers - exclude Checkpoint TAC cases and other reference numbers
    actual_phone_redactions = 0
    def phone_replacer(match):
        nonlocal actual_phone_redactions
        full_match = match.group(0)
        
        # Check context around the match
        start_pos = match.start()
        if start_pos > 0:
            preceding_text = text[max(0, start_pos-15):start_pos].lower()
            
            # Exclude Checkpoint TAC case numbers (6-followed by 10 digits)
            if preceding_text.endswith('6-') and len(full_match) == 10 and full_match.isdigit():
                return full_match
            
            # Only skip if it's clearly a case/reference number with # symbol
            if '#' in preceding_text:
                return full_match
        
        actual_phone_redactions += 1
        return "[REDACTED PHONE]"
    
    # Apply phone number redaction with enhanced pattern for better detection
    # Enhanced pattern to catch more phone formats: (555) 123-4567, 555-123-4567, +1-555-123-4567, etc.
    phone_pattern = r"(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b"
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
    
    # Run By fields - redact user information after "Run By:" (ServiceNow export metadata)
    # Handle both "Run by:" and "Run By:" variations with flexible spacing
    run_by_pattern = r"(Run [Bb]y\s*:\s*)[^\n]+"
    run_by_matches = re.findall(run_by_pattern, text)
    redaction_stats['run_by_fields'] = len(run_by_matches)
    text = re.sub(run_by_pattern, r"\1[REDACTED]", text)
    
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
            'falls', 'stadium', 'island', 'hotel', 'casino', 'racetrack', 'banquet', 'buffet',
            'showroom', 'employee', 'lounge', 'giftshop', 'sportsbook', 'human', 'resources',
            'pointe', 'restaurant', 'datacenter', 'promotions', 'spare', 'production',
            
            # Business/Service terms (removed common first/last names like 'jeremy', 'murray')
            'security', 'service', 'management', 'client', 'customer', 'activity', 'change',
            'incident', 'request', 'access', 'event', 'status', 'pending', 'hold', 'time',
            'integration', 'monitoring', 'network', 'device', 'system', 'server', 'router',
            'switch', 'firewall', 'appliance', 'configuration', 'automation', 'logic',
            'checkpoint', 'verizon', 'logicmonitor', 'datacenter', 'center', 'unified',
            'communications', 'manager', 'vmware', 'vcenter', 'instance', 'compute', 'storage',
            
            # Technical system identifiers and model numbers
            'gewig', 'gewiggafw', 'gewigga', 'gewigoamt', 'gewig16nv', 'gewig16dhcp',
            'gewigfpclus', 'gewigagysws', 'gewig16v1ws', 'gewig19clus', 'gewiggavrapp',
            'gewig19fp', 'meraki', 'cisco', 'catalyst', 'proliant', 'nimble', 'checkpoint',
            'mr32', 'ws-c3560x', 'ws-c2960', 'bl460c', 'gen9', 'esxi', 'windows', 'linux',
            'ubuntu', 'redhat', 'centos', 'vmware', 'microsoft', 'intel', 'amd', 'hp', 'dell',
            'itrak', 'everi', 'floor', 'monitor', 'unavailable', 'offline', 'online',
            
            # Company names and business entities
            'companies', 'inc', 'corp', 'ltd', 'llc', 'north', 'services', 'offering',
            'category', 'subcategory', 'carrier', 'vendor', 'circuit', 'wireless',
            'comcast', 'segra', 'start', 'metro', 'eline', 'etta', 'lopp', 'cfw',
            
            # Time and process terms - EXPANDED
            'daylight', 'standard', 'mountain', 'pacific', 'atlantic', 'worked', 'notes',
            'steps', 'team', 'group', 'resolution', 'escalation', 'priority', 'impact',
            'urgency', 'assignment', 'billing', 'reporting', 'entitlement', 'date', 'run',
            'opened', 'closed', 'updated', 'created', 'resolved', 'assigned', 'caller',
            'contact', 'description', 'summary', 'comments', 'worknotes', 'private', 'public',
            'minutes', 'seconds', 'hours', 'days', 'weeks', 'months', 'years', 'elapsed',
            'percentage', 'achieved', 'cancelled', 'breached', 'threshold', 'alert', 'level',
            
            # Ticket states and workflow terms
            'progress', 'pending', 'hold', 'cancelled', 'new', 'draft', 'review', 'approved',
            'rejected', 'processing', 'complete', 'failed', 'success', 'waiting', 'active',
            'inactive', 'enabled', 'disabled', 'available', 'unavailable', 'maintenance',
            'operational', 'critical', 'high', 'medium', 'low', 'informational', 'warning',
            'error', 'debug', 'trace', 'verbose', 'quiet', 'silent',
            
            # Technical terms
            'resource', 'offline', 'online', 'critical', 'medium', 'high', 'low',
            'vmware', 'microsoft', 'windows', 'linux', 'cisco', 'meraki', 'unity',
            'ethernet', 'fabric', 'virtual', 'backup', 'restore', 'patch', 'managed',
            'collaboration', 'engineer', 'datacenter', 'storage', 'compute', 'hypervisor',
            'vmotion', 'drs', 'ha', 'cluster', 'domain', 'controller', 'dhcp', 'dns',
            'ntp', 'snmp', 'ssh', 'rdp', 'vnc', 'console', 'terminal', 'shell', 'bash',
            'powershell', 'cmd', 'registry', 'service', 'daemon', 'process', 'thread',
            'memory', 'cpu', 'disk', 'network', 'interface', 'port', 'protocol', 'tcp',
            'udp', 'icmp', 'http', 'https', 'ftp', 'sftp', 'smtp', 'pop3', 'imap',
            
            # Monitoring and alerting terms
            'monitor', 'alert', 'notification', 'threshold', 'baseline', 'metric',
            'dashboard', 'report', 'analytics', 'statistics', 'performance', 'utilization',
            'capacity', 'availability', 'reliability', 'scalability', 'security',
            'compliance', 'audit', 'log', 'event', 'incident', 'problem', 'change',
            'release', 'deployment', 'rollback', 'maintenance', 'upgrade', 'downgrade',
            
            # ServiceNow and ticket fields
            'caller', 'opened', 'assigned', 'resolved', 'closed', 'updated', 'created',
            'description', 'summary', 'comments', 'worknotes', 'private', 'public',
            'ticket', 'number', 'state', 'reason', 'follow', 'contact', 'business',
            'location', 'impact', 'urgency', 'priority', 'assignment', 'handoff',
            
            # ServiceNow field abbreviations (to prevent accidental truncation)
            'report', 'configuration', 'alert', 'query', 'related', 'problem', 
            'parent', 'customer', 'service', 'business', 'time', 'priority',
            'assignment', 'escalation', 'primary', 'secondary', 'reference'
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
            'security engineer', 'network engineer', 'systems engineer', 'run date',
            'run by', 'opened by', 'assigned to', 'contact type', 'ticket integration',
            'business service', 'configuration item', 'service restored', 'additional comments',
            'short description', 'current status', 'next steps', 'work notes', 'incident number',
            'customer ticket', 'time worked', 'assignment group', 'responsible party',
            'service offering', 'network management', 'escalation group', 'primary agreement',
            # Common ticket states and workflow combinations
            'in progress', 'on hold', 'pending client', 'pending vendor', 'pending approval',
            'work in', 'under review', 'awaiting approval', 'pending closure',
            'pending customer', 'pending internal', 'high priority', 'low priority',
            'medium priority', 'critical priority', 'service restored', 'service degraded',
            'in review', 'work progress', 'solution provided',
            
            # ServiceNow field labels and patterns
            'report type', 'configuration item', 'alert count', 'query condition',
            'related list', 'problem ticket', 'parent incident', 'customer ticket',
            'service restored', 'business impact', 'time worked', 'priority impact',
            'assignment group', 'escalation group', 'primary agreement', 'secondary contact',
            'reference number', 'last resolved', 'last updated', 'last touched',
            
            # Technical system combinations
            'access point', 'network gear', 'ip switch', 'network switch', 'ip firewall',
            'esx server', 'vmware esxi', 'windows server', 'linux server', 'blade server',
            'storage device', 'backup device', 'monitoring device', 'security appliance',
            'network appliance', 'presidio appliance', 'managed device', 'compute device',
            'virtual machine', 'virtual server', 'virtual appliance', 'compute resource',
            'storage resource', 'network resource', 'backup resource', 'security resource',
            
            # Location and facility terms
            'wheeling downs', 'melbourne docklands', 'hotel casino', 'casino racetrack',
            'gaming hotel', 'hotel guest', 'production network', 'guest network',
            'employee lounge', 'human resources', 'sports book', 'gift shop',
            'pointe restaurant', 'banquet comcast', 'data center', 'spare production',
            
            # Service and business process terms
            'business service', 'network services', 'managed services', 'data protection',
            'patch management', 'carrier case', 'dispatch services', 'backup services',
            'cloud foundations', 'select tier', 'priority email', 'quarterly true',
            'ticket integration', 'shared document', 'meraki portal', 'live tracking',
            'high touch', 'remote access', 'time resolve', 'escalation via',
            'logicmonitor monitoring', 'allied servicedesk', 'cattools monitoring',
            'high wire', 'redundant appliance', 'snmp configure', 'logicmonitor backups'
        }
        
        if compound_lower in compound_terms:
            return full_match  # Keep original
        
        # Check for technical naming patterns (often contain numbers, underscores, or domain-like structures)
        # Enhanced technical identifier detection
        technical_patterns = [
            r'^[A-Z]{3,}[A-Z0-9]+$',  # GEWIGGAFW01, DELWA001, etc.
            r'^[a-z]+[0-9]+[a-z]*[0-9]*$',  # gewig16v1ws01, etc.
            r'^[A-Z]+[0-9]+[A-Z]*[0-9]*$',  # INC11973728, etc.
            r'.*\.(ad\.dncinc\.com|prod\.presidiosecure\.com)$',  # Domain names
            r'^[A-Z]{2,}\d{2,}$',  # MR32, etc.
            r'^Q2[A-Z0-9-]+$',  # Serial numbers like Q2JD-GRKF-3VJF
            r'^[A-Z]{3}[0-9]{6}$',  # FCQ1601X4V8 style codes
        ]
        
        if (re.search(r'\d', full_match) or '_' in full_match or 
            '.' in full_match or any(tech in full_match.lower() 
            for tech in ['vm', 'srv', 'app', 'db', 'fw', 'sw', 'rtr', 'ws', 'inc', 'gewig']) or
            any(re.match(pattern, full_match) for pattern in technical_patterns)):
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

