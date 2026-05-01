import requests
from flask import Flask, render_template_string, request, Response
from datetime import datetime

app = Flask(__name__)

# ── Twilio Credentials ─────────────────────────────────────────
# Get these from: https://console.twilio.com
# Account SID starts with "AC..."

# ── Twilio Credentials (ADDED) ─────────────────────────────────
TWILIO_ACCOUNT_SID = "ACfacdfd193a7a692c4bfb59fca7c15415"
TWILIO_AUTH_TOKEN  = "5d226d975795b242b1d3250a711d3c05"

HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PhoneTrace — Phone Intelligence</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --bg:      #080b10;
    --surface: #0e1318;
    --border:  #1c2535;
    --border2: #253045;
    --accent:  #00e5ff;
    --accent2: #7b61ff;
    --green:   #00ffa3;
    --red:     #ff4d6d;
    --yellow:  #ffd166;
    --text:    #e8edf5;
    --muted:   #5a6a80;
  }
  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Syne', sans-serif;
    min-height: 100vh;
    overflow-x: hidden;
  }
  body::before {
    content: '';
    position: fixed; inset: 0;
    background-image:
      linear-gradient(rgba(0,229,255,0.025) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0,229,255,0.025) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none; z-index: 0;
  }
  .wrap { position:relative; z-index:1; max-width:880px; margin:0 auto; padding:44px 20px 80px; }

  /* Header */
  .header { text-align:center; margin-bottom:48px; }
  .logo-line { display:flex; align-items:center; justify-content:center; gap:12px; margin-bottom:10px; }
  .logo-icon { width:46px; height:46px; background:linear-gradient(135deg,var(--accent),var(--accent2)); border-radius:13px; display:flex; align-items:center; justify-content:center; font-size:22px; }
  h1 { font-size:2.5rem; font-weight:800; letter-spacing:-1px; background:linear-gradient(135deg,#fff 30%,var(--accent)); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
  .tagline { color:var(--muted); font-family:'DM Mono',monospace; font-size:0.8rem; letter-spacing:2px; text-transform:uppercase; }

  /* Search Card */
  .search-card { background:var(--surface); border:1px solid var(--border); border-radius:20px; padding:28px; margin-bottom:28px; }
  .input-row { display:flex; gap:12px; flex-wrap:wrap; align-items:flex-end; }
  .input-group { flex:1; min-width:200px; }
  .input-group label { display:block; font-family:'DM Mono',monospace; font-size:0.68rem; color:var(--muted); text-transform:uppercase; letter-spacing:1.5px; margin-bottom:8px; }
  .input-group input { width:100%; background:#0a0e14; border:1px solid var(--border2); border-radius:10px; padding:13px 16px; color:var(--text); font-family:'DM Mono',monospace; font-size:0.95rem; outline:none; transition:border-color 0.2s,box-shadow 0.2s; }
  .input-group input:focus { border-color:var(--accent); box-shadow:0 0 0 3px rgba(0,229,255,0.1); }
  .input-group input::placeholder { color:var(--muted); }

  /* Credentials notice */
  .cred-notice { background:rgba(255,209,102,0.07); border:1px solid rgba(255,209,102,0.2); border-radius:12px; padding:12px 16px; margin-bottom:20px; font-family:'DM Mono',monospace; font-size:0.78rem; color:var(--yellow); }
  .cred-notice strong { display:block; margin-bottom:4px; }

  .btn-analyze { padding:13px 32px; background:linear-gradient(135deg,var(--accent),var(--accent2)); border:none; border-radius:10px; color:#080b10; font-family:'Syne',sans-serif; font-size:0.95rem; font-weight:700; cursor:pointer; transition:opacity 0.2s,transform 0.1s; white-space:nowrap; }
  .btn-analyze:hover { opacity:0.85; transform:translateY(-1px); }

  /* Error */
  .error-box { background:rgba(255,77,109,0.08); border:1px solid rgba(255,77,109,0.25); border-radius:12px; padding:16px 20px; color:var(--red); font-family:'DM Mono',monospace; font-size:0.82rem; margin-bottom:24px; line-height:1.7; }
  .error-box strong { display:block; margin-bottom:6px; font-size:0.88rem; }
  .error-box a { color:var(--accent); text-decoration:none; }
  .error-box a:hover { text-decoration:underline; }

  /* Result header */
  .result-header { display:flex; align-items:center; gap:16px; margin-bottom:20px; padding:18px 22px; background:var(--surface); border:1px solid var(--border); border-radius:16px; }
  .validity-badge { padding:6px 16px; border-radius:20px; font-family:'DM Mono',monospace; font-size:0.75rem; font-weight:500; letter-spacing:1px; text-transform:uppercase; }
  .valid   { background:rgba(0,255,163,0.1); color:var(--green); border:1px solid rgba(0,255,163,0.2); }
  .invalid { background:rgba(255,77,109,0.1); color:var(--red);   border:1px solid rgba(255,77,109,0.2); }
  .result-number { font-family:'DM Mono',monospace; font-size:1.25rem; color:var(--accent); letter-spacing:1px; }

  /* Caller Name */
  .caller-card { background:linear-gradient(135deg,rgba(0,229,255,0.05),rgba(123,97,255,0.05)); border:1px solid rgba(0,229,255,0.18); border-radius:14px; padding:18px 22px; display:flex; align-items:center; gap:16px; margin-bottom:16px; }
  .caller-avatar { width:50px; height:50px; background:linear-gradient(135deg,var(--accent),var(--accent2)); border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:22px; flex-shrink:0; }
  .caller-name-label { font-family:'DM Mono',monospace; font-size:0.63rem; color:var(--muted); text-transform:uppercase; letter-spacing:2px; margin-bottom:4px; }
  .caller-name-value { font-size:1.35rem; font-weight:700; color:var(--text); }
  .caller-name-sub { font-family:'DM Mono',monospace; font-size:0.7rem; color:var(--muted); margin-top:3px; }

  /* No caller name notice */
  .no-caller { background:rgba(90,106,128,0.1); border:1px solid var(--border2); border-radius:12px; padding:14px 18px; font-family:'DM Mono',monospace; font-size:0.78rem; color:var(--muted); margin-bottom:16px; }

  /* Grids */
  .grid-2 { display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-bottom:14px; }
  .grid-3 { display:grid; grid-template-columns:1fr 1fr 1fr; gap:14px; margin-bottom:14px; }
  @media(max-width:600px){ .grid-2,.grid-3{grid-template-columns:1fr;} .input-row{flex-direction:column;} }

  .info-card { background:var(--surface); border:1px solid var(--border); border-radius:13px; padding:16px 18px; transition:border-color 0.2s; }
  .info-card:hover { border-color:var(--border2); }
  .ic-label { font-family:'DM Mono',monospace; font-size:0.62rem; color:var(--muted); text-transform:uppercase; letter-spacing:2px; margin-bottom:8px; }
  .ic-icon  { font-size:1.3rem; margin-bottom:8px; display:block; }
  .ic-value { font-size:1rem; font-weight:600; color:var(--text); }
  .ic-value.mono { font-family:'DM Mono',monospace; font-size:0.9rem; color:var(--accent); }

  .line-pill { display:inline-block; padding:4px 14px; border-radius:20px; font-family:'DM Mono',monospace; font-size:0.75rem; font-weight:500; text-transform:uppercase; letter-spacing:1px; }
  .pill-mobile   { background:rgba(0,229,255,0.1);  color:var(--accent);  border:1px solid rgba(0,229,255,0.2); }
  .pill-landline { background:rgba(255,209,102,0.1); color:var(--yellow); border:1px solid rgba(255,209,102,0.2); }
  .pill-voip     { background:rgba(123,97,255,0.1);  color:var(--accent2); border:1px solid rgba(123,97,255,0.2); }
  .pill-unknown  { background:rgba(90,106,128,0.1);  color:var(--muted);   border:1px solid var(--border2); }

  /* Section label */
  .section-label { font-family:'DM Mono',monospace; font-size:0.65rem; color:var(--muted); text-transform:uppercase; letter-spacing:3px; margin:24px 0 14px; display:flex; align-items:center; gap:10px; }
  .section-label::after { content:''; flex:1; height:1px; background:var(--border); }

  /* Report */
  .report-section { background:var(--surface); border:1px solid var(--border); border-radius:16px; overflow:hidden; margin-top:8px; }
  .report-header { display:flex; justify-content:space-between; align-items:center; padding:12px 18px; border-bottom:1px solid var(--border); background:#0b1016; }
  .report-title { font-family:'DM Mono',monospace; font-size:0.7rem; color:var(--muted); text-transform:uppercase; letter-spacing:2px; }
  .report-btns { display:flex; gap:8px; }
  .btn-copy,.btn-txt { padding:5px 14px; border-radius:7px; font-family:'DM Mono',monospace; font-size:0.7rem; cursor:pointer; border:none; transition:opacity 0.2s; }
  .btn-copy { background:rgba(0,229,255,0.1); color:var(--accent); border:1px solid rgba(0,229,255,0.2); }
  .btn-txt  { background:rgba(90,106,128,0.12); color:var(--muted); border:1px solid var(--border2); text-decoration:none; display:inline-flex; align-items:center; }
  .btn-copy:hover,.btn-txt:hover { opacity:0.7; }
  #reportBox { padding:20px; font-family:'DM Mono',monospace; font-size:0.77rem; color:#8fa3bf; white-space:pre; overflow-x:auto; line-height:1.85; background:#060a0f; }
</style>
</head>
<body>
<div class="wrap">

  <div class="header">
    <div class="logo-line">
      <div class="logo-icon">📡</div>
      <h1>PhoneTrace</h1>
    </div>
    <p class="tagline">Phone Number Intelligence · Powered by Twilio</p>
  </div>

  {% if cred_error %}
  <div class="cred-notice">
    <strong>⚠ Credentials not configured</strong>
    Open <code>phone_twilio.py</code> and replace <code>TWILIO_ACCOUNT_SID</code> and <code>TWILIO_AUTH_TOKEN</code> with your actual values from
    <a href="https://console.twilio.com" target="_blank" style="color:var(--yellow)">console.twilio.com</a>
  </div>
  {% endif %}

  <div class="search-card">
    <form action="/scan" method="get">
      <div class="input-row">
        <div class="input-group" style="flex:2;min-width:240px;">
          <label>Phone Number (with country code)</label>
          <input type="text" name="n" placeholder="+919973XXXXXX" required value="{{ form.n }}">
        </div>
        <div class="input-group" style="max-width:120px;">
          
          
        </div>
        <button type="submit" class="btn-analyze">Analyze →</button>
      </div>
    </form>
  </div>

  {% if error %}
  <div class="error-box">
    <strong>⚠ {{ error.title }}</strong>
    {{ error.detail }}
    {% if error.fix %}<br><br>{{ error.fix | safe }}{% endif %}
  </div>
  {% endif %}

  {% if data %}

  <!-- Validity -->
  <div class="result-header">
    <span class="validity-badge {{ 'valid' if data.valid else 'invalid' }}">
      {{ '✓ Valid' if data.valid else '✗ Invalid' }}
    </span>
    <span class="result-number">{{ data.intl_format or data.num }}</span>
  </div>

  {% if data.caller_name %}
  <div class="caller-card">
    <div class="caller-avatar">👤</div>
    <div>
      <div class="caller-name-label">Caller Name (CNAM)</div>
      <div class="caller-name-value">{{ data.caller_name }}</div>
      <div class="caller-name-sub"> PhoneTrace: {{ data.caller_type or '—' }}</div>
    </div>
  </div>
  {% endif %}

  <!-- Details -->
  <div class="section-label">Number Details</div>
  <div class="grid-2">
    <div class="info-card">
      <span class="ic-icon">🌍</span>
      <div class="ic-label">Country</div>
      <div class="ic-value">{{ data.country_name }}{% if data.calling_country_code %} &nbsp;<span style="color:var(--muted);font-size:0.85em;">(+{{ data.calling_country_code }})</span>{% endif %}</div>
    </div>
    <div class="info-card">
      <span class="ic-icon">📶</span>
      <div class="ic-label">Carrier / Operator</div>
      <div class="ic-value">{{ data.carrier or '—' }}</div>
    </div>
  </div>
  <div class="grid-3">
    <div class="info-card">
      <span class="ic-icon">📱</span>
      <div class="ic-label">Line Type</div>
      <div class="ic-value">
        {% set lt = (data.line_type or 'unknown')|lower %}
        {% if 'mobile' in lt %}
          <span class="line-pill pill-mobile">Mobile</span>
        {% elif 'land' in lt or 'fixed' in lt %}
          <span class="line-pill pill-landline">Landline</span>
        {% elif 'voip' in lt %}
          <span class="line-pill pill-voip">VoIP</span>
        {% else %}
          <span class="line-pill pill-unknown">{{ data.line_type or 'Unknown' }}</span>
        {% endif %}
      </div>
    </div>
    <div class="info-card">
      <span class="ic-icon">🔢</span>
      <div class="ic-label">National Format</div>
      <div class="ic-value mono">{{ data.national_format or '—' }}</div>
    </div>
    <div class="info-card">
      <span class="ic-icon">🌐</span>
      <div class="ic-label">International Format</div>
      <div class="ic-value mono">{{ data.intl_format or '—' }}</div>
    </div>
  </div>

  <!-- Plain Text Report -->
  <div class="section-label">Plain Text Report</div>
  <div class="report-section">
    <div class="report-header">
      <span class="report-title">Full Report</span>
      <div class="report-btns">
        <button class="btn-copy" onclick="copyReport()">Copy All</button>
        <a class="btn-txt" href="/report?n={{ form.n|urlencode }}&cc={{ form.cc|urlencode }}" target="_blank">Open as .txt</a>
      </div>
    </div>
    <div id="reportBox">{{ report }}</div>
  </div>

  {% endif %}
</div>
<script>
function copyReport(){
  const t = document.getElementById('reportBox').innerText;
  navigator.clipboard.writeText(t).then(()=>{
    const b = document.querySelector('.btn-copy');
    b.innerText = 'Copied!';
    setTimeout(()=>b.innerText='Copy All', 2000);
  });
}
</script>
</body>
</html>
'''


def make_error(title, detail, fix=None):
    return {"title": title, "detail": detail, "fix": fix}


def check_credentials():
    """Return True if credentials look valid (not placeholder)."""
    if TWILIO_ACCOUNT_SID.startswith("ACxx") or TWILIO_AUTH_TOKEN.startswith("xxxx"):
        return False
    if not TWILIO_ACCOUNT_SID.startswith("AC"):
        return False
    return True


def twilio_lookup(phone, country_code=''):
    url    = f"https://lookups.twilio.com/v2/PhoneNumbers/{requests.utils.quote(phone)}"
    params = {"Fields": "line_type_intelligence,caller_name"}
    if country_code:
        params["CountryCode"] = country_code.upper()
    resp = requests.get(url, params=params,
                        auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
                        timeout=12)
    return resp.status_code, resp.json()


def parse_twilio(raw):
    lti         = raw.get("line_type_intelligence") or {}
    caller_data = raw.get("caller_name") or {}

    caller_name = caller_data.get("caller_name") if caller_data else None
    caller_type = caller_data.get("caller_type") if caller_data else None

    # country name fallback — Twilio v2 returns country_code not full name
    country_code = raw.get("country_code", "")
    country_names = {
        "IN":"India","US":"United States","GB":"United Kingdom","AU":"Australia",
        "CA":"Canada","PK":"Pakistan","BD":"Bangladesh","NP":"Nepal","AE":"UAE",
        "SG":"Singapore","MY":"Malaysia","NG":"Nigeria","ZA":"South Africa",
        "DE":"Germany","FR":"France","IT":"Italy","ES":"Spain","BR":"Brazil",
    }
    country_name = country_names.get(country_code, country_code)

    return {
        "valid":                raw.get("valid", False),
        "num":                  raw.get("phone_number", ""),
        "intl_format":          raw.get("phone_number", ""),
        "national_format":      raw.get("national_format", ""),
        "calling_country_code": raw.get("calling_country_code", ""),
        "country_code":         country_code,
        "country_name":         country_name,
        "carrier":              lti.get("carrier_name") or "—",
        "line_type":            lti.get("type") or "—",
        "caller_name":          caller_name,
        "caller_type":          caller_type,
        "_raw":                 raw,
        "_lti":                 lti,
        "_caller":              caller_data,
    }


def build_report(d, now):
    sep  = "=" * 64
    sep2 = "-" * 64
    lines = []
    lines.append(sep)
    lines.append("                      MADE BY CODEINNIGHT")
    lines.append(sep)
    lines.append(f"  Generated At              : {now}")
    lines.append(sep2)

    lines.append("")
    lines.append("[ 1 ]  NUMBER DETAILS")
    lines.append(sep2)
    lines.append(f"  Valid                     : {'YES ✓' if d['valid'] else 'NO ✗'}")
    lines.append(f"  Phone Number (E.164)      : {d['num'] or '—'}")
    lines.append(f"  National Format           : {d['national_format'] or '—'}")
    lines.append(f"  International Format      : {d['intl_format'] or '—'}")
    lines.append(f"  Calling Country Code      : +{d['calling_country_code'] or '—'}")
    lines.append(f"  Country Code (ISO)        : {d['country_code'] or '—'}")
    lines.append(f"  Country Name              : {d['country_name'] or '—'}")
    lines.append(f"  Carrier / Operator        : {d['carrier'] or '—'}")
    lines.append(f"  Line Type                 : {str(d['line_type']).upper() if d['line_type'] else '—'}")

    lines.append("")
    lines.append("[ 2 ]  CALLER NAME (CNAM)")
    lines.append(sep2)
    if d['caller_name']:
        lines.append(f"  Caller Name               : {d['caller_name']}")
        lines.append(f"  Caller Type               : {d['caller_type'] or '—'}")
    else:
        lines.append("  Caller Name               : Not available")
        lines.append("  Reason                    : CNAM database has limited coverage")
        lines.append("                              for non-US/Canada numbers.")
        lines.append("  Alternative               : https://www.truecaller.com/search/in/" + d['num'].replace('+','').replace(' ',''))

    lines.append("")
    lines.append("[ 3 ]  LINE TYPE INTELLIGENCE (RAW)")
    lines.append(sep2)
    lti = d.get('_lti') or {}
    if lti:
        for k, v in lti.items():
            lines.append(f"  {k:<28}: {v if v is not None else '—'}")
    else:
        lines.append("  No line type data returned.")

    lines.append("")
    lines.append("[ 4 ]  FULL RAW API RESPONSE")
    lines.append(sep2)
    raw = d.get('_raw', {})
    for k, v in raw.items():
        if k not in ('caller_name', 'line_type_intelligence'):
            lines.append(f"  {k:<28}: {v if v is not None else '—'}")

    lines.append("")
    lines.append("[ 5 ]  ALTERNATIVE LOOKUP LINKS")
    lines.append(sep2)
    num_raw = d['num'].replace('+','').replace(' ','')
    num_enc = requests.utils.quote(d['num'])
    lines.append(f"  Truecaller                : https://www.truecaller.com/search/in/{num_raw}")
    lines.append(f"  Sync.me                   : https://sync.me/search/?number={num_enc}")
    lines.append(f"  NumLookup                 : https://www.numlookup.com/?number={num_enc}")
    lines.append(f"  Should I Answer           : https://www.shouldianswer.com/phone-number/{num_raw}")
    lines.append(f"  Google Search             : https://www.google.com/search?q=%22{num_enc}%22")

    lines.append("")
    lines.append(sep)
    lines.append("  END OF REPORT")
    lines.append(sep)
    return "\n".join(lines)


def get_params():
    return (
        request.args.get('n',  '').strip(),
        request.args.get('cc', '').strip(),
    )


@app.route('/scan')
def scan():
    num, cc = get_params()
    form = {"n": num, "cc": cc}
    cred_ok = check_credentials()

    if not num:
        return render_template_string(HTML, data=None, error=None, report="",
                                      form=form, cred_error=not cred_ok)

    if not cred_ok:
        err = make_error(
            "Credentials not configured",
            "Open phone_twilio.py and replace TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN "
            "with your real values.",
            'Get them at <a href="https://console.twilio.com" target="_blank">console.twilio.com</a>'
        )
        return render_template_string(HTML, data=None, error=err, report="",
                                      form=form, cred_error=True)

    try:
        status, raw = twilio_lookup(num, cc)
    except requests.exceptions.Timeout:
        err = make_error("Timeout", "The request to Twilio timed out. Try again.")
        return render_template_string(HTML, data=None, error=err, report="", form=form, cred_error=False)
    except Exception as e:
        err = make_error("Connection Error", str(e))
        return render_template_string(HTML, data=None, error=err, report="", form=form, cred_error=False)

    # Handle Twilio error responses
    if status == 401:
        err = make_error(
            "Authentication Failed (401)",
            "Your Account SID or Auth Token is incorrect.",
            'Double-check them at <a href="https://console.twilio.com" target="_blank">console.twilio.com</a> — '
            'Account SID starts with <strong>AC</strong> and is ~34 characters long.'
        )
        return render_template_string(HTML, data=None, error=err, report="", form=form, cred_error=True)

    if status == 404:
        err = make_error("Number Not Found (404)", "This number could not be found or is not a valid E.164 format.",
                         "Make sure you include the country code, e.g. <strong>+91</strong>9973XXXXXX for India.")
        return render_template_string(HTML, data=None, error=err, report="", form=form, cred_error=False)

    if status != 200:
        msg = raw.get("message") or raw.get("detail") or f"HTTP {status}"
        err = make_error(f"Twilio Error ({status})", msg)
        return render_template_string(HTML, data=None, error=err, report="", form=form, cred_error=False)

    d      = parse_twilio(raw)
    now    = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = build_report(d, now)

    return render_template_string(HTML, data=d, report=report, error=None,
                                  form=form, cred_error=False)


@app.route('/report')
def plain_report():
    num, cc = get_params()
    if not num:
        return "No number provided.", 400
    if not check_credentials():
        return "Twilio credentials not configured in phone_twilio.py", 500
    try:
        status, raw = twilio_lookup(num, cc)
        if status != 200:
            return f"Twilio Error {status}: {raw.get('message','Unknown')}", 400
        d      = parse_twilio(raw)
        now    = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report = build_report(d, now)
        return Response(report, mimetype='text/plain')
    except Exception as e:
        return f"Error: {e}", 500


@app.route('/')
def index():
    cred_ok = check_credentials()
    return render_template_string(HTML, data=None, error=None, report="",
        form={"n": "", "cc": ""}, cred_error=not cred_ok)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)