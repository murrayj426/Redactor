"""
Step-by-Step Interactive Auditor
Goes through each audit question one at a time with AI discussion
"""

import os
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

class StepByStepAuditor:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.conversation_history = []
        self.current_question = 0
        self.audit_results = {}
        self.incident_text = None
        self.procedures = None
        
    def load_procedures(self):
        """Load the Network Team procedures"""
        try:
            with open('incident_handling_procedures.txt', 'r') as f:
                return f.read()
        except FileNotFoundError:
            return "Network Team procedures not found."
    
    def get_question_details(self, question_num):
        """Get the details for a specific question"""
        questions = {
            1: {
                "question": "Identify and display the ServiceNow INC######## number from the ticket",
                "standard": "Simply identify the incident number for reference",
                "type": "identification"
            },
            2: {
                "question": "Are CI/Location, State/Pending, Service Offering/Category properly populated?",
                "standard": "Configuration Item, CI Location, Service Offering/Category must be verified for accuracy",
                "type": "compliance"
            },
            3: {
                "question": "Was First Access properly checked/marked when first accessing device or contacting client?",
                "standard": "First access should be checked when logging into device/contacting client",
                "type": "compliance"
            },
            4: {
                "question": "Did engineer acknowledge ownership to customer with ticket summary?",
                "standard": "Engineer should acknowledge ownership with update to client including ticket summary",
                "type": "compliance"
            },
            5: {
                "question": "Are Event Dates used accurately for next follow-up scheduling?",
                "standard": "Event Date should accurately reflect the time for next follow up",
                "type": "compliance"
            },
            6: {
                "question": "Are Pending Codes used correctly per Network Team procedures?",
                "standard": "Correct usage of Pending Codes (Client Action Required, Client Hold, RMA, Carrier, etc.). Accept common abbreviations like 'Client H.' for 'Client Hold'",
                "type": "compliance"
            },
            7: {
                "question": "Are Current Status/Next Steps updated appropriately?",
                "standard": "Any change in current status or next steps requires documentation",
                "type": "compliance"
            },
            8: {
                "question": "Are detailed, professional updates provided to client?",
                "standard": "All client facing updates must be professional, detailed, and proofread",
                "type": "compliance"
            },
            9: {
                "question": "Are troubleshooting steps documented thoroughly with evidence?",
                "standard": "Troubleshooting steps must be documented with evidence and explanations",
                "type": "compliance"
            },
            10: {
                "question": "Were updates provided per Network Team priority standards?",
                "standard": "P1/P2: hourly updates, P3: every 2 days, P4: every 3 days",
                "type": "compliance"
            },
            11: {
                "question": "Were Network Team procedures and templates followed correctly?",
                "standard": "Must follow Ticket Acceptance/Update Templates and manual SNC email process",
                "type": "compliance"
            },
            12: {
                "question": "Were necessary Activity & Change tasks opened appropriately?",
                "standard": "Proper Activity and Change task creation when required",
                "type": "compliance_optional"
            },
            13: {
                "question": "Is Time Worked accurately documented for cost tracking?",
                "standard": "Time Worked field must be populated accurately for cost evaluation",
                "type": "compliance"
            },
            14: {
                "question": "Do Close Notes reflect work done with evidence of resolution?",
                "standard": "Close notes should include issue summary, steps taken, and resolution evidence",
                "type": "compliance_optional"
            },
            15: {
                "question": "Rate overall engineer performance on this incident (1-10 scale)",
                "standard": "Overall compliance with Network Team incident management procedures",
                "type": "rating"
            }
        }
        return questions.get(question_num, None)
    
    def start_audit(self, incident_text, model="gpt-4o-mini"):
        """Start the step-by-step audit process"""
        self.incident_text = incident_text
        self.procedures = self.load_procedures()
        self.current_question = 1
        self.audit_results = {}
        self.conversation_history = []
        
        # Initialize conversation with context
        system_prompt = f"""You are an expert Network Team incident auditor. You will be going through a 15-question audit step by step, one question at a time.

NETWORK TEAM PROCEDURES (Reference):
{self.procedures[:2000]}...

IMPORTANT GUIDANCE:
- Accept common abbreviations and reasonable variations in format
- "Client H." should be interpreted as "Client Hold" 
- "CAR" should be interpreted as "Client Action Required"
- Focus on substance over exact wording format
- Be reasonable - minor format differences should not fail compliance

INCIDENT TEXT:
{incident_text[:5000]}{'...' if len(incident_text) > 5000 else ''}

You will analyze each question thoroughly and provide detailed responses. Be ready to discuss and clarify your findings."""

        self.conversation_history = [
            {"role": "system", "content": system_prompt}
        ]
        
        return self.ask_current_question(model)
    
    def ask_current_question(self, model="gpt-4o-mini"):
        """Ask the current question and get AI response"""
        if self.current_question > 15:
            return self.generate_final_report()
        
        question_details = self.get_question_details(self.current_question)
        if not question_details:
            return "Error: Invalid question number"
        
        # Create prompt for current question
        if question_details["type"] == "identification":
            prompt = f"""
**QUESTION {self.current_question}: {question_details['question']}**

**Network Team Standard**: {question_details['standard']}

**Instructions**: Simply identify and display the ServiceNow INC number found in the incident text. If not found, state "Not Found".

Please provide your response.
"""
        elif question_details["type"] == "rating":
            prompt = f"""
**QUESTION {self.current_question}: {question_details['question']}**

**Network Team Standard**: {question_details['standard']}

**Instructions**: Based on all the previous questions and overall compliance with Network Team procedures, provide a rating from 1-10 and explain your reasoning.

Please provide:
1. **RATING**: [1-10 score]
2. **REASONING**: Detailed explanation of the rating based on Network Team compliance
"""
        else:
            na_note = " (N/A allowed only if truly not applicable)" if question_details["type"] == "compliance_optional" else " (N/A not allowed)"
            
            prompt = f"""
**QUESTION {self.current_question}: {question_details['question']}**

**Network Team Standard**: {question_details['standard']}

**Instructions**: Analyze the incident text against this Network Team standard{na_note}.

Please provide:
1. **ANSWER**: Yes/No{' or N/A if not applicable' if question_details["type"] == "compliance_optional" else ''}
2. **EVIDENCE**: Quote specific text from the ticket that supports your answer
3. **ANALYSIS**: Explain what you looked for and your reasoning based on Network Team standards

If you cannot find evidence, answer "No" and explain what should be there per Network Team procedures.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=self.conversation_history + [
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            ai_response = response.choices[0].message.content
            
            # Store the question and response
            self.audit_results[self.current_question] = {
                "question": question_details["question"],
                "standard": question_details["standard"],
                "response": ai_response
            }
            
            # Add to conversation history
            self.conversation_history.append({"role": "user", "content": prompt})
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            return ai_response
            
        except Exception as e:
            return f"Error processing question {self.current_question}: {str(e)}"
    
    def continue_discussion(self, user_input, model="gpt-4o-mini"):
        """Continue discussing the current question"""
        if self.current_question > 15:
            return "Audit complete. Use generate_final_report() to get the summary."
        
        prompt = f"""The user wants to discuss the current question further: "{user_input}"

Please respond with additional analysis or clarification about Question {self.current_question}, keeping the Network Team standards in mind."""
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=self.conversation_history + [
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.3
            )
            
            ai_response = response.choices[0].message.content
            
            # Add to conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            return ai_response
            
        except Exception as e:
            return f"Error in discussion: {str(e)}"
    
    def next_question(self, model="gpt-4o-mini"):
        """Move to the next question"""
        self.current_question += 1
        return self.ask_current_question(model)
    
    def previous_question(self):
        """Go back to previous question"""
        if self.current_question > 1:
            self.current_question -= 1
            question_details = self.get_question_details(self.current_question)
            stored_result = self.audit_results.get(self.current_question)
            
            if stored_result:
                return f"**QUESTION {self.current_question}: {stored_result['question']}**\n\n**Previous Response:**\n{stored_result['response']}"
            else:
                return f"**QUESTION {self.current_question}: {question_details['question']}**\n\nNo previous response recorded."
        else:
            return "Already at the first question."
    
    def get_progress(self):
        """Get current progress"""
        return f"Question {self.current_question} of 15 ({(self.current_question-1)/15*100:.1f}% complete)"
    
    def generate_final_report(self):
        """Generate final audit report"""
        if not self.audit_results:
            return "No audit results to report."
        
        report = f"""
=== STEP-BY-STEP AUDIT REPORT ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total Questions: {len(self.audit_results)}
{'='*60}

"""
        
        for q_num in sorted(self.audit_results.keys()):
            result = self.audit_results[q_num]
            report += f"""
**QUESTION {q_num}: {result['question']}**
**Network Team Standard**: {result['standard']}

{result['response']}

{'-'*50}
"""
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reports/step_by_step_audit_{timestamp}.txt"
        
        try:
            with open(filename, "w") as f:
                f.write(report)
            report += f"\n\nReport saved to: {filename}"
        except:
            pass
        
        return report
    
    def get_current_question_info(self):
        """Get info about current question"""
        if self.current_question > 15:
            return "Audit complete."
        
        question_details = self.get_question_details(self.current_question)
        return f"""
**Current Question**: {self.current_question} of 15
**Question**: {question_details['question']}
**Network Team Standard**: {question_details['standard']}
**Progress**: {(self.current_question-1)/15*100:.1f}% complete
"""
