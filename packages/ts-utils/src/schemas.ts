import { z } from 'zod';

// CaseJSON schema using Zod for TypeScript validation
export const CaseConditionSchema = z.object({
  text: z.string(),
  icd10: z.string().optional(),
  snomed: z.string().optional(),
  mesh: z.string().optional(),
});

export const CaseAnatomySchema = z.object({
  site: z.string(),
  laterality: z.enum(['left', 'right', 'bilateral', 'unspecified']).optional(),
  arterial_segments: z.array(z.string()).optional(),
});

export const CasePriorInterventionSchema = z.object({
  name: z.string(),
  target: z.string().optional(),
  status: z.enum(['completed', 'failed', 'partial', 'ongoing']).optional(),
  date_approx: z.string().optional(),
});

export const CaseJSONSchema = z.object({
  condition: CaseConditionSchema,
  anatomy: CaseAnatomySchema,
  prior_interventions: z.array(CasePriorInterventionSchema).optional(),
  comorbidities: z.array(z.string()).optional(),
  goals: z.array(z.string()).optional(),
  urgency: z.enum(['low', 'medium', 'high']).default('medium'),
  keywords: z.array(z.string()).optional(),
  date_anchor: z.string().regex(/^[0-9]{4}-[0-9]{2}$/).optional(),
});

// Match Result schema
export const MatchEvidenceSchema = z.object({
  type: z.enum(['pubmed', 'ctgov', 'nih_reporter', 'crossref', 'openalex']),
  title: z.string(),
  year: z.number().min(1900).max(2030).optional(),
  url: z.string().url().optional(),
  relevance_score: z.number().min(0).max(1).optional(),
  pmid: z.string().optional(),
  nct_id: z.string().regex(/^NCT[0-9]{8}$/).optional(),
  project_id: z.string().optional(),
  doi: z.string().optional(),
  role: z.string().optional(),
});

export const MatchScoreComponentsSchema = z.object({
  pubs_5y: z.number().min(0),
  trials_pi: z.number().min(0),
  citations_bucket: z.number().min(0).max(3),
  inst_pubs: z.number().min(0),
  inst_trials: z.number().min(0),
  nih_grants: z.number().min(0),
});

export const MatchResultSchema = z.object({
  doctor_id: z.string().uuid(),
  doctor_name: z.string(),
  institution: z.string(),
  specialty: z.string().optional(),
  total_score: z.number().min(0),
  doctor_score: z.number().min(0),
  institution_score: z.number().min(0),
  components: MatchScoreComponentsSchema,
  evidence: z.array(MatchEvidenceSchema),
  explanation: z.string(),
  location: z.string().optional(),
  years_experience: z.number().min(0).optional(),
  board_certifications: z.array(z.string()).optional(),
  languages: z.array(z.string()).optional(),
  contact_info: z.object({
    email: z.string().email().optional(),
    phone: z.string().optional(),
    office_address: z.string().optional(),
  }).optional(),
});

// Type exports
export type CaseCondition = z.infer<typeof CaseConditionSchema>;
export type CaseAnatomy = z.infer<typeof CaseAnatomySchema>;
export type CasePriorIntervention = z.infer<typeof CasePriorInterventionSchema>;
export type CaseJSON = z.infer<typeof CaseJSONSchema>;
export type MatchEvidence = z.infer<typeof MatchEvidenceSchema>;
export type MatchScoreComponents = z.infer<typeof MatchScoreComponentsSchema>;
export type MatchResult = z.infer<typeof MatchResultSchema>;