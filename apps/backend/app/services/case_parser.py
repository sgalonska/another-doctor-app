from typing import Dict, Any, List, Optional
import re
import json

class CaseParserService:
    """
    Service for parsing medical text and extracting structured information.
    Uses rule-based NLP with scispaCy/MedCAT integration (implementation stub).
    """
    
    def __init__(self):
        # TODO: Initialize scispaCy models and medical dictionaries
        pass
    
    def parse_medical_text(self, text: str) -> Dict[str, Any]:
        """
        Parse medical text and return CaseJSON structure.
        This is a simplified implementation - production would use scispaCy/MedCAT.
        """
        # Clean and preprocess text
        cleaned_text = self._clean_text(text)
        
        # Extract entities using rule-based approach
        entities = self._extract_entities(cleaned_text)
        
        # Map to CaseJSON schema
        case_json = self._build_case_json(entities, cleaned_text)
        
        return case_json
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize medical text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Standardize common abbreviations
        replacements = {
            r'\bpt\b': 'patient',
            r'\bPT\b': 'patient',
            r'\bhx\b': 'history',
            r'\bHx\b': 'history',
            r'\bdx\b': 'diagnosis',
            r'\bDx\b': 'diagnosis',
        }
        
        for pattern, replacement in replacements.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract medical entities from text.
        This is a simplified rule-based approach.
        """
        entities = {
            'conditions': [],
            'anatomy': [],
            'procedures': [],
            'laterality': None,
            'urgency': 'medium',
            'goals': []
        }
        
        # Simple pattern matching for common conditions
        condition_patterns = {
            'critical limb ischemia': {
                'icd10': 'I70.25',
                'snomed': '443165006',
                'mesh': 'D016491'
            },
            'peripheral arterial disease': {
                'icd10': 'I73.9',
                'snomed': '399957001',
                'mesh': 'D016491'
            },
            'diabetes': {
                'icd10': 'E11.9',
                'snomed': '44054006',
                'mesh': 'D003920'
            }
        }
        
        for condition, codes in condition_patterns.items():
            if condition.lower() in text.lower():
                entities['conditions'].append({
                    'text': condition,
                    **codes
                })
        
        # Extract laterality
        if re.search(r'\bleft\b', text, re.IGNORECASE):
            entities['laterality'] = 'left'
        elif re.search(r'\bright\b', text, re.IGNORECASE):
            entities['laterality'] = 'right'
        elif re.search(r'\bbilateral\b', text, re.IGNORECASE):
            entities['laterality'] = 'bilateral'
        
        # Extract anatomical sites
        anatomy_patterns = ['foot', 'leg', 'arm', 'hand', 'toe', 'finger']
        for anatomy in anatomy_patterns:
            if anatomy.lower() in text.lower():
                entities['anatomy'].append(anatomy)
        
        # Extract procedures
        procedure_patterns = ['angioplasty', 'bypass', 'stent', 'amputation', 'revascularization']
        for procedure in procedure_patterns:
            if procedure.lower() in text.lower():
                entities['procedures'].append(procedure)
        
        # Determine urgency
        if any(word in text.lower() for word in ['emergency', 'urgent', 'critical', 'acute']):
            entities['urgency'] = 'high'
        elif any(word in text.lower() for word in ['routine', 'elective', 'stable']):
            entities['urgency'] = 'low'
        
        # Extract goals
        goal_patterns = {
            'avoid amputation': ['avoid amputation', 'prevent amputation', 'limb salvage'],
            'pain relief': ['pain relief', 'reduce pain', 'manage pain'],
            'improve mobility': ['improve mobility', 'restore function', 'walking']
        }
        
        for goal, patterns in goal_patterns.items():
            if any(pattern in text.lower() for pattern in patterns):
                entities['goals'].append(goal)
        
        return entities
    
    def _build_case_json(self, entities: Dict[str, Any], text: str) -> Dict[str, Any]:
        """Build CaseJSON from extracted entities."""
        
        # Primary condition (take first if multiple)
        primary_condition = entities['conditions'][0] if entities['conditions'] else {
            'text': 'unspecified condition',
            'icd10': '',
            'snomed': '',
            'mesh': ''
        }
        
        case_json = {
            'condition': primary_condition,
            'anatomy': {
                'site': entities['anatomy'][0] if entities['anatomy'] else 'unspecified',
                'laterality': entities['laterality'] or 'unspecified',
                'arterial_segments': self._extract_arterial_segments(text)
            },
            'prior_interventions': self._extract_prior_interventions(text, entities['procedures']),
            'comorbidities': [cond['text'] for cond in entities['conditions'][1:]] if len(entities['conditions']) > 1 else [],
            'goals': entities['goals'] or ['improve symptoms'],
            'urgency': entities['urgency'],
            'keywords': self._generate_keywords(entities),
            'date_anchor': '2025-09'  # Current month
        }
        
        return case_json
    
    def _extract_arterial_segments(self, text: str) -> List[str]:
        """Extract arterial segment mentions."""
        segments = []
        segment_patterns = [
            'anterior tibial', 'posterior tibial', 'peroneal', 'dorsalis pedis',
            'femoral', 'popliteal', 'carotid', 'subclavian'
        ]
        
        for segment in segment_patterns:
            if segment in text.lower():
                segments.append(segment)
        
        return segments
    
    def _extract_prior_interventions(self, text: str, procedures: List[str]) -> List[Dict[str, str]]:
        """Extract prior interventions with status."""
        interventions = []
        
        for procedure in procedures:
            intervention = {'name': procedure, 'target': 'unspecified', 'status': 'completed'}
            
            # Look for failure indicators
            failure_words = ['failed', 'unsuccessful', 'did not work', 'no improvement']
            procedure_context = self._get_procedure_context(text, procedure)
            
            if any(word in procedure_context.lower() for word in failure_words):
                intervention['status'] = 'failed'
            
            interventions.append(intervention)
        
        return interventions
    
    def _get_procedure_context(self, text: str, procedure: str) -> str:
        """Get text context around a procedure mention."""
        pattern = rf'.{{0,50}}{re.escape(procedure)}.{{0,50}}'
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(0) if match else ''
    
    def _generate_keywords(self, entities: Dict[str, Any]) -> List[str]:
        """Generate search keywords from entities."""
        keywords = []
        
        # Add procedure-related keywords
        procedure_keywords = {
            'angioplasty': ['balloon angioplasty', 'PTA'],
            'bypass': ['distal bypass', 'pedal loop', 'bypass surgery'],
            'revascularization': ['endovascular', 'surgical revascularization']
        }
        
        for procedure in entities['procedures']:
            keywords.extend(procedure_keywords.get(procedure, [procedure]))
        
        # Add anatomy-based keywords
        if 'foot' in entities['anatomy']:
            keywords.extend(['pedal', 'distal', 'infrapopliteal'])
        
        return list(set(keywords))  # Remove duplicates
    
    def generate_synthetic_abstract(self, case_json: Dict[str, Any]) -> str:
        """Generate synthetic abstract for vector embedding."""
        
        condition = case_json['condition']['text']
        anatomy = case_json['anatomy']
        site = anatomy['site']
        laterality = anatomy['laterality']
        goals = ', '.join(case_json['goals'])
        
        # Build synthetic abstract
        abstract_parts = [
            f"Adult with peripheral arterial disease presenting as {condition}"
        ]
        
        if site != 'unspecified' and laterality != 'unspecified':
            abstract_parts.append(f"of the {laterality} {site}")
        elif site != 'unspecified':
            abstract_parts.append(f"of the {site}")
        
        if case_json['prior_interventions']:
            failed_interventions = [
                i['name'] for i in case_json['prior_interventions'] 
                if i['status'] == 'failed'
            ]
            if failed_interventions:
                abstract_parts.append(f"Prior {', '.join(failed_interventions)} was unsuccessful")
        
        if goals:
            abstract_parts.append(f"Goal: {goals}")
        
        if case_json['keywords']:
            relevant_keywords = case_json['keywords'][:3]  # Top 3 keywords
            abstract_parts.append(f"Consider {', '.join(relevant_keywords)}")
        
        return '. '.join(abstract_parts) + '.'
    
    def generate_human_brief(self, case_json: Dict[str, Any], editable: bool = True) -> str:
        """Generate human-readable brief for user review."""
        
        condition = case_json['condition']['text']
        anatomy = case_json['anatomy']
        site = anatomy['site']
        laterality = anatomy['laterality']
        
        brief_parts = [
            f"We read your report as showing **{condition}**"
        ]
        
        if site != 'unspecified' and laterality != 'unspecified':
            brief_parts.append(f"in your **{laterality} {site}**")
        elif site != 'unspecified':
            brief_parts.append(f"in your **{site}**")
        
        if case_json['prior_interventions']:
            failed_interventions = [
                i['name'] for i in case_json['prior_interventions'] 
                if i['status'] == 'failed'
            ]
            if failed_interventions:
                brief_parts.append(f"A previous **{failed_interventions[0]}** did not succeed")
        
        if case_json['goals']:
            goals_text = ' and '.join([f"**{goal}**" for goal in case_json['goals']])
            brief_parts.append(f"Your goal is to {goals_text}")
        
        brief = '. '.join(brief_parts) + '.'
        
        if editable:
            brief += "\n\n*This summary is based on our analysis. Please review and edit if needed.*"
        
        return brief