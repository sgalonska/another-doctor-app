"""
Development database seeding script.
Seeds the database with sample data for local development.
"""

import uuid
from datetime import datetime, timedelta
from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text

from app.core.config import settings
from app.models.institution import Institution
from app.models.doctor import Doctor, DoctorAffiliation
from app.models.work import Work, DoctorWork
from app.models.topic import Topic, DoctorTopicScore
from app.models.case import CaseSpec


def seed_development_data():
    """Seed the database with development data."""
    
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
    
    with engine.begin() as conn:
        # Create session
        session = Session(bind=conn)
        
        try:
            print("🌱 Seeding development database...")
            
            # Clear existing data
            print("  Clearing existing data...")
            session.execute(text("TRUNCATE doctor_work CASCADE"))
            session.execute(text("TRUNCATE doctor_topic_score CASCADE"))
            session.execute(text("TRUNCATE doctor_affiliation CASCADE"))
            session.execute(text("TRUNCATE work CASCADE"))
            session.execute(text("TRUNCATE doctor CASCADE"))
            session.execute(text("TRUNCATE topic CASCADE"))
            session.execute(text("TRUNCATE institution CASCADE"))
            session.execute(text("TRUNCATE case_spec CASCADE"))
            
            # Seed institutions
            institutions = seed_institutions(session)
            print(f"  ✅ Created {len(institutions)} institutions")
            
            # Seed topics
            topics = seed_topics(session)
            print(f"  ✅ Created {len(topics)} topics")
            
            # Seed doctors
            doctors = seed_doctors(session, institutions)
            print(f"  ✅ Created {len(doctors)} doctors")
            
            # Seed works (publications, trials, grants)
            works = seed_works(session, doctors)
            print(f"  ✅ Created {len(works)} works")
            
            # Seed doctor topic scores
            seed_doctor_topic_scores(session, doctors, topics)
            print(f"  ✅ Created doctor topic scores")
            
            # Seed sample cases
            cases = seed_cases(session)
            print(f"  ✅ Created {len(cases)} sample cases")
            
            session.commit()
            print("🎉 Development database seeded successfully!")
            
        except Exception as e:
            print(f"❌ Error seeding database: {e}")
            session.rollback()
            raise
        finally:
            session.close()


def seed_institutions(session: Session) -> List[Institution]:
    """Seed institutions."""
    institutions_data = [
        {
            "name": "Cleveland Clinic",
            "city": "Cleveland",
            "state": "OH",
            "country": "USA",
            "source": ["manual_seed"]
        },
        {
            "name": "Mayo Clinic",
            "city": "Rochester", 
            "state": "MN",
            "country": "USA",
            "source": ["manual_seed"]
        },
        {
            "name": "Johns Hopkins Hospital",
            "city": "Baltimore",
            "state": "MD", 
            "country": "USA",
            "source": ["manual_seed"]
        },
        {
            "name": "Massachusetts General Hospital",
            "city": "Boston",
            "state": "MA",
            "country": "USA",
            "source": ["manual_seed"]
        },
        {
            "name": "Stanford University Medical Center",
            "city": "Stanford",
            "state": "CA",
            "country": "USA",
            "source": ["manual_seed"]
        }
    ]
    
    institutions = []
    for data in institutions_data:
        institution = Institution(
            institution_id=uuid.uuid4(),
            **data
        )
        session.add(institution)
        institutions.append(institution)
    
    session.flush()
    return institutions


def seed_topics(session: Session) -> List[Topic]:
    """Seed medical topics."""
    topics_data = [
        {
            "name": "Critical Limb Ischemia",
            "synonyms": ["CLI", "limb ischemia", "peripheral arterial disease"]
        },
        {
            "name": "Coronary Artery Disease", 
            "synonyms": ["CAD", "coronary disease", "heart disease"]
        },
        {
            "name": "Heart Failure",
            "synonyms": ["cardiac failure", "congestive heart failure", "CHF"]
        },
        {
            "name": "Vascular Surgery",
            "synonyms": ["endovascular", "bypass surgery", "revascularization"]
        },
        {
            "name": "Interventional Cardiology",
            "synonyms": ["PCI", "cardiac intervention", "angioplasty"]
        }
    ]
    
    topics = []
    for data in topics_data:
        topic = Topic(
            topic_id=uuid.uuid4(),
            **data
        )
        session.add(topic)
        topics.append(topic)
    
    session.flush()
    return topics


def seed_doctors(session: Session, institutions: List[Institution]) -> List[Doctor]:
    """Seed doctors."""
    doctors_data = [
        {
            "full_name": "Dr. Sarah Johnson",
            "orcid": "0000-0002-1234-5678",
            "primary_specialty": "Vascular Surgery",
            "institution": institutions[0],  # Cleveland Clinic
            "role": "Attending Physician"
        },
        {
            "full_name": "Dr. Michael Chen",
            "orcid": "0000-0003-2345-6789", 
            "primary_specialty": "Interventional Cardiology",
            "institution": institutions[1],  # Mayo Clinic
            "role": "Department Chief"
        },
        {
            "full_name": "Dr. Emily Rodriguez",
            "orcid": "0000-0004-3456-7890",
            "primary_specialty": "Vascular Surgery", 
            "institution": institutions[2],  # Johns Hopkins
            "role": "Associate Professor"
        },
        {
            "full_name": "Dr. David Kim",
            "orcid": "0000-0005-4567-8901",
            "primary_specialty": "Cardiothoracic Surgery",
            "institution": institutions[3],  # Mass General
            "role": "Senior Surgeon"
        },
        {
            "full_name": "Dr. Lisa Wang",
            "orcid": "0000-0006-5678-9012",
            "primary_specialty": "Interventional Cardiology",
            "institution": institutions[4],  # Stanford
            "role": "Professor"
        }
    ]
    
    doctors = []
    for data in doctors_data:
        institution = data.pop("institution")
        role = data.pop("role")
        
        doctor = Doctor(
            doctor_id=uuid.uuid4(),
            **data
        )
        session.add(doctor)
        
        # Add affiliation
        affiliation = DoctorAffiliation(
            doctor_id=doctor.doctor_id,
            institution_id=institution.institution_id,
            role=role,
            start_year=2015
        )
        session.add(affiliation)
        
        doctors.append(doctor)
    
    session.flush()
    return doctors


def seed_works(session: Session, doctors: List[Doctor]) -> List[Work]:
    """Seed works (publications, trials, grants)."""
    works_data = [
        {
            "source": "pubmed",
            "source_key": "12345678",
            "title": "Outcomes of Distal Bypass Surgery for Critical Limb Ischemia",
            "abstract": "This study examines outcomes of distal bypass procedures...",
            "year": 2023,
            "doi": "10.1016/j.jvs.2023.01.001",
            "mesh_terms": ["D016491", "D058729"],
            "url": "https://pubmed.ncbi.nlm.nih.gov/12345678/",
            "doctor": doctors[0]  # Dr. Sarah Johnson
        },
        {
            "source": "ctgov",
            "source_key": "NCT01234567", 
            "title": "Pedal Loop Revascularization Trial for CLI",
            "abstract": "Randomized controlled trial comparing pedal loop bypass...",
            "year": 2022,
            "url": "https://clinicaltrials.gov/ct2/show/NCT01234567",
            "doctor": doctors[0],  # Dr. Sarah Johnson as PI
            "is_pi": True
        },
        {
            "source": "pubmed",
            "source_key": "23456789",
            "title": "Coronary Stenting Outcomes in Complex Lesions",
            "abstract": "Analysis of outcomes following coronary stent placement...",
            "year": 2023,
            "doi": "10.1016/j.jacc.2023.02.015",
            "mesh_terms": ["D003324", "D015607"],
            "url": "https://pubmed.ncbi.nlm.nih.gov/23456789/",
            "doctor": doctors[1]  # Dr. Michael Chen
        },
        {
            "source": "nih_reporter",
            "source_key": "R01HL123456",
            "title": "Novel Approaches to Limb Salvage in PAD",
            "abstract": "This study investigates innovative techniques...",
            "year": 2024,
            "url": "https://reporter.nih.gov/project-details/R01HL123456",
            "doctor": doctors[2]  # Dr. Emily Rodriguez
        }
    ]
    
    works = []
    for data in works_data:
        doctor = data.pop("doctor")
        is_pi = data.pop("is_pi", False)
        
        work = Work(
            work_id=uuid.uuid4(),
            **data
        )
        session.add(work)
        
        # Add doctor-work relationship
        doctor_work = DoctorWork(
            doctor_id=doctor.doctor_id,
            work_id=work.work_id,
            author_position=1,
            is_pi=is_pi
        )
        session.add(doctor_work)
        
        works.append(work)
    
    session.flush()
    return works


def seed_doctor_topic_scores(session: Session, doctors: List[Doctor], topics: List[Topic]):
    """Seed doctor topic scores."""
    
    # Create some realistic scoring scenarios
    scoring_data = [
        # Dr. Sarah Johnson - Vascular Surgery expert
        {
            "doctor": doctors[0],
            "topic": next(t for t in topics if t.name == "Critical Limb Ischemia"),
            "components": {
                "pubs_5y": 8,
                "trials_pi": 2,
                "citations_bucket": 3,
                "inst_pubs": 45,
                "inst_trials": 12,
                "nih_grants": 3
            }
        },
        # Dr. Michael Chen - Interventional Cardiology expert  
        {
            "doctor": doctors[1],
            "topic": next(t for t in topics if t.name == "Coronary Artery Disease"),
            "components": {
                "pubs_5y": 12,
                "trials_pi": 3,
                "citations_bucket": 3,
                "inst_pubs": 89,
                "inst_trials": 18,
                "nih_grants": 5
            }
        },
        # Cross-specialty scoring
        {
            "doctor": doctors[0],  # Vascular surgeon
            "topic": next(t for t in topics if t.name == "Vascular Surgery"),
            "components": {
                "pubs_5y": 15,
                "trials_pi": 4,
                "citations_bucket": 3,
                "inst_pubs": 78,
                "inst_trials": 15,
                "nih_grants": 4
            }
        }
    ]
    
    for data in scoring_data:
        # Calculate total score using the scoring formula
        components = data["components"]
        doctor_score = (
            2 * components["pubs_5y"] + 
            5 * components["trials_pi"] + 
            1 * components["citations_bucket"]
        )
        institution_score = (
            0.5 * components["inst_pubs"] + 
            2 * components["inst_trials"] + 
            0.5 * components["nih_grants"]
        )
        total_score = doctor_score + 0.5 * institution_score
        
        score = DoctorTopicScore(
            doctor_id=data["doctor"].doctor_id,
            topic_id=data["topic"].topic_id,
            components=components,
            score=total_score
        )
        session.add(score)
    
    session.flush()


def seed_cases(session: Session) -> List[CaseSpec]:
    """Seed sample cases."""
    cases_data = [
        {
            "casejson": {
                "condition": {
                    "text": "critical limb ischemia",
                    "icd10": "I70.25",
                    "snomed": "443165006", 
                    "mesh": "D016491"
                },
                "anatomy": {
                    "site": "foot",
                    "laterality": "left",
                    "arterial_segments": ["anterior tibial"]
                },
                "prior_interventions": [
                    {
                        "name": "angioplasty",
                        "target": "anterior tibial",
                        "status": "failed"
                    }
                ],
                "comorbidities": ["type 2 diabetes"],
                "goals": ["avoid amputation", "limb salvage"],
                "urgency": "high",
                "keywords": ["distal bypass", "pedal loop", "revascularization"],
                "date_anchor": "2024-09"
            },
            "version": "v1"
        },
        {
            "casejson": {
                "condition": {
                    "text": "coronary artery disease",
                    "icd10": "I25.10",
                    "snomed": "414545008",
                    "mesh": "D003324"
                },
                "anatomy": {
                    "site": "coronary arteries",
                    "arterial_segments": ["LAD", "RCA"]
                },
                "prior_interventions": [
                    {
                        "name": "medical management",
                        "status": "partial"
                    }
                ],
                "comorbidities": ["hypertension", "hyperlipidemia"],
                "goals": ["symptom relief", "improve quality of life"],
                "urgency": "medium",
                "keywords": ["PCI", "stenting", "CABG"],
                "date_anchor": "2024-09"
            },
            "version": "v1"
        }
    ]
    
    cases = []
    for data in cases_data:
        case = CaseSpec(
            case_id=uuid.uuid4(),
            **data
        )
        session.add(case)
        cases.append(case)
    
    session.flush()
    return cases


if __name__ == "__main__":
    seed_development_data()