#!/usr/bin/env python3
"""
Script to populate Materials Science modules for demonstration
This script will delete existing modules and create new ones with diverse content
"""

import requests
import json
import time

# API base URL - adjust if needed
API_BASE = "http://localhost:8000/api"

# Sample Materials Science modules with various types and sections
MATERIALS_SCIENCE_MODULES = [
    # Unit 1: Fundamentals
    {
        "eventName": "Materials Science",
        "title": "Introduction to Materials Science",
        "duration": "15 min",
        "unit": "Unit 1: Fundamentals",
        "order": 1,
        "points": 10,
        "prerequisites": [],
        "content": {
            "overview": "Get introduced to the fascinating world of materials science and understand how the structure of materials determines their properties.",
            "objectives": [
                "Define materials science and its interdisciplinary nature",
                "Identify the four main classes of materials",
                "Understand the structure-property relationship",
                "Recognize applications of materials science in everyday life"
            ],
            "resources": [
                {
                    "title": "Materials Science and Engineering Textbook Chapter 1",
                    "description": "Comprehensive introduction to materials science fundamentals",
                    "url": "https://example.com/textbook-ch1",
                    "type": "reading"
                },
                {
                    "title": "What is Materials Science?",
                    "description": "5-minute overview video explaining materials science basics",
                    "url": "https://youtube.com/watch?v=example1",
                    "type": "video"
                }
            ]
        },
        "validationType": "none",
        "problems": [],
        "systemPrompt": ""
    },
    {
        "eventName": "Materials Science",
        "title": "Atomic Structure & Bonding",
        "duration": "25 min",
        "unit": "Unit 1: Fundamentals",
        "order": 2,
        "points": 15,
        "prerequisites": ["materials_science_01"],
        "content": {
            "overview": "Explore how atomic structure influences material properties through various types of chemical bonding.",
            "objectives": [
                "Describe atomic structure and electron configuration",
                "Explain ionic, covalent, and metallic bonding",
                "Understand how bonding affects material properties",
                "Identify bonding types in different materials"
            ],
            "resources": [
                {
                    "title": "Chemical Bonding in Materials",
                    "description": "Interactive video on atomic bonding mechanisms",
                    "url": "https://youtube.com/watch?v=example2",
                    "type": "video"
                },
                {
                    "title": "Bonding Theory Guide",
                    "description": "Detailed guide with diagrams and examples",
                    "url": "https://example.com/bonding-guide",
                    "type": "reading"
                }
            ]
        },
        "validationType": "problems",
        "problems": [
            "Calculate the coordination number for a face-centered cubic (FCC) crystal structure.",
            "Explain the difference between ionic and covalent bonding in materials.",
            "What is the relationship between atomic radius and crystal structure?"
        ],
        "systemPrompt": "You are a materials science tutor. Help students understand atomic structure and bonding concepts."
    },
    {
        "eventName": "Materials Science",
        "title": "Crystal Structures",
        "duration": "30 min",
        "unit": "Unit 1: Fundamentals",
        "order": 3,
        "points": 20,
        "prerequisites": ["materials_science_01", "materials_science_02"],
        "content": {
            "overview": "Investigate various crystal structures and understand how atomic arrangement affects material behavior.",
            "objectives": [
                "Identify common crystal structures (FCC, BCC, HCP)",
                "Calculate coordination numbers and atomic packing factors",
                "Understand the relationship between structure and properties",
                "Analyze crystal defects and their effects"
            ],
            "resources": [
                {
                    "title": "Crystal Structure Database",
                    "description": "Interactive database of crystal structures",
                    "url": "https://example.com/crystal-db",
                    "type": "research"
                },
                {
                    "title": "Crystal Structure AI Tutor",
                    "description": "AI-powered tutor for crystal structure problems",
                    "url": "https://example.com/ai-tutor",
                    "type": "AIconversation"
                }
            ]
        },
        "validationType": "AIconversation",
        "problems": [],
        "systemPrompt": "You are an AI tutor specializing in crystal structures. Help students understand FCC, BCC, and HCP crystal systems, coordination numbers, and atomic packing factors. Provide clear explanations and guide them through calculations."
    },
    
    # Unit 2: Material Properties
    {
        "eventName": "Materials Science",
        "title": "Mechanical Properties",
        "duration": "20 min",
        "unit": "Unit 2: Material Properties",
        "order": 4,
        "points": 15,
        "prerequisites": ["materials_science_01", "materials_science_02", "materials_science_03"],
        "content": {
            "overview": "Learn about mechanical properties including strength, ductility, and toughness.",
            "objectives": [
                "Interpret stress-strain curves",
                "Define elastic and plastic deformation",
                "Calculate Young's modulus and yield strength",
                "Compare brittle vs. ductile behavior"
            ],
            "resources": [
                {
                    "title": "Mechanical Testing Handbook",
                    "description": "Comprehensive guide to mechanical property testing",
                    "url": "https://example.com/mech-testing",
                    "type": "reading"
                },
                {
                    "title": "Stress-Strain Analysis",
                    "description": "Visual explanation of stress-strain relationships",
                    "url": "https://youtube.com/watch?v=example3",
                    "type": "video"
                }
            ]
        },
        "validationType": "problems",
        "problems": [
            "Calculate Young's modulus from a stress-strain curve.",
            "Define the difference between elastic and plastic deformation.",
            "Explain how yield strength is determined from a stress-strain curve.",
            "Compare the mechanical properties of brittle vs. ductile materials."
        ],
        "systemPrompt": "You are a materials science tutor. Help students understand mechanical properties and stress-strain relationships."
    },
    {
        "eventName": "Materials Science",
        "title": "Thermal Properties",
        "duration": "18 min",
        "unit": "Unit 2: Material Properties",
        "order": 5,
        "points": 12,
        "prerequisites": ["materials_science_01", "materials_science_02", "materials_science_03"],
        "content": {
            "overview": "Examine how materials respond to temperature changes and heat transfer.",
            "objectives": [
                "Define thermal conductivity and heat capacity",
                "Explain thermal expansion mechanisms",
                "Understand phase transitions",
                "Analyze thermal stress effects"
            ],
            "resources": [
                {
                    "title": "Thermal Properties Explained",
                    "description": "Animation showing thermal behavior in materials",
                    "url": "https://youtube.com/watch?v=example4",
                    "type": "video"
                }
            ]
        },
        "validationType": "notesUpload",
        "problems": [],
        "systemPrompt": ""
    },
    {
        "eventName": "Materials Science",
        "title": "Electrical Properties",
        "duration": "22 min",
        "unit": "Unit 2: Material Properties",
        "order": 6,
        "points": 18,
        "prerequisites": ["materials_science_01", "materials_science_02", "materials_science_03"],
        "content": {
            "overview": "Explore electrical conduction mechanisms and electronic properties of materials.",
            "objectives": [
                "Classify materials by electrical conductivity",
                "Understand band theory",
                "Explain semiconductor doping",
                "Analyze temperature effects on conductivity"
            ],
            "resources": [
                {
                    "title": "Electronic Properties AI Lab",
                    "description": "Interactive AI simulations of electronic behavior",
                    "url": "https://example.com/ai-electronics",
                    "type": "AIconversation"
                }
            ]
        },
        "validationType": "AIconversation",
        "problems": [],
        "systemPrompt": "You are an AI tutor specializing in electrical properties of materials. Help students understand conductors, semiconductors, and insulators. Explain band theory, doping, and temperature effects on conductivity."
    },
    
    # Unit 3: Material Classes
    {
        "eventName": "Materials Science",
        "title": "Metals and Alloys",
        "duration": "25 min",
        "unit": "Unit 3: Material Classes",
        "order": 7,
        "points": 16,
        "prerequisites": ["materials_science_01", "materials_science_02", "materials_science_03", "materials_science_04"],
        "content": {
            "overview": "Study the structure and properties of metals and their alloys.",
            "objectives": [
                "Describe metallic bonding and structure",
                "Understand alloy formation and phase diagrams",
                "Explain strengthening mechanisms",
                "Identify applications of common alloys"
            ],
            "resources": [
                {
                    "title": "Metallurgy Fundamentals",
                    "description": "Complete guide to metallic materials",
                    "url": "https://example.com/metallurgy",
                    "type": "reading"
                }
            ]
        },
        "validationType": "problems",
        "problems": [
            "Explain the difference between metallic and ionic bonding.",
            "Describe how alloy formation affects material properties.",
            "What are the main strengthening mechanisms in metals?",
            "Identify common applications for steel, aluminum, and titanium alloys."
        ],
        "systemPrompt": "You are a materials science tutor. Help students understand metallic materials and alloy systems."
    },
    {
        "eventName": "Materials Science",
        "title": "Ceramics and Glasses",
        "duration": "28 min",
        "unit": "Unit 3: Material Classes",
        "order": 8,
        "points": 20,
        "prerequisites": ["materials_science_01", "materials_science_02", "materials_science_03", "materials_science_04"],
        "content": {
            "overview": "Investigate the structure and applications of ceramic and glass materials.",
            "objectives": [
                "Compare crystalline and amorphous structures",
                "Understand ceramic processing techniques",
                "Explain brittleness in ceramics",
                "Identify high-tech ceramic applications"
            ],
            "resources": [
                {
                    "title": "Advanced Ceramics Research",
                    "description": "Latest research in ceramic materials",
                    "url": "https://example.com/ceramics-research",
                    "type": "research"
                }
            ]
        },
        "validationType": "notesUpload",
        "problems": [],
        "systemPrompt": ""
    },
    {
        "eventName": "Materials Science",
        "title": "Polymers and Composites",
        "duration": "24 min",
        "unit": "Unit 3: Material Classes",
        "order": 9,
        "points": 17,
        "prerequisites": ["materials_science_01", "materials_science_02", "materials_science_03", "materials_science_04"],
        "content": {
            "overview": "Learn about polymer structure and composite material design principles.",
            "objectives": [
                "Classify polymers by structure and properties",
                "Understand polymerization processes",
                "Explain composite reinforcement mechanisms",
                "Analyze fiber-matrix interactions"
            ],
            "resources": [
                {
                    "title": "Polymer Science Basics",
                    "description": "Introduction to polymer chemistry and physics",
                    "url": "https://youtube.com/watch?v=example5",
                    "type": "video"
                }
            ]
        },
        "validationType": "problems",
        "problems": [
            "Compare crystalline and amorphous structures in ceramics.",
            "Explain why ceramics are typically brittle materials.",
            "Describe the processing steps for making ceramic materials.",
            "What are some high-tech applications of advanced ceramics?"
        ],
        "systemPrompt": "You are a materials science tutor. Help students understand ceramic and glass materials."
    },
    
    # Unit 4: Advanced Topics
    {
        "eventName": "Materials Science",
        "title": "Nanomaterials",
        "duration": "30 min",
        "unit": "Unit 4: Advanced Topics",
        "order": 10,
        "points": 25,
        "prerequisites": ["materials_science_01", "materials_science_02", "materials_science_03", "materials_science_04", "materials_science_05", "materials_science_06", "materials_science_07", "materials_science_08", "materials_science_09"],
        "content": {
            "overview": "Explore the fascinating world of nanomaterials and nanotechnology applications.",
            "objectives": [
                "Define nanomaterials and size effects",
                "Understand quantum confinement",
                "Explore synthesis methods",
                "Identify nanotechnology applications"
            ],
            "resources": [
                {
                    "title": "Nanomaterials AI Simulator",
                    "description": "Simulate nanomaterial properties and behavior",
                    "url": "https://example.com/nano-sim",
                    "type": "AIconversation"
                }
            ]
        },
        "validationType": "AIconversation",
        "problems": [],
        "systemPrompt": "You are an AI tutor specializing in nanomaterials. Help students understand size effects, quantum confinement, synthesis methods, and nanotechnology applications. Provide clear explanations of nanoscale phenomena."
    },
    {
        "eventName": "Materials Science",
        "title": "Smart Materials",
        "duration": "35 min",
        "unit": "Unit 4: Advanced Topics",
        "order": 11,
        "points": 30,
        "prerequisites": ["materials_science_01", "materials_science_02", "materials_science_03", "materials_science_04", "materials_science_05", "materials_science_06", "materials_science_07", "materials_science_08", "materials_science_09", "materials_science_10"],
        "content": {
            "overview": "Study materials that can change properties in response to external stimuli.",
            "objectives": [
                "Define smart material categories",
                "Understand shape memory alloys",
                "Explore piezoelectric materials",
                "Analyze biomimetic approaches"
            ],
            "resources": [
                {
                    "title": "Smart Materials Database",
                    "description": "Comprehensive database of smart material applications",
                    "url": "https://example.com/smart-materials",
                    "type": "research"
                }
            ]
        },
        "validationType": "notesUpload",
        "problems": [],
        "systemPrompt": ""
    }
]

def delete_all_modules():
    """Delete all existing learning modules"""
    try:
        print("🗑️  Deleting existing modules...")
        response = requests.get(f"{API_BASE}/LearningModules")
        if response.status_code == 200:
            modules = response.json()
            for module_data in modules:
                if isinstance(module_data, dict):
                    # Handle Firebase format
                    module_id = list(module_data.keys())[0]
                else:
                    module_id = module_data.get('id')
                
                if module_id:
                    delete_response = requests.delete(f"{API_BASE}/LearningModules/{module_id}")
                    if delete_response.status_code == 200:
                        print(f"   ✅ Deleted module {module_id}")
                    else:
                        print(f"   ❌ Failed to delete module {module_id}")
                    time.sleep(0.1)  # Small delay to avoid overwhelming the API
        print("✨ Cleanup complete!")
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

def create_modules():
    """Create new Materials Science modules"""
    print("🚀 Creating new Materials Science modules...")
    
    for i, module_data in enumerate(MATERIALS_SCIENCE_MODULES, 1):
        try:
            # Add unique ID and creation timestamp
            module_data['id'] = f"materials_science_{i:02d}"
            module_data['createdAt'] = '2024-01-15T00:00:00Z'
            
            response = requests.post(
                f"{API_BASE}/LearningModules",
                headers={'Content-Type': 'application/json'},
                json=module_data
            )
            
            if response.status_code in [200, 201]:
                print(f"   ✅ Created: {module_data['title']} ({module_data['unit']})")
            else:
                print(f"   ❌ Failed to create: {module_data['title']} - {response.status_code}")
                print(f"      Response: {response.text}")
            
            time.sleep(0.2)  # Small delay between requests
            
        except Exception as e:
            print(f"   ❌ Error creating {module_data['title']}: {e}")

def main():
    """Main execution function"""
    print("🎯 Materials Science Module Population Script")
    print("=" * 50)
    
    # Step 1: Clean up existing modules
    delete_all_modules()
    
    # Step 2: Create new modules
    create_modules()
    
    print("=" * 50)
    print("🎉 Script completed!")
    print()
    print("📋 Summary:")
    print(f"   • Created {len(MATERIALS_SCIENCE_MODULES)} new modules")
    print("   • Organized into 4 units:")
    print("     - Unit 1: Fundamentals (3 modules)")
    print("     - Unit 2: Material Properties (3 modules)")
    print("     - Unit 3: Material Classes (3 modules)")
    print("     - Unit 4: Advanced Topics (2 modules)")
    print()
    print("🎨 Features demonstrated:")
    print("   • Progressive XP rewards (10-30 points)")
    print("   • Prerequisites system for module dependencies")
    print("   • Various validation types (none, problems, notesUpload, AIconversation)")
    print("   • Rich content with objectives and resources")
    print("   • Proper unit organization for learning paths")
    print()
    print("🌐 Navigate to the Events page and select Materials Science to see the results!")

if __name__ == "__main__":
    main() 