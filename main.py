from mcp.server.fastmcp import FastMCP
import os
import requests
# import random
from thefuzz import fuzz
import json

def load_linkedin_data():
    """Load LinkedIn data from static JSON file"""
    try:
        linkedin_data_path = os.path.join(os.path.dirname(__file__), "linkedin_data.json")
        with open(linkedin_data_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading LinkedIn data: {e}")
        return None

LINKEDIN_DATA = load_linkedin_data()

mcp_port = str(os.getenv('MCP_HTTP_PORT', '5000'))
print(f"Starting MCP server on port {mcp_port}")
mcp_host = str(os.getenv('MCP_HTTP_HOST', '127.0.0.1'))
print(f"Binding MCP server to host {mcp_host}")

print("Using static LinkedIn data from linkedin_data.json")

mcp = FastMCP(name="RemoteMCP", port=mcp_port, host=mcp_host, stateless_http=True, json_response=True)

@mcp.resource(uri="status://health", name="Health Check", description="Returns the health status of the server.")
def health_check_resource():
    return {"status": "ok"}

@mcp.resource(uri="resource://about_me", name="Information for Ishaan Koradia", description="Ishaan Koradia's skills, contact info, interests, and fun facts")
def about_me_resource():
    path = os.path.join(os.path.dirname(__file__), "about_me.txt")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

@mcp.resource(uri="resource://personal_website", name="Personal Website Info", description="Provides details about Ishaan Koradia's personal website, including tech stack and GitHub project.")
def personal_website_resource():
    path = os.path.join(os.path.dirname(__file__), "personal_website.txt")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

# @mcp.resource(uri="resource://read_projects", name="Current Projects of Ishaan Koradia", description="Lists current projects Ishaan Koradia is working on, meaning 'Transformi' and 'Daily Motivation'.")
# def read_projects_resource():
#     path = os.path.join(os.path.dirname(__file__), "read_projects.txt")
#     with open(path, "r", encoding="utf-8") as f:
#         return f.read()
    
@mcp.tool(name="add", description="Adds two numbers")
def add_tool(a: int, b: int) -> int:
    return a + b

@mcp.tool(
    name="get_about_ishaan_text",
    description="Returns general information about Ishaan Koradia (skills, contact info, interests, fun facts). Use ONLY for questions about Ishaan himself, NOT about his projects or code.",
    annotations={
        "resource_name": "Optional. Defaults to 'resource://about_me'"
    }
)
async def read_resources_tool(resource_name="resource://about_me") -> str:
    resource_contents = await mcp.read_resource(resource_name)
    if resource_contents and isinstance(resource_contents, list):
        return resource_contents[0].content
    return "Resource content not found or invalid."

# @mcp.tool(name="get_transformi_and_daily_motivation_projects",
#     description="Returns information like their description, technologies, impact, strengths, and opportunities for growth about Ishaan Koradia's current projects which are Transformi (Discord bot for data transformations) and Daily Motivation (Twitter bot). Use this tool when asked about Transformi and Daily Motivation.",
#     annotations={
#             "resource_name": "Optional. Defaults to 'resource://read_projects'"
#     }
# )
# async def read_projects_tool(resource_name="resource://read_projects") -> str:
#     resource_contents = await mcp.read_resource(resource_name)
#     if resource_contents and isinstance(resource_contents, list):
#         print(f"Resource content found: {resource_contents[0].content[:100]}...")
#         return resource_contents[0].content
#     return "Resource content not found or invalid."

@mcp.tool(
    name="get_ishaan_linkedin_basic_profile",
    description="Get Ishaan Koradia's basic LinkedIn profile information (name, headline, location, industry, summary). Fast and lightweight using static data."
)
def get_linkedin_profile_tool() -> str:
    """
    Get basic LinkedIn profile data for Ishaan Koradia using static data
    """
    if not LINKEDIN_DATA:
        return json.dumps({
            "error": "LinkedIn data not available",
            "status": "error"
        }, indent=2)
    
    profile_data = {
        "name": f"{LINKEDIN_DATA.get('first_name', '')} {LINKEDIN_DATA.get('last_name', '')}".strip(),
        "linkedin_url": f"https://www.linkedin.com/in/{LINKEDIN_DATA.get('public_identifier', 'ishaankoradia')}",
        "profile_username": LINKEDIN_DATA.get("public_identifier", "ishaankoradia"),
        "headline": LINKEDIN_DATA.get("headline", ""),
        "location": LINKEDIN_DATA.get("location", ""),
        "connections_count": LINKEDIN_DATA.get("connections_count", 0),
        "follower_count": LINKEDIN_DATA.get("follower_count", 0),
        "is_premium": LINKEDIN_DATA.get("is_premium", False),
        "is_creator": LINKEDIN_DATA.get("is_creator", False),
        "contact_info": LINKEDIN_DATA.get("contact_info", {}),
        "languages": LINKEDIN_DATA.get("languages", []),
        "extraction_method": "static_linkedin_data",
        "status": "success",
        "data_source": "linkedin_data.json"
    }
    
    return json.dumps(profile_data, indent=2)

@mcp.tool(
    name="get_ishaan_linkedin_experience",
    description="Get work experience history for Ishaan Koradia from LinkedIn using static data"
)
def get_linkedin_experience_tool() -> str:
    """
    Get LinkedIn work experience data for Ishaan Koradia using static data
    """
    if not LINKEDIN_DATA:
        return json.dumps({
            "error": "LinkedIn data not available",
            "status": "error"
        }, indent=2)
    
    experience_profile = {
        "name": f"{LINKEDIN_DATA.get('first_name', '')} {LINKEDIN_DATA.get('last_name', '')}".strip(),
        "linkedin_url": f"https://www.linkedin.com/in/{LINKEDIN_DATA.get('public_identifier', 'ishaankoradia')}",
        "profile_username": LINKEDIN_DATA.get("public_identifier", "ishaankoradia"),
        "extraction_method": "static_linkedin_data",
        "status": "success",
        "experience": []
    }
    
    work_experience = LINKEDIN_DATA.get("work_experience", [])
    for exp in work_experience:
        exp_data = {
            "company": exp.get("company", ""),
            "position": exp.get("position", ""),
            "location": exp.get("location", ""),
            "start_date": exp.get("start", ""),
            "end_date": exp.get("end", ""),
            "skills": exp.get("skills", []),
            "company_id": exp.get("company_id", "")
        }
        experience_profile["experience"].append(exp_data)
    
    experience_profile["summary_stats"] = {
        "total_experiences": len(experience_profile["experience"]),
        "companies": list(set([exp.get("company", "") for exp in work_experience if exp.get("company")])),
        "total_skills": len(set([skill for exp in work_experience for skill in exp.get("skills", [])]))
    }
    
    return json.dumps(experience_profile, indent=2)

@mcp.tool(
    name="get_ishaan_linkedin_education",
    description="Get education history for Ishaan Koradia from LinkedIn using static data"
)
def get_linkedin_education_tool() -> str:
    """
    Get LinkedIn education data for Ishaan Koradia using static data
    """
    if not LINKEDIN_DATA:
        return json.dumps({
            "error": "LinkedIn data not available",
            "status": "error"
        }, indent=2)
    
    education_profile = {
        "name": f"{LINKEDIN_DATA.get('first_name', '')} {LINKEDIN_DATA.get('last_name', '')}".strip(),
        "linkedin_url": f"https://www.linkedin.com/in/{LINKEDIN_DATA.get('public_identifier', 'ishaankoradia')}",
        "profile_username": LINKEDIN_DATA.get("public_identifier", "ishaankoradia"),
        "extraction_method": "static_linkedin_data",
        "status": "success",
        "education": []
    }
    
    education_data = LINKEDIN_DATA.get("education", [])
    for edu in education_data:
        edu_data = {
            "school": edu.get("school", ""),
            "degree": edu.get("degree", ""),
            "start_date": edu.get("start", ""),
            "end_date": edu.get("end", "")
        }
        education_profile["education"].append(edu_data)
    
    education_profile["summary_stats"] = {
        "total_education": len(education_profile["education"]),
        "schools": list(set([edu.get("school", "") for edu in education_data if edu.get("school")])),
        "degrees": [edu.get("degree", "") for edu in education_data if edu.get("degree")]
    }
    
    return json.dumps(education_profile, indent=2)

@mcp.tool(
    name="get_ishaan_linkedin_skills",
    description="Get skills and endorsements for Ishaan Koradia from LinkedIn using static data"
)
def get_linkedin_skills_tool() -> str:
    """
    Get LinkedIn skills data for Ishaan Koradia using static data
    """
    if not LINKEDIN_DATA:
        return json.dumps({
            "error": "LinkedIn data not available",
            "status": "error"
        }, indent=2)
    
    skills_profile = {
        "name": f"{LINKEDIN_DATA.get('first_name', '')} {LINKEDIN_DATA.get('last_name', '')}".strip(),
        "linkedin_url": f"https://www.linkedin.com/in/{LINKEDIN_DATA.get('public_identifier', 'ishaankoradia')}",
        "profile_username": LINKEDIN_DATA.get("public_identifier", "ishaankoradia"),
        "extraction_method": "static_linkedin_data",
        "status": "success",
        "skills": []
    }
    
    skills_data = LINKEDIN_DATA.get("skills", [])
    for skill in skills_data:
        skill_data = {
            "name": skill.get("name", ""),
            "endorsement_count": skill.get("endorsement_count", 0),
            "endorsed": skill.get("endorsed", False),
            "insights": skill.get("insights", [])
        }
        skills_profile["skills"].append(skill_data)
    
    skills_profile["summary_stats"] = {
        "total_skills": len(skills_profile["skills"]),
        "total_endorsements": sum(skill.get("endorsement_count", 0) for skill in skills_data),
        "top_skills": [skill.get("name", "") for skill in sorted(skills_data, key=lambda x: x.get("endorsement_count", 0), reverse=True)[:5]]
    }
    
    return json.dumps(skills_profile, indent=2)

@mcp.tool(
    name="get_ishaan_linkedin_connections",
    description="Get connections preview for Ishaan Koradia from LinkedIn using static data"
)
def get_linkedin_connections_tool() -> str:
    """
    Get LinkedIn connections data for Ishaan Koradia using static data
    """
    if not LINKEDIN_DATA:
        return json.dumps({
            "error": "LinkedIn data not available",
            "status": "error"
        }, indent=2)
    
    connections_profile = {
        "name": f"{LINKEDIN_DATA.get('first_name', '')} {LINKEDIN_DATA.get('last_name', '')}".strip(),
        "linkedin_url": f"https://www.linkedin.com/in/{LINKEDIN_DATA.get('public_identifier', 'ishaankoradia')}",
        "profile_username": LINKEDIN_DATA.get("public_identifier", "ishaankoradia"),
        "extraction_method": "static_linkedin_data",
        "status": "success",
        "connections_count": LINKEDIN_DATA.get("connections_count", 0),
        "follower_count": LINKEDIN_DATA.get("follower_count", 0),
        "connection_summary": {
            "total_connections": LINKEDIN_DATA.get("connections_count", 0),
            "followers": LINKEDIN_DATA.get("follower_count", 0),
            "note": "Static data from LinkedIn profile export"
        }
    }
    
    return json.dumps(connections_profile, indent=2)

@mcp.tool(
    name="get_ishaan_linkedin_certifications",
    description="Get certifications and licenses for Ishaan Koradia from LinkedIn using static data"
)
def get_linkedin_certifications_tool() -> str:
    """
    Get LinkedIn certifications data for Ishaan Koradia using static data
    """
    if not LINKEDIN_DATA:
        return json.dumps({
            "error": "LinkedIn data not available",
            "status": "error"
        }, indent=2)
    
    certifications_profile = {
        "name": f"{LINKEDIN_DATA.get('first_name', '')} {LINKEDIN_DATA.get('last_name', '')}".strip(),
        "linkedin_url": f"https://www.linkedin.com/in/{LINKEDIN_DATA.get('public_identifier', 'ishaankoradia')}",
        "profile_username": LINKEDIN_DATA.get("public_identifier", "ishaankoradia"),
        "extraction_method": "static_linkedin_data",
        "status": "success",
        "certifications": []
    }
    
    certifications_data = LINKEDIN_DATA.get("certifications", [])
    for cert in certifications_data:
        cert_data = {
            "name": cert.get("name", ""),
            "organization": cert.get("organization", ""),
            "url": cert.get("url", ""),
            "credential_id": cert.get("credential_id", "")
        }
        certifications_profile["certifications"].append(cert_data)
    
    certifications_profile["summary_stats"] = {
        "total_certifications": len(certifications_profile["certifications"]),
        "organizations": list(set([cert.get("organization", "") for cert in certifications_data if cert.get("organization")])),
        "has_urls": len([cert for cert in certifications_data if cert.get("url")]),
        "google_certifications": len([cert for cert in certifications_data if "Google" in cert.get("organization", "")])
    }
    
    return json.dumps(certifications_profile, indent=2)

@mcp.tool(
    name="get_ishaan_linkedin_activity",
    description="Get recent activity and posts for Ishaan Koradia from LinkedIn using static data"
)
def get_linkedin_activity_tool() -> str:
    """
    Get LinkedIn activity data for Ishaan Koradia using static data (limited)
    """
    if not LINKEDIN_DATA:
        return json.dumps({
            "error": "LinkedIn data not available",
            "status": "error"
        }, indent=2)
    
    activity_profile = {
        "name": f"{LINKEDIN_DATA.get('first_name', '')} {LINKEDIN_DATA.get('last_name', '')}".strip(),
        "linkedin_url": f"https://www.linkedin.com/in/{LINKEDIN_DATA.get('public_identifier', 'ishaankoradia')}",
        "profile_username": LINKEDIN_DATA.get("public_identifier", "ishaankoradia"),
        "extraction_method": "static_linkedin_data",
        "status": "limited",
        "activity_note": "LinkedIn activity data is not included in static export",
        "available_data": {
            "hashtags": LINKEDIN_DATA.get("hashtags", []),
            "volunteering_experience": LINKEDIN_DATA.get("volunteering_experience", []),
            "recommendations_received": len(LINKEDIN_DATA.get("recommendations", {}).get("received", [])),
            "recommendations_given": len(LINKEDIN_DATA.get("recommendations", {}).get("given", [])),
            "projects": LINKEDIN_DATA.get("projects", [])
        },
        "summary_stats": {
            "hashtags_count": len(LINKEDIN_DATA.get("hashtags", [])),
            "volunteering_experiences": len(LINKEDIN_DATA.get("volunteering_experience", [])),
            "total_recommendations": len(LINKEDIN_DATA.get("recommendations", {}).get("received", []) + LINKEDIN_DATA.get("recommendations", {}).get("given", []))
        }
    }
    
    return json.dumps(activity_profile, indent=2)

def fetch_github_projects():
    url = "https://api.github.com/users/ishaankor/repos"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        projects = response.json()
        return [
            {
                "name": project["name"],
                "description": project.get("description", "No description provided"),
                "url": project["html_url"],
                "language": project.get("language", "Not specified"),
                "stars": project.get("stargazers_count", 0),
                "forks": project.get("forks_count", 0),
                "created_at": project.get("created_at", "Unknown"),
                "updated_at": project.get("updated_at", "Unknown"),
                "topics": project.get("topics", []),
                "homepage": project.get("homepage", None)
            }
            for project in projects
        ]
    return {"error": f"Failed to fetch projects: {response.status_code}"}

@mcp.tool(
    name="list_all_github_projects",
    description="Lists ALL public GitHub repositories owned by Ishaan Koradia. Use ONLY if the user asks to see all projects that are NOT 'Transformi' nor 'Daily Motivation' nor 'NotesTaker'. Do NOT use for project details or structure—use get_github_project_details or list_project_files instead.",
)
def list_github_projects_tool():
    projects = fetch_github_projects()
    return json.dumps(projects, indent=2)

def fuzzy_match_project(query, projects):
    query = query.lower()
    scored = [
        (project, max(
            fuzz.partial_ratio(query, project["name"].lower()),
            fuzz.partial_ratio(query, (project.get("description") or "").lower())
        ))
        for project in projects
    ]
    scored.sort(key=lambda x: x[1], reverse=True)
    matches = [project for project, score in scored if score > 60]
    if matches:
        best = matches[0]
        return {
            "name": best["name"],
            "description": best.get("description", "No description provided"),
            "url": best["html_url"],
            "language": best.get("language", "Not specified"),
            "stars": best.get("stargazers_count", 0),
            "forks": best.get("forks_count", 0),
            "created_at": best.get("created_at", "Unknown"),
            "updated_at": best.get("updated_at", "Unknown"),
            "topics": best.get("topics", []),
            "homepage": best.get("homepage", None)
        }
    matches = [project for project in projects if query in project["name"].lower() or query in (project.get("description") or "").lower()]
    if matches:
        best = matches[0]
        return {
            "name": best["name"],
            "description": best.get("description", "No description provided"),
            "url": best["html_url"],
            "language": best.get("language", "Not specified"),
            "stars": best.get("stargazers_count", 0),
            "forks": best.get("forks_count", 0),
            "created_at": best.get("created_at", "Unknown"),
            "updated_at": best.get("updated_at", "Unknown"),
            "topics": best.get("topics", []),
            "homepage": best.get("homepage", None)
        }
    return {"error": f"No matching project found for '{query}'. Please clarify or check the name."}

def fetch_specific_github_project(project_name):
    url = f"https://api.github.com/repos/ishaankor/{project_name}"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        project = response.json()
        return {
            "name": project["name"],
            "description": project.get("description", "No description provided"),
            "url": project["html_url"],
            "language": project.get("language", "Not specified"),
            "stars": project.get("stargazers_count", 0),
            "forks": project.get("forks_count", 0),
            "created_at": project.get("created_at", "Unknown"),
            "updated_at": project.get("updated_at", "Unknown"),
            "topics": project.get("topics", []),
            "homepage": project.get("homepage", None)
        }
    else:
        projects_url = "https://api.github.com/users/ishaankor/repos"
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        projects_resp = requests.get(projects_url, headers=headers)
        if projects_resp.status_code == 200:
            projects = projects_resp.json()
            return fuzzy_match_project(project_name, projects)
        return {"error": f"Failed to fetch projects for fuzzy search: {projects_resp.status_code}"}

@mcp.tool(
    name="get_github_project_details",
    description="Returns detailed information about ONE project (name, description, URL, language, stars, forks, etc.) that's NOT 'Transformi', 'Daily Motivation', or 'NotesTaker'. Use for questions about a specific project, even with unknown names. Do NOT use for file structure or 'how he built it' queries —- use list_project_files or explain_project_build instead.",
    annotations={
        "project_name": "The GitHub project name, or partial/fuzzy name. E.g., 'personal website', 'mobile game', 'resume site'."
    }
)

def get_specific_github_project_tool(project_name: str):
    if not project_name:
        return {"error": "project name must be provided."}
    return fetch_specific_github_project(project_name)


@mcp.tool(name="get_personal_website_project", description="Get details about Ishaan Koradia's personal website project, tech stack, and how he developed this project.")
def get_personal_website_project_tool():
    return personal_website_resource()

def fetch_personal_website_project_details():
    project_name = "my-personal-website"
    url = f"https://api.github.com/repos/ishaankor/{project_name}"
    readme_url = f"https://api.github.com/repos/ishaankor/{project_name}/readme"

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    project_resp = requests.get(url, headers=headers)
    readme_resp = requests.get(readme_url, headers=headers)
    details = {}
    if project_resp.status_code == 200:
        project = project_resp.json()
        details = {
            "name": project["name"],
            "description": project.get("description", "No description provided"),
            "url": project["html_url"],
            "language": project.get("language", "Not specified"),
            "stars": project.get("stargazers_count", 0),
            "forks": project.get("forks_count", 0),
            "created_at": project.get("created_at", "Unknown"),
            "updated_at": project.get("updated_at", "Unknown"),
            "topics": project.get("topics", []),
            "homepage": project.get("homepage", None)
        }
    if readme_resp.status_code == 200:
        details["readme"] = readme_resp.text
    else:
        details["readme"] = "README not found."
    return json.dumps(details, indent=2)

@mcp.tool(
    name="analyze_personal_website_project",
    description=(
        "Fetches the metadata and README of Ishaan Koradia's personal website project. "
        "Use when the user asks about the website’s structure, purpose, tech stack, or how it was built."
    )
)
def analyze_personal_website_project_tool():
    return fetch_personal_website_project_details()

@mcp.tool(
    name="list_project_files",
    description="Lists files and folders inside a GitHub project. Use ONLY for questions about project structure, file organization, or to see the contents of a repo. Do NOT use for general project info or build explanations—use get_github_project_details or explain_project_build instead.",
    annotations={
        "project_name": "Name of the GitHub repo (e.g., 'personal-website')",
        "path": "Optional sub-path to list contents inside a folder (e.g., 'src/')"
    }
)
def list_project_files(project_name: str, path: str = ""):
    if not project_name:
        return {"error": "project name must be provided."}
    url = f"https://api.github.com/repos/ishaankor/{project_name}/contents/{path}" if path else f"https://api.github.com/repos/ishaankor/{project_name}/contents/"

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        items = response.json()
        if isinstance(items, dict):
            return {
                "name": items.get("name"),
                "type": items.get("type"),
                "download_url": items.get("download_url"),
                "size": items.get("size"),
                "content": items.get("content", "")
            }
        else:
            return [
                {
                    "name": item.get("name"),
                    "type": item.get("type"),
                    "download_url": item.get("download_url"),
                    "size": item.get("size")
                }
                for item in items
            ]
    projects_url = "https://api.github.com/users/ishaankor/repos"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    projects_resp = requests.get(projects_url, headers=headers)
    if projects_resp.status_code == 200:
        projects = projects_resp.json()
        match = fuzzy_match_project(project_name, projects)
        if "name" in match:
            url = f"https://api.github.com/repos/ishaankor/{match['name']}/contents/{path}" if path else f"https://api.github.com/repos/ishaankor/{match['name']}/contents/"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                items = response.json()
                if isinstance(items, dict):
                    return {
                        "name": items.get("name"),
                        "type": items.get("type"),
                        "download_url": items.get("download_url"),
                        "size": items.get("size"),
                        "content": items.get("content", "")
                    }
                else:
                    return [
                        {
                            "name": item.get("name"),
                            "type": item.get("type"),
                            "download_url": item.get("download_url"),
                            "size": item.get("size")
                        }
                        for item in items
                    ]
        return match
    return {"error": f"Failed to fetch contents: {response.status_code}"}

@mcp.tool(
    name="explain_project_build",
    description=(
        "Explains how a GitHub project was built, using its README and file structure. Use ONLY for questions about the build process, tech stack, or how a project was developed. Do NOT use for general info or file listing—use get_github_project_details or list_project_files instead."
    ),
    annotations={
        "project_name": "The project name (can be partial or fuzzy)."
    }
)
def explain_project_build_tool(project_name: str):
    if not project_name:
        return {"error": "Project name must be provided."}
    projects_url = "https://api.github.com/users/ishaankor/repos"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    projects_resp = requests.get(projects_url, headers=headers)
    if projects_resp.status_code == 200:
        projects = projects_resp.json()
        match = fuzzy_match_project(project_name, projects)
        if "name" in match:
            repo_name = match["name"]
        else:
            return match
    else:
        repo_name = project_name
    url = f"https://api.github.com/repos/ishaankor/{repo_name}"
    readme_url = f"https://api.github.com/repos/ishaankor/{repo_name}/readme"
    contents_url = f"https://api.github.com/repos/ishaankor/{repo_name}/contents/"
    project_resp = requests.get(url, headers=headers)
    readme_resp = requests.get(readme_url, headers=headers)
    contents_resp = requests.get(contents_url, headers=headers)
    summary = {}
    if project_resp.status_code == 200:
        project = project_resp.json()
        summary["name"] = project["name"]
        summary["description"] = project.get("description", "No description provided")
        summary["url"] = project["html_url"]
        summary["language"] = project.get("language", "Not specified")
        summary["topics"] = project.get("topics", [])
    if readme_resp.status_code == 200:
        summary["readme"] = readme_resp.text
    else:
        summary["readme"] = "README not found."
    if contents_resp.status_code == 200:
        files = contents_resp.json()
        summary["files"] = [file["name"] for file in files if "name" in file]
    else:
        summary["files"] = []
    return json.dumps(summary, indent=2)

@mcp.tool(
    name="read_all_repo_files",
    description="Reads ALL files from a GitHub repository automatically. Fetches the content of all text files in the repo to understand the complete project structure and how it was built.",
    annotations={
        "project_name": "The GitHub project name (can be partial or fuzzy, e.g., 'ratings recipe', 'personal website')"
    }
)
def read_all_repo_files_tool(project_name: str):
    if not project_name:
        return {"error": "Project name must be provided."}
    
    projects_url = "https://api.github.com/users/ishaankor/repos"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    projects_resp = requests.get(projects_url, headers=headers)

    if projects_resp.status_code == 200:
        projects = projects_resp.json()
        match = fuzzy_match_project(project_name, projects)
        if "name" in match:
            repo_name = match["name"]
        else:
            return match
    else:
        repo_name = project_name
    
    def get_all_files(path=""):
        """Recursively get all files from the repository"""
        url = f"https://api.github.com/repos/ishaankor/{repo_name}/contents/{path}" if path else f"https://api.github.com/repos/ishaankor/{repo_name}/contents/"
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return []
        
        files = []
        items = response.json()
        
        for item in items:
            if item["type"] == "file":
                files.append(item)
            elif item["type"] == "dir":
                sub_files = get_all_files(item["path"])
                files.extend(sub_files)
        
        return files
    
    all_files = get_all_files()
    
    if not all_files:
        return {"error": f"No files found in repository '{repo_name}' or repository doesn't exist"}
    
    repo_content = {
        "project": repo_name,
        "total_files": len(all_files),
        "files": {}
    }
    
    readable_extensions = {
        '.py', '.js', '.ts', '.css', '.json', '.md', '.txt', '.yml', '.yaml', 
        '.xml', '.sql', '.sh', '.bash', '.env', '.gitignore', '.dockerfile', '.toml',
        '.ini', '.cfg', '.conf', '.csv', '.jsx', '.tsx', '.vue', '.php', 
        '.rb', '.go', '.java', '.cpp', '.c', '.h', '.cs', '.swift', '.kt', '.rs',
        '.r', '.scala', '.clj', '.hs', '.elm', '.dart', '.lua', '.pl', '.ps1'
    }
    
    excluded_patterns = {
        'graph.html', 'chart.html', '_graph.html', '_chart.html', 'plot.html',
        'visualization.html', 'vis.html', '.ipynb_checkpoints', '__pycache__',
        '.pyc', '.pyo', '.class', '.o', '.obj', '.dll', '.so', '.dylib',
        'node_modules', '.git', '.DS_Store', 'Thumbs.db'
    }
    
    for file_info in all_files:
        file_path = file_info["path"]
        file_name = file_info["name"]
        file_size = file_info["size"]
        
        if any(pattern in file_name.lower() or pattern in file_path.lower() for pattern in excluded_patterns):
            repo_content["files"][file_path] = {
                "name": file_name,
                "size": file_size,
                "content": f"[Excluded file: {file_name}]",
                "type": "excluded"
            }
            continue
        
        if file_size > 50000:
            repo_content["files"][file_path] = {
                "name": file_name,
                "size": file_size,
                "content": f"[File too large to display: {file_size} bytes]",
                "type": "large_file"
            }
            continue
        
        _, ext = os.path.splitext(file_name.lower())
        if ext not in readable_extensions and not any(name in file_name.lower() for name in ['readme', 'license', 'changelog', 'makefile', 'dockerfile']):
            repo_content["files"][file_path] = {
                "name": file_name,
                "size": file_size,
                "content": f"[Binary file not displayed]",
                "type": "binary"
            }
            continue
        
        file_url = f"https://api.github.com/repos/ishaankor/{repo_name}/contents/{file_path}"

        file_response = requests.get(file_url, headers=headers)

        if file_response.status_code == 200:
            content = file_response.text
            repo_content["files"][file_path] = {
                "name": file_name,
                "size": file_size,
                "content": content,
                "type": "text",
                "extension": ext
            }
        else:
            repo_content["files"][file_path] = {
                "name": file_name,
                "size": file_size,
                "content": f"[Error reading file: {file_response.status_code}]",
                "type": "error"
            }
    
    return json.dumps(repo_content, indent=2)

@mcp.tool(
    name="get_project_pages",
    description="Reads content from his deployed projects and websites to understand how they work and what they contain about the project's final output.",
    annotations={
        "project_name": "The project name (e.g., 'my-personal-website', 'data-science-portfolio', 'ratings-recipe-analysis') but it CAN BE a partial or fuzzy name",
        "path": "Optional. Specific path on the site (e.g., '/about', '/projects/demo.html'). Default: root page"
    }
)
def get_project_pages(project_name: str, path: str = ""):
    if not project_name:
        return json.dumps({"error": "Project name must be provided."}, indent=2)
    
    projects_url = "https://api.github.com/users/ishaankor/repos"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    projects_resp = requests.get(projects_url, headers=headers)

    actual_project_name = project_name
    
    if projects_resp.status_code == 200:
        projects = projects_resp.json()
        match = fuzzy_match_project(project_name, projects)
        if "name" in match:
            actual_project_name = match["name"]
            potential_names = [
                match["name"],
                match["name"].replace("_", "-"),
                match["name"].replace("-", "_"),
                match["name"].lower(),
                match["name"].replace(" ", "-").lower()
            ]
        else:
            potential_names = [
                project_name,
                project_name.replace("_", "-"),
                project_name.replace("-", "_"),
                project_name.lower(),
                project_name.replace(" ", "-").lower()
            ]
    else:
        potential_names = [
            project_name,
            project_name.replace("_", "-"),
            project_name.replace("-", "_"),
            project_name.lower(),
            project_name.replace(" ", "-").lower()
        ]
    
    last_error = None
    for name_attempt in potential_names:
        base_url = f"https://ishaankor.github.io/{name_attempt}"
        if path:
            if not path.startswith('/'):
                path = '/' + path
            url = base_url + path
        else:
            url = base_url
        
        try:
            headers = {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
                "X-GitHub-Api-Version": "2022-11-28",
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                try:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    text_content = soup.get_text()
                    
                    lines = (line.strip() for line in text_content.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    text_content = '\n'.join(chunk for chunk in chunks if chunk)
                    
                    return json.dumps({
                        "project": name_attempt,
                        "original_query": project_name,
                        "url": url,
                        "status_code": response.status_code,
                        "content": text_content,
                        "content_length": len(text_content),
                        "extraction_method": "BeautifulSoup (text only)"
                    }, indent=2)
                    
                except ImportError:
                    import re
                    html_content = response.text
                    
                    html_content = re.sub(r'<script.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
                    html_content = re.sub(r'<style.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
                    
                    text_content = re.sub(r'<[^>]+>', '', html_content)
                    
                    text_content = re.sub(r'\s+', ' ', text_content).strip()
                    
                    return json.dumps({
                        "project": name_attempt,
                        "original_query": project_name,
                        "url": url,
                        "status_code": response.status_code,
                        "content": text_content,
                        "content_length": len(text_content),
                        "extraction_method": "Regex (text only)"
                    }, indent=2)
            
            elif response.status_code == 404:
                last_error = f"Project '{name_attempt}' not found on GitHub Pages"
                continue
            else:
                last_error = f"HTTP {response.status_code} for '{name_attempt}'"
                continue
                
        except requests.exceptions.RequestException as e:
            last_error = f"Network error for '{name_attempt}': {str(e)}"
            continue
        except Exception as e:
            last_error = f"Unexpected error for '{name_attempt}': {str(e)}"
            continue
    
    return json.dumps({
        "error": f"Could not find GitHub Pages site for project matching '{project_name}'. Tried: {', '.join(potential_names)}",
        "last_error": last_error,
        "original_query": project_name,
        "attempted_names": potential_names,
        "suggestion": "Check if the project has GitHub Pages enabled or try a more specific project name"
    }, indent=2)

if __name__ == "__main__":
    mcp.run(transport='streamable-http')