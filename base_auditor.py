"""
Base Auditor Class - Shared audit logic for Network Team compliance
Contains all shared functionality between OpenAI and Claude auditors
"""

import os
from datetime import datetime
from abc import ABC, abstractmethod
import pathlib

# Import optimization utilities
from utils.error_handling import smart_error_handler, monitor_performance
from utils.cache_utils import load_network_procedures
from utils.ai_utils import optimize_prompt_for_model, RateLimiter
import json

class BaseAuditor(ABC):
    def __init__(self):
        self.rate_limiter = RateLimiter()
        # Load incident documentation with caching
        self.incident_documentation = load_network_procedures()
    
    def load_incident_documentation(self):
        """Load incident handling documentation if available"""
        doc_paths = [
            "incident_handling_procedures.txt",
            "incident_documentation.md",
            "procedures/incident_handling.txt",
            "docs/incident_procedures.md"
        ]
        
        for path in doc_paths:
            try:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        return f.read()
            except:
                continue
        
        return None

    def create_audit_prompt(self, redacted_text):
        """Create the audit prompt using Network Team procedures and explicit question blocks"""
        procedures = self.incident_documentation or self.load_incident_documentation() or "(Procedures not found)"
        snippet = procedures[:2000] + ("..." if len(procedures) > 2000 else "")

        template_path = pathlib.Path('prompts/audit_prompt_template.md')
        if not template_path.exists():
            raise FileNotFoundError("Missing prompt template at prompts/audit_prompt_template.md")
        template = template_path.read_text(encoding='utf-8')

        questions_path = pathlib.Path('prompts/audit_questions.md')
        if not questions_path.exists():
            raise FileNotFoundError("Missing question block file at prompts/audit_questions.md")
        question_blocks = questions_path.read_text(encoding='utf-8')

        prompt = (template
                  .replace('{{PROCEDURES_SNIPPET}}', snippet)
                  .replace('{{QUESTION_BLOCKS}}', question_blocks)
                  .replace('{{INCIDENT_TEXT}}', redacted_text))
        return prompt
        
    # (Legacy inline question block removed in favor of external file injection)
    
    @abstractmethod
    def audit_ticket(self, redacted_text, model=None):
        """Abstract method - must be implemented by provider-specific classes"""
        pass
    
    def save_audit_report(self, audit_result, filename_prefix="audit"):
        """Save audit report to file with structured format"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reports/{filename_prefix}_{timestamp}.txt"
        
        # Ensure reports directory exists
        os.makedirs("reports", exist_ok=True)
        
        with open(filename, "w") as f:
            f.write(f"=== INCIDENT AUDIT REPORT (16-QUESTION FRAMEWORK) ===\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Audit Type: {filename_prefix.replace('_audit', '').upper()}\n")
            f.write(f"{'='*60}\n\n")
            f.write(audit_result)
            f.write(f"\n\n{'='*60}\n")
            f.write(f"Report saved to: {filename}\n")
        
        return filename
    
    def create_audit_summary(self, audit_result):
        """Extract key metrics from audit result for dashboard with proper N/A handling"""
        try:
            # Prefer JSON summary if the model followed instructions
            json_summary = self.parse_json_summary(audit_result)
            if json_summary:
                pass_count = 0
                fail_count = 0
                na_count = 0
                # Expect keys like q2..q12, q14, q15
                for key, value in json_summary.items():
                    if not key.lower().startswith('q'):
                        continue
                    norm = str(value).strip().upper()
                    if norm == 'PASS':
                        pass_count += 1
                    elif norm == 'FAIL':
                        fail_count += 1
                    elif norm in ('N/A', 'NA'):
                        na_count += 1
                total_scoreable = 13  # Questions 2-12, 14, 15
                total_applicable = total_scoreable - na_count
                total_answered = pass_count + fail_count
                return {
                    'pass_count': pass_count,
                    'fail_count': fail_count,
                    'total_answered': total_answered,
                    'total_questions': 16,
                    'scoreable_questions': total_scoreable,
                    'applicable_questions': total_applicable,
                    'na_responses': na_count,
                    'compliance_percentage': (pass_count / total_answered * 100) if total_answered > 0 else None,
                    'json_summary_used': True
                }
            # Count PASS/FAIL responses only - no more 1-10 scoring
            lines = audit_result.split('\n')
            pass_count = 0
            fail_count = 0
            na_count = 0
            
            for line in lines:
                if '⚠️' in line and 'N/A' in line:
                    # Check if this is Q12 (Task Management) or Q15 (Close Notes) - the only questions that can be N/A
                    if any(q in line for q in ['12', '15', 'Task Management', 'Close Notes', 'Resolution Documentation']):
                        na_count += 1
                elif '✅' in line and 'PASS' in line:
                    pass_count += 1
                elif '❌' in line and 'FAIL' in line:
                    fail_count += 1
            
            # Based on actual audit form: Q2-12 (11 questions), Q14, Q15 (2 questions) = 13 total scoreable
            # Q1, Q13, Q16 are not scored (identification/text fields)
            total_scoreable = 13  # Questions 2-12, 14, 15
            total_applicable = total_scoreable - na_count
            total_answered = pass_count + fail_count
            
            return {
                'pass_count': pass_count,
                'fail_count': fail_count,
                'total_answered': total_answered,
                'total_questions': 16,  # Total framework questions
                'scoreable_questions': total_scoreable,  # Questions 2-12, 14, 15
                'applicable_questions': total_applicable,  # Scoreable minus N/A
                'na_responses': na_count,
                'compliance_percentage': (pass_count / total_answered * 100) if total_answered > 0 else None
            }
        except:
            return None

    def extract_audit_score_from_text(self, audit_text):
        """Enhanced audit score extraction with PASS/FAIL counting and debug information"""
        import re
        
        # Patterns for modern audit format with emojis
        pass_patterns = [
            r'✅\s*PASS\s*\(Score:\s*(\d+)/(\d+)\)',  # "✅ PASS (Score: 9/10)"
            r'✅\s*PASS',
            r'STATUS.*?✅.*?PASS', 
            r'PASS.*?✅',
            r'✅.*?PASS'
        ]
        
        fail_patterns = [
            r'❌\s*FAIL\s*\(Score:\s*(\d+)/(\d+)\)',  # "❌ FAIL (Score: 2/10)"
            r'❌\s*FAIL',
            r'STATUS.*?❌.*?FAIL',
            r'FAIL.*?❌', 
            r'❌.*?FAIL'
        ]
        
        pass_count = 0
        fail_count = 0
        extracted_scores = []
        
        # Try multiple patterns to catch all variations
        for pattern in pass_patterns:
            matches = re.findall(pattern, audit_text, re.IGNORECASE | re.DOTALL)
            if matches:
                if isinstance(matches[0], tuple) and len(matches[0]) == 2:
                    # Pattern captured score (numerator, denominator)
                    for match in matches:
                        extracted_scores.append((int(match[0]), int(match[1])))
                    pass_count = len(matches)
                else:
                    # Simple PASS pattern
                    pass_count = max(pass_count, len(matches))
        
        for pattern in fail_patterns:
            matches = re.findall(pattern, audit_text, re.IGNORECASE | re.DOTALL)
            if matches:
                if isinstance(matches[0], tuple) and len(matches[0]) == 2:
                    # Pattern captured score (numerator, denominator)
                    for match in matches:
                        extracted_scores.append((int(match[0]), int(match[1])))
                    fail_count = len(matches)
                else:
                    # Simple FAIL pattern
                    fail_count = max(fail_count, len(matches))
        
        # Count total questions for verification (should be 16 total, Q2-12,14,15 are scored)
        question_count = len(re.findall(r'\*\*QUESTION\s+\d+', audit_text, re.IGNORECASE))
        
        # If we found PASS/FAIL counts, use them (this is the primary scoring method)
        if pass_count > 0 or fail_count > 0:
            total = pass_count + fail_count
            pct = round((pass_count/total) * 100) if total > 0 else 0
            
            # Note: Based on actual audit form structure:
            # Q1: INC# (not scored), Q2-12: Yes/No (11 questions), Q13: Text field (not scored)
            # Q14: Yes/No/N/A, Q15: Yes/No/N/A, Q16: Audit notes (not scored)  
            # Total scoreable: Q2-12, Q14, Q15 = 13 questions maximum
            max_scoreable = 13  # Questions 2-12, 14, 15
            
            if total == max_scoreable:
                debug_info = ""  # Clean display for full audit
            else:
                debug_info = f" ({total}/13)"
            
            return f"{pass_count}/{total} ({pct}%){debug_info}"
        
        # If we extracted individual scores from PASS/FAIL patterns, use them
        if extracted_scores:
            # Sum up all individual scores
            total_score = sum(score[0] for score in extracted_scores)
            total_possible = sum(score[1] for score in extracted_scores)
            pct = round((total_score/total_possible) * 100) if total_possible > 0 else 0
            return f"{total_score}/{total_possible} ({pct}%)"
        
        # Look for traditional score patterns as fallback
        score_patterns = [
            r'(\d+)/(\d+)\s*\((\d+)%\)',  # "11/12 (92%)"
            r'\(Score:\s*(\d+)/(\d+)\)',   # "(Score: 9/10)"
            r'Score:\s*(\d+)/(\d+)',      # "Score: 9/10"
            r'TOTAL.*?(\d+)/(\d+)',       # "TOTAL: 11/12"
            r'SCORE.*?(\d+)/(\d+)',       # "SCORE: 11/12"
            r'(\d+)\s*out\s*of\s*(\d+)',  # "11 out of 15"
        ]
        
        for pattern in score_patterns:
            matches = re.findall(pattern, audit_text, re.IGNORECASE)
            if matches:
                match = matches[-1]  # Get last match
                if len(match) == 3:  # Full pattern with percentage
                    return f"{match[0]}/{match[1]} ({match[2]}%)"
                elif len(match) == 2:
                    try:
                        num, den = int(match[0]), int(match[1])
                        pct = round((num/den) * 100)
                        return f"{num}/{den} ({pct}%)"
                    except (ValueError, ZeroDivisionError):
                        return f"{match[0]}/{match[1]}"
        
        return "Score not available"

    def parse_json_summary(self, audit_text):
        """Extract JSON summary dict from final line matching prefix JSON_SUMMARY:"""
        try:
            lines = [l.strip() for l in audit_text.strip().splitlines() if l.strip()]
            # Search from bottom up for the JSON line
            for line in reversed(lines):
                if line.startswith('JSON_SUMMARY:'):
                    raw = line.split('JSON_SUMMARY:', 1)[1].strip()
                    # Strip code fences if present
                    if raw.startswith('```'):
                        raw = raw.strip('`')
                    # Sometimes model may wrap in backticks or add trailing text
                    # Attempt to isolate JSON object heuristically
                    first_brace = raw.find('{')
                    last_brace = raw.rfind('}')
                    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                        candidate = raw[first_brace:last_brace+1]
                    else:
                        candidate = raw
                    # Replace smart quotes just in case
                    candidate = candidate.replace('“', '"').replace('”', '"')
                    return json.loads(candidate)
        except Exception as e:
            print(f"JSON summary parse failed: {e}")
        return None
