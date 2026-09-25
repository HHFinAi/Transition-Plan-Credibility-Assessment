"""Offline source/package checks. Does not verify remote URLs or research accuracy."""
from __future__ import annotations
import hashlib
import json
import re
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from sf_agent import engine
from sf_agent.analytics import OPERATIONS
from sf_agent.validation import DataError,load_json,require,validate_dag,validate_request

def check(root=ROOT):
    config=load_json(root/'agent.json');metadata=load_json(root/'repository-metadata.json')
    for path in ('README.md','SKILL.md','AGENTS.md','LICENSE','CITATION.cff','WORKFLOW.md','docs/INSTITUTIONAL_QUALITY.md','docs/VALIDATION.md','docs/FAQ.md','docs/GEO_SEO.md','examples/reports/synthetic-packet.md','examples/reports/source-study-packet.md'):
        require((root/path).is_file(),f'missing file: {path}')
    for file in root.rglob('*.json'):
        if not any(part in {'runs','exports','.git'} for part in file.relative_to(root).parts): load_json(file)
    for route in config['routes'].values():
        validate_dag(route['nodes']);require(all(n['id'] in config['stages'] for n in route['nodes']),'unregistered stage')
    for stage in config['stages'].values():
        require((root/stage['prompt_path']).is_file(),'missing prompt')
    for skill in [root/'SKILL.md',*root.glob('skills/*/SKILL.md')]:
        text=skill.read_text();require(text.startswith('---\n'),'missing skill frontmatter')
        name=re.search(r'^name: ([a-z0-9-]+)$',text,re.M)
        require(name is not None and 1<=len(name[1])<=64,'invalid skill name')
        require(name[1]==(config['name'] if skill.parent==root else skill.parent.name),'skill/folder mismatch')
        require(bool(re.search(r'^description: .+',text,re.M)),'missing description')
    require(len(metadata['topics'])<=20 and len(metadata['topics'])==len(set(metadata['topics'])),'topic count/duplicates')
    require(all(re.fullmatch('[a-z0-9-]{1,50}',t) for t in metadata['topics']),'invalid topic')
    require(metadata['owner']=='HHFinAi','wrong owner')
    require(metadata['publication_status']=='prepared-not-published','unverified publication status')
    for f in ('synthetic-request.json','source-study-request.json','research-request-template.json'):
        validate_request(load_json(root/'examples'/f),config)
    core=load_json(root/'COMMON_CORE_MANIFEST.json')['files']
    for name,expected in core.items(): require(hashlib.sha256((root/'sf_agent'/name).read_bytes()).hexdigest()==expected,f'common runtime mismatch: {name}')
    # Markdown local links. Remote links are intentionally not requested here.
    for file in root.rglob('*.md'):
        if any(part in {'runs','exports','.git'} for part in file.relative_to(root).parts): continue
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',file.read_text()):
            if re.match(r'[a-zA-Z][a-zA-Z0-9+.-]*:',target) or target.startswith('#'):continue
            relative=target.split('#')[0]
            require((file.parent/relative).exists(),f'broken local link: {file.relative_to(root)} -> {target}')
    return {'agent':config['name'],'routes':len(config['routes']),'stages':len(config['stages']),'operations':len(OPERATIONS),'checks':'PASS','remote_urls_checked':False}

if __name__=='__main__':
    try: print(json.dumps(check(),indent=2))
    except (DataError,OSError,ValueError) as exc: print(f'ERROR: {exc}',file=sys.stderr);raise SystemExit(1)
