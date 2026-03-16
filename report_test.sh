#!/usr/bin/env bash

set -u

BASE="${BASE:-http://127.0.0.1:8000/api}"
UPLOAD_IMAGE="${UPLOAD_IMAGE:-/Users/dr_puff/workspace/UoG/IT/COMPSCI5012_IT_CW/assessment/examples/wireframe.png}"
USER_NAME="report_$(date +%s)"
EMAIL="${USER_NAME}@example.com"
PASSWORD="Passw0rd!"

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

pass() {
  printf '%s PASS\n' "$1"
}

section() {
  printf '\n== %s ==\n' "$1"
}

fail() {
  printf '%s FAIL\n' "$1"
  if [ -n "${2:-}" ]; then
    printf '%s\n' "$2"
  fi
  exit 1
}

curl_json() {
  local method="$1"
  local url="$2"
  local body="${3:-}"
  local auth="${4:-}"
  local outfile="$tmpdir/response.json"
  local http_code

  if [ -n "$auth" ]; then
    http_code="$(curl -sS -o "$outfile" -w '%{http_code}' -X "$method" "$url" \
      -H "Authorization: Bearer $auth" \
      -H "Content-Type: application/json" \
      -d "$body")"
  else
    http_code="$(curl -sS -o "$outfile" -w '%{http_code}' -X "$method" "$url" \
      -H "Content-Type: application/json" \
      -d "$body")"
  fi

  printf '%s\n' "$http_code"
}

curl_form() {
  local method="$1"
  local url="$2"
  local auth="$3"
  shift 3
  local outfile="$tmpdir/response.json"
  local http_code

  http_code="$(curl -sS -o "$outfile" -w '%{http_code}' -X "$method" "$url" \
    -H "Authorization: Bearer $auth" \
    "$@")"

  printf '%s\n' "$http_code"
}

json_get() {
  local expr="$1"
  python3 - "$tmpdir/response.json" "$expr" <<'PY'
import json
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text())
expr = sys.argv[2]
value = payload
for part in expr.split("."):
    if part.isdigit():
        value = value[int(part)]
    else:
        value = value[part]
if isinstance(value, (dict, list)):
    print(json.dumps(value))
else:
    print(value)
PY
}

json_assert() {
  local code="$1"
  python3 - "$tmpdir/response.json" "$code" <<'PY'
import json
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text())
namespace = {"payload": payload}
exec(sys.argv[2], namespace, namespace)
PY
}

assert_http() {
  local expected="$1"
  local actual="$2"
  local label="$3"
  if [ "$expected" != "$actual" ]; then
    local body
    body="$(cat "$tmpdir/response.json" 2>/dev/null)"
    fail "$label" "HTTP $actual: $body"
  fi
}

register_login() {
  local code
  section "Module 1 Authentication"

  code="$(curl_json POST "$BASE/auth/user/register/" "{\"username\":\"$USER_NAME\",\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")"
  assert_http 201 "$code" "Auth Register"
  json_assert 'assert payload["username"] == "'"$USER_NAME"'"; assert payload["email"] == "'"$EMAIL"'"; assert "id" in payload'
  pass "Auth Register"

  code="$(curl_json POST "$BASE/auth/user/login/" "{\"username\":\"$USER_NAME\",\"password\":\"$PASSWORD\"}")"
  assert_http 200 "$code" "Auth Login"
  json_assert 'assert payload["access"]; assert payload["refresh"]'
  ACCESS="$(json_get access)"
  REFRESH="$(json_get refresh)"
  pass "Auth Login"

  code="$(curl_json GET "$BASE/auth/me/" "" "$ACCESS")"
  assert_http 200 "$code" "Auth Me"
  json_assert 'assert payload["username"] == "'"$USER_NAME"'"; assert payload["role"] == "user"; assert payload["is_staff"] is False'
  pass "Auth Me"

  code="$(curl_json POST "$BASE/auth/refresh/" "{\"refresh\":\"$REFRESH\"}")"
  assert_http 200 "$code" "Auth Refresh"
  json_assert 'assert payload["access"]; assert payload["refresh"]'
  REFRESH="$(json_get refresh)"
  pass "Auth Refresh"

  pass "Module 1 Authentication"
}

wardrobe_crud() {
  local code
  section "Module 2 Wardrobe CRUD"

  code="$(curl_form POST "$BASE/wardrobe/items/" "$ACCESS" \
    -F "category=top" \
    -F "item=Report Top" \
    -F 'style_semantics=["casual"]' \
    -F 'season_semantics=["winter"]' \
    -F 'usage_semantics=["daily"]' \
    -F "color_semantics=white" \
    -F "description=report top item")"
  assert_http 201 "$code" "Wardrobe Create Top"
  json_assert 'assert payload["category"] == "top"; assert payload["item"] == "Report Top"'
  TOP_ID="$(json_get id)"
  pass "Wardrobe Create Top"

  code="$(curl_form POST "$BASE/wardrobe/items/" "$ACCESS" \
    -F "category=bottom" \
    -F "item=Report Bottom" \
    -F 'style_semantics=["casual"]' \
    -F 'season_semantics=["winter"]' \
    -F 'usage_semantics=["daily"]' \
    -F "color_semantics=black" \
    -F "description=report bottom item")"
  assert_http 201 "$code" "Wardrobe Create Bottom"
  json_assert 'assert payload["category"] == "bottom"; assert payload["item"] == "Report Bottom"'
  BOTTOM_ID="$(json_get id)"
  pass "Wardrobe Create Bottom"

  code="$(curl_form POST "$BASE/wardrobe/items/" "$ACCESS" \
    -F "category=shoes" \
    -F "item=Report Shoes" \
    -F 'style_semantics=["casual"]' \
    -F 'season_semantics=["winter"]' \
    -F 'usage_semantics=["daily"]' \
    -F "color_semantics=brown" \
    -F "description=report shoes item")"
  assert_http 201 "$code" "Wardrobe Create Shoes"
  json_assert 'assert payload["category"] == "shoes"; assert payload["item"] == "Report Shoes"'
  SHOES_ID="$(json_get id)"
  pass "Wardrobe Create Shoes"

  code="$(curl_form POST "$BASE/wardrobe/items/" "$ACCESS" \
    -F "category=top" \
    -F "item=Delete Me" \
    -F 'style_semantics=["casual"]' \
    -F 'season_semantics=["winter"]' \
    -F 'usage_semantics=["daily"]' \
    -F "color_semantics=grey" \
    -F "description=temp item for delete test")"
  assert_http 201 "$code" "Wardrobe Create Delete Candidate"
  DELETE_ITEM_ID="$(json_get id)"
  pass "Wardrobe Create Delete Candidate"

  code="$(curl_json GET "$BASE/wardrobe/items/" "" "$ACCESS")"
  assert_http 200 "$code" "Wardrobe List Items"
  json_assert 'assert isinstance(payload, list); assert len(payload) >= 4'
  pass "Wardrobe List Items"

  code="$(curl_form PATCH "$BASE/wardrobe/items/$TOP_ID/" "$ACCESS" \
    -F "description=updated report top item")"
  assert_http 200 "$code" "Wardrobe Update Item"
  json_assert 'assert payload["description"] == "updated report top item"'
  pass "Wardrobe Update Item"

  code="$(curl -sS -o "$tmpdir/delete_item.txt" -w '%{http_code}' -X DELETE "$BASE/wardrobe/items/$DELETE_ITEM_ID/" \
    -H "Authorization: Bearer $ACCESS")"
  assert_http 204 "$code" "Wardrobe Delete Item"
  pass "Wardrobe Delete Item"

  pass "Module 2 Wardrobe CRUD"
}

history_check() {
  local code
  section "Module 3 History"
  code="$(curl_json GET "$BASE/outfits/history/" "" "$ACCESS")"
  assert_http 200 "$code" "History List Initial"
  json_assert 'assert isinstance(payload, list)'
  pass "History List Initial"
}

ootd_check() {
  local code
  section "Module 4 OOTD Recommend"
  code="$(curl_json POST "$BASE/outfits/recommend/" '{"latitude":55.8642,"longitude":-4.2518}' "$ACCESS")"
  assert_http 200 "$code" "OOTD Recommend Request"
  json_assert 'assert "weather" in payload; assert "recommendation" in payload; assert "outfit" in payload; assert "history" in payload'
  pass "OOTD Recommend Request"
  json_assert 'assert payload["weather"]["location"]; assert payload["weather"]["condition"]'
  pass "OOTD Weather Response"
  json_assert 'assert payload["recommendation"]["summary"]; assert "recommendations" in payload["recommendation"]'
  pass "OOTD Recommendation Payload"
  json_assert 'assert payload["outfit"]["top"] is not None; assert "recommendation_text" in payload["outfit"]'
  pass "OOTD Outfit Record"
  json_assert 'assert payload["history"]["id"]; assert payload["history"]["outfit"] == payload["outfit"]["id"]'
  pass "OOTD Auto History"
  OUTFIT_ID="$(json_get outfit.id)"
  AUTO_HISTORY_ID="$(json_get history.id)"
  pass "Module 4 OOTD Recommend"
}

history_crud() {
  local code
  section "Module 5 History CRUD"

  code="$(curl_json GET "$BASE/outfits/history/" "" "$ACCESS")"
  assert_http 200 "$code" "History List After OOTD"
  json_assert 'assert isinstance(payload, list); assert len(payload) >= 1'
  pass "History List After OOTD"

  code="$(curl_json POST "$BASE/outfits/history/" "{\"outfit\":$OUTFIT_ID,\"rating\":5,\"feedback\":\"manual history entry\"}" "$ACCESS")"
  assert_http 201 "$code" "History Create"
  json_assert 'assert payload["outfit"] == '"$OUTFIT_ID"'; assert payload["rating"] == 5'
  MANUAL_HISTORY_ID="$(json_get id)"
  pass "History Create"

  code="$(curl_json PATCH "$BASE/outfits/history/$MANUAL_HISTORY_ID/" '{"rating":4,"feedback":"updated manual history entry"}' "$ACCESS")"
  assert_http 200 "$code" "History Update"
  json_assert 'assert payload["rating"] == 4; assert payload["feedback"] == "updated manual history entry"'
  pass "History Update"

  code="$(curl -sS -o "$tmpdir/delete_history.txt" -w '%{http_code}' -X DELETE "$BASE/outfits/history/$MANUAL_HISTORY_ID/" \
    -H "Authorization: Bearer $ACCESS")"
  assert_http 204 "$code" "History Delete"
  pass "History Delete"

  pass "Module 5 History CRUD"
}

upload_check() {
  local outfile="$tmpdir/upload.json"
  local code
  section "Module 6 Upload"

  code="$(curl -sS -o "$outfile" -w '%{http_code}' -X POST "$BASE/wardrobe/items/upload/" \
    -H "Authorization: Bearer $ACCESS" \
    -F "file=@$UPLOAD_IMAGE")"

  if [ "$code" = "200" ]; then
    python3 - "$outfile" <<'PY' || fail "Upload Analyze Image" "$(cat "$outfile" 2>/dev/null)"
import json
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text())
assert payload["category"]
assert payload["item"]
assert payload["description"] is not None
PY
    pass "Upload Analyze Image"
    pass "Module 6 Upload"
    return
  fi

  if [ "$code" = "422" ]; then
    python3 - "$outfile" <<'PY' || fail "Upload Analyze Image" "$(cat "$outfile" 2>/dev/null)"
import json
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text())
assert payload["code"] == "recognition_failed"
PY
    pass "Upload Analyze Image"
    pass "Module 6 Upload"
    return
  fi

  fail "Module 6 Upload" "HTTP $code: $(cat "$outfile" 2>/dev/null)"
}

logout_check() {
  local outfile="$tmpdir/logout.txt"
  local code
  section "Module 7 Logout"
  code="$(curl -sS -o "$outfile" -w '%{http_code}' -X POST "$BASE/auth/logout/" \
    -H "Authorization: Bearer $ACCESS" \
    -H "Content-Type: application/json" \
    -d "{\"refresh\":\"$REFRESH\"}")"
  assert_http 204 "$code" "Auth Logout"
  pass "Auth Logout"
  pass "Module 7 Logout"
}

ACCESS=""
REFRESH=""
TOP_ID=""
BOTTOM_ID=""
SHOES_ID=""
DELETE_ITEM_ID=""
OUTFIT_ID=""
AUTO_HISTORY_ID=""
MANUAL_HISTORY_ID=""

register_login
wardrobe_crud
history_check
ootd_check
history_crud
upload_check
logout_check

printf 'Overall PASS\n'
