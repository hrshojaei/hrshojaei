#!/usr/bin/env python
"""
Script to import candidates from CSV file
"""
import csv
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.candidate_manager import CandidateManager
from loguru import logger


def import_from_csv(csv_file: str):
    """Import candidates from CSV file"""

    logger.info(f"Importing candidates from {csv_file}")

    manager = CandidateManager()
    added_count = 0
    error_count = 0

    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            # Validate headers
            required_fields = ['name', 'phone']
            if not all(field in reader.fieldnames for field in required_fields):
                print(f"❌ Error: CSV must contain columns: {', '.join(required_fields)}")
                print(f"Found columns: {', '.join(reader.fieldnames)}")
                return

            print(f"\n📋 Found columns: {', '.join(reader.fieldnames)}")
            print("=" * 60)

            for i, row in enumerate(reader, 1):
                try:
                    # Required fields
                    name = row.get('name', '').strip()
                    phone = row.get('phone', '').strip()

                    if not name or not phone:
                        print(f"⚠️  Row {i}: Skipping - missing name or phone")
                        error_count += 1
                        continue

                    # Optional fields
                    email = row.get('email', '').strip() or None
                    current_company = row.get('current_company', '').strip() or None
                    current_position = row.get('current_position', '').strip() or None
                    notes = row.get('notes', '').strip() or None

                    experience_years = row.get('experience_years', '').strip()
                    experience_years = int(experience_years) if experience_years else None

                    # Add candidate
                    candidate_id = manager.add_candidate(
                        name=name,
                        phone=phone,
                        email=email,
                        current_company=current_company,
                        current_position=current_position,
                        experience_years=experience_years,
                        notes=notes
                    )

                    print(f"✅ Row {i}: Added {name} (ID: {candidate_id})")
                    added_count += 1

                except Exception as e:
                    print(f"❌ Row {i}: Error - {e}")
                    error_count += 1

        print("\n" + "=" * 60)
        print(f"✅ Successfully imported: {added_count} candidates")
        if error_count > 0:
            print(f"⚠️  Errors: {error_count}")
        print()

    except FileNotFoundError:
        print(f"❌ Error: File '{csv_file}' not found")
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")


def create_example_csv():
    """Create an example CSV file"""
    example_file = "candidates_example.csv"

    with open(example_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'name', 'phone', 'email', 'current_company',
            'current_position', 'experience_years', 'notes'
        ])
        writer.writeheader()
        writer.writerows([
            {
                'name': 'Max Mustermann',
                'phone': '+4915112345671',
                'email': 'max.mustermann@example.com',
                'current_company': 'Hörakustik Excellence',
                'current_position': 'Hörakustikmeister',
                'experience_years': '5',
                'notes': 'Interessiert an Führungsposition'
            },
            {
                'name': 'Anna Schmidt',
                'phone': '+4915112345672',
                'email': 'anna.schmidt@example.com',
                'current_company': 'Hören & Verstehen GmbH',
                'current_position': 'Hörakustikerin',
                'experience_years': '3',
                'notes': 'Möchte sich weiterentwickeln'
            },
            {
                'name': 'Peter Weber',
                'phone': '+4915112345673',
                'email': 'peter.weber@example.com',
                'current_company': 'Klang & Raum',
                'current_position': 'Filialleiter',
                'experience_years': '8',
                'notes': 'Sucht neue Herausforderung'
            }
        ])

    print(f"✅ Created example CSV: {example_file}")
    print(f"\nEdit this file and then run:")
    print(f"  python scripts/import_candidates.py {example_file}")
    print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""
📥 Candidate CSV Import Tool

Usage:
    python scripts/import_candidates.py <csv_file>    - Import candidates from CSV
    python scripts/import_candidates.py --example     - Create example CSV file

CSV Format:
    Required columns:
        - name: Full name of candidate
        - phone: Phone number with country code (e.g., +4915112345678)

    Optional columns:
        - email: Email address
        - current_company: Current employer
        - current_position: Current job title
        - experience_years: Years of experience (number)
        - notes: Additional notes

Example:
    python scripts/import_candidates.py candidates.csv
        """)
        sys.exit(0)

    if sys.argv[1] == '--example':
        create_example_csv()
    else:
        csv_file = sys.argv[1]
        import_from_csv(csv_file)
