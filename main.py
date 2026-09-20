import os
import json
import time
import urllib.request
import urllib.error
import re
import math
import difflib
import uuid
from dataclasses import dataclass, field
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

mcp_port = str(os.getenv('MCP_HTTP_PORT', '5000'))
print(f"Starting MCP server on port {mcp_port}")
mcp_host = str(os.getenv('MCP_HTTP_HOST', '127.0.0.1'))
print(f"Binding MCP server to host {mcp_host}")

mcp = FastMCP(name="RemoteMCP", port=mcp_port, host=mcp_host, stateless_http=True, json_response=True)

@mcp.custom_route("/health", methods=["GET", "HEAD"])
async def health_check(request: Request):
    return JSONResponse({"status": "healthy", "service": "personal-mcp-server"})

@mcp.custom_route("/", methods=["GET", "HEAD"])
async def root(request: Request):
    return JSONResponse({"status": "healthy", "service": "personal-mcp-server"})

# ---------------------------------------------------------------------------
# SPOTIFY TELEMETRY INTEGRATION
# ---------------------------------------------------------------------------
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "40d8aa08c0e34cc8aebd8249ea3d0bea")
SPOTIFY_REFRESH_TOKEN = os.getenv("SPOTIFY_REFRESH_TOKEN", "AQAMVxm1X_pNm2nBd9Sx-1I_JpA2a2MeqGqwU35rQ80-BKpBMl_vvgnPv7lz8qxfGTyPRzH5MrGbEW1BPuseNSbmq7QsLbAro42Io7jlvuKbpyOGk7nCTP1UiIbAFf7Whuo")

_SPOTIFY_ACCESS_TOKEN: Optional[str] = None
_SPOTIFY_TOKEN_EXPIRES: float = 0.0

def _get_spotify_access_token() -> Optional[str]:
    global _SPOTIFY_ACCESS_TOKEN, _SPOTIFY_TOKEN_EXPIRES
    now = time.time()
    if _SPOTIFY_ACCESS_TOKEN and _SPOTIFY_TOKEN_EXPIRES > now + 60:
        return _SPOTIFY_ACCESS_TOKEN
    
    if not SPOTIFY_REFRESH_TOKEN:
        return None
        
    try:
        import base64
        import ssl
        import urllib.parse
        auth_header = base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
        data = urllib.parse.urlencode({
            "grant_type": "refresh_token",
            "refresh_token": SPOTIFY_REFRESH_TOKEN
        }).encode()
        req = urllib.request.Request("https://accounts.spotify.com/api/token", data=data, headers={
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded"
        })
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(req, context=ctx, timeout=8) as resp:
            tokens = json.loads(resp.read().decode())
            _SPOTIFY_ACCESS_TOKEN = tokens.get("access_token")
            _SPOTIFY_TOKEN_EXPIRES = now + float(tokens.get("expires_in", 3600))
            return _SPOTIFY_ACCESS_TOKEN
    except Exception as e:
        print(f"[Spotify] Error refreshing token: {e}")
        return None

def get_spotify_playback() -> Dict[str, Any]:
    token = _get_spotify_access_token()
    if not token:
        return {"isPlaying": False, "message": "Spotify not configured"}
        
    import ssl
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    try:
        req = urllib.request.Request("https://api.spotify.com/v1/me/player/currently-playing", headers={
            "Authorization": f"Bearer {token}"
        })
        with urllib.request.urlopen(req, context=ctx, timeout=8) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode())
                item = data.get("item")
                if item:
                    album = item.get("album", {})
                    images = album.get("images", [])
                    return {
                        "isPlaying": data.get("is_playing", False),
                        "title": item.get("name"),
                        "artist": ", ".join(a.get("name", "") for a in item.get("artists", [])),
                        "album": album.get("name", ""),
                        "albumImageUrl": images[0].get("url") if images else None,
                        "songUrl": item.get("external_urls", {}).get("spotify"),
                        "progressMs": data.get("progress_ms"),
                        "durationMs": item.get("duration_ms"),
                    }
    except Exception:
        pass
        
    try:
        req = urllib.request.Request("https://api.spotify.com/v1/me/player/recently-played?limit=1", headers={
            "Authorization": f"Bearer {token}"
        })
        with urllib.request.urlopen(req, context=ctx, timeout=8) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode())
                items = data.get("items", [])
                if items:
                    track = items[0].get("track", {})
                    album = track.get("album", {})
                    images = album.get("images", [])
                    return {
                        "isPlaying": False,
                        "recentlyPlayed": True,
                        "title": track.get("name"),
                        "artist": ", ".join(a.get("name", "") for a in track.get("artists", [])),
                        "album": album.get("name", ""),
                        "albumImageUrl": images[0].get("url") if images else None,
                        "songUrl": track.get("external_urls", {}).get("spotify"),
                    }
    except Exception as e:
        print(f"[Spotify] Error fetching recently played: {e}")
        
    return {"isPlaying": False}

@mcp.custom_route("/spotify", methods=["GET", "HEAD", "OPTIONS"])
async def spotify_route(request: Request):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
        "Access-Control-Allow-Headers": "*"
    }
    if request.method == "OPTIONS":
        return JSONResponse({}, headers=headers)
    data = get_spotify_playback()
    return JSONResponse(data, headers=headers)


DATA_DIR = Path("./data")
GITHUB_USERNAME = "ishaankor"
CACHE_TTL = 300

# ---------------------------------------------------------------------------
# CORE DATA STRUCTURES
# ---------------------------------------------------------------------------

@dataclass
class Document:
    """Unified data structure for all indexed knowledge base elements."""
    id: str
    category: str
    source: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)

_REPO_API_CACHE: Optional[List[Dict]] = None
_REPO_API_CACHE_TIME: float = 0.0
_README_CACHE: Dict[str, Tuple[str, float]] = {}

_STATIC_DOCS_BY_CAT: Dict[str, List[Document]] = {"education": [], "experience": [], "biography": [], "projects": [], "certifications": [], "languages": [], "skills": [], "profile": []}
_STATIC_BUILT: bool = False
_BM25_INDEXES: Dict[str, 'PreindexedBM25'] = {}
_DYNAMIC_KB_TIME: float = 0.0

# ---------------------------------------------------------------------------
# WEIGHTED SYNONYMS & EXPANSION MAP
# ---------------------------------------------------------------------------

WEIGHTED_SYNONYM_GROUPS = {
    "major": {"degree": 2, "bs": 2, "study": 1, "education": 1, "specialization": 1},
    "minor": {"study": 1, "education": 1},
    "college": {"university": 2, "school": 2, "ucsd": 2, "uc san diego": 2, "high school": 1},
    "job": {"position": 2, "role": 2, "career": 1, "experience": 1, "work": 1, "internship": 1, "engineer": 1},
    "built": {"project": 2, "created": 2, "developed": 2, "repo": 1, "bot": 1, "website": 1, "game": 1, "clone": 1},
    "certification": {"certificate": 2, "certifications": 2, "certificates": 2, "cert": 2, "certs": 2, "credential": 2, "credentials": 2, "course": 1, "training": 1, "google": 1},
    "skill": {"skills": 3, "technology": 2, "tool": 1, "framework": 1},
    "language": {"languages": 3, "speak": 2, "speaks": 2, "spoken": 2, "fluent": 2, "bilingual": 2, "native": 1},
}

EXPANSION_MAP: Dict[str, List[Tuple[str, int]]] = {}

_temp_map = {}
for base, syns in WEIGHTED_SYNONYM_GROUPS.items():
    if base not in _temp_map:
        _temp_map[base] = {}
    for word, weight in syns.items():
        _temp_map[base][word] = max(_temp_map[base].get(word, 0), weight)
        if word not in _temp_map:
            _temp_map[word] = {}
        _temp_map[word][base] = max(_temp_map[word].get(base, 0), 1)

for word, syns in _temp_map.items():
    EXPANSION_MAP[word] = [(s, w) for s, w in syns.items()]


# ---------------------------------------------------------------------------
# DATA LOADING & RESOLUTION UTILS
# ---------------------------------------------------------------------------

def load_json_file(filename: str) -> Dict:
    filepath = DATA_DIR / filename
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def load_text_file(filename: str) -> str:
    filepath = DATA_DIR / filename
    if filepath.exists():
        return filepath.read_text(encoding='utf-8')
    return ""

def resolve_project_name(query_name: str, repos: List[Dict]) -> Optional[str]:
    """Resolves project queries using an Alias -> Exact -> Fuzzy matching hierarchy."""
    query_lower = query_name.lower()
    keywords_map = load_json_file("project_keywords.json").get("project_keywords", {})
    
    for alias_key, repo_list in keywords_map.items():
        if query_lower == alias_key.lower() and repo_list:
            return repo_list[0]
            
    repo_names = [r.get("name", "") for r in repos]
    
    for name in repo_names:
        if name.lower() == query_lower:
            return name
            
    matches = difflib.get_close_matches(query_name, repo_names, n=1, cutoff=0.4)
    if matches:
        return matches[0]
        
    return None

# ---------------------------------------------------------------------------
# GITHUB DATA MINING & CONCURRENT RETRIEVAL
# ---------------------------------------------------------------------------

def fetch_live_github_repos() -> List[Dict]:
    global _REPO_API_CACHE, _REPO_API_CACHE_TIME
    current_time = time.time()
    
    if _REPO_API_CACHE and (current_time - _REPO_API_CACHE_TIME < CACHE_TTL):
        return _REPO_API_CACHE
        
    url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos?per_page=100&sort=updated"
    req = urllib.request.Request(url, headers={'User-Agent': 'MCP-Portfolio-Server'})
    try:
        with urllib.request.urlopen(req) as response:
            _REPO_API_CACHE = json.loads(response.read().decode())
            _REPO_API_CACHE_TIME = current_time
            return _REPO_API_CACHE
    except urllib.error.URLError as e:
        print(f"GitHub API fetch failed: {e}")
        return _REPO_API_CACHE if _REPO_API_CACHE else []

def _fetch_url(url: str) -> Optional[str]:
    """Helper for threaded README fetching."""
    req = urllib.request.Request(url, headers={'User-Agent': 'MCP-Portfolio-Server'})
    try:
        with urllib.request.urlopen(req) as response:
            return response.read().decode()
    except urllib.error.HTTPError:
        return None

def fetch_live_readme(repo_name: str) -> str:
    """Fetches README data using thread pooling to check branches concurrently, cached via TTL."""
    current_time = time.time()
    if repo_name in _README_CACHE and (current_time - _README_CACHE[repo_name][1] < CACHE_TTL):
        return _README_CACHE[repo_name][0]

    urls = [
        f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{repo_name}/main/README.md",
        f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{repo_name}/master/README.md"
    ]
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {executor.submit(_fetch_url, url): url for url in urls}
        for future in as_completed(futures):
            result = future.result()
            if result:
                _README_CACHE[repo_name] = (result, current_time)
                return result

    _README_CACHE[repo_name] = ("", current_time)
    return ""

def _chunk_readme_text(readme_text: str, repo_name: str) -> List[Document]:
    """Partitions markdown files cleanly using regex-based hierarchy preservation."""
    chunks = []
    current_section = "Overview"
    current_content = []
    
    for line in readme_text.split("\n"):
        if re.match(r"^#{1,6}\s", line):
            if current_content:
                chunks.append(Document(
                    id=f"{repo_name}_{uuid.uuid4().hex[:6]}",
                    category="projects",
                    source=f"README: {repo_name} - {current_section}",
                    content="\n".join(current_content).strip(),
                    metadata={"repository": repo_name, "section": current_section}
                ))
            current_section = re.sub(r"^#{1,6}\s", "", line).strip()
            current_content = [line]
        else:
            current_content.append(line)
            
    if current_content:
        chunks.append(Document(
            id=f"{repo_name}_{uuid.uuid4().hex[:6]}",
            category="projects",
            source=f"README: {repo_name} - {current_section}",
            content="\n".join(current_content).strip(),
            metadata={"repository": repo_name, "section": current_section}
        ))
    return chunks

# ---------------------------------------------------------------------------
# OPTIMIZED NATIVE BM25 ENGINE
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> List[str]:
    """Tokenizes text while splitting camelCase words (e.g., DataCamp -> data camp)."""
    camel_split = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', str(text))
    return re.findall(r'\w+', camel_split.lower())

class PreindexedBM25:
    """Highly efficient BM25 ranking engine featuring O(1) Counter and Phrase Boosting."""
    def __init__(self, corpus: List[Document]):
        self.corpus = corpus
        self.doc_count = len(corpus)
        self.tokenized_docs = [_tokenize(doc.content) for doc in corpus]
        self.doc_lengths = [len(doc) for doc in self.tokenized_docs]
        self.avg_doc_len = sum(self.doc_lengths) / self.doc_count if self.doc_count > 0 else 1.0
        
        self.doc_counters = [Counter(doc) for doc in self.tokenized_docs]
        self.df: Dict[str, int] = {}
        for doc in self.tokenized_docs:
            for token in set(doc):
                self.df[token] = self.df.get(token, 0) + 1
                
        self.k1 = 1.5
        self.b = 0.75

    def score(self, query_tokens: List[str], raw_query_string: str = "") -> List[Tuple[Document, float]]:
        scores = []
        
        for index, counts in enumerate(self.doc_counters):
            score = 0.0
            doc_len = self.doc_lengths[index]
            
            for token in query_tokens:
                tf = counts.get(token, 0)
                if tf == 0:
                    continue
                df_val = self.df.get(token, 0)
                idf = math.log((self.doc_count - df_val + 0.5) / (df_val + 0.5) + 1.0)
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * (doc_len / self.avg_doc_len))
                score += idf * (numerator / denominator)
            
            if raw_query_string and len(raw_query_string.split()) > 1 and raw_query_string in self.corpus[index].content.lower():
                score += 3.0
                
            scores.append((self.corpus[index], score))
        return scores

# ---------------------------------------------------------------------------
# INCREMENTAL KNOWLEDGE BASE
# ---------------------------------------------------------------------------

def _build_static_kb():
    """Compiles local static sources once during system lifetime."""
    global _STATIC_BUILT, _BM25_INDEXES
    
    linkedin = load_json_file("linkedin_data.json")
    contact = linkedin.get("contact_info", {})
    emails = ", ".join(contact.get("emails", []))
    
    content_str = (
        f"Based / Profile Location: {linkedin.get('location', '')}. "
        f"Followers / Follower count: {linkedin.get('follower_count', 0)}. "
        f"Connections / Connection count: {linkedin.get('connections_count', 0)}. "
        f"Contact email: {emails}."
        f"Website / Websites: {', '.join(linkedin.get('websites', []))}."
    )
    
    _STATIC_DOCS_BY_CAT["profile"].append(Document(
        id=uuid.uuid4().hex, 
        category="profile", 
        source="LinkedIn",
        content=content_str
    ))

    for edu in linkedin.get("education", []):
        priority = 10 if "UC San Diego" in edu.get('school', '') or "California" in edu.get('school', '') else 5
        
        _STATIC_DOCS_BY_CAT["education"].append(Document(
            id=uuid.uuid4().hex, 
            category="education", 
            source="LinkedIn",
            content=f"School: {edu.get('school')}. Degree: {edu.get('degree')}. Timeline: {edu.get('start')} - {edu.get('end')}.",
            metadata={"priority": priority}
        ))
    for job in linkedin.get("work_experience", []):
        _STATIC_DOCS_BY_CAT["experience"].append(Document(
            id=uuid.uuid4().hex, category="experience", source="LinkedIn",
            content=f"Company: {job.get('company')}. Position: {job.get('position')}. Description: {job.get('description')}."
        ))
    for cert in linkedin.get("certifications", []):
        _STATIC_DOCS_BY_CAT["certifications"].append(Document(
            id=uuid.uuid4().hex, 
            category="certifications", 
            source="LinkedIn",
            content=f"Certification / Credential: {cert.get('name', '')} issued by {cert.get('organization', '')}.",
            metadata={"url": cert.get("url", "")}
        ))
    
    for lang in linkedin.get("languages", []):
        if isinstance(lang, dict):
            lang_name = lang.get('name', '')
            prof = lang.get('proficiency', '')
        else:
            lang_name = str(lang)
            prof = "Spoken"
            
        _STATIC_DOCS_BY_CAT["languages"].append(Document(
            id=uuid.uuid4().hex, 
            category="languages", 
            source="LinkedIn",
            content=(
                f"Spoken language: {lang_name}. "
                f"Language spoken by Ishaan Koradia. "
                f"Speaks {lang_name}. "
                f"Proficiency: {prof}."
            ),
        ))
    
    for skill in linkedin.get("skills", []):
        _STATIC_DOCS_BY_CAT["skills"].append(Document(
            id=uuid.uuid4().hex, 
            category="skills", 
            source="LinkedIn",
            content=f"Skill / Skills: {skill.get('name', '')}. Endorsement(s): {skill.get('endorsement_count', '')}.",
        ))
        
    _STATIC_DOCS_BY_CAT["biography"].append(Document(
        id=uuid.uuid4().hex, category="biography", source="about_me.txt", content=load_text_file("about_me.txt")
    ))
    _BM25_INDEXES["profile"] = PreindexedBM25(_STATIC_DOCS_BY_CAT["profile"])
    _BM25_INDEXES["education"] = PreindexedBM25(_STATIC_DOCS_BY_CAT["education"])
    _BM25_INDEXES["experience"] = PreindexedBM25(_STATIC_DOCS_BY_CAT["experience"])
    _BM25_INDEXES["certifications"] = PreindexedBM25(_STATIC_DOCS_BY_CAT["certifications"])
    _BM25_INDEXES["biography"] = PreindexedBM25(_STATIC_DOCS_BY_CAT["biography"])
    _BM25_INDEXES["languages"] = PreindexedBM25(_STATIC_DOCS_BY_CAT["languages"])
    _BM25_INDEXES["skills"] = PreindexedBM25(_STATIC_DOCS_BY_CAT["skills"])
    _STATIC_BUILT = True

def get_indexed_kb() -> Dict[str, PreindexedBM25]:
    """Retrieves cached indexes, incrementally merging dynamic GitHub data via TTL."""
    global _DYNAMIC_KB_TIME, _BM25_INDEXES
    if not _STATIC_BUILT:
        _build_static_kb()

    current_time = time.time()
    if "projects" not in _BM25_INDEXES or (current_time - _DYNAMIC_KB_TIME > CACHE_TTL):
        dynamic_projects = []
        for repo in fetch_live_github_repos():
            dynamic_projects.append(Document(
                id=repo.get("name", ""),
                category="projects",
                source=f"GitHub API - {repo.get('name')}",
                content=f"Repository: {repo.get('name')}. Language: {repo.get('language')}. Overview: {repo.get('description')}.",
                metadata={"url": repo.get("html_url"), "stars": repo.get("stargazers_count")}
            ))
            
        combined_projects = _STATIC_DOCS_BY_CAT["projects"] + dynamic_projects
        _BM25_INDEXES["projects"] = PreindexedBM25(combined_projects)
        _DYNAMIC_KB_TIME = current_time

    return _BM25_INDEXES

# ---------------------------------------------------------------------------
# CORE EXPOSED MCP SYSTEM TOOLS
# ---------------------------------------------------------------------------

@mcp.tool()
def search_ishaan(query: str) -> Dict[str, Any]:
    """Unified retrieval pipeline with Intent-Based Pre-Routing."""
    indexes = get_indexed_kb()
    DOMAIN_STOP_WORDS = {"ishaan", "koradia", "he", "his", "him", "tell", "me", "about", "what", "are", "does", "have", "has", "is", "any"}
    
    raw_tokens = _tokenize(query)
    query_tokens = [t for t in raw_tokens if t not in DOMAIN_STOP_WORDS]
    
    if not query_tokens:
        query_tokens = raw_tokens
        
    query_lower = query.lower()
    query_token_set = set(query_tokens)
    
    CATEGORY_KEYWORDS = {
        "languages": {"language", "languages", "speak", "speaks", "spoken", "fluent", "bilingual", "native"},
        "certifications": {"certificate", "certification", "certifications", "certificates", "credential", "credentials", "course", "training", "cert", "certs"},
        "skills": {"skill", "skills", "technology", "technologies", "framework", "frameworks", "tool", "tools", "programming", "stack", "code", "coding", "program", "language", "languages"},
        "education": {"education", "university", "college", "school", "degree", "major", "minor", "ucsd", "study"},
        "experience": {"experience", "job", "position", "role", "work", "internship", "career", "company"},
        "projects": {"project", "projects", "built", "repo", "github", "website", "app", "bot", "game"},
        "profile": {"location", "email", "contact", "follower", "followers", "connections", "connect"}
    }
    
    target_categories = set()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if query_token_set & keywords:
            target_categories.add(category)
            
    if not target_categories:
        target_categories = set(indexes.keys())
        
    target_categories.add("biography")

    expanded_list = []
    for token in query_tokens:
        expanded_list.extend([token] * 3)
        for synonym, weight in EXPANSION_MAP.get(token, []):
            expanded_list.extend([synonym] * weight)

    all_scored_docs = []
    
    # 🎯 Only search the pre-routed target categories
    for cat in target_categories:
        if cat in indexes:
            ranker = indexes[cat]
            scored_docs = ranker.score(expanded_list, raw_query_string=query_lower)
            
            # Apply Metadata Priority Boost
            boosted_docs = []
            for doc, score in scored_docs:
                priority = doc.metadata.get("priority", 1)
                final_score = score * (1 + (priority / 10))
                boosted_docs.append((doc, final_score))
                
            all_scored_docs.extend(boosted_docs)

    all_scored_docs.sort(key=lambda x: x[1], reverse=True)

    valid_matches = [res for res in all_scored_docs if res[1] > 0.0]
    top_matches = []
    
    if valid_matches:
        MINIMUM_CONFIDENCE_FLOOR = 0.5 
        top_matches = [res for res in valid_matches if res[1] >= MINIMUM_CONFIDENCE_FLOOR][:15]

    formatted_citations = []
    for doc, score in top_matches:
        formatted_citations.append({
            "content": doc.content,
            "source": doc.source,
            "category": doc.category,
            "confidence": round(score, 2),
            "metadata": doc.metadata
        })
        
    return {"insights": formatted_citations if formatted_citations else [{"message": "No direct match found."}]}

@mcp.tool()
def list_projects() -> Dict[str, Any]:
    """Exposes an exhaustive structured index of all GitHub repositories and metadata."""
    repos = fetch_live_github_repos()
    catalog = []
    
    for repo in repos:
        catalog.append({
            "name": repo.get("name"),
            "description": repo.get("description", "No description available."),
            "primary_language": repo.get("language", "Not specified"),
            "github_url": repo.get("html_url"),
            "topics": repo.get("topics", []),
            "metrics": {
                "stars": repo.get("stargazers_count", 0),
                "open_issues": repo.get("open_issues_count", 0),
            },
            "timeline": {
                "last_updated": repo.get("updated_at")
            }
        })
    return {"portfolio_repositories": catalog}

@mcp.tool()
def get_project_details(project_name: str) -> Dict[str, Any]:
    """Unpacks technical architecture by retrieving and chunking specific READMEs."""
    repos = fetch_live_github_repos()
    target_name = resolve_project_name(project_name, repos)
            
    if not target_name:
        return {"error": f"Repository '{project_name}' could not be located via fuzzy index lookup."}
        
    repo_meta = next(r for r in repos if r.get("name") == target_name)
    raw_readme = fetch_live_readme(target_name)
    
    readme_chunks = _chunk_readme_text(raw_readme, target_name) if raw_readme else []
    
    formatted_sections = []
    for chunk in readme_chunks[:4]:
        formatted_sections.append({
            "section": chunk.metadata.get("section"),
            "content": chunk.content
        })
    
    return {
        "resolved_name": target_name,
        "description": repo_meta.get("description", ""),
        "github_url": repo_meta.get("html_url"),
        "primary_language": repo_meta.get("language"),
        "topics": repo_meta.get("topics", []),
        "segmented_readme_documentation": formatted_sections
    }

@mcp.tool()
def get_current_music() -> str:
    """Check what music Ishaan is currently listening to (or recently played) on Spotify."""
    info = get_spotify_playback()
    if info.get("isPlaying"):
        return f"Ishaan is currently listening to '{info.get('title')}' by {info.get('artist')} on Spotify. Link: {info.get('songUrl')}"
    elif info.get("title"):
        return f"Ishaan recently listened to '{info.get('title')}' by {info.get('artist')} on Spotify. Link: {info.get('songUrl')}"
    return "No music playback currently active on Spotify."

app = mcp.streamable_http_app()
    
if __name__ == "__main__":
    mcp.run(transport='streamable-http')