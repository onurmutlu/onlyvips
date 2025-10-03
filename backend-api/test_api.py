"""Quick API Test Script"""
import sys
from app.api.api import api_router

# Test all endpoint tags
tags = set()
for route in api_router.routes:
    if hasattr(route, 'tags') and route.tags:
        tags.add(route.tags[0])

# Expected endpoints per tag
expected_endpoints = {
    'auth': 6,
    'users': 8,
    'tasks': 10,  # minimum
    'badges': 7,  # minimum
    'content': 7,
    'showcus': 9,
    'payments': 9,
    'admin': 10,
    'health': 5
}

print("🧪 API Endpoint Test")
print("=" * 50)
print(f"✅ Total Routes: {len(api_router.routes)}")
print(f"✅ Total Tags: {len(tags)}")
print(f"✅ Tags: {sorted(tags)}")
print()

# Check each tag
all_good = True
for tag, min_count in expected_endpoints.items():
    count = sum(1 for r in api_router.routes if hasattr(r, 'tags') and tag in r.tags)
    status = "✅" if count >= min_count else "❌"
    print(f"{status} {tag}: {count} endpoints (expected: {min_count}+)")
    if count < min_count:
        all_good = False

print()
if all_good:
    print("🎉 ALL TESTS PASSED!")
    sys.exit(0)
else:
    print("❌ SOME TESTS FAILED!")
    sys.exit(1)
