#!/usr/bin/env python
"""List all available skills."""
import os
import glob

skills_dir = ".claude/skills"

print("Available Claude Skills:\n")
print("=" * 60)

for skill_path in glob.glob(f"{skills_dir}/*/"):
    skill_name = os.path.basename(skill_path.rstrip('/'))
    if skill_name in ['__pycache__']:
        continue
    
    skill_md = os.path.join(skill_path, "SKILL.md")
    if os.path.exists(skill_md):
        with open(skill_md, 'r') as f:
            lines = f.readlines()
            # Extract description from frontmatter
            in_frontmatter = False
            description = ""
            for line in lines:
                if line.strip() == '---':
                    in_frontmatter = not in_frontmatter
                    continue
                if in_frontmatter and line.startswith('description:'):
                    description = line.split(':', 1)[1].strip()
                    break
        
        print(f"\n📦 {skill_name}")
        print(f"   {description}")
        print(f"   Location: {skill_path}")

print("\n" + "=" * 60)
print("\nTo run a skill:")
print("  source venv/bin/activate")
print("  python .claude/skills/<skill-name>/scripts/<script>.py")
