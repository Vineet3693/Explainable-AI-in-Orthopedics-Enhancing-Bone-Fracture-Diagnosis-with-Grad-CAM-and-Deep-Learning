# 📚 Prompts Library - Complete Guide

## Overview
Complete collection of LLM prompts for fracture detection AI system with Gemini and Groq integration.

---

## 📁 Directory Structure

```
prompts_library/
├── gemini_prompts/              (3 files) ✅
│   ├── fracture_analysis.txt
│   ├── report_generation.txt
│   └── medical_recommendations.txt
│
├── groq_prompts/                (2 files) ✅
│   ├── quick_analysis.txt
│   └── summary_generation.txt
│
├── structured_schemas/          (1 file) ✅
│   └── analysis_schema.json
│
├── examples/                    (2 files) ✅
│   ├── good_examples/
│   │   └── proper_fracture_report.txt
│   └── bad_examples/
│       └── poor_fracture_report.txt
│
├── PROMPTS_SUMMARY.md          ✅
└── README.md                   ← This file
```

**Total: 9 files created** ✅

---

## 🎯 Prompt Files

### **Gemini Prompts** (Detailed, Comprehensive)

#### 1. fracture_analysis.txt
**Purpose:** Detailed medical analysis of X-ray images  
**Use When:** Need comprehensive fracture assessment  
**Output:** 8-section detailed analysis  
**Length:** ~500-800 words  

**Key Features:**
- Visual assessment framework
- Fracture classification
- Severity grading
- Confidence analysis
- Clinical correlation
- Structured output format

---

#### 2. report_generation.txt
**Purpose:** Generate formal medical reports  
**Use When:** Creating patient records, documentation  
**Output:** 12-section professional report  
**Length:** ~1000-1500 words  

**Key Features:**
- Complete medical report structure
- Patient information section
- AI analysis findings
- Radiologist review section
- Legal disclaimers
- Technical appendix

---

#### 3. medical_recommendations.txt
**Purpose:** Treatment and care recommendations  
**Use When:** Need management guidance  
**Output:** 10-section recommendation guide  
**Length:** ~800-1200 words  

**Key Features:**
- Immediate management
- Treatment options
- Pain management protocol
- Rehabilitation timeline
- Follow-up schedule
- Patient education

---

### **Groq Prompts** (Fast, Concise)

#### 4. quick_analysis.txt
**Purpose:** Fast fracture assessment  
**Use When:** Emergency triage, quick decisions  
**Output:** Concise assessment  
**Length:** ~150-200 words  

**Key Features:**
- Rapid assessment
- Top 3 actions
- Urgency level
- Red flags
- Optimized for speed

---

#### 5. summary_generation.txt
**Purpose:** Generate summaries  
**Use When:** Handoffs, patient communication  
**Output:** 3 types of summaries  
**Length:** ~100-150 words total  

**Key Features:**
- Clinical summary (for doctors)
- Patient summary (simple language)
- Handoff summary (shift changes)

---

## 📊 JSON Schema

#### analysis_schema.json
**Purpose:** Structured response format  
**Use:** Validate AI responses  

**Defines:**
- Report ID format
- Required fields
- Data types
- Enums for categories
- Validation rules

---

## 📖 Examples

#### Good Example
**File:** `good_examples/proper_fracture_report.txt`  
**Shows:** Proper report with all elements  
**Learn:** Best practices, structure, language  

#### Bad Example
**File:** `bad_examples/poor_fracture_report.txt`  
**Shows:** Common mistakes to avoid  
**Learn:** What NOT to do  

---

## 🚀 Usage Guide

### **When to Use Which Prompt**

| Scenario | Use This | Why |
|----------|----------|-----|
| Emergency Department | Groq: quick_analysis.txt | Fast triage needed |
| Formal Documentation | Gemini: report_generation.txt | Complete records |
| Treatment Planning | Gemini: medical_recommendations.txt | Detailed guidance |
| Patient Communication | Groq: summary_generation.txt | Simple explanations |
| Detailed Analysis | Gemini: fracture_analysis.txt | Comprehensive assessment |

---

### **Integration Example**

```python
# Load prompt
with open('prompts_library/gemini_prompts/fracture_analysis.txt', 'r') as f:
    prompt_template = f.read()

# Fill variables
prompt = prompt_template.format(
    resnet50_confidence=93,
    efficientnet_b0_confidence=92,
    efficientnet_b1_confidence=96,
    ensemble_confidence=94,
    age=45,
    gender="Female",
    injury_mechanism="Fall on outstretched hand",
    symptoms="Wrist pain, swelling"
)

# Send to LLM
response = gemini_model.generate_content([prompt, image])
```

---

## 🎯 Workflow Examples

### **Workflow 1: Emergency Department**
```
Patient arrives → X-ray taken
    ↓
AI models predict (94% fractured)
    ↓
Use: groq_prompts/quick_analysis.txt
    ↓
Get rapid assessment (30 seconds)
    ↓
Doctor reviews → Confirms
    ↓
Use: gemini_prompts/report_generation.txt
    ↓
Generate formal report (2 minutes)
    ↓
Save to patient record
```

### **Workflow 2: Radiology Department**
```
Batch of X-rays uploaded
    ↓
AI analyzes all images
    ↓
Use: groq_prompts/quick_analysis.txt (for all)
    ↓
Flag potential fractures
    ↓
Radiologist reviews flagged cases
    ↓
Use: gemini_prompts/fracture_analysis.txt (detailed)
    ↓
Use: gemini_prompts/report_generation.txt (formal)
    ↓
Reports generated and saved
```

### **Workflow 3: Telemedicine**
```
Remote patient sends X-ray
    ↓
AI analyzes image
    ↓
Use: gemini_prompts/fracture_analysis.txt
    ↓
Use: gemini_prompts/medical_recommendations.txt
    ↓
Use: groq_prompts/summary_generation.txt (patient version)
    ↓
Send patient-friendly summary
    ↓
Schedule follow-up
```

---

## 📋 Prompt Variables

### **Common Variables** (used across prompts)

```
Patient Information:
- {patient_id}
- {age}
- {gender}
- {exam_date}

AI Predictions:
- {resnet50_confidence}
- {efficientnet_b0_confidence}
- {efficientnet_b1_confidence}
- {ensemble_confidence}

Clinical Context:
- {injury_mechanism}
- {symptoms}
- {medical_history}
- {location}

Image Details:
- {view_type}
- {quality}
```

---

## ⚙️ Customization Guide

### **Modifying Prompts**

1. **Keep Structure:** Don't remove key sections
2. **Add Context:** Include institution-specific info
3. **Adjust Tone:** Match your clinical environment
4. **Update Examples:** Use real cases (anonymized)
5. **Version Control:** Track prompt changes

### **Creating New Prompts**

1. Start with existing template
2. Define clear purpose
3. Specify input/output format
4. Include examples
5. Add safety disclaimers
6. Test with real data

---

## 🔐 Safety & Compliance

### **All Prompts Include:**
- Medical disclaimers
- Radiologist confirmation requirement
- AI limitation acknowledgment
- Patient safety emphasis
- Emergency protocols

### **Compliance Notes:**
- HIPAA-compliant language
- Professional medical standards
- Evidence-based recommendations
- Appropriate confidence levels

---

## 📊 Performance Tips

### **Gemini (Detailed):**
- Use for complex analysis
- Better for long-form reports
- More nuanced understanding
- Slower but comprehensive

### **Groq (Fast):**
- Use for quick assessments
- Better for summaries
- Optimized for speed
- Concise outputs

---

## 🔄 Maintenance

### **Regular Updates:**
- Review prompt effectiveness
- Update based on feedback
- Add new examples
- Refine language
- Version prompts

### **Quality Assurance:**
- Test with real cases
- Validate against medical standards
- Get radiologist feedback
- Monitor AI responses

---

## 📚 Additional Resources

- **Medical Terminology:** Standard radiology terms
- **Fracture Classification:** AO/OTA system
- **Report Standards:** ACR guidelines
- **AI Ethics:** Medical AI best practices

---

## ✅ Quick Reference

**Need detailed analysis?** → `gemini_prompts/fracture_analysis.txt`  
**Need formal report?** → `gemini_prompts/report_generation.txt`  
**Need treatment plan?** → `gemini_prompts/medical_recommendations.txt`  
**Need quick triage?** → `groq_prompts/quick_analysis.txt`  
**Need summary?** → `groq_prompts/summary_generation.txt`  

---

## 🎯 Success Metrics

**Good Prompt Response:**
- Specific and detailed
- Actionable recommendations
- Appropriate confidence
- Safety-conscious
- Well-structured
- Professional language

**Poor Prompt Response:**
- Vague descriptions
- Missing critical info
- Overconfident
- Unsafe advice
- Disorganized
- Casual language

---

**All prompts ready for production use!** 🚀

For integration code, see: `src/llm_integration/`  
For usage examples, see: `examples/`
