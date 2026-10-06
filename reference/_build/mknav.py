"""Build a self-contained browsable navigator from a reference/ folder.

    python mknav.py <reference-dir> [--title "Repo Name"] [--include DIR=PREFIX]...

Discovers every .md under the folder and every .psv under _data/, embeds them,
and writes navigator.html beside them. No server, no network, no dependencies.

--include mounts another tree of markdown under a prefix, so one navigator can
carry both a reference/ folder and, say, a 400-page wiki beside it:

    python mknav.py reference --include ../wiki=wiki

Deliberately generic: it knows nothing about any particular repository, so the
same navigator works for a database-heavy repo and a three-file Android app.
"""
import sys, os, json, re, csv, io, datetime

args = [a for a in sys.argv[1:] if not a.startswith("--")]
REF = os.path.abspath(args[0])
TITLE = "Reference"
if "--title" in sys.argv:
    TITLE = sys.argv[sys.argv.index("--title") + 1]

SKIP_DIRS = {"_build", "_skills", ".git", "node_modules", "_ingested"}

# --include DIR=PREFIX, repeatable
INCLUDES = []
for i, a in enumerate(sys.argv):
    if a == "--include" and i + 1 < len(sys.argv):
        spec = sys.argv[i + 1]
        d, _, prefix = spec.partition("=")
        # resolve relative to the reference dir first (so "../wiki" reads naturally
        # from inside reference/), then fall back to the working directory
        cand = os.path.abspath(os.path.join(REF, d))
        if not os.path.isdir(cand):
            cand = os.path.abspath(d)
        INCLUDES.append((cand, prefix or os.path.basename(d.rstrip("/\\"))))

# ---------------------------------------------------------------- collect ---
docs = {}
for dirpath, dirnames, filenames in os.walk(REF):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
    for fn in sorted(filenames):
        if fn.lower().endswith(".md"):
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, REF).replace("\\", "/")
            docs[rel] = io.open(full, encoding="utf8").read()

for root, prefix in INCLUDES:
    if not os.path.isdir(root):
        print("  --include: %s not found, skipped" % root)
        continue
    n = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in sorted(filenames):
            if not fn.lower().endswith(".md"):
                continue
            full = os.path.join(dirpath, fn)
            rel = prefix + "/" + os.path.relpath(full, root).replace("\\", "/")
            try:
                docs[rel] = io.open(full, encoding="utf8").read()
                n += 1
            except Exception:
                pass
    print("  --include %s: %d documents mounted at %s/" % (root, n, prefix))

# Images referenced by the mounted trees. Only the PATHS travel into the
# payload -- the browser loads the files from disk beside navigator.html, so a
# 574-image vault costs a few KB here rather than tens of megabytes.
IMG_EXT = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp")
assets = {}


def collect_assets(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if not fn.lower().endswith(IMG_EXT):
                continue
            full = os.path.join(dirpath, fn)
            href = os.path.relpath(full, REF).replace("\\", "/")
            # keyed by bare filename (Obsidian resolves embeds that way) and
            # by path relative to the tree root (for [[assets/foo.png]])
            assets.setdefault(fn.lower(), href)
            assets.setdefault(
                os.path.relpath(full, root).replace("\\", "/").lower(), href)


collect_assets(REF)
for _root, _prefix in INCLUDES:
    collect_assets(_root)

data = {}
ddir = os.path.join(REF, "_data")
if os.path.isdir(ddir):
    for fn in sorted(os.listdir(ddir)):
        if not fn.lower().endswith(".psv"):
            continue
        p = os.path.join(ddir, fn)
        if os.path.getsize(p) > 2_500_000:      # keep the page loadable
            continue
        with io.open(p, encoding="utf8", errors="replace") as f:
            rows = [ln.rstrip("\n").split("|") for ln in f if ln.strip()]
        if len(rows) > 1:
            data[fn] = {"cols": rows[0], "rows": rows[1:4001], "total": len(rows) - 1}

if not docs:
    sys.exit(f"no .md files found under {REF}")

# Where each mounted tree actually lives, relative to navigator.html. The
# doc-key prefix ("wiki/") is not the disk path ("../wiki"), and a link that
# escapes above a mount root can only be resolved correctly on disk.
roots = {}
for _root, _prefix in INCLUDES:
    roots[_prefix] = os.path.relpath(_root, REF).replace("\\", "/")

meta = {"title": TITLE, "built": datetime.date.today().isoformat(),
        "ndocs": len(docs), "ndata": len(data), "nassets": len(assets)}

payload = json.dumps({"meta": meta, "docs": docs, "data": data,
                      "assets": assets, "roots": roots},
                     ensure_ascii=False, separators=(",", ":"))

# Embed the payload as a JS *string literal* rather than as the text of a
# <script type="application/json"> block that the page then reads back out of
# itself. Reading it back makes every render a DOM-text-to-innerHTML flow,
# which is what CodeQL reports as js/xss-through-dom -- 7 high alerts per
# repository, every one of them pointing at this one generated file.
#
# Escaping "<" and ">" as < / > is what makes this safe rather than
# merely quiet: to JSON.parse they are still "<" and ">", but "</script>"
# becomes unrepresentable in the source, so no document content can close the
# script element early. U+2028/29 are escaped because JS treated them as line
# terminators inside string literals before ES2019.
payload = json.dumps(payload)                    # -> a valid JS string literal
for _ch, _esc in (("<", "\\u003c"), (">", "\\u003e"),
                  ("\u2028", "\\u2028"), ("\u2029", "\\u2029")):
    payload = payload.replace(_ch, _esc)
assert "</" not in payload, "payload can still close a <script> element"
json.loads(json.loads(payload))                  # prove it still round-trips

# ------------------------------------------------------------------ page ---
HTML = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
:root{
  --bg:#fbfbfa; --panel:#fff; --ink:#1a1a18; --dim:#6b6b66; --line:#e4e4e0;
  --accent:#3b5bdb; --accent-bg:#eef2ff; --code-bg:#f4f4f2; --mark:#fff3bf;
  --good:#2b8a3e; --warn:#e8590c; --bad:#c92a2a;
}
:root:not([data-theme="light"]){ @media (prefers-color-scheme:dark){
  --bg:#16161a; --panel:#1d1d22; --ink:#e8e8e6; --dim:#9a9a95; --line:#32323a;
  --accent:#8ba4ff; --accent-bg:#22263a; --code-bg:#25252c; --mark:#4a4020;
  --good:#69db7c; --warn:#ffa94d; --bad:#ff8787;
}}
:root[data-theme="dark"]{
  --bg:#16161a; --panel:#1d1d22; --ink:#e8e8e6; --dim:#9a9a95; --line:#32323a;
  --accent:#8ba4ff; --accent-bg:#22263a; --code-bg:#25252c; --mark:#4a4020;
  --good:#69db7c; --warn:#ffa94d; --bad:#ff8787;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font:15px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
header{position:sticky;top:0;z-index:10;background:var(--panel);
  border-bottom:1px solid var(--line);padding:10px 16px;display:flex;
  gap:14px;align-items:center;flex-wrap:wrap}
header h1{font-size:15px;margin:0;font-weight:650;letter-spacing:-.01em}
header .sub{color:var(--dim);font-size:12.5px}
nav{display:flex;gap:2px;margin-left:auto;flex-wrap:wrap}
nav button{background:none;border:1px solid transparent;color:var(--dim);
  padding:5px 11px;border-radius:6px;cursor:pointer;font-size:13.5px;font-weight:500}
nav button:hover{color:var(--ink);background:var(--code-bg)}
nav button.on{color:var(--accent);background:var(--accent-bg);border-color:var(--line)}
main{display:flex;min-height:calc(100vh - 48px)}
aside{width:290px;flex:0 0 290px;border-right:1px solid var(--line);
  background:var(--panel);padding:14px 0 40px;overflow-y:auto;
  max-height:calc(100vh - 48px);position:sticky;top:48px}
aside .grp{padding:14px 16px 5px;font-size:11px;font-weight:700;color:var(--dim);
  text-transform:uppercase;letter-spacing:.07em}
aside a{display:block;padding:6px 16px;color:var(--ink);text-decoration:none;
  font-size:13.5px;border-left:2px solid transparent}
aside a:hover{background:var(--code-bg)}
aside a.on{border-left-color:var(--accent);color:var(--accent);background:var(--accent-bg);font-weight:550}
#search{width:calc(100% - 32px);margin:0 16px 8px;padding:7px 10px;border-radius:6px;
  border:1px solid var(--line);background:var(--bg);color:var(--ink);font-size:13.5px}
article{flex:1;padding:28px 40px 90px;max-width:920px;min-width:0}
article h1{font-size:27px;margin:.1em 0 .5em;letter-spacing:-.02em}
article h2{font-size:20px;margin:1.9em 0 .6em;padding-bottom:.25em;border-bottom:1px solid var(--line)}
article h3{font-size:16.5px;margin:1.5em 0 .45em}
article h4{font-size:14.5px;margin:1.3em 0 .4em;color:var(--dim)}
article p,article li{font-size:14.5px}
article a{color:var(--accent)}
/* wikilinks resolved into navigator routes */
article a.wl{text-decoration:none;border-bottom:1px solid var(--accent-bg)}
article a.wl:hover{border-bottom-color:var(--accent)}
/* a wikilink whose target is not mounted in this navigator -- shown, not hidden,
   because a silently-dropped link is worse than a visibly dead one */
/* a real file on disk that this navigator does not render */
article a.offdoc{color:var(--dim);text-decoration:none;
  border-bottom:1px dashed var(--line)}
article a.offdoc:hover{color:var(--accent)}
article .deadlink{color:var(--bad);border-bottom:1px dotted var(--bad);cursor:help}
article img.wimg{max-width:100%;height:auto;border:1px solid var(--line);
  border-radius:6px;margin:.6em 0}
/* frontmatter, as a metadata strip rather than raw YAML in the body */
article .fmbar{display:flex;flex-wrap:wrap;gap:0 10px;align-items:baseline;
  font-size:12px;color:var(--dim);padding:0 0 10px;margin:0 0 18px;
  border-bottom:1px solid var(--line)}
article .fmbar .fmk{color:var(--ink);opacity:.55;text-transform:uppercase;
  letter-spacing:.04em;font-size:10.5px}
article .fmbar .fmsep{opacity:.35}
article code{background:var(--code-bg);padding:1.5px 5px;border-radius:4px;
  font:13px/1.5 ui-monospace,SFMono-Regular,Consolas,monospace}
article pre{background:var(--code-bg);padding:13px 15px;border-radius:8px;
  overflow-x:auto;border:1px solid var(--line)}
article pre code{background:none;padding:0;font-size:12.5px;line-height:1.55}
article pre.mermaid{background:none;border:0;text-align:center;padding:6px 0;
  font-size:12px;line-height:1.5}
article pre.mermaid svg{max-width:100%;height:auto}
article blockquote{margin:1.1em 0;padding:.1em 1.1em;border-left:3px solid var(--accent);
  background:var(--accent-bg);border-radius:0 6px 6px 0}
article table{border-collapse:collapse;margin:1.1em 0;font-size:13.5px;width:100%}
article th,article td{border:1px solid var(--line);padding:6px 10px;text-align:left;vertical-align:top}
article th{background:var(--code-bg);font-weight:600}
article hr{border:none;border-top:1px solid var(--line);margin:2.2em 0}
.tablewrap{overflow-x:auto;max-width:100%}
mark{background:var(--mark);color:inherit;padding:0 2px;border-radius:2px}
.hit{padding:11px 14px;border:1px solid var(--line);border-radius:8px;margin-bottom:9px;
  background:var(--panel);cursor:pointer}
.hit:hover{border-color:var(--accent)}
.hit .p{font-size:12px;color:var(--dim);margin-bottom:3px}
.hit .s{font-size:13.5px}
.empty{color:var(--dim);padding:40px 0;text-align:center}
.pill{display:inline-block;font-size:11px;padding:1px 7px;border-radius:20px;
  background:var(--code-bg);color:var(--dim);border:1px solid var(--line);margin-left:6px}
@media(max-width:820px){
  main{flex-direction:column}
  aside{width:auto;flex:none;max-height:none;position:static;border-right:none;
    border-bottom:1px solid var(--line)}
  article{padding:20px 16px 70px}
}
</style></head><body>
<header>
  <h1>__TITLE__</h1>
  <span class="sub" id="sub"></span>
  <nav>
    <button data-t="docs" class="on">Documents</button>
    <button data-t="data">Data</button>
    <button data-t="find">Search</button>
    <button id="theme" title="Toggle theme">◐</button>
  </nav>
</header>
<main><aside id="side"></aside><article id="view"></article></main>
<script src="https://cdnjs.cloudflare.com/ajax/libs/mermaid/10.9.1/mermaid.min.js"
        integrity="sha512-6a80OTZVmEJhqYJUmYd5z8yHUCDlYnj6q9XwB/gKOEyNQV/Q8u+XeSG59a2ZKFEHGTYzgfOQKYEBtrZV7vBr+Q=="
        crossorigin="anonymous" referrerpolicy="no-referrer"></script>
<script>
const D = JSON.parse(__PAYLOAD__);
const $ = s => document.querySelector(s);
document.getElementById('sub').textContent =
  D.meta.ndocs + ' documents · ' + D.meta.ndata + ' datasets · built ' + D.meta.built;

/* ---------- markdown ---------- */
/* esc() output is interpolated into "-delimited attributes as well as into
   element bodies, so it has to escape quotes too. It did not, which is what
   CodeQL reports as js/incomplete-html-attribute-sanitization: a title or an
   alt text containing a double quote closed the attribute early. */
const esc = s => String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;')
                          .replace(/>/g,'&gt;').replace(/"/g,'&quot;')
                          .replace(/'/g,'&#39;');
/* Only ever put a vetted scheme in an href. A markdown link inside a document
   is content, and "javascript:..." in one would otherwise run on click.
   No scheme at all means a relative path, which is the normal case here and
   is safe; a scheme has to be one of three. */
function safeUrl(u){
  const s = String(u).replace(/[\u0000-\u0020]/g,'');   // defeat "java\tscript:"
  const m = /^([a-z][a-z0-9+.\-]*):/i.exec(s);
  return (m && !/^(?:https?|mailto)$/i.test(m[1])) ? '#' : String(u);
}
const slug = s => s.toLowerCase().replace(/[^\w\s-]/g,'').trim().replace(/\s+/g,'-');
/* ---------- wikilinks ----------
   An Obsidian vault wires its pages together with [[wikilinks]], which are
   not markdown -- a markdown renderer leaves them as literal text. Resolve
   them the way Obsidian does: by filename stem first, then by the
   frontmatter title, so [[Business Object Posting]] finds
   business-object-posting.md. */
const FM_RE = /^---\r?\n([\s\S]*?)\r?\n---\r?\n?/;
let WX = null;
function wx(){
  if(WX) return WX;
  WX = {path:{}, stem:{}, title:{}};
  Object.keys(D.docs).forEach(p=>{
    const lp = p.toLowerCase();
    WX.path[lp] = p;
    const stem = lp.split('/').pop().replace(/\.md$/,'');
    if(!(stem in WX.stem)) WX.stem[stem] = p;
    const fm = D.docs[p].match(FM_RE);
    if(fm){
      const t = fm[1].match(/^title:[ \t]*["']?(.+?)["']?[ \t]*$/m);
      if(t){ const k = t[1].trim().toLowerCase();
             if(!(k in WX.title)) WX.title[k] = p; }
    }
  });
  return WX;
}
function wres(target){
  const X = wx();
  const t = target.trim().toLowerCase().replace(/\.md$/,'');
  if(!t) return null;
  // [[TL Selector]] must find tl-selector.md: Obsidian matches a link to a
  // filename with whitespace normalised to the file's own separator.
  const base = t.split('/').pop();
  const kb = base.replace(/\s+/g,'-');
  return X.path[t+'.md'] || X.path[t] || X.stem[base] || X.stem[kb]
      || X.title[t] || X.title[base] || null;
}
function wasset(n){
  const A = D.assets||{}, k = n.trim().toLowerCase();
  return A[k] || A[k.split('/').pop()] || null;
}
const UNPIPE = t => t.split(String.fromCharCode(92)+'|').join('|');

function wikiHtml(m){
  const embed = m.charAt(0) === '!';
  const raw = UNPIPE(m.slice(embed ? 3 : 2, -2));
  const bar = raw.indexOf('|');
  const link  = (bar < 0 ? raw : raw.slice(0, bar)).trim();
  const alias = (bar < 0 ? ''  : raw.slice(bar + 1)).trim();
  const hash  = link.indexOf('#');
  const page  = (hash < 0 ? link : link.slice(0, hash)).trim();
  const anch  = (hash < 0 ? ''   : link.slice(hash + 1)).trim();

  if(embed){
    const a = wasset(page || link);
    if(a) return '<img class="wimg" src="'+a+'" alt="'+esc(alias||page)+'" loading="lazy">';
  }
  // [[#Heading]] -- a link within the page being rendered
  if(!page && anch)
    return '<a href="#'+slug(anch)+'" class="wl">'+esc(alias||anch)+'</a>';

  const p = wres(page);
  const label = alias || (anch ? page+' \u203a '+anch : page);
  if(!p) return '<span class="deadlink" title="unresolved wikilink">'
                +esc(label)+'</span>';
  return '<a class="wl" href="#docs/'+p+'" data-wiki="'+p
       + '" data-anchor="'+esc(anch)+'">'+esc(label)+'</a>';
}

function inline(s){
  // Wikilinks are lifted out BEFORE escaping, so wikiHtml can emit real HTML
  // without esc() mangling it, then dropped back in at the end.
  const slots = [];
  const keep = h => { slots.push(h); return '\u0000W'+(slots.length-1)+'\u0000'; };
  // Inline code is masked FIRST: a [[wikilink]] quoted in backticks is a
  // literal being talked about, not a link. log.md quotes historical
  // broken links that way and must keep showing them as text.
  s = s.replace(/`([^`\n]+)`/g,(m,c)=>keep('<code>'+esc(c)+'</code>'));
  s = s.replace(/!?\[\[[^\[\]\n]+?\]\]/g, m=>keep(wikiHtml(m)));
  s = esc(s);
  s = s.replace(/\*\*([^*]+)\*\*/g,'<strong>$1</strong>');
  s = s.replace(/(^|[^*])\*([^*\n]+)\*/g,'$1<em>$2</em>');
  s = s.replace(/\[([^\]]+)\]\(([^)]+)\)/g,(m,t,h)=>
    '<a href="'+h+'" data-link="'+h+'">'+t+'</a>');
  s = s.replace(/\\\|/g,'|');          // leftover table pipe escapes
  s = s.replace(/\u0000W(\d+)\u0000/g,(m,i)=>slots[+i]);
  return s;
}

/* Frontmatter is metadata, not body text. Rendered as a compact strip so the
   page still declares its visibility and currency without four rules and a
   block of raw YAML at the top. */
function splitFm(src){
  const m = src.match(FM_RE);
  return m ? {fm:m[1], body:src.slice(m[0].length)} : {fm:null, body:src};
}
function fmBar(fm){
  if(!fm) return '';
  const keep = ['type','visibility','applies_to','last_updated','status','tags','promoted'];
  const out = [];
  fm.split(/\r?\n/).forEach(ln=>{
    const m = ln.match(/^([A-Za-z_]+):[ \t]*(.*)$/);
    if(!m) return;
    const k = m[1].toLowerCase();
    if(keep.indexOf(k) < 0) return;
    const v = m[2].trim().replace(/^["']|["']$/g,'');
    if(!v) return;
    out.push('<span class="fmk">'+esc(k.replace(/_/g,' '))+'</span>&nbsp;'+esc(v));
  });
  return out.length ? '<div class="fmbar">'+out.join('<span class="fmsep">\u00b7</span>')+'</div>' : '';
}
function md(src){
  const L = src.split(/\r?\n/); let o=[], i=0;
  const listStack=[];
  const closeLists=n=>{ while(listStack.length>n) o.push('</'+listStack.pop()+'>'); };
  while(i<L.length){
    let l=L[i];
    if(/^```/.test(l)){
      const lang=l.slice(3).trim(); i++; const buf=[];
      while(i<L.length && !/^```/.test(L[i])) buf.push(L[i++]);
      i++; closeLists(0);
      if(lang==='mermaid'){
        // mermaid reads textContent, so escaping here is both safe and correct
        o.push('<pre class="mermaid">'+esc(buf.join('\n'))+'</pre>');
      } else {
        o.push('<pre><code class="lang-'+esc(lang)+'">'+esc(buf.join('\n'))+'</code></pre>');
      }
      continue;
    }
    if(/^\s*\|.*\|\s*$/.test(l) && i+1<L.length && /^\s*\|[\s:|-]+\|\s*$/.test(L[i+1])){
      closeLists(0);
      // Obsidian REQUIRES \| for an aliased wikilink inside a table cell.
      // Splitting on a bare | tears those cells in half, so mask the escape
      // first and restore it for inline() to consume.
      const cells=r=>{ const T='\u0000P\u0000';
        return r.trim().replace(/\\\|/g,T).replace(/^\||\|$/g,'').split('|')
                .map(c=>c.split(T).join(String.fromCharCode(92)+'|').trim()); };
      const head=cells(l); i+=2; const body=[];
      while(i<L.length && /^\s*\|.*\|\s*$/.test(L[i])) body.push(cells(L[i++]));
      o.push('<div class="tablewrap"><table><thead><tr>'+
        head.map(c=>'<th>'+inline(c)+'</th>').join('')+'</tr></thead><tbody>'+
        body.map(r=>'<tr>'+r.map(c=>'<td>'+inline(c)+'</td>').join('')+'</tr>').join('')+
        '</tbody></table></div>');
      continue;
    }
    let m;
    if(m=l.match(/^(#{1,5})\s+(.*)$/)){
      closeLists(0); const n=m[1].length, t=m[2];
      o.push('<h'+n+' id="'+slug(t)+'">'+inline(t)+'</h'+n+'>'); i++; continue;
    }
    if(/^\s*(-{3,}|\*{3,}|_{3,})\s*$/.test(l)){ closeLists(0); o.push('<hr>'); i++; continue; }
    if(m=l.match(/^>\s?(.*)$/)){
      closeLists(0); const buf=[];
      while(i<L.length && (m=L[i].match(/^>\s?(.*)$/))){ buf.push(m[1]); i++; }
      o.push('<blockquote>'+md(buf.join('\n'))+'</blockquote>'); continue;
    }
    if(m=l.match(/^(\s*)([-*+]|\d+[.)])\s+(.*)$/)){
      const depth=Math.floor(m[1].length/2)+1;
      const tag=/\d/.test(m[2])?'ol':'ul';
      while(listStack.length<depth) { o.push('<'+tag+'>'); listStack.push(tag); }
      closeLists(depth);
      let txt=m[3]; i++;
      while(i<L.length && /^\s{2,}\S/.test(L[i]) && !/^\s*([-*+]|\d+[.)])\s/.test(L[i])){
        txt+=' '+L[i].trim(); i++;
      }
      o.push('<li>'+inline(txt)+'</li>'); continue;
    }
    if(!l.trim()){ closeLists(0); i++; continue; }
    const buf=[l]; i++;
    while(i<L.length && L[i].trim() && !/^(#{1,5}\s|>|```|\s*([-*+]|\d+[.)])\s|\s*\|)/.test(L[i]))
      buf.push(L[i++]);
    closeLists(0); o.push('<p>'+inline(buf.join(' '))+'</p>');
  }
  closeLists(0);
  return o.join('\n');
}

/* ---------- doc tree ---------- */
const titleOf = p => {
  const m = (D.docs[p]||'').match(/^#\s+(.+)$/m);
  return m ? m[1].trim() : p.split('/').pop().replace(/\.md$/,'');
};
const GROUP = p => {
  const parts = p.split('/');
  if (parts.length === 1) return 'Start here';
  return parts[0].replace(/^\d+-/,'').replace(/^_/,'').replace(/-/g,' ')
                 .replace(/\b\w/g,c=>c.toUpperCase());
};
let tab='docs', cur=null;

function sidebar(){
  const s=$('#side'); s.innerHTML='';
  if(tab==='docs'){
    const groups={};
    Object.keys(D.docs).sort((a,b)=>{
      const d=a.split('/').length-b.split('/').length; return d||a.localeCompare(b);
    }).forEach(p=>{ (groups[GROUP(p)] ||= []).push(p); });
    const order=['Start here']; Object.keys(groups).forEach(g=>{if(g!=='Start here')order.push(g)});
    order.forEach(g=>{
      if(!groups[g]) return;
      const h=document.createElement('div'); h.className='grp'; h.textContent=g; s.appendChild(h);
      groups[g].forEach(p=>{
        const a=document.createElement('a'); a.textContent=titleOf(p);
        a.href='#docs/'+p; if(p===cur) a.className='on'; s.appendChild(a);
      });
    });
  } else if(tab==='data'){
    const h=document.createElement('div'); h.className='grp'; h.textContent='Datasets';
    s.appendChild(h);
    const keys=Object.keys(D.data);
    if(!keys.length){ const e=document.createElement('div');
      e.className='grp'; e.style.textTransform='none'; e.style.fontWeight='400';
      e.textContent='No datasets in this repository.'; s.appendChild(e); return; }
    keys.forEach(k=>{
      const a=document.createElement('a'); a.href='#data/'+k;
      a.textContent=k.replace(/\.psv$/,'');
      const pill=document.createElement('span');
      pill.className='pill'; pill.textContent=D.data[k].total; a.appendChild(pill);
      if(k===cur) a.className='on'; s.appendChild(a);
    });
  } else {
    const i=document.createElement('input'); i.id='search'; i.placeholder='Search all documents…';
    s.appendChild(i); i.addEventListener('input',()=>runSearch(i.value)); i.focus();
  }
}

/* A link is resolved twice: in doc-key space for #docs routing, and in disk
   space for files the navigator does not mount. They differ because a mounted
   tree's key prefix is not its location on disk. */
function joinPath(baseArr, href){
  const base = baseArr.slice();
  href.split('#')[0].split('/').forEach(x=>{
    if(x === '..'){
      // '..' must ACCUMULATE once the base is exhausted or already climbing,
      // or a link like ../../../OtherRepo/x cancels itself and resolves
      // back inside this repository.
      if(base.length && base[base.length-1] !== '..') base.pop();
      else base.push('..');
    }
    else if(x !== '.' && x !== '') base.push(x);
  });
  return base.join('/');
}
function diskDir(p){
  const seg = p.split('/'); seg.pop();
  const pre = seg[0];
  // the root must be SPLIT into segments: '../wiki' is two of them, and a
  // '..' in the link has to pop only 'wiki', leaving the '..' standing.
  if(D.roots && D.roots[pre]) return D.roots[pre].split('/').concat(seg.slice(1));
  return seg;
}

function showDoc(p){
  cur=p; const v=$('#view');
  if(!D.docs[p]){ v.innerHTML='<div class="empty">Not found: '+esc(p)+'</div>'; return; }
  const F=splitFm(D.docs[p]);
  v.innerHTML=fmBar(F.fm)+md(F.body);
  drawDiagrams();
  // Wikilinks route inside the navigator; a heading anchor scrolls after the
  // target page has rendered.
  v.querySelectorAll('a[data-wiki]').forEach(a=>{
    a.addEventListener('click',e=>{
      e.preventDefault();
      pendingAnchor = a.getAttribute('data-anchor') || '';
      const t = a.getAttribute('data-wiki');
      if(t === cur){ scrollToAnchor(); } else { location.hash = '#docs/'+t; }
    });
  });
  v.querySelectorAll('a[data-link]').forEach(a=>{
    const h=a.getAttribute('data-link');
    if(/^https?:|^mailto:/.test(h)){ a.target='_blank'; a.rel='noopener'; return; }
    if(h.startsWith('#')) return;
    const t    = joinPath(p.split('/').slice(0,-1), h);   // doc-key space
    const disk = joinPath(diskDir(p), h);                 // on-disk space
    // Datasets (.psv -- pipe-separated values) live in the Data tab, not
    // the doc tree. A prose link to one would otherwise route to
    // #docs/_data/foo.psv and report "Not found".
    if(/\.psv$/i.test(t)){
      const key=t.split('/').pop();
      if(D.data[key]){
        a.href='#data/'+key;
        a.addEventListener('click',e=>{ e.preventDefault(); location.hash='#data/'+key; });
        return;
      }
    }
    if(!D.docs[t]){
      // Not a mounted document, but usually a real file sitting beside the
      // navigator -- a script, CLAUDE.md, a config. Link to it on disk so
      // local browsing works instead of routing into a doc tree that has no
      // such page.
      a.href=safeUrl(disk); a.className='offdoc'; a.title='opens '+disk+' on disk';
      return;
    }
    a.href='#docs/'+t;
    a.addEventListener('click',e=>{ e.preventDefault(); location.hash='#docs/'+t; });
  });
  if(pendingAnchor){ scrollToAnchor(); }
  else { v.scrollIntoView({block:'start'}); window.scrollTo(0,0); }
  sidebar();
}

let pendingAnchor='';
function scrollToAnchor(){
  const id=slug(pendingAnchor); pendingAnchor='';
  if(!id) return;
  const el=document.getElementById(id);
  if(el) el.scrollIntoView({block:'start'});
  else window.scrollTo(0,0);
}

function showData(k){
  cur=k; const d=D.data[k], v=$('#view');
  if(!d){ v.innerHTML='<div class="empty">No dataset selected.</div>'; return; }
  const note = d.rows.length < d.total
    ? '<p style="color:var(--dim);font-size:13px">Showing the first '+d.rows.length+
      ' of '+d.total+' rows. Read <code>_data/'+esc(k)+'</code> for the full set.</p>' : '';
  v.innerHTML='<h1>'+esc(k)+'</h1>'+note+
    '<div class="tablewrap"><table><thead><tr>'+
    d.cols.map(c=>'<th>'+esc(c)+'</th>').join('')+'</tr></thead><tbody>'+
    d.rows.map(r=>'<tr>'+d.cols.map((_,i)=>'<td>'+esc(r[i]===undefined?'':r[i])+'</td>').join('')+'</tr>').join('')+
    '</tbody></table></div>';
  window.scrollTo(0,0); sidebar();
}

function runSearch(q){
  const v=$('#view');
  if(!q || q.length<2){ v.innerHTML='<div class="empty">Type at least two characters.</div>'; return; }
  const rx=new RegExp(q.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'),'ig');
  let out=[], n=0;
  Object.keys(D.docs).forEach(p=>{
    const lines=D.docs[p].split(/\r?\n/);
    lines.forEach((ln,i)=>{
      if(n>=180) return;
      rx.lastIndex=0;
      if(rx.test(ln)){
        n++;
        out.push('<div class="hit" data-go="'+p+'"><div class="p">'+esc(titleOf(p))+
          ' · line '+(i+1)+'</div><div class="s">'+
          esc(ln.trim()).replace(new RegExp(rx.source,'ig'),m=>'<mark>'+m+'</mark>')+'</div></div>');
      }
    });
  });
  v.innerHTML = out.length
    ? '<h1>'+n+' match'+(n===1?'':'es')+'</h1>'+out.join('')
    : '<div class="empty">Nothing found for “'+esc(q)+'”.</div>';
  v.querySelectorAll('.hit').forEach(h=>h.addEventListener('click',
    ()=>{ location.hash='#docs/'+h.dataset.go; }));
}

function route(){
  const h=decodeURIComponent(location.hash.replace(/^#/,''));
  const [t,...rest]=h.split('/'); const arg=rest.join('/');
  tab = ['docs','data','find'].includes(t) ? t : 'docs';
  document.querySelectorAll('nav button[data-t]').forEach(b=>
    b.classList.toggle('on', b.dataset.t===tab));
  sidebar();
  if(tab==='docs') showDoc(arg || (D.docs['README.md'] ? 'README.md' : Object.keys(D.docs)[0]));
  else if(tab==='data') showData(arg || Object.keys(D.data)[0]);
  else runSearch(arg||'');
}
document.querySelectorAll('nav button[data-t]').forEach(b=>
  b.addEventListener('click',()=>{ location.hash='#'+b.dataset.t; }));
$('#theme').addEventListener('click',()=>{
  const cur=document.documentElement.getAttribute('data-theme');
  const next = cur==='dark' ? 'light' : cur==='light' ? 'dark'
    : (matchMedia('(prefers-color-scheme:dark)').matches?'light':'dark');
  document.documentElement.setAttribute('data-theme',next);
  try{ localStorage.setItem('navtheme',next); }catch(e){}
  if(mermaidReady) drawDiagrams();
});
try{ const t=localStorage.getItem('navtheme');
  if(t) document.documentElement.setAttribute('data-theme',t); }catch(e){}
// Diagrams. Degrades to the raw mermaid source if the CDN is unreachable (offline, air-gapped),
// which stays readable — that is deliberate, not a fallback worth hiding.
let mermaidReady=false;
function darkNow(){
  const t=document.documentElement.getAttribute('data-theme');
  if(t) return t==='dark';
  return matchMedia('(prefers-color-scheme: dark)').matches;
}
function drawDiagrams(){
  const nodes=[...document.querySelectorAll('pre.mermaid')];
  if(!nodes.length || !window.mermaid) return;
  for(const n of nodes){
    if(!n.dataset.src) n.dataset.src=n.textContent;   // keep source for re-theming
    else { n.textContent=n.dataset.src; n.removeAttribute('data-processed'); }
  }
  try{
    mermaid.initialize({startOnLoad:false, securityLevel:'strict',
                        theme: darkNow()?'dark':'default'});
    mermaidReady=true;
    mermaid.run({nodes});
  }catch(e){ /* leave the source visible */ }
}
addEventListener('hashchange',route); route();
</script></body></html>
"""

out = HTML.replace("__TITLE__", TITLE).replace("__PAYLOAD__", payload)
dest = os.path.join(REF, "navigator.html")
io.open(dest, "w", encoding="utf8").write(out)
print(f"{dest}: {len(out):,} bytes  ({len(docs)} docs, {len(data)} datasets)")
