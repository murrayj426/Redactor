"""
Batch processing system for multiple PDF redaction and auditing
"""
import os
import time
import zipfile
import io
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, asdict
import json

from pdf_parser import extract_text_from_pdf, redact_sensitive
from claude_auditor import ClaudeAuditor
from openai_auditor import TicketAuditor
from utils.error_handling import smart_error_handler, monitor_performance
from utils.cache_utils import cached_ai_response

@dataclass
class BatchFileResult:
    """Result for a single file in batch processing"""
    filename: str
    status: str  # 'success', 'error', 'processing'
    redacted_text: str = ""
    audit_report: str = ""
    redaction_count: int = 0
    redaction_details: Dict[str, int] = None
    audit_score: str = ""
    error_message: str = ""
    processing_time: float = 0.0
    file_size: int = 0

    def __post_init__(self):
        if self.redaction_details is None:
            self.redaction_details = {}

@dataclass 
class BatchResult:
    """Overall batch processing result"""
    total_files: int
    successful_files: int
    failed_files: int
    total_redactions: int
    average_score: float
    processing_time: float
    files: List[BatchFileResult]
    common_issues: List[str] = None

    def __post_init__(self):
        if self.common_issues is None:
            self.common_issues = []

class BatchProcessor:
    """Handle batch processing of multiple PDFs"""
    
    def __init__(self, auditor_type: str = "claude"):
        self.auditor_type = auditor_type
        self.auditor = ClaudeAuditor() if auditor_type == "claude" else TicketAuditor()
        self.results: Dict[str, BatchFileResult] = {}
    
    @smart_error_handler(retry_count=1)
    @monitor_performance
    def process_single_file(self, uploaded_file, file_index: int) -> BatchFileResult:
        """Process a single PDF file"""
        start_time = time.time()
        
        try:
            # Initialize result
            result = BatchFileResult(
                filename=uploaded_file.name,
                status='processing',
                file_size=len(uploaded_file.getvalue())
            )
            
            # Extract text from PDF
            text = extract_text_from_pdf(uploaded_file)
            
            if not text or text.strip() == "":
                result.status = 'error'
                result.error_message = "No text could be extracted from PDF"
                return result
            
            # Redact sensitive information
            redacted_text, redaction_stats = redact_sensitive(text)
            result.redacted_text = redacted_text
            result.redaction_count = sum(redaction_stats.values())
            result.redaction_details = redaction_stats
            
            # Perform audit
            audit_report = self.auditor.audit_ticket(text)
            result.audit_report = audit_report
            
            # Extract audit score from report
            result.audit_score = self._extract_audit_score(audit_report)
            
            # Mark as successful
            result.status = 'success'
            result.processing_time = time.time() - start_time
            
            return result
            
        except Exception as e:
            result.status = 'error'
            result.error_message = str(e)
            result.processing_time = time.time() - start_time
            return result
    
    def _extract_audit_score(self, audit_report: str) -> str:
        """Extract audit score from the report"""
        try:
            # Look for common score patterns
            import re
            
            # Pattern for "X/Y" scores
            score_pattern = r'(\d+)/(\d+)'
            matches = re.findall(score_pattern, audit_report)
            
            if matches:
                # Get the most common score format or the last one
                score_match = matches[-1]
                numerator, denominator = int(score_match[0]), int(score_match[1])
                percentage = round((numerator / denominator) * 100)
                return f"{numerator}/{denominator} ({percentage}%)"
            
            # Look for percentage patterns
            percent_pattern = r'(\d+)%'
            percent_matches = re.findall(percent_pattern, audit_report)
            if percent_matches:
                return f"{percent_matches[-1]}%"
            
            return "Score not available"
            
        except Exception:
            return "Score not available"
    
    @monitor_performance
    def process_batch(self, uploaded_files: List, progress_callback=None) -> BatchResult:
        """Process multiple files in parallel"""
        start_time = time.time()
        
        total_files = len(uploaded_files)
        successful_files = 0
        failed_files = 0
        total_redactions = 0
        
        # Process files in parallel
        with ThreadPoolExecutor(max_workers=min(3, len(uploaded_files))) as executor:
            # Submit all jobs
            future_to_file = {
                executor.submit(self.process_single_file, file, i): (file, i) 
                for i, file in enumerate(uploaded_files)
            }
            
            # Collect results as they complete
            file_results = []
            completed = 0
            
            for future in as_completed(future_to_file):
                file, file_index = future_to_file[future]
                
                try:
                    result = future.result()
                    file_results.append(result)
                    
                    if result.status == 'success':
                        successful_files += 1
                        total_redactions += result.redaction_count
                    else:
                        failed_files += 1
                    
                    completed += 1
                    
                    # Update progress
                    if progress_callback:
                        progress_callback(completed, total_files, result)
                        
                except Exception as e:
                    # Handle unexpected errors
                    error_result = BatchFileResult(
                        filename=file.name,
                        status='error',
                        error_message=f"Unexpected error: {str(e)}"
                    )
                    file_results.append(error_result)
                    failed_files += 1
                    completed += 1
                    
                    if progress_callback:
                        progress_callback(completed, total_files, error_result)
        
        # Calculate average score
        scores = []
        for result in file_results:
            if result.status == 'success' and result.audit_score:
                # Extract numeric percentage from score
                import re
                percent_match = re.search(r'(\d+)%', result.audit_score)
                if percent_match:
                    scores.append(int(percent_match.group(1)))
        
        average_score = sum(scores) / len(scores) if scores else 0
        
        # Analyze common issues
        common_issues = self._analyze_common_issues(file_results)
        
        # Create batch result
        batch_result = BatchResult(
            total_files=total_files,
            successful_files=successful_files,
            failed_files=failed_files,
            total_redactions=total_redactions,
            average_score=average_score,
            processing_time=time.time() - start_time,
            files=file_results,
            common_issues=common_issues
        )
        
        return batch_result
    
    def _analyze_common_issues(self, file_results: List[BatchFileResult]) -> List[str]:
        """Analyze audit reports to find common issues"""
        issues = []
        
        # Count successful audits
        successful_audits = [r for r in file_results if r.status == 'success' and r.audit_report]
        
        if not successful_audits:
            return issues
        
        # Common audit failure patterns to look for
        issue_patterns = {
            'First Access': ['first access', 'First Access'],
            'Time Tracking': ['time worked', 'Time Tracking', 'time tracking'],
            'Heading Fields': ['heading fields', 'CI/Location', 'Service Offering'],
            'Client Communication': ['client communication', 'client updates'],
            'Resolution Documentation': ['resolution', 'Resolution Documentation']
        }
        
        # Count issues across all audits
        issue_counts = {}
        
        for pattern_name, patterns in issue_patterns.items():
            count = 0
            for result in successful_audits:
                audit_text = result.audit_report.lower()
                
                # Look for actual negative findings, not just mentions
                for pattern in patterns:
                    pattern_lower = pattern.lower()
                    
                    # Look for patterns that indicate actual failures
                    negative_indicators = [
                        f"❌" in result.audit_report and pattern_lower in audit_text,
                        f"no {pattern_lower}" in audit_text,
                        f"not {pattern_lower}" in audit_text,
                        f"{pattern_lower} not" in audit_text,
                        f"**answer:** no" in audit_text and pattern_lower in audit_text,
                        f"**answer: no" in audit_text and pattern_lower in audit_text
                    ]
                    
                    # Exclude positive mentions
                    positive_indicators = [
                        f"✅" in result.audit_report and pattern_lower in audit_text,
                        f"no issues" in audit_text,
                        f"no problems" in audit_text
                    ]
                    
                    if any(negative_indicators) and not any(positive_indicators):
                        count += 1
                        break
            
            if count > 0:
                percentage = round((count / len(successful_audits)) * 100)
                if percentage >= 20:  # Only report if 20% or more files have this issue
                    issue_counts[pattern_name] = percentage
        
        # Format issues for display
        for issue, percentage in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True):
            issues.append(f"{issue} failing in {percentage}% of files")
        
        return issues[:3]  # Return top 3 issues
    
    def create_results_zip(self, batch_result: BatchResult) -> bytes:
        """Create a ZIP file with all successful results"""
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file_result in batch_result.files:
                if file_result.status == 'success':
                    # Add redacted text file
                    redacted_filename = f"redacted_{file_result.filename.replace('.pdf', '.txt')}"
                    zip_file.writestr(redacted_filename, file_result.redacted_text)
                    
                    # Add audit report
                    audit_filename = f"audit_{file_result.filename.replace('.pdf', '.txt')}"
                    zip_file.writestr(audit_filename, file_result.audit_report)
            
            # Add batch summary
            summary = self._create_batch_summary(batch_result)
            zip_file.writestr("batch_summary.txt", summary)
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue()
    
    def _create_batch_summary(self, batch_result: BatchResult) -> str:
        """Create a text summary of the batch processing results"""
        summary = f"""
BATCH PROCESSING SUMMARY
========================
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

OVERVIEW:
- Total Files: {batch_result.total_files}
- Successful: {batch_result.successful_files}
- Failed: {batch_result.failed_files}
- Total Redactions: {batch_result.total_redactions}
- Average Score: {batch_result.average_score:.1f}%
- Processing Time: {batch_result.processing_time:.1f} seconds

COMMON ISSUES:
"""
        
        if batch_result.common_issues:
            for issue in batch_result.common_issues:
                summary += f"- {issue}\n"
        else:
            summary += "- No common issues identified\n"
        
        summary += "\nFILE DETAILS:\n"
        summary += "=" * 50 + "\n"
        
        for file_result in batch_result.files:
            summary += f"\nFile: {file_result.filename}\n"
            summary += f"Status: {file_result.status.upper()}\n"
            
            if file_result.status == 'success':
                summary += f"Score: {file_result.audit_score}\n"
                summary += f"Redactions: {file_result.redaction_count}\n"
                summary += f"Processing Time: {file_result.processing_time:.1f}s\n"
                
                if file_result.redaction_details:
                    summary += "Redaction Details:\n"
                    for redaction_type, count in file_result.redaction_details.items():
                        summary += f"  - {redaction_type}: {count}\n"
            else:
                summary += f"Error: {file_result.error_message}\n"
            
            summary += "-" * 30 + "\n"
        
        return summary
