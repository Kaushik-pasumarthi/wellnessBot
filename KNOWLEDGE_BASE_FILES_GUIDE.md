# Knowledge Base File Editing Guide

## Files Modified by Admin Dashboard - Edit Knowledge Base Section

### 📁 **When Adding/Editing SYMPTOMS:**

**File Modified:** `kb_csv.json`
- **Location:** Root directory of your project
- **Purpose:** Main knowledge base containing all symptom information
- **What gets added/modified:**
  - Symptom name and display name
  - List of synonyms for better recognition
  - Symptom description and category
  - Frequency counter and related diseases

**Example structure in kb_csv.json:**
```json
{
  "symptoms": [
    {
      "name": "headache",
      "display_name": "Headache",
      "synonyms": ["head pain", "migraine", "head ache"],
      "description": "Pain in the head or neck area",
      "category": "Neurological",
      "frequency": 0,
      "related_diseases": []
    }
  ]
}
```

### 🏥 **When Adding/Editing DISEASES:**

**Files Modified:**

1. **`symptom_Description.csv`**
   - **Purpose:** Contains disease names and their medical descriptions
   - **Format:** Disease,Description
   - **Example:** `Common Cold,A viral infection affecting the upper respiratory system`

2. **`symptom_precaution.csv`**
   - **Purpose:** Contains preventive measures for each disease
   - **Format:** Disease,Precaution_1,Precaution_2,Precaution_3,Precaution_4
   - **Example:** `Common Cold,Rest,Drink fluids,Avoid cold exposure,Take vitamin C`

### 🔄 **How Changes Take Effect:**

1. **Immediate:** Files are updated instantly when you submit forms
2. **Bot Recognition:** Changes take effect after bot restart or system refresh
3. **Data Persistence:** All changes are permanently saved to the CSV and JSON files

### ⚠️ **Important Notes:**

- **Backup First:** Always backup your knowledge base files before making bulk changes
- **File Format:** Don't manually edit CSV files while using the admin interface
- **Encoding:** All files use UTF-8 encoding to support multiple languages
- **Validation:** The system validates entries before saving to prevent corruption

### 📊 **File Locations:**
```
your-project/
├── kb_csv.json                 # Main symptoms knowledge base
├── symptom_Description.csv     # Disease descriptions
├── symptom_precaution.csv      # Disease precautions
└── admin_dashboard.py          # Admin interface
```

### 🛠️ **Admin Dashboard Sections:**

1. **Add New Symptom** → Modifies `kb_csv.json`
2. **Add New Disease** → Modifies both CSV files
3. **Edit Existing Entries** → Modifies respective files based on selection
4. **File Information** → Shows current file status and sizes

This ensures you always know exactly which files are being modified when you use the knowledge base editing features!