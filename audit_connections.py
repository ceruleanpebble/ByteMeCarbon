"""
Detailed HTML/CSS/JS Connectivity Audit
"""

print("=" * 70)
print("HTML-CSS-JS CONNECTIVITY AUDIT")
print("=" * 70)

# Read files
with open('templates/index.html', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

with open('static/style.css', 'r', encoding='utf-8', errors='ignore') as f:
    css = f.read()

with open('static/script.js', 'r', encoding='utf-8', errors='ignore') as f:
    js = f.read()

# Extract element IDs from HTML
import re
html_ids = re.findall(r'id="([^"]+)"', html)
print(f"\n✓ HTML Element IDs found: {len(html_ids)}")
for id in sorted(set(html_ids)):
    print(f"  - {id}")

# Extract CSS classes
css_classes = re.findall(r'\.([a-zA-Z0-9\-]+)\s*\{', css)
print(f"\n✓ CSS Classes defined: {len(set(css_classes))}")
for cls in sorted(set(css_classes))[:20]:
    print(f"  - {cls}")

# Find classes used in HTML
html_classes = re.findall(r'class="([^"]+)"', html)
all_html_classes = set()
for cls_str in html_classes:
    for cls in cls_str.split():
        all_html_classes.add(cls)

print(f"\n✓ HTML Classes used: {len(all_html_classes)}")
for cls in sorted(all_html_classes):
    print(f"  - {cls}")

# Check for undefined CSS classes
undefined = []
for cls in all_html_classes:
    if cls not in css_classes and cls not in [':', 'hover']:
        undefined.append(cls)

if undefined:
    print(f"\n✗ UNDEFINED CSS CLASSES ({len(set(undefined))}):")
    for cls in sorted(set(undefined)):
        print(f"  - {cls}")
else:
    print(f"\n✓ All CSS classes defined")

# Check JS getElementById calls
js_getelements = re.findall(r"getElementById\('([^']+)'\)", js)
js_getelements += re.findall(r'getElementById\("([^"]+)"\)', js)

print(f"\n✓ JavaScript getElementById() calls: {len(set(js_getelements))}")
for elem_id in sorted(set(js_getelements)):
    print(f"  - {elem_id}")

# Check if all JS getElementById match HTML IDs
missing_ids = []
for elem_id in js_getelements:
    if elem_id not in html_ids:
        missing_ids.append(elem_id)

if missing_ids:
    print(f"\n✗ MISSING HTML ELEMENTS ({len(set(missing_ids))}):")
    for elem_id in sorted(set(missing_ids)):
        print(f"  - {elem_id} (referenced in JS but not in HTML)")
else:
    print(f"\n✓ All JavaScript getElementById() calls have matching HTML elements")

# Check for HTML elements not used in JS
unused_ids = []
for html_id in html_ids:
    if html_id not in js_getelements:
        unused_ids.append(html_id)

if unused_ids:
    print(f"\n⚠ Potentially unused HTML elements ({len(set(unused_ids))}):")
    for elem_id in sorted(set(unused_ids)):
        print(f"  - {elem_id}")

# Check CSS for duplicate rules
css_rules = re.findall(r'\.([\w\-]+)\s*\{[^}]*\}', css)
duplicates = {}
for rule in css_rules:
    if rule in duplicates:
        duplicates[rule] += 1
    else:
        duplicates[rule] = 1

dup_rules = {k: v for k, v in duplicates.items() if v > 1}
if dup_rules:
    print(f"\n⚠ DUPLICATE CSS RULES ({len(dup_rules)}):")
    for cls, count in sorted(dup_rules.items()):
        print(f"  - .{cls} defined {count} times")
else:
    print(f"\n✓ No duplicate CSS rules")

# Check event listeners
event_listeners = re.findall(r"addEventListener\('([^']+)'", js)
print(f"\n✓ Event Listeners registered: {len(event_listeners)}")
for event in sorted(set(event_listeners)):
    print(f"  - {event}")

# Check onclick handlers in HTML
onclick = re.findall(r"onclick=\"([^\"]+)\"", html)
print(f"\n✓ onClick handlers in HTML: {len(set(onclick))}")
for handler in sorted(set(onclick)):
    print(f"  - {handler}")

# Check CSS Grid and Layout
grid_rules = re.findall(r'\.([a-zA-Z0-9\-]*grid[a-zA-Z0-9\-]*)\s*\{', css)
print(f"\n✓ CSS Grid/Layout classes: {len(set(grid_rules))}")
for cls in sorted(set(grid_rules)):
    print(f"  - .{cls}")

print("\n" + "=" * 70)
print("CONNECTIVITY SUMMARY")
print("=" * 70)

issues = []
if missing_ids:
    issues.append(f"✗ {len(set(missing_ids))} missing HTML elements")
if dup_rules:
    issues.append(f"⚠ {len(dup_rules)} duplicate CSS rules")
if undefined:
    issues.append(f"⚠ {len(set(undefined))} undefined CSS classes")

if not issues:
    print("✓ All connections are properly established!")
else:
    print("Issues found:")
    for issue in issues:
        print(f"  {issue}")
